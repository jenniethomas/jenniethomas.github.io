# Updating this site

Hands-on guide for keeping **jenniethomas.github.io** up to date. If you are
picking this repo up cold, read this file top to bottom: it explains how the
site works and how to do every common update task. For the build history,
content sources and past decisions, see `HISTORY.md`.

## How the site works

- Four pages: `index.html` (home), `publications.html`, `models.html`,
  `projects.html`.
- Plain HTML plus one stylesheet (`assets/css/style.css`). No framework, no
  build step.
- **`publications.html` is generated** by `tools/build_pubs.py`. Never edit it
  by hand: edit the `PUBS` list in the script and re-run it.
- The header navigation and footer are duplicated on every page. When you
  change them, change **all four pages plus the `PAGE_TEMPLATE` inside
  `tools/build_pubs.py`** (which generates the publications page).
- Hosting: GitHub Pages serves the `main` branch. Pushing to `main` makes the
  change live at <https://jenniethomas.github.io> within about a minute.

## Preview locally

```
cd ~/projects/jenniethomas.github.io
python3 -m http.server 8000
```

Open <http://localhost:8000>. After CSS edits, hard-refresh with ⌘⇧R to
bypass the cached stylesheet.

## Add a publication (most common task)

1. Open `tools/build_pubs.py`. The `PUBS` list at the top holds every entry as

   ```
   (year, "Title", "Journal volume, pages", "F Firstauthor, ..., JL Thomas, ...", "")
   ```

   Add your entry; keep newer years at the top of the list.

2. For a **preprint of unpublished work**, set the last field to `"preprint"`.
   Preprints are shown in their own section on the publications page.

3. Generate the page:

   ```
   python3 tools/build_pubs.py
   ```

   The script queries the Crossref API for the DOI, full author list, journal,
   volume and pages, and rewrites `publications.html`. Jennie's name is
   bolded automatically.

4. Watch the script output. If it prints `No DOI found for: <your title>`,
   add the DOI to the `DOI_OVERRIDES` dictionary (just above `PUBS`) and
   re-run:

   ```python
   DOI_OVERRIDES = {
       "Overview paper: New insights into aerosol and climate in the Arctic":
           "10.5194/acp-19-2527-2019",
       ...
   }
   ```

5. Skim the generated `publications.html` (search for the title) to confirm
   the entry looks right, then commit and push (see Deploy).

### When a preprint is accepted

Nothing to edit. Just re-run `python3 tools/build_pubs.py`: the script notices
the published version on Crossref and moves the entry from the preprints
section into the year sections automatically. (Example: Segur et al. moved
into *Microplastics and Nanoplastics* 6, 45 (2026) this way.)

### Remove an entry

Delete its tuple from `PUBS` and re-run the script. Crossref responses are
cached in `tools/crossref_cache.json`; stale cache entries are harmless.

## Edit page content

| Task | Place |
| --- | --- |
| Home bio, research interests, CV timeline | `index.html` |
| Projects (CERTAINTY, CRiceS, Bubbleplast, ATMO-PLASTIC, past projects; CERTAINTY and CRiceS have logos) | `projects.html` |
| Models (WRF-Chem-Polar, microplastics GEOS-Chem, tools, past developments) | `models.html` |
| Page titles / meta descriptions | `<head>` of each page (title separator is `\|`) |
| Colours, spacing, typography | `assets/css/style.css` |

## Change navigation or footer links

The same header and footer markup is repeated in `index.html`,
`models.html`, `projects.html` and the `PAGE_TEMPLATE` inside
`tools/build_pubs.py`. Edit **all four** consistently, then re-run the script
to regenerate `publications.html`. Current footer links: Google Scholar, IGE,
OPERA group. The "Credits" column carries the banner photo and project-logo
attributions.

## Add or change an image

1. Put the file in `assets/img/` and reference it relative to the page root,
   e.g. `assets/img/arctic-hero.jpg`.
2. **Check the licence.** Only publish images you have the right to use.
3. Credit licensed images in the footer "Credits" column. The banner photo
   shows the format: source, author, licence, link. The project logos are
   a second example: source website plus a note that they identify the
   projects.

## Writing style

- No em-dashes (—) in site prose; they read as AI-generated. Use commas,
  colons or parentheses instead. En-dashes in scientific compounds
  (aerosol–cloud, ocean–sea ice–snow–atmosphere) are standard and fine.
- Page `<title>` separator is `|`.
- First person, concise.

## Deploy

```
git add -A
git commit -m "Short description of the change"
git push
```

The site rebuilds on GitHub Pages within about a minute. Verify at
<https://jenniethomas.github.io> in a private/incognito browser window
(regular tabs may serve cached CSS).

## Troubleshooting

- **Publications page did not change** → `publications.html` is generated;
  re-run `python3 tools/build_pubs.py` instead of editing it by hand.
- **"No DOI found" for a paper that clearly exists** → add it to
  `DOI_OVERRIDES` and re-run.
- **Odd venue or missing authors on one entry** → that journal's Crossref
  record is incomplete; check the DOI, or write the full venue/author string
  directly in the `PUBS` entry (it is used as a fallback).
- **Crossref queries fail** → just re-run the script; cached results in
  `tools/crossref_cache.json` make re-runs fast and only missing entries are
  fetched again.
