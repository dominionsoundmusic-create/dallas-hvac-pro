# Prompts 1 to 3: fact brief, architecture, baseline (Oct 3 2026)

## 1 Client fact brief
Source: INTAKE.md (Maurice's statements, Sep 23 to Oct 3 2026) and SERVICES.md.

| Item | Value | Status |
|---|---|---|
| Name | Dallas Air & Heating, d/b/a of Dominion Digital Group | Confirmed |
| Category | Free phone line connecting callers with independent local HVAC companies | Confirmed |
| Services | 6 service pages, 2 guides | Confirmed |
| Areas | Dallas + 15 DFW cities (Sep 23 2026 research) | Confirmed |
| Address / email | Not displayed | Confirmed |
| Phone | (469) 649-7066, tel:+14696497066 (GHL "Dallas Trades") | Confirmed |
| Hours | Answered 24/7 by an automated assistant | Confirmed |
| CTA | Call; secondary links to real pages; no forms | Confirmed |
| Brand | Navy #0c1f2e, burnt orange #e85d26, existing logo | Confirmed |
| Partner licensing/insurance | Never claimed; TDLR check explained | Confirmed rule |
| Reviews, team, awards | None | Confirmed |
| Analytics, social | None yet | Deferrable |
| Domain | https://dallasairandheating.com | Confirmed |
Contradictions: none. Launch blocker: Netlify must be switched to the `build` branch with publish
"dist" when Maurice says "push". Deferred: 35 planned photos (pages show existing photos meanwhile).

## 2 Architecture
Static pre-rendered HTML (Python + Jinja2 build.py, YAML front matter, central src/data/site.json),
copied from treeserviceorlandofl.com. Every title, canonical, heading, body and JSON-LD is in the raw
HTML. Commands: `python3 build.py`, `python3 scripts/check.py`. PASS.

## 3 Baseline and route matrix
Old live site (repo root on main) moved to docs/old-site/ for reference. Every existing URL kept;
new: /services/ content rebuilt, /service-areas/, /how-it-works/, /hvac-company/. Retired form
thank-you pages redirect (src/static/_redirects). All 33 routes are static files; all indexable
except /404.html; all in the sitemap and nav or footer.
