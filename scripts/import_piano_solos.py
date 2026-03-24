from __future__ import annotations

import csv
import html
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STATIC_DATA_DIR = ROOT / "static" / "data"
SOURCE_CSV_PATH = ROOT / "data" / "uil_piano_solos_source.csv"
CLARINET_SOURCE_CSV_PATH = ROOT / "data" / "uil_clarinet_solos_source.csv"
FRENCH_HORN_SOURCE_CSV_PATH = ROOT / "data" / "uil_french_horn_solos_source.csv"
SAXOPHONE_SOURCE_CSV_PATH = ROOT / "data" / "uil_saxophone_solos_source.csv"
TROMBONE_SOURCE_CSV_PATH = ROOT / "data" / "uil_trombone_solos_source.csv"
TRUMPET_SOURCE_CSV_PATH = ROOT / "data" / "uil_trumpet_solos_source.csv"
TUBA_SOURCE_CSV_PATH = ROOT / "data" / "uil_tuba_solos_source.csv"
FLUTE_SOURCE_CSV_PATH = ROOT / "data" / "uil_flute_solos_source.csv"
OBOE_SOURCE_CSV_PATH = ROOT / "data" / "uil_oboe_solos_source.csv"
BASSOON_SOURCE_CSV_PATH = ROOT / "data" / "uil_bassoon_solos_source.csv"
ALTO_SAXOPHONE_SOURCE_CSV_PATH = ROOT / "data" / "uil_alto_saxophone_solos_source.csv"
VIOLIN_SOURCE_CSV_PATH = ROOT / "data" / "uil_violin_solos_source.csv"
VIOLA_SOURCE_CSV_PATH = ROOT / "data" / "uil_viola_solos_source.csv"
CELLO_SOURCE_CSV_PATH = ROOT / "data" / "uil_cello_solos_source.csv"
STRING_BASS_SOURCE_CSV_PATH = ROOT / "data" / "uil_string_bass_solos_source.csv"
EUPHONIUM_SOURCE_CSV_PATH = ROOT / "data" / "uil_euphonium_solos_source.csv"
PICCOLO_SOURCE_CSV_PATH = ROOT / "data" / "uil_piccolo_solos_source.csv"
ENGLISH_HORN_SOURCE_CSV_PATH = ROOT / "data" / "uil_english_horn_solos_source.csv"
SNARE_DRUM_SOURCE_CSV_PATH = ROOT / "data" / "uil_snare_drum_solos_source.csv"
TIMPANI_SOURCE_CSV_PATH = ROOT / "data" / "uil_timpani_solos_source.csv"
KEYBOARD_PERCUSSION_SOURCE_CSV_PATH = ROOT / "data" / "uil_keyboard_percussion_solos_source.csv"
MULTIPLE_PERCUSSION_SOURCE_CSV_PATH = ROOT / "data" / "uil_multiple_percussion_solos_source.csv"
DRUM_SET_SOURCE_CSV_PATH = ROOT / "data" / "uil_drum_set_solos_source.csv"
STEEL_PAN_SOURCE_CSV_PATH = ROOT / "data" / "uil_steel_pan_solos_source.csv"
WOODWIND_TRIO_SOURCE_CSV_PATH = ROOT / "data" / "uil_woodwind_trio_source.csv"
FLUTE_TRIO_SOURCE_CSV_PATH = ROOT / "data" / "uil_flute_trio_source.csv"
BB_CLARINET_TRIO_SOURCE_CSV_PATH = ROOT / "data" / "uil_bb_clarinet_trio_source.csv"
MIXED_CLARINET_TRIO_SOURCE_CSV_PATH = ROOT / "data" / "uil_mixed_clarinet_trio_source.csv"
WOODWIND_QUARTET_SOURCE_CSV_PATH = ROOT / "data" / "uil_woodwind_quartet_source.csv"
FLUTE_QUARTET_SOURCE_CSV_PATH = ROOT / "data" / "uil_flute_quartet_source.csv"
BB_CLARINET_QUARTET_SOURCE_CSV_PATH = ROOT / "data" / "uil_bb_clarinet_quartet_source.csv"
MIXED_CLARINET_QUARTET_SOURCE_CSV_PATH = ROOT / "data" / "uil_mixed_clarinet_quartet_source.csv"
SAXOPHONE_QUARTET_SOURCE_CSV_PATH = ROOT / "data" / "uil_saxophone_quartet_source.csv"
WOODWIND_QUINTET_SOURCE_CSV_PATH = ROOT / "data" / "uil_woodwind_quintet_source.csv"
MISC_WOODWIND_ENSEMBLE_SOURCE_CSV_PATH = ROOT / "data" / "uil_misc_woodwind_ensemble_source.csv"
DOUBLE_REED_ENSEMBLE_SOURCE_CSV_PATH = ROOT / "data" / "uil_double_reed_ensemble_source.csv"
FLUTE_CHOIR_SOURCE_CSV_PATH = ROOT / "data" / "uil_flute_choir_source.csv"
CLARINET_CHOIR_SOURCE_CSV_PATH = ROOT / "data" / "uil_clarinet_choir_source.csv"
MISC_SAXOPHONE_ENSEMBLE_SOURCE_CSV_PATH = ROOT / "data" / "uil_misc_saxophone_ensemble_source.csv"
TRUMPET_TRIO_SOURCE_CSV_PATH = ROOT / "data" / "uil_trumpet_trio_source.csv"
TROMBONE_TRIO_SOURCE_CSV_PATH = ROOT / "data" / "uil_trombone_trio_source.csv"
EUPHONIUM_BARITONE_TRIO_SOURCE_CSV_PATH = ROOT / "data" / "uil_euphonium_baritone_trio_source.csv"
BRASS_TRIO_SOURCE_CSV_PATH = ROOT / "data" / "uil_brass_trio_source.csv"
TRUMPET_QUARTET_SOURCE_CSV_PATH = ROOT / "data" / "uil_trumpet_quartet_source.csv"
HORN_QUARTET_SOURCE_CSV_PATH = ROOT / "data" / "uil_horn_quartet_source.csv"
EUPHONIUM_BARITONE_QUARTET_SOURCE_CSV_PATH = ROOT / "data" / "uil_euphonium_baritone_quartet_source.csv"
BRASS_QUARTET_SOURCE_CSV_PATH = ROOT / "data" / "uil_brass_quartet_source.csv"
TROMBONE_QUARTET_SOURCE_CSV_PATH = ROOT / "data" / "uil_trombone_quartet_source.csv"
TUBA_EUPHONIUM_QUARTET_SOURCE_CSV_PATH = ROOT / "data" / "uil_tuba_euphonium_quartet_source.csv"
BRASS_QUINTET_SOURCE_CSV_PATH = ROOT / "data" / "uil_brass_quintet_source.csv"
BRASS_SEXTET_SOURCE_CSV_PATH = ROOT / "data" / "uil_brass_sextet_source.csv"
SIX_OR_MORE_BRASS_SOURCE_CSV_PATH = ROOT / "data" / "uil_six_or_more_brass_source.csv"
TRUMPET_CHOIR_SOURCE_CSV_PATH = ROOT / "data" / "uil_trumpet_choir_source.csv"
MISC_HORN_ENSEMBLE_SOURCE_CSV_PATH = ROOT / "data" / "uil_misc_horn_ensemble_source.csv"
TROMBONE_CHOIR_SOURCE_CSV_PATH = ROOT / "data" / "uil_trombone_choir_source.csv"
PERCUSSION_ENSEMBLE_SOURCE_CSV_PATH = ROOT / "data" / "uil_percussion_ensemble_source.csv"
STEEL_BAND_SOURCE_CSV_PATH = ROOT / "data" / "uil_steel_band_source.csv"
MISC_MIXED_ENSEMBLE_SOURCE_CSV_PATH = ROOT / "data" / "uil_misc_mixed_ensemble_source.csv"
ACOUSTICAL_GUITAR_SOURCE_CSV_PATH = ROOT / "data" / "uil_acoustical_guitar_solos_source.csv"
PIANO_TRIO_SOURCE_CSV_PATH = ROOT / "data" / "uil_piano_trio_source.csv"
VIOLIN_TRIO_SOURCE_CSV_PATH = ROOT / "data" / "uil_violin_trio_source.csv"
STRING_TRIO_SOURCE_CSV_PATH = ROOT / "data" / "uil_string_trio_source.csv"
MISC_STRING_TRIO_SOURCE_CSV_PATH = ROOT / "data" / "uil_misc_string_trio_source.csv"
GUITAR_TRIO_SOURCE_CSV_PATH = ROOT / "data" / "uil_guitar_trio_source.csv"
VIOLIN_QUARTETS_SOURCE_CSV_PATH = ROOT / "data" / "uil_violin_quartets_source.csv"
STRING_QUARTET_SOURCE_CSV_PATH = ROOT / "data" / "uil_string_quartet_source.csv"
MISC_STRING_QUARTET_SOURCE_CSV_PATH = ROOT / "data" / "uil_misc_string_quartet_source.csv"
GUITAR_QUARTET_SOURCE_CSV_PATH = ROOT / "data" / "uil_guitar_quartet_source.csv"
STRING_QUINTET_SOURCE_CSV_PATH = ROOT / "data" / "uil_string_quintet_source.csv"
MISC_STRING_QUINTET_SOURCE_CSV_PATH = ROOT / "data" / "uil_misc_string_quintet_source.csv"
MISC_STRING_ENSEMBLE_SOURCE_CSV_PATH = ROOT / "data" / "uil_misc_string_ensemble_source.csv"
MISC_GUITAR_ENSEMBLE_SOURCE_CSV_PATH = ROOT / "data" / "uil_misc_guitar_ensemble_source.csv"
CELLO_CHOIR_SOURCE_CSV_PATH = ROOT / "data" / "uil_cello_choir_source.csv"
HARP_SOURCE_CSV_PATH = ROOT / "data" / "uil_harp_solos_source.csv"
HARP_ENSEMBLE_SOURCE_CSV_PATH = ROOT / "data" / "uil_harp_ensemble_source.csv"
FULL_ORCHESTRA_SOURCE_CSV_PATH = ROOT / "data" / "uil_full_orchestra_source.csv"
STRING_ORCHESTRA_SOURCE_CSV_PATH = ROOT / "data" / "uil_string_orchestra_source.csv"
VOCAL_SOURCE_CSV_PATH = ROOT / "data" / "uil_vocal_solos_source.csv"
TREBLE_SMALL_ENSEMBLE_SOURCE_CSV_PATH = ROOT / "data" / "uil_treble_small_ensemble_source.csv"
TENOR_BASS_SMALL_ENSEMBLE_SOURCE_CSV_PATH = ROOT / "data" / "uil_tenor_bass_small_ensemble_source.csv"
MADRIGAL_SOURCE_CSV_PATH = ROOT / "data" / "uil_madrigal_source.csv"
MIXED_CHORUS_SOURCE_CSV_PATH = ROOT / "data" / "uil_mixed_chorus_source.csv"
TENOR_BASS_CHORUS_SOURCE_CSV_PATH = ROOT / "data" / "uil_tenor_bass_chorus_source.csv"
TREBLE_CHORUS_SOURCE_CSV_PATH = ROOT / "data" / "uil_treble_chorus_source.csv"
DEFAULT_SCHOOL_YEAR = "2025-2026"
TAG_PATTERN = re.compile(r"<[^>]+>")
OPTION_PATTERN = re.compile(r"<option[^>]*>(.*?)</option>", re.IGNORECASE | re.DOTALL)

INSTRUMENT_CONFIGS = {
    "piano": {
        "event_name": "Piano Solo",
        "event_names": ["Piano Solo"],
        "title": "Piano Solos",
        "csv_path": SOURCE_CSV_PATH,
        "songs_output": STATIC_DATA_DIR / "piano-solos.json",
        "stats_output": STATIC_DATA_DIR / "piano-stats.json",
        "legacy_stats_output": STATIC_DATA_DIR / "stats.json",
    },
    "clarinet": {
        "event_name": "Bb Clarinet Solo",
        "event_names": [
            "Bb Clarinet Solo",
            "Bass Clarinet Solo",
            "Alto Clarinet Solo",
            "Eb Clarinet Solo",
            "Contra Bass Clarinet Solo",
        ],
        "title": "Clarinet Family Solos",
        "csv_path": CLARINET_SOURCE_CSV_PATH,
        "songs_output": STATIC_DATA_DIR / "clarinet-solos.json",
        "stats_output": STATIC_DATA_DIR / "clarinet-stats.json",
    },
    "french-horn": {
        "event_name": "French Horn Solo",
        "event_names": ["French Horn Solo"],
        "title": "French Horn Solos",
        "csv_path": FRENCH_HORN_SOURCE_CSV_PATH,
        "songs_output": STATIC_DATA_DIR / "french-horn-solos.json",
        "stats_output": STATIC_DATA_DIR / "french-horn-stats.json",
    },
    "saxophone": {
        "event_name": "Alto Saxophone Solo",
        "event_names": [
            "Soprano Saxophone Solo",
            "Alto Saxophone Solo",
            "Tenor Saxophone Solo",
            "Baritone Saxophone Solo",
        ],
        "title": "Saxophone Family Solos",
        "csv_path": SAXOPHONE_SOURCE_CSV_PATH,
        "songs_output": STATIC_DATA_DIR / "saxophone-solos.json",
        "stats_output": STATIC_DATA_DIR / "saxophone-stats.json",
    },
    "trombone": {
        "event_name": "Tenor Trombone Solo",
        "event_names": ["Tenor Trombone Solo", "Bass Trombone Solo"],
        "title": "Trombone Solos",
        "csv_path": TROMBONE_SOURCE_CSV_PATH,
        "songs_output": STATIC_DATA_DIR / "trombone-solos.json",
        "stats_output": STATIC_DATA_DIR / "trombone-stats.json",
    },
    "trumpet": {
        "event_name": "Cornet/Trumpet Solo",
        "event_names": ["Cornet/Trumpet Solo"],
        "title": "Trumpet Solos",
        "csv_path": TRUMPET_SOURCE_CSV_PATH,
        "songs_output": STATIC_DATA_DIR / "trumpet-solos.json",
        "stats_output": STATIC_DATA_DIR / "trumpet-stats.json",
    },
    "tuba": {
        "event_name": "Tuba Solo",
        "event_names": ["Tuba Solo"],
        "title": "Tuba Solos",
        "csv_path": TUBA_SOURCE_CSV_PATH,
        "songs_output": STATIC_DATA_DIR / "tuba-solos.json",
        "stats_output": STATIC_DATA_DIR / "tuba-stats.json",
    },
    "flute": {
        "event_name": "Flute Solo",
        "event_names": ["Flute Solo"],
        "title": "Flute Solos",
        "csv_path": FLUTE_SOURCE_CSV_PATH,
        "songs_output": STATIC_DATA_DIR / "flute-solos.json",
        "stats_output": STATIC_DATA_DIR / "flute-stats.json",
    },
    "oboe": {
        "event_name": "Oboe Solo",
        "event_names": ["Oboe Solo"],
        "title": "Oboe Solos",
        "csv_path": OBOE_SOURCE_CSV_PATH,
        "songs_output": STATIC_DATA_DIR / "oboe-solos.json",
        "stats_output": STATIC_DATA_DIR / "oboe-stats.json",
    },
    "bassoon": {
        "event_name": "Bassoon Solo",
        "event_names": ["Bassoon Solo"],
        "title": "Bassoon Solos",
        "csv_path": BASSOON_SOURCE_CSV_PATH,
        "songs_output": STATIC_DATA_DIR / "bassoon-solos.json",
        "stats_output": STATIC_DATA_DIR / "bassoon-stats.json",
    },
    "alto-saxophone": {
        "event_name": "Alto Saxophone Solo",
        "event_names": ["Alto Saxophone Solo"],
        "title": "Alto Saxophone Solos",
        "csv_path": ALTO_SAXOPHONE_SOURCE_CSV_PATH,
        "songs_output": STATIC_DATA_DIR / "alto-saxophone-solos.json",
        "stats_output": STATIC_DATA_DIR / "alto-saxophone-stats.json",
    },
    "violin": {
        "event_name": "Violin Solo",
        "event_names": ["Violin Solo"],
        "title": "Violin Solos",
        "csv_path": VIOLIN_SOURCE_CSV_PATH,
        "songs_output": STATIC_DATA_DIR / "violin-solos.json",
        "stats_output": STATIC_DATA_DIR / "violin-stats.json",
    },
    "viola": {
        "event_name": "Viola Solo",
        "event_names": ["Viola Solo"],
        "title": "Viola Solos",
        "csv_path": VIOLA_SOURCE_CSV_PATH,
        "songs_output": STATIC_DATA_DIR / "viola-solos.json",
        "stats_output": STATIC_DATA_DIR / "viola-stats.json",
    },
    "cello": {
        "event_name": "Cello Solo",
        "event_names": ["Cello Solo"],
        "title": "Cello Solos",
        "csv_path": CELLO_SOURCE_CSV_PATH,
        "songs_output": STATIC_DATA_DIR / "cello-solos.json",
        "stats_output": STATIC_DATA_DIR / "cello-stats.json",
    },
    "string-bass": {
        "event_name": "String Bass Solo",
        "event_names": ["String Bass Solo"],
        "title": "String Bass Solos",
        "csv_path": STRING_BASS_SOURCE_CSV_PATH,
        "songs_output": STATIC_DATA_DIR / "string-bass-solos.json",
        "stats_output": STATIC_DATA_DIR / "string-bass-stats.json",
    },
    "euphonium": {
        "event_name": "Euphonium/Baritone Horn Solo",
        "event_names": ["Euphonium/Baritone Horn Solo"],
        "title": "Euphonium and Baritone Horn Solos",
        "csv_path": EUPHONIUM_SOURCE_CSV_PATH,
        "songs_output": STATIC_DATA_DIR / "euphonium-solos.json",
        "stats_output": STATIC_DATA_DIR / "euphonium-stats.json",
    },
    "piccolo": {
        "event_name": "Piccolo Solo",
        "event_names": ["Piccolo Solo"],
        "title": "Piccolo Solos",
        "csv_path": PICCOLO_SOURCE_CSV_PATH,
        "songs_output": STATIC_DATA_DIR / "piccolo-solos.json",
        "stats_output": STATIC_DATA_DIR / "piccolo-stats.json",
    },
    "english-horn": {
        "event_name": "English Horn Solo",
        "event_names": ["English Horn Solo"],
        "title": "English Horn Solos",
        "csv_path": ENGLISH_HORN_SOURCE_CSV_PATH,
        "songs_output": STATIC_DATA_DIR / "english-horn-solos.json",
        "stats_output": STATIC_DATA_DIR / "english-horn-stats.json",
    },
    "snare-drum": {
        "event_name": "Snare Drum Solo",
        "event_names": ["Snare Drum Solo"],
        "title": "Snare Drum Solos",
        "csv_path": SNARE_DRUM_SOURCE_CSV_PATH,
        "songs_output": STATIC_DATA_DIR / "snare-drum-solos.json",
        "stats_output": STATIC_DATA_DIR / "snare-drum-stats.json",
    },
    "timpani": {
        "event_name": "Timpani Solo",
        "event_names": ["Timpani Solo"],
        "title": "Timpani Solos",
        "csv_path": TIMPANI_SOURCE_CSV_PATH,
        "songs_output": STATIC_DATA_DIR / "timpani-solos.json",
        "stats_output": STATIC_DATA_DIR / "timpani-stats.json",
    },
    "keyboard-percussion": {
        "event_name": "Keyboard Percussion Solo",
        "event_names": ["Keyboard Percussion Solo"],
        "title": "Keyboard Percussion Solos",
        "csv_path": KEYBOARD_PERCUSSION_SOURCE_CSV_PATH,
        "songs_output": STATIC_DATA_DIR / "keyboard-percussion-solos.json",
        "stats_output": STATIC_DATA_DIR / "keyboard-percussion-stats.json",
    },
    "multiple-percussion": {
        "event_name": "Multiple Percussion Solo",
        "event_names": ["Multiple Percussion Solo"],
        "title": "Multiple Percussion Solos",
        "csv_path": MULTIPLE_PERCUSSION_SOURCE_CSV_PATH,
        "songs_output": STATIC_DATA_DIR / "multiple-percussion-solos.json",
        "stats_output": STATIC_DATA_DIR / "multiple-percussion-stats.json",
    },
    "drum-set": {
        "event_name": "Drum Set Solo",
        "event_names": ["Drum Set Solo"],
        "title": "Drum Set Solos",
        "csv_path": DRUM_SET_SOURCE_CSV_PATH,
        "songs_output": STATIC_DATA_DIR / "drum-set-solos.json",
        "stats_output": STATIC_DATA_DIR / "drum-set-stats.json",
    },
    "steel-pan": {
        "event_name": "Steel Pan Solo",
        "event_names": ["Steel Pan Solo"],
        "title": "Steel Pan Solos",
        "csv_path": STEEL_PAN_SOURCE_CSV_PATH,
        "songs_output": STATIC_DATA_DIR / "steel-pan-solos.json",
        "stats_output": STATIC_DATA_DIR / "steel-pan-stats.json",
    },
    "woodwind-trio": {
        "event_name": "Woodwind Trio",
        "event_names": ["Woodwind Trio"],
        "title": "Woodwind Trios",
        "csv_path": WOODWIND_TRIO_SOURCE_CSV_PATH,
        "songs_output": STATIC_DATA_DIR / "woodwind-trio.json",
        "stats_output": STATIC_DATA_DIR / "woodwind-trio-stats.json",
    },
    "flute-trio": {
        "event_name": "Flute Trio",
        "event_names": ["Flute Trio"],
        "title": "Flute Trios",
        "csv_path": FLUTE_TRIO_SOURCE_CSV_PATH,
        "songs_output": STATIC_DATA_DIR / "flute-trio.json",
        "stats_output": STATIC_DATA_DIR / "flute-trio-stats.json",
    },
    "bb-clarinet-trio": {
        "event_name": "Bb Clarinet Trio",
        "event_names": ["Bb Clarinet Trio"],
        "title": "Bb Clarinet Trios",
        "csv_path": BB_CLARINET_TRIO_SOURCE_CSV_PATH,
        "songs_output": STATIC_DATA_DIR / "bb-clarinet-trio.json",
        "stats_output": STATIC_DATA_DIR / "bb-clarinet-trio-stats.json",
    },
    "mixed-clarinet-trio": {
        "event_name": "Mixed Clarinet Trio",
        "event_names": ["Mixed Clarinet Trio"],
        "title": "Mixed Clarinet Trios",
        "csv_path": MIXED_CLARINET_TRIO_SOURCE_CSV_PATH,
        "songs_output": STATIC_DATA_DIR / "mixed-clarinet-trio.json",
        "stats_output": STATIC_DATA_DIR / "mixed-clarinet-trio-stats.json",
    },
    "woodwind-quartet": {
        "event_name": "Woodwind Quartet",
        "event_names": ["Woodwind Quartet"],
        "title": "Woodwind Quartets",
        "csv_path": WOODWIND_QUARTET_SOURCE_CSV_PATH,
        "songs_output": STATIC_DATA_DIR / "woodwind-quartet.json",
        "stats_output": STATIC_DATA_DIR / "woodwind-quartet-stats.json",
    },
    "flute-quartet": {
        "event_name": "Flute Quartet",
        "event_names": ["Flute Quartet"],
        "title": "Flute Quartets",
        "csv_path": FLUTE_QUARTET_SOURCE_CSV_PATH,
        "songs_output": STATIC_DATA_DIR / "flute-quartet.json",
        "stats_output": STATIC_DATA_DIR / "flute-quartet-stats.json",
    },
    "bb-clarinet-quartet": {
        "event_name": "Bb Clarinet Quartet",
        "event_names": ["Bb Clarinet Quartet"],
        "title": "Bb Clarinet Quartets",
        "csv_path": BB_CLARINET_QUARTET_SOURCE_CSV_PATH,
        "songs_output": STATIC_DATA_DIR / "bb-clarinet-quartet.json",
        "stats_output": STATIC_DATA_DIR / "bb-clarinet-quartet-stats.json",
    },
    "mixed-clarinet-quartet": {
        "event_name": "Mixed Clarinet Quartet",
        "event_names": ["Mixed Clarinet Quartet"],
        "title": "Mixed Clarinet Quartets",
        "csv_path": MIXED_CLARINET_QUARTET_SOURCE_CSV_PATH,
        "songs_output": STATIC_DATA_DIR / "mixed-clarinet-quartet.json",
        "stats_output": STATIC_DATA_DIR / "mixed-clarinet-quartet-stats.json",
    },
    "saxophone-quartet": {
        "event_name": "Saxophone Quartet",
        "event_names": ["Saxophone Quartet"],
        "title": "Saxophone Quartets",
        "csv_path": SAXOPHONE_QUARTET_SOURCE_CSV_PATH,
        "songs_output": STATIC_DATA_DIR / "saxophone-quartet.json",
        "stats_output": STATIC_DATA_DIR / "saxophone-quartet-stats.json",
    },
    "woodwind-quintet": {
        "event_name": "Woodwind Quintet",
        "event_names": ["Woodwind Quintet"],
        "title": "Woodwind Quintets",
        "csv_path": WOODWIND_QUINTET_SOURCE_CSV_PATH,
        "songs_output": STATIC_DATA_DIR / "woodwind-quintet.json",
        "stats_output": STATIC_DATA_DIR / "woodwind-quintet-stats.json",
    },
    "misc-woodwind-ensemble": {
        "event_name": "Miscellaneous Woodwind Ensemble",
        "event_names": ["Miscellaneous Woodwind Ensemble"],
        "title": "Miscellaneous Woodwind Ensembles",
        "csv_path": MISC_WOODWIND_ENSEMBLE_SOURCE_CSV_PATH,
        "songs_output": STATIC_DATA_DIR / "misc-woodwind-ensemble.json",
        "stats_output": STATIC_DATA_DIR / "misc-woodwind-ensemble-stats.json",
    },
    "double-reed-ensemble": {
        "event_name": "Double Reed Ensemble",
        "event_names": ["Double Reed Ensemble"],
        "title": "Double Reed Ensembles",
        "csv_path": DOUBLE_REED_ENSEMBLE_SOURCE_CSV_PATH,
        "songs_output": STATIC_DATA_DIR / "double-reed-ensemble.json",
        "stats_output": STATIC_DATA_DIR / "double-reed-ensemble-stats.json",
    },
    "flute-choir": {
        "event_name": "Flute Choir",
        "event_names": ["Flute Choir"],
        "title": "Flute Choirs",
        "csv_path": FLUTE_CHOIR_SOURCE_CSV_PATH,
        "songs_output": STATIC_DATA_DIR / "flute-choir.json",
        "stats_output": STATIC_DATA_DIR / "flute-choir-stats.json",
    },
    "clarinet-choir": {
        "event_name": "Clarinet Choir",
        "event_names": ["Clarinet Choir"],
        "title": "Clarinet Choirs",
        "csv_path": CLARINET_CHOIR_SOURCE_CSV_PATH,
        "songs_output": STATIC_DATA_DIR / "clarinet-choir.json",
        "stats_output": STATIC_DATA_DIR / "clarinet-choir-stats.json",
    },
    "misc-saxophone-ensemble": {
        "event_name": "Miscellaneous Saxophone Ensemble",
        "event_names": ["Miscellaneous Saxophone Ensemble"],
        "title": "Miscellaneous Saxophone Ensembles",
        "csv_path": MISC_SAXOPHONE_ENSEMBLE_SOURCE_CSV_PATH,
        "songs_output": STATIC_DATA_DIR / "misc-saxophone-ensemble.json",
        "stats_output": STATIC_DATA_DIR / "misc-saxophone-ensemble-stats.json",
    },
    "trumpet-trio": {
        "event_name": "Trumpet Trio",
        "event_names": ["Trumpet Trio"],
        "title": "Trumpet Trios",
        "csv_path": TRUMPET_TRIO_SOURCE_CSV_PATH,
        "songs_output": STATIC_DATA_DIR / "trumpet-trio.json",
        "stats_output": STATIC_DATA_DIR / "trumpet-trio-stats.json",
    },
    "trombone-trio": {
        "event_name": "Trombone Trio",
        "event_names": ["Trombone Trio"],
        "title": "Trombone Trios",
        "csv_path": TROMBONE_TRIO_SOURCE_CSV_PATH,
        "songs_output": STATIC_DATA_DIR / "trombone-trio.json",
        "stats_output": STATIC_DATA_DIR / "trombone-trio-stats.json",
    },
    "euphonium-baritone-trio": {
        "event_name": "Euphonium-Baritone Trio",
        "event_names": ["Euphonium-Baritone Trio"],
        "title": "Euphonium-Baritone Trios",
        "csv_path": EUPHONIUM_BARITONE_TRIO_SOURCE_CSV_PATH,
        "songs_output": STATIC_DATA_DIR / "euphonium-baritone-trio.json",
        "stats_output": STATIC_DATA_DIR / "euphonium-baritone-trio-stats.json",
    },
    "brass-trio": {
        "event_name": "Brass Trio",
        "event_names": ["Brass Trio"],
        "title": "Brass Trios",
        "csv_path": BRASS_TRIO_SOURCE_CSV_PATH,
        "songs_output": STATIC_DATA_DIR / "brass-trio.json",
        "stats_output": STATIC_DATA_DIR / "brass-trio-stats.json",
    },
    "trumpet-quartet": {
        "event_name": "Trumpet Quartet",
        "event_names": ["Trumpet Quartet"],
        "title": "Trumpet Quartets",
        "csv_path": TRUMPET_QUARTET_SOURCE_CSV_PATH,
        "songs_output": STATIC_DATA_DIR / "trumpet-quartet.json",
        "stats_output": STATIC_DATA_DIR / "trumpet-quartet-stats.json",
    },
    "horn-quartet": {
        "event_name": "Horn Quartet",
        "event_names": ["Horn Quartet"],
        "title": "Horn Quartets",
        "csv_path": HORN_QUARTET_SOURCE_CSV_PATH,
        "songs_output": STATIC_DATA_DIR / "horn-quartet.json",
        "stats_output": STATIC_DATA_DIR / "horn-quartet-stats.json",
    },
    "euphonium-baritone-quartet": {
        "event_name": "Euphonium/Baritone Horn Quartet",
        "event_names": ["Euphonium/Baritone Horn Quartet"],
        "title": "Euphonium and Baritone Horn Quartets",
        "csv_path": EUPHONIUM_BARITONE_QUARTET_SOURCE_CSV_PATH,
        "songs_output": STATIC_DATA_DIR / "euphonium-baritone-quartet.json",
        "stats_output": STATIC_DATA_DIR / "euphonium-baritone-quartet-stats.json",
    },
    "brass-quartet": {
        "event_name": "Brass Quartet",
        "event_names": ["Brass Quartet"],
        "title": "Brass Quartets",
        "csv_path": BRASS_QUARTET_SOURCE_CSV_PATH,
        "songs_output": STATIC_DATA_DIR / "brass-quartet.json",
        "stats_output": STATIC_DATA_DIR / "brass-quartet-stats.json",
    },
    "trombone-quartet": {
        "event_name": "Trombone Quartet",
        "event_names": ["Trombone Quartet"],
        "title": "Trombone Quartets",
        "csv_path": TROMBONE_QUARTET_SOURCE_CSV_PATH,
        "songs_output": STATIC_DATA_DIR / "trombone-quartet.json",
        "stats_output": STATIC_DATA_DIR / "trombone-quartet-stats.json",
    },
    "tuba-euphonium-quartet": {
        "event_name": "Tuba/Euphonium Quartet",
        "event_names": ["Tuba/Euphonium Quartet"],
        "title": "Tuba and Euphonium Quartets",
        "csv_path": TUBA_EUPHONIUM_QUARTET_SOURCE_CSV_PATH,
        "songs_output": STATIC_DATA_DIR / "tuba-euphonium-quartet.json",
        "stats_output": STATIC_DATA_DIR / "tuba-euphonium-quartet-stats.json",
    },
    "brass-quintet": {
        "event_name": "Brass Quintet",
        "event_names": ["Brass Quintet"],
        "title": "Brass Quintets",
        "csv_path": BRASS_QUINTET_SOURCE_CSV_PATH,
        "songs_output": STATIC_DATA_DIR / "brass-quintet.json",
        "stats_output": STATIC_DATA_DIR / "brass-quintet-stats.json",
    },
    "brass-sextet": {
        "event_name": "Brass Sextet",
        "event_names": ["Brass Sextet"],
        "title": "Brass Sextets",
        "csv_path": BRASS_SEXTET_SOURCE_CSV_PATH,
        "songs_output": STATIC_DATA_DIR / "brass-sextet.json",
        "stats_output": STATIC_DATA_DIR / "brass-sextet-stats.json",
    },
    "six-or-more-brass": {
        "event_name": "Six or More Brass",
        "event_names": ["Six or More Brass"],
        "title": "Six or More Brass Ensembles",
        "csv_path": SIX_OR_MORE_BRASS_SOURCE_CSV_PATH,
        "songs_output": STATIC_DATA_DIR / "six-or-more-brass.json",
        "stats_output": STATIC_DATA_DIR / "six-or-more-brass-stats.json",
    },
    "trumpet-choir": {
        "event_name": "Trumpet Choir",
        "event_names": ["Trumpet Choir"],
        "title": "Trumpet Choirs",
        "csv_path": TRUMPET_CHOIR_SOURCE_CSV_PATH,
        "songs_output": STATIC_DATA_DIR / "trumpet-choir.json",
        "stats_output": STATIC_DATA_DIR / "trumpet-choir-stats.json",
    },
    "misc-horn-ensemble": {
        "event_name": "Miscellaneous Horn Ensemble",
        "event_names": ["Miscellaneous Horn Ensemble"],
        "title": "Miscellaneous Horn Ensembles",
        "csv_path": MISC_HORN_ENSEMBLE_SOURCE_CSV_PATH,
        "songs_output": STATIC_DATA_DIR / "misc-horn-ensemble.json",
        "stats_output": STATIC_DATA_DIR / "misc-horn-ensemble-stats.json",
    },
    "trombone-choir": {
        "event_name": "Trombone Choir",
        "event_names": ["Trombone Choir"],
        "title": "Trombone Choirs",
        "csv_path": TROMBONE_CHOIR_SOURCE_CSV_PATH,
        "songs_output": STATIC_DATA_DIR / "trombone-choir.json",
        "stats_output": STATIC_DATA_DIR / "trombone-choir-stats.json",
    },
    "percussion-ensemble": {
        "event_name": "Percussion Ensemble",
        "event_names": ["Percussion Ensemble"],
        "title": "Percussion Ensembles",
        "csv_path": PERCUSSION_ENSEMBLE_SOURCE_CSV_PATH,
        "songs_output": STATIC_DATA_DIR / "percussion-ensemble.json",
        "stats_output": STATIC_DATA_DIR / "percussion-ensemble-stats.json",
    },
    "steel-band": {
        "event_name": "Steel Band",
        "event_names": ["Steel Band"],
        "title": "Steel Bands",
        "csv_path": STEEL_BAND_SOURCE_CSV_PATH,
        "songs_output": STATIC_DATA_DIR / "steel-band.json",
        "stats_output": STATIC_DATA_DIR / "steel-band-stats.json",
    },
    "misc-mixed-ensemble": {
        "event_name": "Miscellaneous Mixed Ensemble",
        "event_names": ["Miscellaneous Mixed Ensemble"],
        "title": "Miscellaneous Mixed Ensembles",
        "csv_path": MISC_MIXED_ENSEMBLE_SOURCE_CSV_PATH,
        "songs_output": STATIC_DATA_DIR / "misc-mixed-ensemble.json",
        "stats_output": STATIC_DATA_DIR / "misc-mixed-ensemble-stats.json",
    },
    "acoustical-guitar": {
        "event_name": "Acoustical Guitar Solo",
        "event_names": ["Acoustical Guitar Solo"],
        "title": "Acoustical Guitar Solos",
        "csv_path": ACOUSTICAL_GUITAR_SOURCE_CSV_PATH,
        "songs_output": STATIC_DATA_DIR / "acoustical-guitar-solos.json",
        "stats_output": STATIC_DATA_DIR / "acoustical-guitar-stats.json",
    },
    "piano-trio": {
        "event_name": "Piano Trio",
        "event_names": ["Piano Trio"],
        "title": "Piano Trios",
        "csv_path": PIANO_TRIO_SOURCE_CSV_PATH,
        "songs_output": STATIC_DATA_DIR / "piano-trio.json",
        "stats_output": STATIC_DATA_DIR / "piano-trio-stats.json",
    },
    "violin-trio": {
        "event_name": "Violin Trio",
        "event_names": ["Violin Trio"],
        "title": "Violin Trios",
        "csv_path": VIOLIN_TRIO_SOURCE_CSV_PATH,
        "songs_output": STATIC_DATA_DIR / "violin-trio.json",
        "stats_output": STATIC_DATA_DIR / "violin-trio-stats.json",
    },
    "string-trio": {
        "event_name": "String Trio",
        "event_names": ["String Trio"],
        "title": "String Trios",
        "csv_path": STRING_TRIO_SOURCE_CSV_PATH,
        "songs_output": STATIC_DATA_DIR / "string-trio.json",
        "stats_output": STATIC_DATA_DIR / "string-trio-stats.json",
    },
    "misc-string-trio": {
        "event_name": "Miscellaneous String Trio",
        "event_names": ["Miscellaneous String Trio"],
        "title": "Miscellaneous String Trios",
        "csv_path": MISC_STRING_TRIO_SOURCE_CSV_PATH,
        "songs_output": STATIC_DATA_DIR / "misc-string-trio.json",
        "stats_output": STATIC_DATA_DIR / "misc-string-trio-stats.json",
    },
    "guitar-trio": {
        "event_name": "Guitar Trio",
        "event_names": ["Guitar Trio"],
        "title": "Guitar Trios",
        "csv_path": GUITAR_TRIO_SOURCE_CSV_PATH,
        "songs_output": STATIC_DATA_DIR / "guitar-trio.json",
        "stats_output": STATIC_DATA_DIR / "guitar-trio-stats.json",
    },
    "violin-quartets": {
        "event_name": "Violin Quartets",
        "event_names": ["Violin Quartets"],
        "title": "Violin Quartets",
        "csv_path": VIOLIN_QUARTETS_SOURCE_CSV_PATH,
        "songs_output": STATIC_DATA_DIR / "violin-quartets.json",
        "stats_output": STATIC_DATA_DIR / "violin-quartets-stats.json",
    },
    "string-quartet": {
        "event_name": "String Quartet",
        "event_names": ["String Quartet"],
        "title": "String Quartets",
        "csv_path": STRING_QUARTET_SOURCE_CSV_PATH,
        "songs_output": STATIC_DATA_DIR / "string-quartet.json",
        "stats_output": STATIC_DATA_DIR / "string-quartet-stats.json",
    },
    "misc-string-quartet": {
        "event_name": "Miscellaneous String Quartet",
        "event_names": ["Miscellaneous String Quartet"],
        "title": "Miscellaneous String Quartets",
        "csv_path": MISC_STRING_QUARTET_SOURCE_CSV_PATH,
        "songs_output": STATIC_DATA_DIR / "misc-string-quartet.json",
        "stats_output": STATIC_DATA_DIR / "misc-string-quartet-stats.json",
    },
    "guitar-quartet": {
        "event_name": "Guitar Quartet",
        "event_names": ["Guitar Quartet"],
        "title": "Guitar Quartets",
        "csv_path": GUITAR_QUARTET_SOURCE_CSV_PATH,
        "songs_output": STATIC_DATA_DIR / "guitar-quartet.json",
        "stats_output": STATIC_DATA_DIR / "guitar-quartet-stats.json",
    },
    "string-quintet": {
        "event_name": "String Quintet",
        "event_names": ["String Quintet"],
        "title": "String Quintets",
        "csv_path": STRING_QUINTET_SOURCE_CSV_PATH,
        "songs_output": STATIC_DATA_DIR / "string-quintet.json",
        "stats_output": STATIC_DATA_DIR / "string-quintet-stats.json",
    },
    "misc-string-quintet": {
        "event_name": "Miscellaneous String Quintet",
        "event_names": ["Miscellaneous String Quintet"],
        "title": "Miscellaneous String Quintets",
        "csv_path": MISC_STRING_QUINTET_SOURCE_CSV_PATH,
        "songs_output": STATIC_DATA_DIR / "misc-string-quintet.json",
        "stats_output": STATIC_DATA_DIR / "misc-string-quintet-stats.json",
    },
    "misc-string-ensemble": {
        "event_name": "Miscellaneous String Ensemble",
        "event_names": ["Miscellaneous String Ensemble"],
        "title": "Miscellaneous String Ensembles",
        "csv_path": MISC_STRING_ENSEMBLE_SOURCE_CSV_PATH,
        "songs_output": STATIC_DATA_DIR / "misc-string-ensemble.json",
        "stats_output": STATIC_DATA_DIR / "misc-string-ensemble-stats.json",
    },
    "misc-guitar-ensemble": {
        "event_name": "Miscellaneous Guitar Ensemble",
        "event_names": ["Miscellaneous Guitar Ensemble"],
        "title": "Miscellaneous Guitar Ensembles",
        "csv_path": MISC_GUITAR_ENSEMBLE_SOURCE_CSV_PATH,
        "songs_output": STATIC_DATA_DIR / "misc-guitar-ensemble.json",
        "stats_output": STATIC_DATA_DIR / "misc-guitar-ensemble-stats.json",
    },
    "cello-choir": {
        "event_name": "Cello Choir",
        "event_names": ["Cello Choir"],
        "title": "Cello Choirs",
        "csv_path": CELLO_CHOIR_SOURCE_CSV_PATH,
        "songs_output": STATIC_DATA_DIR / "cello-choir.json",
        "stats_output": STATIC_DATA_DIR / "cello-choir-stats.json",
    },
    "harp": {
        "event_name": "Harp Solo",
        "event_names": ["Harp Solo"],
        "title": "Harp Solos",
        "csv_path": HARP_SOURCE_CSV_PATH,
        "songs_output": STATIC_DATA_DIR / "harp-solos.json",
        "stats_output": STATIC_DATA_DIR / "harp-stats.json",
    },
    "harp-ensemble": {
        "event_name": "Harp Ensemble",
        "event_names": ["Harp Ensemble"],
        "title": "Harp Ensembles",
        "csv_path": HARP_ENSEMBLE_SOURCE_CSV_PATH,
        "songs_output": STATIC_DATA_DIR / "harp-ensemble.json",
        "stats_output": STATIC_DATA_DIR / "harp-ensemble-stats.json",
    },
    "full-orchestra": {
        "event_name": "Full Orchestra",
        "event_names": ["Full Orchestra"],
        "title": "Full Orchestra",
        "csv_path": FULL_ORCHESTRA_SOURCE_CSV_PATH,
        "songs_output": STATIC_DATA_DIR / "full-orchestra.json",
        "stats_output": STATIC_DATA_DIR / "full-orchestra-stats.json",
    },
    "string-orchestra": {
        "event_name": "String Orchestra",
        "event_names": ["String Orchestra"],
        "title": "String Orchestra",
        "csv_path": STRING_ORCHESTRA_SOURCE_CSV_PATH,
        "songs_output": STATIC_DATA_DIR / "string-orchestra.json",
        "stats_output": STATIC_DATA_DIR / "string-orchestra-stats.json",
    },
    "vocal": {
        "event_name": "Vocal Solo",
        "event_names": ["Vocal Solo"],
        "title": "Vocal Solos",
        "csv_path": VOCAL_SOURCE_CSV_PATH,
        "songs_output": STATIC_DATA_DIR / "vocal-solos.json",
        "stats_output": STATIC_DATA_DIR / "vocal-stats.json",
    },
    "treble-small-ensemble": {
        "event_name": "Treble Small Ensemble",
        "event_names": ["Treble Small Ensemble"],
        "title": "Treble Small Ensembles",
        "csv_path": TREBLE_SMALL_ENSEMBLE_SOURCE_CSV_PATH,
        "songs_output": STATIC_DATA_DIR / "treble-small-ensemble.json",
        "stats_output": STATIC_DATA_DIR / "treble-small-ensemble-stats.json",
    },
    "tenor-bass-small-ensemble": {
        "event_name": "Tenor-Bass Small Ensemble",
        "event_names": ["Tenor-Bass Small Ensemble"],
        "title": "Tenor-Bass Small Ensembles",
        "csv_path": TENOR_BASS_SMALL_ENSEMBLE_SOURCE_CSV_PATH,
        "songs_output": STATIC_DATA_DIR / "tenor-bass-small-ensemble.json",
        "stats_output": STATIC_DATA_DIR / "tenor-bass-small-ensemble-stats.json",
    },
    "madrigal": {
        "event_name": "Madrigal",
        "event_names": ["Madrigal"],
        "title": "Madrigals",
        "csv_path": MADRIGAL_SOURCE_CSV_PATH,
        "songs_output": STATIC_DATA_DIR / "madrigal.json",
        "stats_output": STATIC_DATA_DIR / "madrigal-stats.json",
    },
    "mixed-chorus": {
        "event_name": "Mixed Chorus",
        "event_names": ["Mixed Chorus"],
        "title": "Mixed Choruses",
        "csv_path": MIXED_CHORUS_SOURCE_CSV_PATH,
        "songs_output": STATIC_DATA_DIR / "mixed-chorus.json",
        "stats_output": STATIC_DATA_DIR / "mixed-chorus-stats.json",
    },
    "tenor-bass-chorus": {
        "event_name": "Tenor-Bass Chorus",
        "event_names": ["Tenor-Bass Chorus"],
        "title": "Tenor-Bass Choruses",
        "csv_path": TENOR_BASS_CHORUS_SOURCE_CSV_PATH,
        "songs_output": STATIC_DATA_DIR / "tenor-bass-chorus.json",
        "stats_output": STATIC_DATA_DIR / "tenor-bass-chorus-stats.json",
    },
    "treble-chorus": {
        "event_name": "Treble Chorus",
        "event_names": ["Treble Chorus"],
        "title": "Treble Choruses",
        "csv_path": TREBLE_CHORUS_SOURCE_CSV_PATH,
        "songs_output": STATIC_DATA_DIR / "treble-chorus.json",
        "stats_output": STATIC_DATA_DIR / "treble-chorus-stats.json",
    },
}


@dataclass
class SoloRow:
    code: str
    event_name: str
    title: str
    composer: str
    arranger: str
    publisher_text: str
    grade: int
    specification: str


PianoSoloRow = SoloRow


def normalize_publishers(raw_value: str) -> list[str]:
    if "<option" in (raw_value or "").lower():
        publishers = []
        for value in OPTION_PATTERN.findall(raw_value):
            cleaned = html.unescape(TAG_PATTERN.sub("", value)).strip()
            if cleaned and cleaned.lower() != "multiple publishers":
                publishers.append(cleaned)
        return publishers

    publishers = []
    for value in (raw_value or "").split(";"):
        cleaned = html.unescape(TAG_PATTERN.sub("", value)).strip()
        if cleaned:
            publishers.append(cleaned)
    return publishers


def clean_text(value: str) -> str:
    cleaned = html.unescape(TAG_PATTERN.sub("", value or "")).replace("\xa0", " ")
    return " ".join(cleaned.split())


def instrument_slug_for_event(event_name: str) -> str:
    normalized = clean_text(event_name).lower()
    for slug, config in INSTRUMENT_CONFIGS.items():
        event_names = config.get("event_names", [config["event_name"]])
        if normalized in {name.lower() for name in event_names}:
            return slug
    slug = normalized.replace("&", "and").replace("/", " ")
    slug = re.sub(r"[^a-z0-9]+", "-", slug).strip("-")
    return slug.removesuffix("-solo")


def solo_row_to_dict(row: SoloRow) -> dict:
    publishers = normalize_publishers(row.publisher_text)
    clean_specification = clean_text(row.specification)
    instrument_slug = instrument_slug_for_event(row.event_name)
    return {
        "uilCode": row.code,
        "instrumentSlug": instrument_slug,
        "instrumentName": INSTRUMENT_CONFIGS.get(instrument_slug, {}).get(
            "title", clean_text(row.event_name)
        ),
        "eventName": row.event_name,
        "title": clean_text(row.title),
        "composer": clean_text(row.composer),
        "arranger": clean_text(row.arranger),
        "publishers": publishers,
        "publisherText": ";".join(publishers),
        "classLevel": row.grade,
        "specification": clean_specification,
        "noMemoryRequired": "NMR:" in clean_specification,
    }


def write_source_csv(rows: list[SoloRow], destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(
            [
                "Code",
                "Event Name",
                "Title",
                "Composer",
                "Arranger",
                "Publisher [Collection]",
                "Grade",
                "Specification",
            ]
        )
        for row in rows:
            cleaned = solo_row_to_dict(row)
            writer.writerow(
                [
                    row.code,
                    row.event_name,
                    cleaned["title"],
                    cleaned["composer"],
                    cleaned["arranger"],
                    cleaned["publisherText"],
                    row.grade,
                    cleaned["specification"],
                ]
            )


def read_rows_from_csv(csv_path: Path) -> list[SoloRow]:
    with csv_path.open(newline="", encoding="utf-8-sig") as csv_file:
        reader = csv.DictReader(csv_file)
        return [
            SoloRow(
                code=row["Code"].strip(),
                event_name=row["Event Name"].strip(),
                title=row["Title"].strip(),
                composer=row["Composer"].strip(),
                arranger=row["Arranger"].strip(),
                publisher_text=row["Publisher [Collection]"].strip(),
                grade=int(row["Grade"].strip()),
                specification=row["Specification"].strip(),
            )
            for row in reader
        ]


def dataset_note_rows(source_label: str) -> list[tuple[str, str]]:
    return [
        (
            "dataset_audit",
            (
                f"Sourced from {source_label}. "
                f"Imported {datetime.now(timezone.utc).isoformat()}."
            ),
        ),
    ]


def build_outputs(
    rows: list[SoloRow],
    *,
    school_year: str,
    source_label: str,
    instrument_slug: str,
    source_csv_path: Path | None = None,
    public_domain_links: dict[str, dict] | None = None,
) -> dict:
    STATIC_DATA_DIR.mkdir(parents=True, exist_ok=True)

    config = INSTRUMENT_CONFIGS[instrument_slug]
    songs_payload = []

    for row in rows:
        payload = solo_row_to_dict(row)
        link_info = (public_domain_links or {}).get(row.code, {})
        payload["publicDomainPdfUrl"] = link_info.get("pdfUrl")
        payload["publicDomainSource"] = link_info.get("source")
        songs_payload.append(payload)

    songs_payload.sort(
        key=lambda song: (-song["classLevel"], song["composer"], song["title"])
    )

    note_rows = dataset_note_rows(source_label)
    stats_payload = {
        "schoolYear": school_year,
        "instrumentSlug": instrument_slug,
        "instrumentName": config["title"],
        "songCount": len(songs_payload),
        "publisherCount": sum(len(song["publishers"]) for song in songs_payload),
        "noteCount": len(note_rows),
        "databaseRecordCount": len(songs_payload) + len(note_rows),
        "classBreakdown": {
            "3": sum(song["classLevel"] == 3 for song in songs_payload),
            "2": sum(song["classLevel"] == 2 for song in songs_payload),
            "1": sum(song["classLevel"] == 1 for song in songs_payload),
        },
        "noMemoryRequiredCount": sum(
            song["noMemoryRequired"] for song in songs_payload
        ),
        "publicDomainPdfCount": sum(
            bool(song["publicDomainPdfUrl"]) for song in songs_payload
        ),
        "eventBreakdown": {
            event_name: sum(song["eventName"] == event_name for song in songs_payload)
            for event_name in sorted({song["eventName"] for song in songs_payload})
        },
        "notes": {key: value for key, value in note_rows},
    }

    config["songs_output"].write_text(
        json.dumps(songs_payload, indent=2), encoding="utf-8"
    )
    config["stats_output"].write_text(
        json.dumps(stats_payload, indent=2), encoding="utf-8"
    )

    legacy_stats_output = config.get("legacy_stats_output")
    if legacy_stats_output:
        legacy_stats_output.write_text(
            json.dumps(stats_payload, indent=2), encoding="utf-8"
        )

    if source_csv_path is not None:
        write_source_csv(rows, source_csv_path)

    return stats_payload


def build_from_csv(
    csv_path: Path = SOURCE_CSV_PATH,
    *,
    school_year: str = DEFAULT_SCHOOL_YEAR,
    source_label: str = "local CSV snapshot",
    instrument_slug: str = "piano",
    public_domain_links: dict[str, dict] | None = None,
) -> dict:
    rows = read_rows_from_csv(csv_path)
    return build_outputs(
        rows,
        school_year=school_year,
        source_label=source_label,
        instrument_slug=instrument_slug,
        source_csv_path=csv_path,
        public_domain_links=public_domain_links,
    )


def build_all_from_csv(
    *,
    school_year: str = DEFAULT_SCHOOL_YEAR,
    source_label: str = "local CSV snapshots",
    public_domain_links_by_instrument: dict[str, dict[str, dict]] | None = None,
) -> dict[str, dict]:
    outputs = {}
    for instrument_slug, config in INSTRUMENT_CONFIGS.items():
        csv_path = config["csv_path"]
        if not csv_path.exists():
            continue
        outputs[instrument_slug] = build_from_csv(
            csv_path,
            school_year=school_year,
            source_label=source_label,
            instrument_slug=instrument_slug,
            public_domain_links=(public_domain_links_by_instrument or {}).get(
                instrument_slug
            ),
        )
    return outputs


if __name__ == "__main__":
    build_all_from_csv()
