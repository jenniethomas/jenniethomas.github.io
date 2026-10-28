# jenniethomas.github.io

Personal research website of **Jennie L. Thomas** — CNRS Senior Researcher at the
Institut des Géosciences de l'Environnement (IGE), Université Grenoble Alpes.

Live at: **https://jenniethomas.github.io**

The site is hand-built static HTML/CSS with no build step. Pushing to `main`
deploys automatically via GitHub Pages.

## Structure

```
index.html           Home — hero, bio, research interests, featured pubs, short CV, news
publications.html    All publications by year (generated — see below)
projects.html        CERTAINTY, CRiceS, past projects, models & tools
group.html           OPERA research group, supervision
teaching.html        Teaching, supervision, outreach & policy
news.html            News items
assets/css/          Stylesheet (no dependencies)
assets/img/          Profile photo, banner photo, favicon
tools/build_pubs.py  Publication list generator
.nojekyll            Tells GitHub Pages to serve files as-is
```

## Editing

Plain HTML — open any page in a text editor. Shared layout (header nav, footer)
is duplicated across pages, so edit consistently. Google Scholar, ORCID and
project links live in the footer of every page.

## Updating the publication list

The publications page is **generated** by `tools/build_pubs.py`:

1. Add a new entry to the `PUBS` list at the top of the script —
   `(year, title, fallback venue, fallback authors, flag)` where `flag` is
   `""` for a publication and `"preprint"` for preprints.
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
- Profile photo: from the [OPERA group](https://ige-opera.github.io/people/) website.
