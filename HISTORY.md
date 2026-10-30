# History & maintenance guide

This file records how the site was built, where every piece of content came
from, what decisions were made, and what is still to do — so that future
updates are easy to pick up without reverse-engineering anything.
For repo structure and publication-list mechanics, see also `README.md`.

## Quick reference: where to add things

For step-by-step instructions for every update task, see **`UPDATING.md`**.
The short version:

| I want to add… | Do this |
| --- | --- |
| A new paper or preprint | Add a tuple to `PUBS` in `tools/build_pubs.py` (set flag `"preprint"` for unpublished work), run `python3 tools/build_pubs.py`, commit |
| A project | Add an `<article class="project-card">` in `projects.html` (ongoing projects), or a card in the "Past projects" grid |
| A model or tool | Add an `<article class="project-card">` (developed models) or a card in the grids of `models.html` |
| A CV entry | `index.html` — the `<ol class="timeline">` block |
| A page-wide footer/header link | Every page duplicates the header nav and footer — edit all four `.html` files consistently (`tools/build_pubs.py` holds the template used to generate `publications.html`) |
| An image | Put the file in `assets/img/`, check its licence, and credit it in the footer "Credits" column |

## Build log

### 2026-10-28 — initial build (first draft)

- Cloned the repo (previously contained only `index.md` saying "test site").
- Content mined from: Google Scholar profile (user `FMPvz8gAAAAJ`), the old
  Google Site (jennielthomas.fr), the OPERA group site (ige-opera.github.io),
  the CRiceS (crices-h2020.eu), CERTAINTY (certainty-aci.eu) and ANR project
  pages, and Wikimedia Commons (hero image).
- Built six hand-written pages (no framework, no build step) plus
  `assets/css/style.css`, favicon, `.nojekyll`.
- Wrote `tools/build_pubs.py`: generates `publications.html` from a curated
  list, enriching each entry from the Crossref API (DOI, full author list,
  journal, volume, pages). Responses cached in `tools/crossref_cache.json`.
- Banner photo (Arctic ice) used under CC BY-SA 3.0 with attribution in the
  footer. Profile photo taken from the OPERA group site.
- Committed as "First draft of new research profile site".

### 2026-10-28 — projects & preprints updates

- Added two ANR projects (as IGE partner): **Bubbleplast** (2023–2027, ANR-23-CE34-0012)
  and **ATMO-PLASTIC** (2020–2024, concluded, ANR-20-CE34-0014) to `projects.html`.
- Added preprint **"Reduced global atmospheric microplastic emissions from
  size-harmonized observations"** (Hough et al., Research Square, under review,
  DOI 10.21203/rs.3.rs-10231003/v1).
- Restructured the publications page: unpublished preprints are listed in a
  dedicated "Preprints & under review" section; published work is grouped by
  year. The script re-checks preprints on every run and **automatically moves
  them to the year sections once Crossref reports the accepted final version**.
  Example: Segur et al. (power-law microplastic size distributions) moved from
  preprint to *Microplastics and Nanoplastics* 6, 45 (2026) this way.
- Created this file.

### 2026-10-28 — ERCA on the teaching page

- Added **ERCA (European Research Course on the Atmosphere)** to the teaching
  page: Jennie has co-directed the Grenoble school with Hélène Angot since
  2025 (initial direction team with Emmanuel Cosme). Sources: the
  [UGA ERCA 2026 page](https://faculte-sciences.univ-grenoble-alpes.fr/international/erca-2026/),
  the [OSUG course page](https://www.osug.fr/en/missions/research/scientific-events/erca-european-research-course-on-atmospheres.html),
  and the [IGE announcement](https://www.ige-grenoble.fr/New-Direction-team-announced-for-the-European-Research-Course-on-Atmospheres).

### 2026-10-28 — review round: site streamlined to four pages

Applied Jennie's feedback series:

- **Profile photo removed** from the home page (did not look right); the
  `assets/img/profile.png` file and its footer credit were removed too.
- **Citation metrics block removed** from the home page hero.
- **1D modeling re-framed as past work** (home page hero + About + open-science
  card reworded; PACT-1D moved to "Past developments" on the models page).
- **New dedicated Models page** (`models.html`): current developments
  **WRF-Chem-Polar** ([wrf-chem-polar.eu](https://wrf-chem-polar.eu)) and the
  **microplastics-enabled GEOS-Chem**
  ([GEOS-Chem-IGE](https://github.com/GEOS-Chem-IGE): GCClassic-MP, HEMCO-MP,
  GEOS-Chem-infra); tools used (FLEXPART, FLEXPART-WRF); past developments
  (PACT-1D). The old WRF-Chem card is superseded by the WRF-Chem-Polar entry.
- **Group & supervision, Teaching (incl. ERCA) and News pages removed** on
  request. Navigation is now Home · Publications · Models · Projects. ERCA
  currently has no mention on the site — re-add on the home page or
  publications page if desired.
- **OPERA team link** added to the home page About text.
- **Rejected preprint removed** (Cesler-Maloney et al., Fairbanks boundary
  layers). 87 entries remain, 2 of them preprints (Hough et al., Price et al.).
- **Style feedback**: research-interests subtitle line removed; page-hero
  headings no longer sit on an ice-blue background (now white, avoiding
  blue-on-blue); profile photo removed from the hero at Jennie's request;
  hero links recolored (light ice blue with underline) so they stay readable
  over the banner image.
- **Em-dashes removed from all site copy** (they read as an AI-generation
  tell). Page titles now use "|"; prose uses commas, colons and parentheses.
  En-dashes in scientific compounds (e.g. "aerosol–cloud") are kept, as they
  are standard in the field.
- **ORCID and X/Twitter links removed** site-wide (footers, publications
  lede, CV section). Footer links are now Google Scholar, IGE, OPERA group.

### 2026-10-28 — content trimming, project logos, publications cleanup

Second review round (commits `cb9dd92`, `c3b09bd`, `a15cc0d`); `UPDATING.md`
was written between the rounds as the step-by-step guide for future updates:

- **Home**: "Featured publications" section removed; CERTAINTY in the About
  text now links to [certainty-aci.eu](https://certainty-aci.eu); the CV
  section is titled "Short Curriculum Vitae" with no sub-title.
- **Publications page**: the intro paragraph under the heading was removed,
  then a one-line "complete record on Google Scholar" link restored under
  the heading at Jennie's request (the old paragraph had carried the page's
  only Google Scholar link). The browse-by-year tab strip and per-year
  publication counts are gone: year headings are bare ("2026", "2025", …)
  and the preprints section says just "Preprints & under review". The search
  filter box stays.
- **Models / Projects pages**: intro paragraphs under the page headings
  removed (headings stand alone, as on Publications).
- **Project logos**: the CERTAINTY and CRiceS cards on `projects.html` show
  their project logos (floated top-right, stacked above the text on narrow
  screens), resampled to 800px wide from the originals. Sources:
  CERTAINTY from the site's declared logo on
  [certainty-aci.eu](https://certainty-aci.eu); CRiceS from the project's
  [Zenodo community](https://zenodo.org/communities/crices-h2020) logo
  (identical to the project site's banner image). Credited in the footer
  "Credits" column — which, like all footer changes, meant editing the four
  pages plus the `PAGE_TEMPLATE` and regenerating `publications.html`.
  **Bubbleplast and ATMO-PLASTIC have no logos**: the ANR projects have no
  websites and the ANR pages carry only ANR branding.
- **Dead CSS removed** after auditing every class in `style.css` against all
  pages and the build script: featured-pubs and news-list styles, the hero
  stats block, `.page-lede`, `.year-jump`, `.badge`/`.badge-preprint`,
  `.people-note` (old group page), `.hero-photo` and `.more-link`. The audit
  now comes back clean.

### 2026-10-30 — publication cleanup, past-project links, ICE-ARC

- **Removed two publications that are not Jennie's**: "Climate change in the
  Arctic" (2014) and "Developing oil and gas resources in Arctic waters"
  (2014), both curated as chapters of the EU report *Strategic Assessment of
  Development of the Arctic*. Verified against the official PDF (University
  of Lapland repository, 183 pp.): those chapters are by Mikko Strahlendorff
  and Michał Łuszczuk, and "Thomas" appears nowhere in the report — the
  entries look like a Google Scholar author merge. Because the titles are
  generic, the Crossref matcher had also attached the wrong papers to them
  on the live page (Bracegirdle & Stephenson, *Journal of Climate* 26,
  669-678; Nair, *Journal of Unconventional Oil and Gas Resources* 6, 1-3).
  Removed both tuples from `PUBS`, purged the wrong cache records, and
  regenerated the page: 85 entries, all with Crossref DOIs.
- **Verified** the similar-looking 2016 chapters in *The Changing Arctic and
  the European Union* (Brill): publisher metadata lists Jennie Thomas as
  co-author of both "Arctic offshore hydrocarbons and the European Union:
  more constraints and less opportunities" and "Changes in Arctic maritime
  transport", so they stay.
- **iCUPE link fixed** on `projects.html`: now points to
  <https://www.atm.helsinki.fi/icupe/> (the old deep link returns 404).
- **NETCARE link fixed**: now points to the project's ACP special issue,
  <https://acp.copernicus.org/articles/special_issue835.html>
  (netcare-project.ca is a parked domain for sale).
- **ICE-ARC added** to "Past projects" (EU FP7, 2014-2017, quantifying the
  global economic and societal costs of Arctic change), linked to its CORDIS
  results article *The high cost of Arctic change* — the project website is
  dead, so the CORDIS article is the most stable reference.
- **ACCESS link fixed**: now points to its CORDIS project reporting page,
  <https://cordis.europa.eu/project/id/265863/reporting> (access-eu.org
  serves unrelated spam content). With this, all "Past projects" links are
  verified working; the PARCS and CATCH sites are still alive.
- **Author-name typo fixed**: Crossref metadata for the Linke et al. 2026
  *Journal of Climate* paper rendered "BjØrn H. Samset"; corrected to
  "Bjørn H. Samset" in the cached record and the page regenerated. If the
  entry is ever re-fetched from Crossref, the typo will come back.
- **Full author names on the publications page**: first names expanded,
  middle names kept as initials ("William R. Simpson"), Jennie shown as
  "Jennie L. Thomas" throughout. New pipeline in `tools/build_pubs.py`:
  Crossref records now store raw author data (`cr_authors`) in
  `tools/crossref_cache.json`; the display list is rebuilt on every run.
  Abbreviated first names are expanded from `MANUAL_NAME_FIXES` (hand-verified
  names: 25 from ORCID records, 8 from OpenAlex author profiles checked
  against their institutions — Schlager, Dibb, Flemming, Scheibe, Boxe,
  Stock, Baumann, Roiger, Dahlkötter, Platt — and 5 confirmed by Jennie:
  von Glasow, von Salzen, Klán, Le Roux, Denier van der Gon) and from
  OpenAlex author profiles (cached in `tools/openalex_cache.json`). The
  careful checks corrected several near-miss guesses: A. Roiger is **Anke**
  (not Andreas), G. Pfister is **Gabriele** (not Guido), D. W. Toohey is
  **Darin** (not David), S. Starkweather is **Sandra** (not Sarah),
  S.-W. Kim is **Sang-Woo** (not Sang-Won), and A. Reiter is **Annika**.
  An expansion only applies when the candidate first name matches the
  Crossref initials. Three co-authors stay as initials on purpose (unknown
  full names, Jennie's decision): M. Piot (GSHOX, LATMOS), M. Rose and
  J. Kim (ACCESS campaign, DLR IPA) — listed in `INTENTIONALLY_ABBREVIATED`.
  Compound surnames are protected from middle-initial abbreviation
  (Carlos Pérez García-Pando, Beatriz Ferreira Araujo), and names published
  with a leading initial keep it when no fuller form is verifiable
  (V. Faye McNeill, V. Holly L. Winton, W. Richard Leaitch). The build now
  prints any author it could not expand, so this cannot silently regress.
  The conventions, the verified-name decision log (with ORCID sources) and
  the new-paper checklist are documented in **`NAMES.md`**, which mirrors the
  script's name data one-to-one.
- **R. Benny Gerber corrected** (follow-up the same day): the OpenAlex
  expansion had rendered him "Robert B. Gerber"; Jennie pointed to his
  research-group page at the Hebrew University of Jerusalem
  (<https://robert-benny-gerber.huji.ac.il/>), which publishes him as
  "R. Benny Gerber". Added a `MANUAL_NAME_FIXES` entry to keep the leading
  initial (rule N4 in `NAMES.md`) and regenerated the page.
- **Published name forms pinned** (Jennie-confirmed, same day):
  "Kathy S. Law" everywhere — Crossref deposits "Katharine S." on 3 papers
  and "Kathy" without the middle initial on 2, while OpenAlex consistently
  says Kathy; "Christopher M. Polashenski" — his Dartmouth faculty page,
  <https://engineering.dartmouth.edu/community/faculty/christopher-polashenski>;
  "Gérard Ancellet" with the accent — his theses.fr person record,
  <https://theses.fr/081917821>. All three are `GIVEN_ALIASES` entries, now
  applied after expansion so they also catch OpenAlex-derived variants. The
  Ancellet middle initial (present on 4 of his 9 slots) remains open in
  `NAMES.md`.

## Publication list: scope decisions

- 85 curated entries: peer-reviewed articles, book chapters (*Sea Ice*,
  *The Changing Arctic and the European Union*), and preprints.
- Excluded from the Google Scholar record: an ACPD discussion-paper duplicate,
  a BAMS supplement duplicate, a 2022 ACS correction notice, the POLAR 2018
  conference abstract, the 2007 PhD thesis, and the two *Strategic Assessment
  of Development of the Arctic* chapters (removed 2026-10-30, see build log:
  authored by Strahlendorff and Łuszczuk, not by Jennie).
- Name bolding is automatic: any author with family name "Thomas" and a given
  name starting with "J" is bolded.
- The Crossref matcher rejects preprint/discussion versions of papers that
  have a final version, conference abstracts (EGU `egusphere-eguNN-*` DOIs), and
  records whose journal name is missing. *Faraday Discussions* is treated as a
  peer-reviewed journal.
- Manually verified DOIs that Crossref search fails to rank well live in
  `DOI_OVERRIDES` in `tools/build_pubs.py` (currently: the ACP Arctic aerosol
  overview paper; the Hough et al. Research Square preprint).

## Known TODOs (need Jennie's input)

- [ ] **Profile photo** — none on the site since the review round; add a favourite to the home page hero when available (the `.hero-photo` rules were removed in the 2026-10-28 dead-CSS pass; restore them from git history if wanted).
- [ ] **ORCID** — the record (0000-0003-2243-8137) contains an erroneous entry ("Cada-3 System Review", 2026) worth removing.
- [ ] **Spot-check DOIs** — Crossref metadata is usually right but can carry
      typos. The one known instance ("BjØrn" for "Bjørn", Linke et al.,
      Journal of Climate 39) was corrected in the cached record on 2026-10-30;
      if that entry is ever re-fetched from Crossref the typo would return.
- [ ] **Old website** — jennielthomas.fr is retired/maintained separately by Jennie; consider adding a link there to this site.
- [ ] **Author-name confirmations** — see the "Open items" section of
      `NAMES.md` (2026-10-30): full names for M. Piot, M. Rose and J. Kim
      (ask the co-authors); confirm the OpenAlex-sourced expansions (Narayana
      P. Anilkumar, Min H. Kuo, Ragnhild B. Skeie, the Allens, Chris D.
      Holmes); decide the Ancellet middle initial (M. on 4 papers, none on
      the other 5). (Kathy S. Law, Christopher M. Polashenski, Gérard
      Ancellet and R. Benny Gerber were settled on 2026-10-30.)

## Image licences

| Image | Source | Licence |
| --- | --- | --- |
| `arctic-hero.jpg` | [Arctic Ice 2.JPG](https://commons.wikimedia.org/wiki/File:Arctic_Ice_2.JPG) by Pink floyd88 a, via Wikimedia Commons | [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/) — credited in site footer |
| `favicon.svg` | Created for this site | — |
| `logo-certainty.png` | CERTAINTY project logo, via [certainty-aci.eu](https://certainty-aci.eu) | Project branding; used to identify the project; credited in site footer |
| `logo-crices.png` | CRiceS project logo, via the [CRiceS Zenodo community](https://zenodo.org/communities/crices-h2020) | Project branding; used to identify the project; credited in site footer |

## Deployment

Push to `main` — GitHub Pages rebuilds the site in about a minute
(live at <https://jenniethomas.github.io>). No build step needed server-side;
`.nojekyll` makes sure files are served exactly as committed.
