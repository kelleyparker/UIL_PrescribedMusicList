# UIL Prescribed Music List Solos

This project is a lightweight Python website for browsing UIL Prescribed Music List solo and small-ensemble datasets for piano, woodwinds, brass, percussion, and strings, with a GitHub Pages deployment and a monthly GitHub Actions sync.

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
  - `data/uil_woodwind_trio_source.csv`
  - `data/uil_flute_trio_source.csv`
  - `data/uil_bb_clarinet_trio_source.csv`
  - `data/uil_mixed_clarinet_trio_source.csv`
  - `data/uil_woodwind_quartet_source.csv`
  - `data/uil_flute_quartet_source.csv`
  - `data/uil_bb_clarinet_quartet_source.csv`
  - `data/uil_mixed_clarinet_quartet_source.csv`
  - `data/uil_saxophone_quartet_source.csv`
  - `data/uil_woodwind_quintet_source.csv`
  - `data/uil_misc_woodwind_ensemble_source.csv`
  - `data/uil_double_reed_ensemble_source.csv`
  - `data/uil_flute_choir_source.csv`
  - `data/uil_clarinet_choir_source.csv`
  - `data/uil_misc_saxophone_ensemble_source.csv`
  - `data/uil_trumpet_trio_source.csv`
  - `data/uil_trombone_trio_source.csv`
  - `data/uil_euphonium_baritone_trio_source.csv`
  - `data/uil_brass_trio_source.csv`
  - `data/uil_trumpet_quartet_source.csv`
  - `data/uil_horn_quartet_source.csv`
  - `data/uil_euphonium_baritone_quartet_source.csv`
  - `data/uil_brass_quartet_source.csv`
  - `data/uil_trombone_quartet_source.csv`
  - `data/uil_tuba_euphonium_quartet_source.csv`
  - `data/uil_brass_quintet_source.csv`
  - `data/uil_brass_sextet_source.csv`
  - `data/uil_six_or_more_brass_source.csv`
  - `data/uil_trumpet_choir_source.csv`
  - `data/uil_misc_horn_ensemble_source.csv`
  - `data/uil_trombone_choir_source.csv`
  - `data/uil_percussion_ensemble_source.csv`
  - `data/uil_steel_band_source.csv`
  - `data/uil_misc_mixed_ensemble_source.csv`

## Update pipeline

- `scripts/sync_uil_pml.py` fetches the UIL homepage and JSON feed, detects the active school year, filters the configured solo events, and rebuilds the project data files.
- `.github/workflows/monthly-sync.yml` runs that sync on the first day of each month and commits changes only when the UIL data changes.
- `.github/workflows/pages.yml` republishes the static site to GitHub Pages after pushes to `main`.

## Dataset notes

- `scripts/import_piano_solos.py` rebuilds the static JSON outputs from normalized UIL solo rows.
- Public-domain download links are attached only when a source can be verified.
- `static/data/stats.json` remains the piano legacy stats file for backwards compatibility.
