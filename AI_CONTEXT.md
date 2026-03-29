# AI Context – UIL Prescribed Music List Project

## Project Overview
This is a web project that aggregates and presents the UIL Prescribed Music List (PML) in a structured, searchable format.

The goal is to:
- Make the PML easier to browse and filter
- Provide clean UI/UX for musicians and educators
- Potentially integrate affiliate links for sheet music/books
- Keep repo documentation aligned with the current dataset, UI, and deployment workflow

## Key Constraints
- DO NOT host or distribute copyrighted sheet music
- Only store and display metadata (titles, composers, publishers, etc.)
- UIL data is publicly available but should not be misrepresented as original work
- This project is an independent tool, not affiliated with UIL
- Affiliate links may be shown for select titles, but disclosures should remain clear in the UI copy

## Data Source
- Data is derived from the official UIL PML
- May be scraped or transformed into structured formats (JSON/CSV)
- Source snapshots are stored in `data/`
- Generated frontend datasets are stored in `static/data/`

## Architecture (High-Level)
- Data ingestion:
  - `scripts/sync_uil_pml.py` fetches UIL data and refreshes local source snapshots
  - `scripts/import_piano_solos.py` normalizes configured categories into static JSON/stats files
- Backend:
  - `app.py` serves the local site and exposes the generated datasets
- Frontend:
  - Static HTML/CSS/JS app in `static/`
  - Searchable/filterable UI grouped by UIL top-level categories such as Band, Orchestra, and Choir
  - Class filter chips are dataset-driven and should reflect the available UIL levels for the active category
  - Prefer individual instrument filters over family buckets when UIL provides distinct event codes for those solos
- Deployment:
  - Pushes to `main` trigger GitHub Pages deployment
  - Annual full sync automation refreshes UIL-backed datasets and runs resume-aware full-catalog link scanning

## Maintenance Workflow
- At the end of meaningful runs, update `README.md` if setup, feature scope, or pipeline behavior changed
- Also update `AI_CONTEXT.md` if architecture, workflow expectations, dataset coverage, or product behavior changed
- Push documentation updates with the related code/data change when needed, rather than leaving repo context stale

## Using This File Across AI Tools Or New Contexts
- Treat `AI_CONTEXT.md` as the canonical project handoff note for AI assistants
- At the start of a new AI session, ask the assistant to read `README.md` and `AI_CONTEXT.md` before making changes
- When switching to a different AI app, attach or paste the important parts of `AI_CONTEXT.md` so the new assistant inherits the same project constraints and workflow expectations
- When starting a fresh thread in the same tool, reference `AI_CONTEXT.md` again instead of assuming the prior conversation is still available
- If a run changes architecture, deployment flow, dataset coverage, documentation expectations, or affiliate-link behavior, update this file before the final push
- If `AI_CONTEXT.md` and the code disagree, bring the file up to date rather than carrying stale instructions forward
- Keep this file concise and operational: it should help the next assistant start safely and quickly, not serve as a full spec

## Data Model (Example)
```json
{
  "instrument": "Trumpet",
  "class": "Class 1",
  "title": "Concerto in E-flat",
  "composer": "Haydn",
  "publisher": "Example Publisher",
  "book": "Selected Trumpet Solos"
}
