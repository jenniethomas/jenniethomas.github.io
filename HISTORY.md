# History & maintenance guide

This file records how the site was built, where every piece of content came
from, what decisions were made, and what is still to do — so that future
updates are easy to pick up without reverse-engineering anything.
For repo structure and publication-list mechanics, see also `README.md`.

## Quick reference: where to add things

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

## Publication list: scope decisions

- 88 curated entries: peer-reviewed articles, book chapters (*Sea Ice*,
  *The Changing Arctic and the European Union*, *Strategic Assessment of
  Development of the Arctic*), and preprints.
- Excluded from the Google Scholar record: an ACPD discussion-paper duplicate,
  a BAMS supplement duplicate, a 2022 ACS correction notice, the POLAR 2018
  conference abstract, and the 2007 PhD thesis.
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

- [ ] **Profile photo** — none on the site since the review round; add a favourite to the home page hero when available (restore `.hero-photo` styles from git history if wanted).
- [ ] **ORCID** — the record (0000-0003-2243-8137) contains an erroneous entry ("Cada-3 System Review", 2026) worth removing.
- [ ] **Spot-check DOIs** — Crossref metadata is usually right but can carry
      typos (e.g. "BjØrn" for "Bjørn" in one Journal of Climate entry).
- [ ] **Old website** — jennielthomas.fr is retired/maintained separately by Jennie; consider adding a link there to this site.

## Image licences

| Image | Source | Licence |
| --- | --- | --- |
| `arctic-hero.jpg` | [Arctic Ice 2.JPG](https://commons.wikimedia.org/wiki/File:Arctic_Ice_2.JPG) by Pink floyd88 a, via Wikimedia Commons | [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/) — credited in site footer |
| `favicon.svg` | Created for this site | — |

## Deployment

Push to `main` — GitHub Pages rebuilds the site in about a minute
(live at <https://jenniethomas.github.io>). No build step needed server-side;
`.nojekyll` makes sure files are served exactly as committed.
