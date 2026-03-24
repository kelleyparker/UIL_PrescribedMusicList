# UIL Prescribed Music List Solos

This project is a lightweight Python website for browsing UIL Prescribed Music List solo datasets for piano, clarinet family, French horn, saxophone family, trombone, trumpet, tuba, flute, oboe, bassoon, alto saxophone, violin, viola, cello, string bass, euphonium, piccolo, English horn, snare drum, timpani, keyboard percussion, multiple percussion, drum set, and steel pan, with a GitHub Pages deployment and a monthly GitHub Actions sync.

## Run locally

```bash
python3 app.py
```

Then open `http://127.0.0.1:8000`.

## Data source

- Official UIL page: `https://www.uiltexas.org/pml/`
- UIL data feed: `https://www.uiltexas.org/pml/pml.php`
- Local source snapshots:
  - `data/uil_piano_solos_source.csv`
  - `data/uil_clarinet_solos_source.csv`
  - `data/uil_french_horn_solos_source.csv`
  - `data/uil_saxophone_solos_source.csv`
  - `data/uil_trombone_solos_source.csv`
  - `data/uil_trumpet_solos_source.csv`
  - `data/uil_tuba_solos_source.csv`
  - `data/uil_flute_solos_source.csv`
  - `data/uil_oboe_solos_source.csv`
  - `data/uil_bassoon_solos_source.csv`
  - `data/uil_alto_saxophone_solos_source.csv`
  - `data/uil_violin_solos_source.csv`
  - `data/uil_viola_solos_source.csv`
  - `data/uil_cello_solos_source.csv`
  - `data/uil_string_bass_solos_source.csv`
  - `data/uil_euphonium_solos_source.csv`
  - `data/uil_piccolo_solos_source.csv`
  - `data/uil_english_horn_solos_source.csv`
  - `data/uil_snare_drum_solos_source.csv`
  - `data/uil_timpani_solos_source.csv`
  - `data/uil_keyboard_percussion_solos_source.csv`
  - `data/uil_multiple_percussion_solos_source.csv`
  - `data/uil_drum_set_solos_source.csv`
  - `data/uil_steel_pan_solos_source.csv`

## Update pipeline

- `scripts/sync_uil_pml.py` fetches the UIL homepage and JSON feed, detects the active school year, filters the configured solo events, and rebuilds the project data files.
- `.github/workflows/monthly-sync.yml` runs that sync on the first day of each month and commits changes only when the UIL data changes.
- `.github/workflows/pages.yml` republishes the static site to GitHub Pages after pushes to `main`.

## Dataset notes

- `scripts/import_piano_solos.py` rebuilds the static JSON outputs from normalized UIL solo rows.
- Public-domain download links are attached only when a source can be verified.
- `static/data/stats.json` remains the piano legacy stats file for backwards compatibility.
