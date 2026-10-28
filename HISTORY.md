# History & maintenance guide

This file records how the site was built, where every piece of content came
from, what decisions were made, and what is still to do — so that future
updates are easy to pick up without reverse-engineering anything.
For repo structure and publication-list mechanics, see also `README.md`.

## Quick reference: where to add things

| I want to add… | Do this |
| --- | --- |
| A new paper or preprint | Add a tuple to `PUBS` in `tools/build_pubs.py` (set flag `"preprint"` for unpublished work), run `python3 tools/build_pubs.py`, commit |
| A news item | Add an `<article class="news-item">` block in `news.html` (and optionally the teaser section in `index.html`) |
| A project | Add an `<article class="project-card">` in `projects.html` (ongoing projects), or a card in the "Past projects" grid |
| A student / postdoc | `group.html` — the "Supervision" section |
| A course | `teaching.html` — the "Teaching" section |
| A CV entry | `index.html` — the `<ol class="timeline">` block |
| Update citation stats | `index.html` — the four `.stat` numbers in the hero, and the "as of" date |
| A page-wide footer/header link | Every page duplicates the header nav and footer — edit all six `.html` files consistently |
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

- [ ] **Teaching page** — real course list at Université Grenoble Alpes (page currently has a placeholder line).
- [ ] **Group page** — names of personally supervised students/postdocs (past and present).
- [ ] **News items** — drafted from papers and project websites; please review, edit, reorder.
- [ ] **Profile photo** — currently the one from the OPERA site; swap in a favourite if preferred.
- [ ] **ORCID** — the record (0000-0003-2243-8137) contains an erroneous entry ("Cada-3 System Review", 2026) worth removing.
- [ ] **Spot-check DOIs** — Crossref metadata is usually right but can carry
      typos (e.g. "BjØrn" for "Bjørn" in one Journal of Climate entry).
- [ ] **Citation stats** — static text ("October 2026"); refresh occasionally.
- [ ] **Old website** — jennielthomas.fr is retired/maintained separately by Jennie; consider adding a link there to this site.

## Image licences

| Image | Source | Licence |
| --- | --- | --- |
| `arctic-hero.jpg` | [Arctic Ice 2.JPG](https://commons.wikimedia.org/wiki/File:Arctic_Ice_2.JPG) by Pink floyd88 a, via Wikimedia Commons | [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/) — credited in site footer |
| `profile.png` | Jennie's own photo, via the [OPERA group site](https://ige-opera.github.io/people/) | Jennie's own |
| `favicon.svg` | Created for this site | — |

## Deployment

Push to `main` — GitHub Pages rebuilds the site in about a minute
(live at <https://jenniethomas.github.io>). No build step needed server-side;
`.nojekyll` makes sure files are served exactly as committed.
