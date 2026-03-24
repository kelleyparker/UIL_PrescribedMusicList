# UIL Piano Solos

This project is a lightweight Python + SQLite website for browsing UIL Prescribed Music List piano solos with a GitHub Pages deployment and a monthly GitHub Actions sync.

## Run locally

```bash
python3 app.py
```

Then open `http://127.0.0.1:8000`.

## Data source

- Official UIL page: `https://www.uiltexas.org/pml/`
- UIL data feed: `https://www.uiltexas.org/pml/pml.php`
- Local source snapshot: `data/uil_piano_solos_source.csv`

## Update pipeline

- `scripts/sync_uil_pml.py` fetches the UIL homepage and JSON feed, detects the active school year, filters Piano Solo entries, and rebuilds the project data files.
- `.github/workflows/monthly-sync.yml` runs that sync on the first day of each month and commits changes only when the UIL data changes.
- `.github/workflows/pages.yml` republishes the static site to GitHub Pages after pushes to `main`.

## Database notes

- `data/uil_piano_solos.db` stores the imported piano solo entries.
- `scripts/import_piano_solos.py` rebuilds the database and static JSON outputs from normalized Piano Solo rows.
- The current UIL Piano Solo dataset contains `334` songs.
- The database also stores `2` dataset audit notes, which brings the total database record count to `336`.
