#!/usr/bin/env python3
"""Build the static Dallas Air & Heating site (dallasairandheating.com).

Pages live in src/pages as Jinja templates with a YAML front matter block.
Shared business data lives in src/data/site.json. Output goes to dist/.

Every URL is root level with a trailing slash (/ac-repair/, /plano-ac-repair/), matching the
URLs the live site already uses. A page can override its URL with `url:` in front matter
(privacy and terms keep their .html URLs).

Usage:
  python3 build.py                 # full build to dist/, also writes docs/image-list.md
  python3 build.py --out DIR       # build somewhere else (no docs written)
"""
import argparse
import html
import json
import re
import shutil
import struct
import sys
from pathlib import Path

import yaml
from jinja2 import ChainableUndefined, Environment, FileSystemLoader, pass_context
from markupsafe import Markup

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
PAGES = SRC / "pages"
STATIC = SRC / "static"
IMAGES = STATIC / "images"
CACHE = ROOT / ".imgcache"  # WebP copies made by the build (git-ignored; rebuilt if missing)
FM_RE = re.compile(r"\A---\n(.*?)\n---\n", re.S)
BUILD_DATE = "2026-10-03"
DEFAULT_HERO = "hvac-hero.jpg"
OG_DEFAULT = "og-default.jpg"


def image_size(path):
    """Return (width, height) for a JPEG/PNG/WebP file, or None."""
    data = path.read_bytes()
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        return struct.unpack(">II", data[16:24])
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        if data[12:16] == b"VP8X":
            w = int.from_bytes(data[24:27], "little") + 1
            h = int.from_bytes(data[27:30], "little") + 1
            return w, h
        return None
    if data[:2] == b"\xff\xd8":
        i = 2
        while i < len(data):
            marker = data[i + 1]
            length = struct.unpack(">H", data[i + 2:i + 4])[0]
            if marker in (0xC0, 0xC1, 0xC2):
                h, w = struct.unpack(">HH", data[i + 5:i + 9])
                return w, h
            i += 2 + length
    return None


def url_for_source(rel):
    """src/pages relative path -> public URL path."""
    parts = list(rel.with_suffix("").parts)
    if parts == ["index"]:
        return "/"
    if parts == ["404"]:
        return "/404.html"
    if parts[-1] == "index":
        parts = parts[:-1]
    return "/" + "/".join(parts) + "/"


def out_path_for(url, out):
    if url.endswith(".html"):
        return out / url.lstrip("/")
    return out / url.strip("/") / "index.html" if url != "/" else out / "index.html"


TABLE_RE = re.compile(r"<table>(.*?)</table>", re.S)
SECTION_RE = re.compile(r'<section class="band band--tint([^"]*)"')


def color_breaks(html_text):
    """Light bands become bold color breaks between white sections: the first is
    steel blue, the next burnt orange, and so on. The FAQ band is always burnt orange."""
    n = [0]
    def one(m):
        if "faq" in m.group(1).split():
            return '<section class="band band--tint band--accent%s"' % m.group(1)
        n[0] += 1
        return '<section class="band band--tint %s%s"' % ("band--blue" if n[0] % 2 else "band--accent", m.group(1))
    return SECTION_RE.sub(one, html_text)


CELL_RE = re.compile(r"<(th|td)\b([^>]*)>", re.S)


def label_table_cells(html_text):
    """Give each body cell a data-label with its column heading, so CSS can stack
    table rows as cards on narrow screens without horizontal scrolling."""
    def one(m):
        body = m.group(1)
        head = re.search(r"<thead>(.*?)</thead>", body, re.S)
        if not head:
            return m.group(0)
        labels = [strip_tags(h) for h in re.findall(r"<th\b[^>]*>(.*?)</th>", head.group(1), re.S)]

        def row(rm):
            i = [0]

            def cell(cm):
                n = i[0]
                i[0] += 1
                if n < len(labels) and labels[n] and "data-label" not in cm.group(2):
                    lab = html.escape(labels[n], quote=True)
                    return f'<{cm.group(1)}{cm.group(2)} data-label="{lab}">'
                return cm.group(0)
            return CELL_RE.sub(cell, rm.group(0))
        tbody = re.sub(r"<tr\b.*?</tr>", row, body[head.end():], flags=re.S)
        return "<table class=\"stack\">" + body[:head.end()] + tbody + "</table>"
    return TABLE_RE.sub(one, html_text)


def strip_tags(text):
    return html.unescape(re.sub(r"<[^>]+>", "", str(text))).strip()


class Builder:
    def __init__(self, out, write_docs):
        self.out = out
        self.write_docs = write_docs
        self.site = json.loads((SRC / "data" / "site.json").read_text())
        self.missing_images = {}  # filename -> dict
        alias_file = SRC / "data" / "image-aliases.json"
        self.aliases = json.loads(alias_file.read_text()) if alias_file.exists() else {}
        self._srcset_cache = {}
        self.env = Environment(
            loader=FileSystemLoader([str(SRC / "templates"), str(PAGES)]),
            undefined=ChainableUndefined,
            autoescape=False,
            trim_blocks=True,
            lstrip_blocks=True,
        )
        self.env.globals.update(
            site=self.site,
            img=self.img,
            webp_srcset=self.webp_srcset,
            picture=self.picture,
            image_exists=lambda f: bool(f) and (IMAGES / f).exists(),
            img_size=lambda f: image_size(IMAGES / f) or (1200, 750),
            svc=self.find("services"),
            guide=self.find("guides"),
            area=self.find("areas"),
        )
        self.env.filters["striptags_plain"] = strip_tags
        self.env.filters["tojson_ld"] = lambda v: Markup(
            json.dumps(v, ensure_ascii=False, indent=1).replace("</", "<\\/")
        )

    def find(self, key):
        items = {i["slug"]: i for i in self.site[key]}

        def get(slug):
            if slug not in items:
                raise KeyError(f"unknown {key} slug: {slug}")
            return items[slug]
        return get

    # ---- images -------------------------------------------------------
    # Phones should not download a 1920px JPEG. For every photo a page uses, the build makes
    # WebP copies at several widths (cached in .imgcache/ so rebuilds are fast) and the page
    # offers them through <picture> + srcset, so each browser fetches only the size it needs.
    # The original JPEG stays as the fallback <img src>.
    WEBP_WIDTHS = (480, 800, 1200, 1600, 1920)
    WEBP_QUALITY = 72

    def webp_srcset(self, file):
        """Return a srcset string of WebP copies for `file`, creating them if needed ('' if none)."""
        if not file or not file.lower().endswith((".jpg", ".jpeg", ".png")):
            return ""
        src = IMAGES / file
        if not src.exists():
            return ""
        if file in self._srcset_cache:
            return self._srcset_cache[file]
        from PIL import Image  # only needed when photos are present
        size = image_size(src)
        if not size:
            return ""
        full_w = size[0]
        widths = sorted({w for w in self.WEBP_WIDTHS if w < full_w} | {full_w})
        stem = Path(file).stem
        CACHE.mkdir(exist_ok=True)
        parts, im = [], None
        for w in widths:
            name = f"{stem}-{w}.webp"
            cached = CACHE / name
            if not cached.exists() or cached.stat().st_mtime < src.stat().st_mtime:
                if im is None:
                    im = Image.open(src).convert("RGB")
                h = round(im.height * w / im.width)
                out = im if w == im.width else im.resize((w, h), Image.LANCZOS)
                out.save(cached, "WEBP", quality=self.WEBP_QUALITY, method=6)
            shutil.copy2(cached, self.out / "images" / name)
            parts.append(f"/images/{name} {w}w")
        self._srcset_cache[file] = ", ".join(parts)
        return self._srcset_cache[file]

    def picture(self, file, alt, width, height, sizes, extra=""):
        """<picture> with WebP sources and the JPEG as fallback. `extra` goes on the <img>."""
        img = (f'<img src="/images/{file}" alt="{html.escape(alt, quote=True)}" '
               f'width="{width}" height="{height}"{extra}>')
        srcset = self.webp_srcset(file)
        if not srcset:
            return Markup(img)
        return Markup(f'<picture><source type="image/webp" srcset="{srcset}" sizes="{sizes}">{img}</picture>')

    @pass_context
    def img(self, ctx, file, alt, width, height, desc="", cls="", caption="", lazy=True,
            fallback="", fallback_alt=""):
        """Render an in-body figure.

        If `file` exists it is shown. If not, it is listed in docs/image-list.md and its tag is
        kept in the page as an HTML comment; if a `fallback` photo that exists is given, that
        photo is shown in its place so the layout never has a hole, a grey box or a broken image.
        """
        page = ctx.get("page", {})
        cap = f"<figcaption>{caption}</figcaption>" if caption else ""
        cls_attr = f' class="fig {cls}"' if cls else ' class="fig"'

        def tag(f, a, w, h):
            return (
                f'<img src="/images/{f}" alt="{html.escape(a, quote=True)}" width="{w}" height="{h}"'
                + (' loading="lazy" decoding="async"' if lazy else "")
                + ">"
            )
        planned = tag(file, alt, width, height)
        alt = self.alias_alt(file, alt)
        file = self.resolve_image(file)
        lazy_attr = ' loading="lazy" decoding="async"' if lazy else ""
        fig_sizes = "(max-width: 900px) 100vw, 900px"
        if (IMAGES / file).exists():
            w, h = image_size(IMAGES / file) or (width, height)
            shown = self.picture(file, alt, w, h, fig_sizes, lazy_attr)
            return Markup(f"<figure{cls_attr}>{shown}{cap}</figure>")
        self.note_missing(file, width, height, alt, desc, page.get("url", "?"))
        comment = f"<!-- image pending (see docs/image-list.md): {planned} -->"
        if fallback and (IMAGES / fallback).exists():
            w, h = image_size(IMAGES / fallback)
            shown = self.picture(fallback, fallback_alt or alt, w, h, fig_sizes, lazy_attr)
            return Markup(f"{comment}<figure{cls_attr}>{shown}{cap}</figure>")
        return Markup(comment)

    def resolve_image(self, file):
        """A planned photo that does not exist yet can be filled by an existing photo listed
        in src/data/image-aliases.json, so one good photo can serve several pages."""
        if file and not (IMAGES / file).exists():
            alias = self.aliases.get(file)
            src = alias.get("src") if isinstance(alias, dict) else alias
            if src and (IMAGES / src).exists():
                return src
        return file

    def alias_alt(self, file, alt):
        """Alt text for an aliased photo: the alias's own alt if given, else the planned alt."""
        alias = self.aliases.get(file)
        return alias.get("alt", alt) if isinstance(alias, dict) else alt

    def note_missing(self, file, width, height, alt, desc, url):
        entry = self.missing_images.setdefault(
            file, {"file": file, "size": f"{width}x{height}", "alt": alt, "desc": desc, "pages": []}
        )
        if url not in entry["pages"]:
            entry["pages"].append(url)
        if desc and not entry["desc"]:
            entry["desc"] = desc

    # ---- pages --------------------------------------------------------
    def load_pages(self):
        pages = []
        for path in sorted(PAGES.rglob("*.html")):
            rel = path.relative_to(PAGES)
            if rel.parts[0].startswith("_"):
                continue
            text = path.read_text()
            m = FM_RE.match(text)
            if not m:
                raise SystemExit(f"{rel}: missing front matter")
            meta = yaml.safe_load(m.group(1)) or {}
            meta["url"] = meta.get("url") or url_for_source(rel)
            meta["source"] = str(rel)
            meta["body"] = text[m.end():]
            pages.append(meta)
        return pages

    def render(self, page, pages):
        layout = page.get("layout", "page")
        hero = page.get("hero")
        if hero:
            if hero.get("image"):
                hero["alt"] = self.alias_alt(hero["image"], hero.get("alt", ""))
            want = self.resolve_image(hero.get("image"))
            if want and not (IMAGES / want).exists():
                self.note_missing(want, 1920, 1080, hero.get("alt", ""), hero.get("desc", ""), page["url"])
                fb = hero.get("fallback", DEFAULT_HERO)
                hero["render_image"] = fb if fb and (IMAGES / fb).exists() else ""
                hero["render_alt"] = hero.get("fallback_alt", hero.get("alt", ""))
            else:
                hero["render_image"] = want
                hero["render_alt"] = hero.get("alt", "")
            size = image_size(IMAGES / hero["render_image"]) if hero["render_image"] else None
            hero["w"], hero["h"] = size if size else (1920, 1080)
        page.setdefault("breadcrumbs", self.breadcrumbs(page))
        page["jsonld"] = self.jsonld(page)
        source = (
            '{% extends "layouts/' + layout + '.html" %}\n'
            '{% import "macros.html" as m with context %}\n' + page["body"]
        )
        tpl = self.env.from_string(source)
        return label_table_cells(tpl.render(page=page, pages=pages))

    # ---- breadcrumbs + structured data --------------------------------
    def breadcrumbs(self, page):
        url = page["url"]
        if url in ("/", "/404.html") or page.get("noindex"):
            return []
        crumbs = [{"label": "Home", "href": "/"}]
        if page.get("type") == "area":
            crumbs.append({"label": "Service Areas", "href": "/service-areas/"})
        if page.get("type") == "service":
            crumbs.append({"label": "Services", "href": "/services/"})
        crumbs.append({"label": page.get("crumb", page.get("h1", page["title"])), "href": url})
        return crumbs

    def jsonld(self, page):
        b = self.site["business"]
        origin = b["origin"]
        url = origin + page["url"]
        org_id = origin + "/#organization"
        areas = [{"@type": "City", "name": "Dallas", "containedInPlace": {"@type": "State", "name": "Texas"}}] + [
            {"@type": "City", "name": a["city"]} for a in self.site["areas"] if a["city"] != "Dallas"
        ]
        org = {
            "@type": "Organization",
            "@id": org_id,
            "name": b["name"],
            "legalName": b["legal_name"],
            "url": origin + "/",
            "logo": origin + b["logo"],
            "telephone": b["phone_tel"],
            "description": b["description"],
            "foundingDate": b["founded"],
            "areaServed": areas,
            "contactPoint": {
                "@type": "ContactPoint",
                "telephone": b["phone_tel"],
                "contactType": "customer service",
                "availableLanguage": ["English"],
                "hoursAvailable": {
                    "@type": "OpeningHoursSpecification",
                    "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
                    "opens": "00:00",
                    "closes": "23:59",
                },
            },
        }
        same_as = [v for v in self.site["social"].values() if v]
        if same_as:
            org["sameAs"] = same_as
        graph = [org]
        if page["url"] == "/":
            graph.append({"@type": "WebSite", "@id": origin + "/#website", "url": origin + "/",
                          "name": b["name"], "publisher": {"@id": org_id}, "inLanguage": "en-US"})
        if page["url"] == "/404.html":
            return {"@context": "https://schema.org", "@graph": graph}
        image = origin + "/images/" + ((page.get("hero") or {}).get("render_image") or OG_DEFAULT)
        webpage = {
            "@type": "WebPage",
            "@id": url + "#webpage",
            "url": url,
            "name": page["title"],
            "description": page["description"],
            "isPartOf": {"@type": "WebSite", "@id": origin + "/#website", "url": origin + "/", "name": b["name"]},
            "about": {"@id": org_id},
            "primaryImageOfPage": {"@type": "ImageObject", "url": image},
            "inLanguage": "en-US",
        }
        if page.get("type") == "contact":
            webpage["@type"] = "ContactPage"
        if page.get("type") == "about":
            webpage["@type"] = "AboutPage"
        graph.append(webpage)
        crumbs = page.get("breadcrumbs") or []
        if crumbs:
            graph.append({
                "@type": "BreadcrumbList",
                "@id": url + "#breadcrumb",
                "itemListElement": [
                    {"@type": "ListItem", "position": i + 1, "name": c["label"], "item": origin + c["href"]}
                    for i, c in enumerate(crumbs)
                ],
            })
            webpage["breadcrumb"] = {"@id": url + "#breadcrumb"}
        svc = page.get("schema_service")
        if svc:
            area = areas
            if page.get("type") == "area":
                area = {"@type": "City", "name": page["city_name"],
                        "containedInPlace": {"@type": "State", "name": "Texas"}}
            graph.append({
                "@type": "Service",
                "@id": url + "#service",
                "name": svc["name"],
                "serviceType": svc["type"],
                "description": svc.get("description", page["description"]),
                "provider": {"@id": org_id},
                "areaServed": area,
                "url": url,
                "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD",
                           "description": "Calling the line and being connected is free. The independent HVAC company quotes its own price for any work."},
            })
        if page.get("type") == "guide":
            graph.append({
                "@type": "Article",
                "@id": url + "#article",
                "headline": page["h1"],
                "description": page["description"],
                "image": image,
                "datePublished": page.get("published", BUILD_DATE),
                "dateModified": page.get("modified", BUILD_DATE),
                "author": page.get("author_ld") or {"@id": org_id},
                "publisher": {"@id": org_id},
                "mainEntityOfPage": {"@id": url + "#webpage"},
                "inLanguage": "en-US",
            })
        faqs = page.get("faqs") or []
        if faqs:
            graph.append({
                "@type": "FAQPage",
                "@id": url + "#faq",
                "mainEntity": [
                    {"@type": "Question", "name": strip_tags(f["q"]),
                     "acceptedAnswer": {"@type": "Answer", "text": re.sub(r"\s+", " ", strip_tags(f["a"]))}}
                    for f in faqs
                ],
            })
        return {"@context": "https://schema.org", "@graph": graph}

    def build(self):
        if self.out.exists():
            shutil.rmtree(self.out)
        shutil.copytree(STATIC, self.out)
        pages = self.load_pages()
        index = {p["url"]: p for p in pages}
        failed = []
        for page in pages:
            try:
                html_out = self.render(page, index)
            except Exception as e:  # report and keep building the other pages
                failed.append(f"{page['source']}: {type(e).__name__}: {e}")
                continue
            dest = out_path_for(page["url"], self.out)
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(color_breaks(html_out))
        self.write_sitemap(pages)
        self.write_robots()
        if self.write_docs:
            self.write_image_list()
        print(f"Built {len(pages) - len(failed)} pages into {self.out}")
        for f in failed:
            print("FAILED", f)
        if failed:
            raise SystemExit(1)
        if self.missing_images:
            print(f"{len(self.missing_images)} planned images still to generate (docs/image-list.md)")

    def write_sitemap(self, pages):
        origin = self.site["business"]["origin"]
        urls = [p for p in pages if not p.get("noindex") and p["url"] != "/404.html"]
        lines = ['<?xml version="1.0" encoding="UTF-8"?>',
                 '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
        for p in sorted(urls, key=lambda p: (p["url"] != "/", p["url"])):
            lines.append(f"  <url><loc>{origin}{p['url']}</loc><lastmod>{BUILD_DATE}</lastmod></url>")
        lines.append("</urlset>")
        (self.out / "sitemap.xml").write_text("\n".join(lines) + "\n")

    def write_robots(self):
        origin = self.site["business"]["origin"]
        (self.out / "robots.txt").write_text(
            "User-agent: *\nAllow: /\n\n"
            f"Sitemap: {origin}/sitemap.xml\n"
        )

    def write_image_list(self):
        rows = sorted(self.missing_images.values(), key=lambda e: (e["size"] != "1920x1080", e["pages"][0], e["file"]))
        out = [
            "# Images still to generate",
            "",
            "Generated by build.py. Every image below already has its tag in the page template.",
            "Until the file exists in src/static/images/, the built page keeps the tag as an HTML",
            "comment and shows an existing photo in its place (or nothing), never a broken image or a",
            "grey box. Generate each one, save it under the exact filename and size below in",
            "src/static/images/, run `python3 build.py`, and it appears on the page.",
            "",
            "Style for every image: bright, clearly visible, Dallas-Fort Worth homes, yards and HVAC",
            "equipment, natural daylight, no text, no logos, no watermarks, no recognizable faces.",
            "Hero photos: wide cinematic landscape shot, subject on the right third of the frame, so",
            "the left side stays calm for the headline.",
            "",
            "Suggested order: the 1920x1080 heroes first (they show on screen straight away), then the",
            "in-body images page by page.",
            "",
            f"Total: {len(rows)} images.",
            "",
        ]
        for n, e in enumerate(rows, 1):
            out += [
                f"## {n}. {e['file']}",
                "",
                f"- Size: {e['size']} px",
                f"- Page(s): {', '.join(e['pages'])}",
                f"- Alt text: {e['alt']}",
                "",
                f"Prompt: {e['desc'] or e['alt']}",
                "",
            ]
        (ROOT / "docs" / "image-list.md").write_text("\n".join(out))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ROOT / "dist"))
    args = ap.parse_args()
    out = Path(args.out).resolve()
    Builder(out, write_docs=(out == ROOT / "dist")).build()


if __name__ == "__main__":
    sys.exit(main())
