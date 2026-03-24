# AI Context – UIL Prescribed Music List Project

## Project Overview
This is a web project that aggregates and presents the UIL Prescribed Music List (PML) in a structured, searchable format.

The goal is to:
- Make the PML easier to browse and filter
- Provide clean UI/UX for musicians and educators
- Potentially integrate affiliate links for sheet music/books

## Key Constraints
- DO NOT host or distribute copyrighted sheet music
- Only store and display metadata (titles, composers, publishers, etc.)
- UIL data is publicly available but should not be misrepresented as original work
- This project is an independent tool, not affiliated with UIL

## Data Source
- Data is derived from the official UIL PML
- May be scraped or transformed into structured formats (JSON/CSV)
- Around ~60 core books for solo instruments (non-band)

## Architecture (High-Level)
- Data ingestion:
  - Scraping or importing PML into structured JSON
- Backend (optional depending on implementation):
  - Lightweight API or static data serving
- Frontend:
  - Searchable/filterable UI
  - Instrument → Class → Piece hierarchy

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
