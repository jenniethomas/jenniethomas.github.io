# jenniethomas.github.io

Personal research website of **Jennie L. Thomas** — CNRS Senior Researcher at the
Institut des Géosciences de l'Environnement (IGE), Université Grenoble Alpes.

Live at: **https://jenniethomas.github.io**

The site is hand-built static HTML/CSS with no build step. Pushing to `main`
deploys automatically via GitHub Pages.

## Structure

```
index.html           Home — hero, bio, research interests, featured pubs, short CV
publications.html    Publications by year + preprints section (generated — see below)
models.html          WRF-Chem-Polar, microplastics-enabled GEOS-Chem, tools, past developments
projects.html        CERTAINTY, CRiceS, Bubbleplast, ATMO-PLASTIC, past projects
assets/css/          Stylesheet (no dependencies)
assets/img/          Banner photo, favicon
tools/build_pubs.py  Publication list generator
UPDATING.md          Step-by-step guide for future updates — start here
HISTORY.md           Build log, content sources, decisions, TODOs
.nojekyll            Tells GitHub Pages to serve files as-is
```

`HISTORY.md` records what was built when, from which sources, and what is
still to do. **`UPDATING.md` is the step-by-step guide for future changes.**

## Editing

Plain HTML — open any page in a text editor. Shared layout (header nav, footer)
is duplicated across pages, so edit consistently. Google Scholar, ORCID and
project links live in the footer of every page.

## Updating the publication list

The publications page is **generated** by `tools/build_pubs.py`:

1. Add a new entry to the `PUBS` list at the top of the script —
   `(year, title, fallback venue, fallback authors, flag)` where `flag` is
   `""` for a publication and `"preprint"` for work not yet accepted.
   Preprints are shown in a separate section and move into the year sections
   automatically once Crossref reports the accepted final version.
2. If Crossref search fails to find a paper, add its DOI to `DOI_OVERRIDES`.
3. Run:

   ```
   python3 tools/build_pubs.py
   ```

The script queries the Crossref API for the DOI, complete author list, journal,
volume and pages, caches responses in `tools/crossref_cache.json` (so re-runs
are fast), and rewrites `publications.html`.

## Image credits

- Banner photo: [Pink floyd88 a](https://commons.wikimedia.org/wiki/File:Arctic_Ice_2.JPG),
  [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/), via Wikimedia Commons.
