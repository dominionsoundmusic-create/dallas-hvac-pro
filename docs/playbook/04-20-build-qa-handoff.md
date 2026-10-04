# Prompts 4 to 20 (Oct 3 2026)

**4 Business data.** All shared values in src/data/site.json (name, d/b/a, phone formats, 24/7,
CTA labels, origin, disclosures, empty social/analytics). No old names (Dallas HVAC Pro, Dallas
Metro HVAC Pro) anywhere in source or output.
**5 Brand.** Tokens in site.css: navy #0c1f2e / #12324a, orange #e85d26 buttons with navy text,
color breaks steel blue #1d5f8f and deep burnt orange #a8431a with white text. Hero capped at 700px.
**6 Navigation.** Services, Service Areas, Guides, How It Works, About, FAQ, Contact; EN/ES toggle;
footer with referral disclosure on every page.
**7 Homepage.** Full-width hero (hvac-hero.jpg), H1 "AC Repair in Dallas, TX...", two CTAs.
**8 Services overview.** /services/ with a problem-to-service table and every service.
**9 Services and guides (8 pages).** Each researched and written for its own keyword by a separate
writer, then validated. **10 Service areas overview** grouped by county. **11 Area pages (15)**,
each researched separately with a "Why [Town] homeowners call the line" section.
**12 About, FAQ (23 questions), how it works, privacy, terms.** **13 Contact** phone only, no forms
(check.py fails any form); free refrigerant guide is a one-click PDF. The PDF's courtesy page was
corrected from the old name to "Dallas Air & Heating".
**14 Reviews/social.** None exist; none added. **15 Media.** 25 existing photos reused; 35 planned
photos listed in docs/image-list.md, each with a fallback so no page has a hole.
**16 SEO.** check.py: 33 pages, 0 errors, 0 warnings (unique titles/descriptions, canonicals, OG,
one H1, one JSON-LD block, FAQ parity, sitemap, robots, links, images).
**17 Remnant sweep.** Old names, Orlando/tree leftovers, other cities, placeholders: none found.
**Independent fact-check.** Two separate agents re-checked every page against sources: 44 small
corrections (softened third-party claims, fixed dates and figures), all re-validated.
**18 Responsive.** Playwright, all routes at 1440/1024/768/390: no horizontal overflow, no JS errors.
**19 Functional.** All internal links resolve; all phone links tel:+14696497066. Not verified: live
404 status, translation toggle and phone routing (need the live site).
**20 Handoff.** Content and code ready on `build`; NOT deployed. To go live: Netlify production
branch -> build, publish "dist". Remaining: 35 photos to generate.
