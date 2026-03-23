# UIL Piano Solos 2025-2026

This project is a lightweight Python + SQLite website for browsing the 2025-2026 UIL Prescribed Music List piano solos.

## Run locally

```bash
python3 app.py
```

Then open `http://127.0.0.1:8000`.

## Data source

- CSV import source: `/Users/kelleyparker/Downloads/UIL Prescribed Music List 2025-26.csv`
- Official UIL page: `https://www.uiltexas.org/pml/`

## Database notes

- `data/uil_piano_solos.db` stores the imported piano solo entries.
- `scripts/import_piano_solos.py` rebuilds the database from the CSV.
- The CSV currently imports `334` piano-solo songs.
- The database also stores `2` dataset audit notes, which brings the total database record count to `336`.
