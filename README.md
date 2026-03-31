# UIL Prescribed Music List

This project is a lightweight Python website for browsing UIL Prescribed Music List solo, ensemble, band, orchestra, and choir datasets, with a GitHub Pages deployment and an annual GitHub Actions sync. **Currently in community beta testing** (see BETA indicator on site).

## Run locally

```bash
python3 app.py
```

Then open `http://127.0.0.1:8000`.

## Data source

- Official UIL page: `https://www.uiltexas.org/pml/`
- UIL data feed: `https://www.uiltexas.org/pml/pml.php`
- Local source snapshots are written to [`data/`](data/) during syncs.
- Generated site datasets are written to [`static/data/`](static/data/).

## Update pipeline

- `scripts/sync_uil_pml.py` fetches the UIL homepage and JSON feed, detects the active school year, filters configured UIL event categories, and rebuilds the project data files.
- `.github/workflows/annual-full-sync.yml` runs yearly on September 4, refreshes all configured UIL PML categories, then runs `scripts/scan_full_catalog.py` to fill missing affiliate links.
- The full scan is resume-aware: it persists attempt/cache progress and future runs continue from remaining unscanned rows by default (`SCAN_RESCAN_MODE=none`).
- If a yearly run times out or fails partway through, re-run `.github/workflows/annual-full-sync.yml` with `workflow_dispatch` to continue from prior progress.
- Manual runs support a `dry_run` input (default `true`) that executes a safe test path: dataset sync runs, full catalog scan is skipped, and no commit/push is performed.
- Email status notifications send on workflow completion (success/failure) when these repository secrets are configured: `SMTP_SERVER`, `SMTP_USERNAME`, `SMTP_PASSWORD`, and `NOTIFY_EMAIL`. Verified working via Gmail SMTP (dawidd6/action-send-mail@v3).
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

## Site Status

- **BETA**: Site is in active community beta testing (BETA badge + banner visible on both pages).
- **Reporting**: Community can submit feedback or data corrections via GitHub issue templates:
  - General feedback: https://github.com/kelleyparker/UIL_PrescribedMusicList/issues/new?template=general-feedback.md
  - Missing songs: https://github.com/kelleyparker/UIL_PrescribedMusicList/issues/new?template=missing-song-link.md
  - Per-song corrections: Use "Report Listing or Suggest Link" button on individual song cards.

## Known Limitations

- Public domain PDF link functionality is currently disabled (non-existent `public_domain_links` module removed in March 2026).
- This feature can be re-implemented in the future if a reliable source is identified.
