# Dallas Air & Heating (dallasairandheating.com)

A static lead-generation site for a free phone line, (469) 649-7066, that connects Dallas-Fort Worth
callers with independent, locally owned heating and air conditioning companies. Owner: Maurice
Johnson, Dominion Digital Group (d/b/a Dallas Air & Heating). Rebuilt Oct 2026 with Playbook 2.0, using
the build system from treeserviceorlandofl.com and the HVAC conventions of austinacservice.com.

## Build
- Pages: `src/pages/*.html`, Jinja templates with YAML front matter. Shared data:
  `src/data/site.json` (business, services, guides, areas, nav). Templates in `src/templates/`.
- `python3 build.py` renders everything into `dist/` and writes `docs/image-list.md`.
- `python3 scripts/check.py` must report 0 errors before any commit.
- Netlify will publish `dist/` (netlify.toml, no build command). Work on the `build` branch.
  Do not push to `main`, deploy, or change Netlify settings unless Maurice says "push".
- The old live site is kept for reference in `docs/old-site/` (not published). Do not paste its text.

## What the business is (read twice)
Dallas Air & Heating is a FREE PHONE LINE and referral service. It never repairs, installs, maintains,
quotes or schedules anything itself, has no technicians, trucks or equipment, and holds no license.
An automated assistant answers 24/7, takes the caller's name, number, city/ZIP and what the system is
doing, and transfers the call to an independent, locally owned heating and air conditioning company.
That company diagnoses, quotes its own price, does the work and is paid directly by the customer. The
companies may pay the line a referral fee. The caller never pays the line.

## Hard rules for every page
1. Never write "our technicians", "our trucks", "our team", "we repair", "we install", "we are
   licensed/insured" or anything implying the line does HVAC work. Write "the company you are put
   through to", "a good technician", "the HVAC company".
2. Never invent licenses, certifications, insurance, reviews, ratings, prices the line charges, years
   in business, team members, job counts, response times, guarantees, awards or statistics. Do NOT
   claim the connected companies are licensed or insured. Tell the reader to ask for the TDLR license
   number and check it (`{{ m.license_check() }}`), and to ask for a certificate of insurance.
3. Never name an HVAC company (partner or competitor).
4. Only Dallas-Fort Worth places. No Houston, Austin, San Antonio or their suburbs, no other Texas
   regions. Statewide facts ("Texas law", "the Texas power grid") are fine.
5. No em dashes or en dashes anywhere in visible copy (use commas, colons, periods, "to" for ranges).
   No eyebrow labels above headings.
6. No DIY instructions for refrigerant, capacitors, contactors, electrical panels, gas valves or
   pilots. Safe homeowner checks are fine: thermostat mode/setting/batteries, one breaker reset,
   air filter, outdoor unit clear of debris, condensate line and float switch visible. Gas smell:
   leave the house and call the gas utility or 911 from outside. CO alarm: get out and call 911.
7. No prices presented as the line's prices. A published, sourced range may be cited with its source
   named in the text and in the Sources list, and must say real quotes vary.
8. Every page except privacy, terms and 404 has 3 to 6 `faqs` in front matter (written the way people
   actually ask), which render as the visible "Common questions" block AND FAQPage JSON-LD.
9. Every page has a hero image plus at least two in-body images via `{{ img(...) }}`, each with
   filename, alt, width and height. Use the existing photos first (catalogue in
   docs/WRITING-GUIDE.md). A planned new photo gets a `desc=` prompt and a `fallback=` existing photo
   so the page never shows a hole. Planned photos are listed in docs/image-list.md automatically.
10. Facts must be real and current. Research each page's topic or town on the web and cite every
    source used in the page's `m.sources([...])` list at the bottom. If you cannot verify a fact,
    leave it out.
11. Each page is written for its own keyword and topic. Never reuse paragraphs or sentence runs
    from another page with names swapped.
12. The footer referral disclosure appears on every page (site.json `short_disclosure`); check.py
    fails any page without it.

## Phone and disclosures
- Phone: (469) 649-7066, tel:+14696497066 (use `{{ site.business.phone_display }}` and
  `{{ site.business.phone_tel }}`; CTA label `{{ site.cta.primary_label }}`).
- Disclosure macro: `{{ m.disclosure() }}`. License check macro: `{{ m.license_check() }}`
  (TDLR license search: https://www.tdlr.texas.gov/LicenseSearch/).
