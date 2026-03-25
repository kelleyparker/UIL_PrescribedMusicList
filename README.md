# UIL Prescribed Music List

This project is a lightweight Python website for browsing UIL Prescribed Music List solo, ensemble, band, orchestra, and choir datasets, with a GitHub Pages deployment and a monthly GitHub Actions sync.

## Run locally

```bash
python3 app.py
```

Then open `http://127.0.0.1:8000`.

## Data source

- Official UIL page: `https://www.uiltexas.org/pml/`
- UIL data feed: `https://www.uiltexas.org/pml/pml.php`
- Local source snapshots are written to [`data/`](/Users/kelleyparker/Documents/Codex/WebApps/UIL_PrescribedMusicList/data) during syncs.
- Generated site datasets are written to [`static/data/`](/Users/kelleyparker/Documents/Codex/WebApps/UIL_PrescribedMusicList/static/data).

## Update pipeline

- `scripts/sync_uil_pml.py` fetches the UIL homepage and JSON feed, detects the active school year, filters the configured solo events, and rebuilds the project data files.
- `.github/workflows/monthly-sync.yml` runs that sync on the first day of each month and commits changes only when the UIL data changes.
- `.github/workflows/pages.yml` republishes the static site to GitHub Pages after pushes to `main`.
- The frontend renders class filters dynamically from the selected dataset, so categories with UIL class levels beyond `1-3` (for example `100 Band`) show the correct range.
- When UIL exposes separate solo event codes within a broader instrument family, the UI should prefer individual instrument filters over a single family bucket.

## AI handoff

- Read `README.md` and `AI_CONTEXT.md` at the start of a new AI session before making repo changes.
- If you switch to a different AI app or a new thread, carry over `AI_CONTEXT.md` so the next assistant has the current project constraints, workflow, and documentation expectations.
- When meaningful work changes the UI, architecture, deployment flow, dataset coverage, or product behavior, update `AI_CONTEXT.md` and `README.md` before the final push if either doc is no longer accurate.

## Dataset notes

- `scripts/import_piano_solos.py` rebuilds the static JSON outputs from normalized UIL solo rows.
- Public-domain download links are attached only when a source can be verified.
- `static/data/stats.json` remains the piano legacy stats file for backwards compatibility.
