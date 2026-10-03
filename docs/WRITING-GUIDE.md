# Writing guide for dallasairandheating.com pages

Repo: /home/claude/dallas-hvac-pro (branch `build`). Read these first, in full:
1. `CLAUDE.md` (what the business is and the hard rules; read "What the business is" twice).
2. `INTAKE.md` and `SERVICES.md` (your page's URL, target keyword and figures).
3. `src/data/site.json` (slugs, names for services, guides and areas).
4. `src/templates/macros.html` (service_cards, guide_cards, area_pills, related, call_box,
   how_it_works_short, disclosure, license_check, sources).
5. MODEL PAGES from a sister site built with the same system for the same kind of business
   (Austin, a different city): `/home/claude/austin-hvac-content/src/pages/ac-repair.html` (service)
   and `/home/claude/austin-hvac-content/src/pages/round-rock-ac-repair.html` (area). Match their
   depth, section rhythm and component use, NEVER their wording, and never their Austin facts.
6. The old Dallas page at `docs/old-site/<slug>/index.html` (if one exists) for research leads only.
   Do not paste or lightly reword it; it was written in contractor voice and had invented claims.

## The business, in one paragraph
A free phone line. An automated assistant answers (469) 649-7066 any hour and transfers the caller to
an independent, locally owned heating and air conditioning company serving their part of DFW. That
company diagnoses, quotes, does the work and is paid by the customer. The line never repairs,
installs, quotes, schedules, supervises or guarantees anything, holds no license and may be paid a
referral fee. Always write "the company you are put through to", "a good technician", "the HVAC
company". Never "our technicians", "we repair", "we install", "we are licensed", "we'll send someone".
Do NOT say the connected companies are licensed or insured; tell readers to check the TDLR license.

## Hard rules (scripts/check.py enforces most)
- No em dashes or en dashes anywhere (copy, titles, descriptions, FAQs, alt text). Use commas,
  colons, periods or "to" ("95 to 100 degrees").
- No eyebrow labels, no badges.
- Never invent licenses, insurance, reviews, ratings, prices, years in business, team members, job
  counts, statistics, response times, guarantees or awards. Public statistics are fine with the source
  named. Prices: explain what drives price; a published range only with its source named on the page
  and a note that real quotes vary.
- Never name any HVAC company or brand-name contractor. Equipment brand names are unnecessary; avoid.
- Only Dallas-Fort Worth places. Never Houston, Austin, San Antonio or their suburbs (not even
  "unlike Houston"). Do not mention Orlando or Florida (check.py fails both: leftover from the
  system this was copied from).
- Banned words the checker catches: "free estimate(s)", "same-day", "guarantee(d)", "best price",
  "cheapest", "top-rated", "years of experience", "#1", "number one", "licensed and insured",
  "within 2 hours" and similar response-time promises.
- No DIY repair instructions for refrigerant, capacitors, contactors, electrical panels or gas.
  Safe checks are fine (thermostat, one breaker reset, filter, outdoor unit clear, condensate line
  and float switch visible). Gas smell: leave and call the gas utility (Atmos Energy serves most of
  DFW; verify for your city) or 911 from outside. CO alarm: get out and call 911.
- Every fact that is not common knowledge carries a source in the page's Sources list.

## Voice
Plain, specific, warm, DFW-local. Second person. Short paragraphs, about a 7th to 8th grade reading
level (explain a technical word the first time). Explain why. No filler ("In today's world", "look no
further"), no superlatives, no keyword stuffing. The target keyword appears naturally in the title, H1,
first paragraph, one H2 and the meta description. H1s use the "in [City]" phrasing where it reads
naturally ("AC Repair in McKinney, TX"), because the Sep 2026 research showed it wins in DFW.

## Page file format
`src/pages/<slug>.html` with YAML front matter, then `{% block content %}...{% endblock %}`.

```yaml
---
type: service            # service | guide | area
title: "..."             # 50 to 65 chars, unique, keyword near the front, ends "| Dallas Air & Heating" only if it fits
description: "..."       # 120 to 160 chars, unique, no dashes
h1: "..."                # one H1, unique
crumb: "AC Repair"
keyword: "ac repair mckinney tx"
city_name: "McKinney"    # area pages only (used in Service JSON-LD)
published: "2026-10-03"  # guides only
hero:
  image: mckinney-ac-repair-hero.jpg   # planned 1920x1080 photo, OR an existing photo used directly
  alt: "..."
  desc: "Image-generator prompt (only for a planned photo)."
  fallback: hvac-01-hero.jpg            # existing photo shown until the planned one exists
  fallback_alt: "..."                   # accurate alt for the fallback photo
  lead: "One or two sentences under the H1."
  secondary_label: "..."   # optional, a real page, never a form
  secondary_href: "/..."
schema_service:          # service and area pages
  name: "Free connection to a local AC repair company in McKinney, Texas"
  type: "Air conditioning repair referral"
cta_title: "..."         # short, specific to the page
faqs:                    # 3 to 6, phrased the way people actually ask
  - q: "..."
    a: "<p>...</p>"
---
```

## Building blocks (use existing classes only; do not edit CSS, templates or site.json)
- Reading column: `<section class="prose">...</section>`. Plain paragraphs, h2, h3, lists.
- Color break: `<section class="band band--tint"><div class="wide">...</div></section>`. The build
  turns these into bold steel-blue / burnt-orange bands with white text. Use ONE or TWO per page,
  with white prose sections between them; never two bands in a row; the FAQ band (automatic) and the
  final call band (automatic) come after your content, so do not end your content with a band.
- Two-column text and photo: inside `.prose`, `<div class="split"><div>text</div>{{ img(...) }}</div>`.
- `<ol class="steps">` numbered process; `<ul class="checks">` checklist; `<div class="grid-2 stack">`
  / `<div class="grid-3">` of `<div class="panel">` (add `panel--do` / `panel--dont`);
  `<ul class="facts">` of `<li><strong>label</strong>text</li>`; tables in
  `<div class="table-wrap"><table>` with `<caption class="sr">`, `<thead>`, `scope` on th;
  `<div class="note">` callout, `<div class="note note--orange">` warning.
- Macros: `{{ m.how_it_works_short() }}`, `{{ m.disclosure() }}`, `{{ m.license_check() }}`,
  `{{ m.call_box('text') }}`, `{{ m.service_cards(['slug', ...]) }}`, `{{ m.guide_cards(['slug']) }}`,
  `{{ m.area_pills(exclude='this-slug') }}`, `{{ m.related(['slug','guide:slug','area:slug'], 'Title') }}`,
  `{{ m.sources([{'label': '...', 'url': '...'}, ...]) }}`.

## Images
Call: `{{ img('file.jpg', 'alt', 1200, 800, desc='prompt', fallback='existing.jpg', fallback_alt='...') }}`.
An existing photo used directly needs no desc/fallback: `{{ img('dallas-about-attic.jpg', 'alt', 1200, 686) }}`.
Every content page: a hero plus at least two in-body images, no photo repeated within one page.
Alt text for photos with technicians must not imply they work for the line ("A technician checks...",
never "our technician"). The hvac-06 photos show a red service van: describe it neutrally.

### The 25 existing photos (src/static/images) — use these first
Heroes (1920x800): `hvac-hero.jpg` (technician working on a condenser beside a brick wall at sunrise),
`hvac-01-hero.jpg` (technician in gloves reading a gauge manifold at an outdoor unit, flower bed),
`hvac-02-hero.jpg` (two technicians servicing a condenser beside a white siding house, evening light),
`hvac-03-hero.jpg` (technician kneeling at large indoor air handlers with a multimeter, city view),
`hvac-04-hero.jpg` (large rooftop HVAC units, worker in a hard hat, downtown skyline),
`hvac-05-hero.jpg` (technician checking an indoor air handler and foil duct, close),
`hvac-06-hero.jpg` (technician walking with a tool bag to a red service van in a driveway at dusk).
Cards (1200x675, same scenes cropped): `hvac-01-card.jpg` to `hvac-06-card.jpg`.
1344x768: `dallas-about-hero.jpg` (two-story blue siding home, condenser beside it, big lawn, sunny),
`dallas-acrepair-hero.jpg` (technician crouched at a condenser beside a brick wall and wood fence),
`dallas-commercial-hero.jpg` (flat roof with rooftop units and a downtown skyline, bright sun),
`dallas-contact-hero.jpg` (smiling woman on a phone call in a bright living room),
`dallas-faq-hero.jpg` (older couple reviewing papers and a tablet at a kitchen table, mini-split on wall),
`dallas-furnace-hero.jpg` (finger pressing a wall thermostat, warm lamp light),
`dallas-install-hero.jpg` (two installers setting a new condenser beside a stone and brick home),
`dallas-services-hero.jpg` (two condensers beside a red brick home, green lawn),
`dallas-tuneup-hero-tech.jpg` (technician reading gauges at a condenser, brick home, wood fence).
1200x686: `dallas-about-attic.jpg` (attic air handler, flex ducts, pink insulation),
`dallas-about-technician.jpg` (SAME image as dallas-tuneup-hero-tech; do not use both on one page),
`dallas-services-furnace.jpg` (gas furnace with its front panel off, flashlight).

### Planned new photos (the "empty spots" Maurice will generate in Artistly)
Only where no existing photo fits. Each planned photo needs a unique, descriptive filename, a `desc=`
prompt and a `fallback=` existing photo. Prompt style: "Wide cinematic landscape shot, subject
positioned on the right third of the frame, well lit," then a specific, bright, realistic DFW scene
(the town's real housing style: e.g. 1960s ranch homes, newer two-story brick, limestone accents,
live oaks, cedar elms, Bradford pears, crape myrtles, wood privacy fences, flat North Texas sky),
"realistic photo, no text, no logos, no house numbers, no recognizable faces". Never use the word
"penetration" (Artistly's filter blocks it).

Per page:
- Area pages: hero = PLANNED `<slug>-hero.jpg` with the fallback assigned below, plus ONE planned
  in-body local photo `<town>-....jpg` (with fallback) and at least one existing photo used directly.
- Service and guide pages: hero = the existing photo assigned below, used directly (no planned hero).
  In-body: existing photos directly; at most ONE planned in-body photo where nothing existing fits
  (with fallback).

Assigned heroes (existing, used directly):
/ac-repair/ hvac-01-hero.jpg · /emergency-ac-repair/ hvac-06-hero.jpg · /ac-installation/
dallas-install-hero.jpg · /furnace-repair/ dallas-furnace-hero.jpg · /hvac-tune-up/ hvac-02-hero.jpg ·
/commercial-hvac/ hvac-04-hero.jpg · /hvac-company/ hvac-05-hero.jpg · /free-ac-guide/
dallas-services-hero.jpg.
Area hero fallbacks: McKinney hvac-hero · Frisco dallas-about-hero · Plano dallas-services-hero ·
Allen hvac-02-hero · Richardson dallas-acrepair-hero · Garland hvac-01-hero · Mesquite
dallas-tuneup-hero-tech · Irving hvac-03-hero · Carrollton dallas-install-hero · Lewisville
hvac-hero · Flower Mound dallas-about-hero · Denton hvac-01-hero · Fort Worth hvac-02-hero ·
Arlington dallas-services-hero · Grand Prairie dallas-acrepair-hero.

## Content each page needs
Service/guide pages (Prompt 9): what it is; who it is for; common problems; what a good technician
does and why; what to expect (process); options; Dallas-specific context (verified: heat records at
DFW Airport, Oncor as the electric wires utility in most of DFW, Atmos Energy gas, Winter Storm Uri
in Feb 2021, City of Dallas mechanical permits, etc., only as sources confirm); safe homeowner checks
where relevant; what to ask; related services; 3 to 6 FAQs; at least one distinctive design treatment
for this topic (symptom table, decision panels, timeline, checklist, comparison table). Around 1,500
to 2,200 words of page-specific copy. Sources list at the end.

Area pages (Prompt 11): hero; FIRST H2 names the town ("McKinney: ..."), with two local paragraphs
and a photo beside them (split); services genuinely relevant here (`m.service_cards`); a section titled
"Why [Town] homeowners call the line" with FOUR distinct local reasons as
`<div class="grid-2 stack">` of four `<div class="panel"><h3>..</h3><p>..</p></div>`, built only
from facts on that page plus what the line truly does (free, 24/7, transfers to an independent local
company, caller pays the company not the line, the site explains the TDLR license check); verified
local context (electric provider: Oncor wires and retail choice in most cities, BUT Garland is served
by Garland Power & Light and Denton by Denton Municipal Electric, and parts of Denton County by
co-ops such as CoServ: verify for your town; gas utility; housing age and type from census or city
data; growth; soil (expansive clay); weather events that hit the town, only as sources confirm; the
city's mechanical permit rules for HVAC replacement; any city or utility rebate); area FAQs;
`m.how_it_works_short()`; nearby areas (`m.area_pills(exclude=...)`); sources. Never claim an
office, address, job history, customer count or travel time. Each city page must be built around
what is actually different there.

## Research standard (this is what makes the page rank)
- Research each page on the web BEFORE writing it (WebSearch, then WebFetch on the URLs the search
  returns). Prefer primary sources: city websites (dallascityhall.com, mckinneytexas.org,
  friscotexas.gov, plano.gov, cityofallen.org, cor.net, garlandtx.gov, cityofmesquite.com,
  cityofirving.org, cityofcarrollton.com, cityoflewisville.com, flower-mound.com, cityofdenton.com,
  fortworthtexas.gov, arlingtontx.gov, gptx.org), TDLR (tdlr.texas.gov), Texas statutes, Oncor,
  Atmos Energy, ERCOT, PUC of Texas, NWS Fort Worth (weather.gov/fwd), NOAA, U.S. Census
  (census.gov QuickFacts), EPA, DOE (energy.gov), ENERGY STAR, ACCA, Texas A&M AgriLife.
- Every number, date, rule, phone number, fee and named program must come from a source you opened,
  and that source goes in the Sources list with its real URL. If you cannot verify it, leave it out.
- If a fact would be shared by many pages (e.g. a DFW heat record), say it in your own words on each
  page and only where it matters to that page; do not repeat the same paragraph.

## Validation (run from the repo root; NEVER a plain `python3 build.py`, it writes dist/)
```
python3 build.py --out /tmp/<your-name>/dist
python3 scripts/check.py --dist /tmp/<your-name>/dist --skip-links --only /<slug>/
```
Fix every ERROR for your pages. A WARN about word count under 1500 (which includes the template)
means the page is thin: add substance, not filler. Do not edit shared files (site.json, templates,
CSS, JS, build.py, check.py) or anyone else's pages. Do not commit or push.

When done, report: files written, word counts, a one-sentence factual summary of each area page's
town (for the service-areas page, max 20 words, no dashes), and any fact you could not verify and
therefore left out.
