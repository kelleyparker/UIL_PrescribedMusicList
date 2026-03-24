const songGrid = document.getElementById("song-grid");
const resultSummary = document.getElementById("result-summary");
const datasetNote = document.getElementById("dataset-note");
const searchInput = document.getElementById("search-input");
const heroTitle = document.getElementById("hero-title");
const heroCopy = document.getElementById("hero-copy");
const songCount = document.getElementById("song-count");
const databaseRecordCount = document.getElementById("database-record-count");
const classBreakdown = document.getElementById("class-breakdown");
const nmrCount = document.getElementById("nmr-count");
const pdfCount = document.getElementById("pdf-count");
const themeSelect = document.getElementById("theme-select");
const filterButtons = [...document.querySelectorAll(".filter-chip")];
const instrumentButtons = [...document.querySelectorAll(".instrument-chip")];
const cardTemplate = document.getElementById("song-card-template");

const instruments = {
  piano: {
    slug: "piano",
    label: "Piano Solos",
    shortLabel: "piano solo",
    songsUrl: "./data/piano-solos.json",
    statsUrl: "./data/piano-stats.json",
    titlePlaceholder: "Try Bach, Sonatina, or Alfred",
    heroCopy:
      "Browse UIL piano solos by class, search titles and composers, and open verified public-domain sheet music where it is available.",
  },
  clarinet: {
    slug: "clarinet",
    label: "Clarinet Family Solos",
    shortLabel: "clarinet solo",
    songsUrl: "./data/clarinet-solos.json",
    statsUrl: "./data/clarinet-stats.json",
    titlePlaceholder: "Try Brahms, Sonata, or Rubank",
    heroCopy:
      "Browse all UIL clarinet-family solo events, including Bb, Bass, Alto, Eb, and Contra Bass Clarinet, then filter by class or No Memory Required and open public-domain sheet music where available.",
  },
  "french-horn": {
    slug: "french-horn",
    label: "French Horn Solos",
    shortLabel: "french horn solo",
    songsUrl: "./data/french-horn-solos.json",
    statsUrl: "./data/french-horn-stats.json",
    titlePlaceholder: "Try Mozart, Sonata, or Boosey",
    heroCopy:
      "Browse UIL French horn solos by class, search titles, composers, and publishers, and open verified public-domain sheet music where it is available.",
  },
  saxophone: {
    slug: "saxophone",
    label: "Saxophone Family Solos",
    shortLabel: "saxophone solo",
    songsUrl: "./data/saxophone-solos.json",
    statsUrl: "./data/saxophone-stats.json",
    titlePlaceholder: "Try Creston, Sonata, or Rubank",
    heroCopy:
      "Browse UIL saxophone-family solos, including soprano, alto, tenor, and baritone saxophone events, then filter by class or No Memory Required and search titles, composers, and publishers.",
  },
  trombone: {
    slug: "trombone",
    label: "Trombone Solos",
    shortLabel: "trombone solo",
    songsUrl: "./data/trombone-solos.json",
    statsUrl: "./data/trombone-stats.json",
    titlePlaceholder: "Try Rimsky, Concertino, or Voxman",
    heroCopy:
      "Browse UIL trombone solos across tenor and bass trombone events, then filter by class or No Memory Required and search titles, composers, and publishers.",
  },
  tuba: {
    slug: "tuba",
    label: "Tuba Solos",
    shortLabel: "tuba solo",
    songsUrl: "./data/tuba-solos.json",
    statsUrl: "./data/tuba-stats.json",
    titlePlaceholder: "Try Vaughan, Suite, or Encore",
    heroCopy:
      "Browse UIL tuba solos by class, search titles, composers, and publishers, and quickly scan No Memory Required repertoire.",
  },
  trumpet: {
    slug: "trumpet",
    label: "Trumpet Solos",
    shortLabel: "trumpet solo",
    songsUrl: "./data/trumpet-solos.json",
    statsUrl: "./data/trumpet-stats.json",
    titlePlaceholder: "Try Arban, Concerto, or Rubank",
    heroCopy:
      "Browse UIL cornet and trumpet solos by class, search titles, composers, and publishers, and open verified public-domain sheet music where it is available.",
  },
  flute: {
    slug: "flute",
    label: "Flute Solos",
    shortLabel: "flute solo",
    songsUrl: "./data/flute-solos.json",
    statsUrl: "./data/flute-stats.json",
    titlePlaceholder: "Try Chaminade, Sonata, or Southern",
    heroCopy:
      "Browse UIL flute solos by class, search titles, composers, and publishers, and open verified public-domain sheet music where it is available.",
  },
  oboe: {
    slug: "oboe",
    label: "Oboe Solos",
    shortLabel: "oboe solo",
    songsUrl: "./data/oboe-solos.json",
    statsUrl: "./data/oboe-stats.json",
    titlePlaceholder: "Try Handel, Sonata, or Belwin",
    heroCopy:
      "Browse UIL oboe solos by class, search titles, composers, and publishers, and open verified public-domain sheet music where it is available.",
  },
  bassoon: {
    slug: "bassoon",
    label: "Bassoon Solos",
    shortLabel: "bassoon solo",
    songsUrl: "./data/bassoon-solos.json",
    statsUrl: "./data/bassoon-stats.json",
    titlePlaceholder: "Try Telemann, Suite, or Schirmer",
    heroCopy:
      "Browse UIL bassoon solos by class, search titles, composers, and publishers, and open verified public-domain sheet music where it is available.",
  },
  "alto-saxophone": {
    slug: "alto-saxophone",
    label: "Alto Saxophone Solos",
    shortLabel: "alto saxophone solo",
    songsUrl: "./data/alto-saxophone-solos.json",
    statsUrl: "./data/alto-saxophone-stats.json",
    titlePlaceholder: "Try Creston, Sonata, or Leduc",
    heroCopy:
      "Browse UIL alto saxophone solos by class, search titles, composers, and publishers, and open verified public-domain sheet music where it is available.",
  },
  violin: {
    slug: "violin",
    label: "Violin Solos",
    shortLabel: "violin solo",
    songsUrl: "./data/violin-solos.json",
    statsUrl: "./data/violin-stats.json",
    titlePlaceholder: "Try Accolay, Concerto, or Suzuki",
    heroCopy:
      "Browse UIL violin solos by class, search titles, composers, and publishers, and quickly scan the current string repertoire.",
  },
  viola: {
    slug: "viola",
    label: "Viola Solos",
    shortLabel: "viola solo",
    songsUrl: "./data/viola-solos.json",
    statsUrl: "./data/viola-stats.json",
    titlePlaceholder: "Try Telemann, Sonata, or Schirmer",
    heroCopy:
      "Browse UIL viola solos by class, search titles, composers, and publishers, and explore the current string literature list.",
  },
  cello: {
    slug: "cello",
    label: "Cello Solos",
    shortLabel: "cello solo",
    songsUrl: "./data/cello-solos.json",
    statsUrl: "./data/cello-stats.json",
    titlePlaceholder: "Try Goltermann, Sonata, or Rubank",
    heroCopy:
      "Browse UIL cello solos by class, search titles, composers, and publishers, and filter quickly through the current solo list.",
  },
  "string-bass": {
    slug: "string-bass",
    label: "String Bass Solos",
    shortLabel: "string bass solo",
    songsUrl: "./data/string-bass-solos.json",
    statsUrl: "./data/string-bass-stats.json",
    titlePlaceholder: "Try Capuzzi, Sonata, or Ludwig",
    heroCopy:
      "Browse UIL string bass solos by class, search titles, composers, and publishers, and review the current orchestral string repertoire.",
  },
  euphonium: {
    slug: "euphonium",
    label: "Euphonium and Baritone Horn Solos",
    shortLabel: "euphonium solo",
    songsUrl: "./data/euphonium-solos.json",
    statsUrl: "./data/euphonium-stats.json",
    titlePlaceholder: "Try Barat, Suite, or Encore",
    heroCopy:
      "Browse UIL euphonium and baritone horn solos by class, search titles, composers, and publishers, and review the current low-brass literature list.",
  },
  piccolo: {
    slug: "piccolo",
    label: "Piccolo Solos",
    shortLabel: "piccolo solo",
    songsUrl: "./data/piccolo-solos.json",
    statsUrl: "./data/piccolo-stats.json",
    titlePlaceholder: "Try Vivaldi, Sonata, or Southern",
    heroCopy:
      "Browse UIL piccolo solos by class, search titles, composers, and publishers, and review the current upper-woodwind literature list.",
  },
  "english-horn": {
    slug: "english-horn",
    label: "English Horn Solos",
    shortLabel: "English horn solo",
    songsUrl: "./data/english-horn-solos.json",
    statsUrl: "./data/english-horn-stats.json",
    titlePlaceholder: "Try Donizetti, Sonata, or Rubank",
    heroCopy:
      "Find a better way to acquire your UIL English horn music, with Amazon affiliate links provided for select titles when you are ready to purchase sheet music.",
  },
  "snare-drum": {
    slug: "snare-drum",
    label: "Snare Drum Solos",
    shortLabel: "snare drum solo",
    songsUrl: "./data/snare-drum-solos.json",
    statsUrl: "./data/snare-drum-stats.json",
    titlePlaceholder: "Try Delecluse, Portraits, or Meredith",
    heroCopy:
      "Browse UIL snare drum solos by class, search titles, composers, and publishers, and review the current percussion solo list.",
  },
  timpani: {
    slug: "timpani",
    label: "Timpani Solos",
    shortLabel: "timpani solo",
    songsUrl: "./data/timpani-solos.json",
    statsUrl: "./data/timpani-stats.json",
    titlePlaceholder: "Try Carter, Sonata, or Meredith",
    heroCopy:
      "Browse UIL timpani solos by class, search titles, composers, and publishers, and review the current percussion solo list.",
  },
  "keyboard-percussion": {
    slug: "keyboard-percussion",
    label: "Keyboard Percussion Solos",
    shortLabel: "keyboard percussion solo",
    songsUrl: "./data/keyboard-percussion-solos.json",
    statsUrl: "./data/keyboard-percussion-stats.json",
    titlePlaceholder: "Try Rosauro, Etude, or Keyboard",
    heroCopy:
      "Browse UIL keyboard percussion solos by class, search titles, composers, and publishers, and review the current mallet literature list.",
  },
  "multiple-percussion": {
    slug: "multiple-percussion",
    label: "Multiple Percussion Solos",
    shortLabel: "multiple percussion solo",
    songsUrl: "./data/multiple-percussion-solos.json",
    statsUrl: "./data/multiple-percussion-stats.json",
    titlePlaceholder: "Try Cahn, Suite, or Studio",
    heroCopy:
      "Browse UIL multiple percussion solos by class, search titles, composers, and publishers, and review the current setup-percussion literature list.",
  },
  "drum-set": {
    slug: "drum-set",
    label: "Drum Set Solos",
    shortLabel: "drum set solo",
    songsUrl: "./data/drum-set-solos.json",
    statsUrl: "./data/drum-set-stats.json",
    titlePlaceholder: "Try Wilcoxon, Solo, or Drumset",
    heroCopy:
      "Browse UIL drum set solos by class, search titles, composers, and publishers, and review the current drum set literature list.",
  },
  "steel-pan": {
    slug: "steel-pan",
    label: "Steel Pan Solos",
    shortLabel: "steel pan solo",
    songsUrl: "./data/steel-pan-solos.json",
    statsUrl: "./data/steel-pan-stats.json",
    titlePlaceholder: "Try Trinidad, Suite, or Pan",
    heroCopy:
      "Browse UIL steel pan solos by class, search titles, composers, and publishers, and review the current steel pan literature list.",
  },
  "woodwind-trio": {
    slug: "woodwind-trio",
    label: "Woodwind Trios",
    shortLabel: "woodwind trio",
    songsUrl: "./data/woodwind-trio.json",
    statsUrl: "./data/woodwind-trio-stats.json",
    titlePlaceholder: "Try Trio, Rubank, or Ensemble",
    heroCopy:
      "Browse UIL woodwind trios, search titles, composers, and publishers, and review the current small-ensemble literature list.",
  },
  "flute-trio": {
    slug: "flute-trio",
    label: "Flute Trios",
    shortLabel: "flute trio",
    songsUrl: "./data/flute-trio.json",
    statsUrl: "./data/flute-trio-stats.json",
    titlePlaceholder: "Try Trio, Southern, or Ensemble",
    heroCopy:
      "Browse UIL flute trios, search titles, composers, and publishers, and review the current chamber literature list.",
  },
  "bb-clarinet-trio": {
    slug: "bb-clarinet-trio",
    label: "Bb Clarinet Trios",
    shortLabel: "Bb clarinet trio",
    songsUrl: "./data/bb-clarinet-trio.json",
    statsUrl: "./data/bb-clarinet-trio-stats.json",
    titlePlaceholder: "Try Trio, Rubank, or Clarinet",
    heroCopy:
      "Browse UIL Bb clarinet trios, search titles, composers, and publishers, and review the current clarinet ensemble literature.",
  },
  "mixed-clarinet-trio": {
    slug: "mixed-clarinet-trio",
    label: "Mixed Clarinet Trios",
    shortLabel: "mixed clarinet trio",
    songsUrl: "./data/mixed-clarinet-trio.json",
    statsUrl: "./data/mixed-clarinet-trio-stats.json",
    titlePlaceholder: "Try Trio, Clarinet, or Ensemble",
    heroCopy:
      "Browse UIL mixed clarinet trios, search titles, composers, and publishers, and review the current clarinet-family chamber literature.",
  },
  "woodwind-quartet": {
    slug: "woodwind-quartet",
    label: "Woodwind Quartets",
    shortLabel: "woodwind quartet",
    songsUrl: "./data/woodwind-quartet.json",
    statsUrl: "./data/woodwind-quartet-stats.json",
    titlePlaceholder: "Try Quartet, Ensemble, or Rubank",
    heroCopy:
      "Browse UIL woodwind quartets, search titles, composers, and publishers, and review the current chamber literature list.",
  },
  "flute-quartet": {
    slug: "flute-quartet",
    label: "Flute Quartets",
    shortLabel: "flute quartet",
    songsUrl: "./data/flute-quartet.json",
    statsUrl: "./data/flute-quartet-stats.json",
    titlePlaceholder: "Try Quartet, Southern, or Flute",
    heroCopy:
      "Browse UIL flute quartets, search titles, composers, and publishers, and review the current flute chamber literature.",
  },
  "bb-clarinet-quartet": {
    slug: "bb-clarinet-quartet",
    label: "Bb Clarinet Quartets",
    shortLabel: "Bb clarinet quartet",
    songsUrl: "./data/bb-clarinet-quartet.json",
    statsUrl: "./data/bb-clarinet-quartet-stats.json",
    titlePlaceholder: "Try Quartet, Clarinet, or Ensemble",
    heroCopy:
      "Browse UIL Bb clarinet quartets, search titles, composers, and publishers, and review the current clarinet chamber literature.",
  },
  "mixed-clarinet-quartet": {
    slug: "mixed-clarinet-quartet",
    label: "Mixed Clarinet Quartets",
    shortLabel: "mixed clarinet quartet",
    songsUrl: "./data/mixed-clarinet-quartet.json",
    statsUrl: "./data/mixed-clarinet-quartet-stats.json",
    titlePlaceholder: "Try Quartet, Ensemble, or Clarinet",
    heroCopy:
      "Browse UIL mixed clarinet quartets, search titles, composers, and publishers, and review the current clarinet-family ensemble literature.",
  },
  "saxophone-quartet": {
    slug: "saxophone-quartet",
    label: "Saxophone Quartets",
    shortLabel: "saxophone quartet",
    songsUrl: "./data/saxophone-quartet.json",
    statsUrl: "./data/saxophone-quartet-stats.json",
    titlePlaceholder: "Try Quartet, Londeix, or Saxophone",
    heroCopy:
      "Browse UIL saxophone quartets, search titles, composers, and publishers, and review the current saxophone ensemble literature.",
  },
  "woodwind-quintet": {
    slug: "woodwind-quintet",
    label: "Woodwind Quintets",
    shortLabel: "woodwind quintet",
    songsUrl: "./data/woodwind-quintet.json",
    statsUrl: "./data/woodwind-quintet-stats.json",
    titlePlaceholder: "Try Quintet, Ensemble, or Rubank",
    heroCopy:
      "Browse UIL woodwind quintets, search titles, composers, and publishers, and review the current chamber literature list.",
  },
  "misc-woodwind-ensemble": {
    slug: "misc-woodwind-ensemble",
    label: "Miscellaneous Woodwind Ensembles",
    shortLabel: "woodwind ensemble",
    songsUrl: "./data/misc-woodwind-ensemble.json",
    statsUrl: "./data/misc-woodwind-ensemble-stats.json",
    titlePlaceholder: "Try Ensemble, Woodwind, or Collection",
    heroCopy:
      "Browse UIL miscellaneous woodwind ensembles, search titles, composers, and publishers, and review the current chamber literature list.",
  },
  "double-reed-ensemble": {
    slug: "double-reed-ensemble",
    label: "Double Reed Ensembles",
    shortLabel: "double reed ensemble",
    songsUrl: "./data/double-reed-ensemble.json",
    statsUrl: "./data/double-reed-ensemble-stats.json",
    titlePlaceholder: "Try Reed, Ensemble, or Oboe",
    heroCopy:
      "Browse UIL double reed ensembles, search titles, composers, and publishers, and review the current reed ensemble literature.",
  },
  "flute-choir": {
    slug: "flute-choir",
    label: "Flute Choirs",
    shortLabel: "flute choir work",
    songsUrl: "./data/flute-choir.json",
    statsUrl: "./data/flute-choir-stats.json",
    titlePlaceholder: "Try Choir, Flute, or Ensemble",
    heroCopy:
      "Browse UIL flute choir literature, search titles, composers, and publishers, and review the current large-flute-ensemble list.",
  },
  "clarinet-choir": {
    slug: "clarinet-choir",
    label: "Clarinet Choirs",
    shortLabel: "clarinet choir work",
    songsUrl: "./data/clarinet-choir.json",
    statsUrl: "./data/clarinet-choir-stats.json",
    titlePlaceholder: "Try Choir, Clarinet, or Ensemble",
    heroCopy:
      "Browse UIL clarinet choir literature, search titles, composers, and publishers, and review the current clarinet choir list.",
  },
  "misc-saxophone-ensemble": {
    slug: "misc-saxophone-ensemble",
    label: "Miscellaneous Saxophone Ensembles",
    shortLabel: "saxophone ensemble",
    songsUrl: "./data/misc-saxophone-ensemble.json",
    statsUrl: "./data/misc-saxophone-ensemble-stats.json",
    titlePlaceholder: "Try Ensemble, Saxophone, or Collection",
    heroCopy:
      "Browse UIL miscellaneous saxophone ensembles, search titles, composers, and publishers, and review the current saxophone ensemble list.",
  },
  "trumpet-trio": {
    slug: "trumpet-trio",
    label: "Trumpet Trios",
    shortLabel: "trumpet trio",
    songsUrl: "./data/trumpet-trio.json",
    statsUrl: "./data/trumpet-trio-stats.json",
    titlePlaceholder: "Try Trio, Trumpet, or Ensemble",
    heroCopy:
      "Browse UIL trumpet trios, search titles, composers, and publishers, and review the current brass chamber literature.",
  },
  "trombone-trio": {
    slug: "trombone-trio",
    label: "Trombone Trios",
    shortLabel: "trombone trio",
    songsUrl: "./data/trombone-trio.json",
    statsUrl: "./data/trombone-trio-stats.json",
    titlePlaceholder: "Try Trio, Trombone, or Ensemble",
    heroCopy:
      "Browse UIL trombone trios, search titles, composers, and publishers, and review the current low-brass chamber literature.",
  },
  "euphonium-baritone-trio": {
    slug: "euphonium-baritone-trio",
    label: "Euphonium-Baritone Trios",
    shortLabel: "euphonium trio",
    songsUrl: "./data/euphonium-baritone-trio.json",
    statsUrl: "./data/euphonium-baritone-trio-stats.json",
    titlePlaceholder: "Try Trio, Baritone, or Ensemble",
    heroCopy:
      "Browse UIL euphonium-baritone trios, search titles, composers, and publishers, and review the current low-brass chamber literature.",
  },
  "brass-trio": {
    slug: "brass-trio",
    label: "Brass Trios",
    shortLabel: "brass trio",
    songsUrl: "./data/brass-trio.json",
    statsUrl: "./data/brass-trio-stats.json",
    titlePlaceholder: "Try Trio, Brass, or Ensemble",
    heroCopy:
      "Browse UIL brass trios, search titles, composers, and publishers, and review the current brass chamber literature.",
  },
  "trumpet-quartet": {
    slug: "trumpet-quartet",
    label: "Trumpet Quartets",
    shortLabel: "trumpet quartet",
    songsUrl: "./data/trumpet-quartet.json",
    statsUrl: "./data/trumpet-quartet-stats.json",
    titlePlaceholder: "Try Quartet, Trumpet, or Ensemble",
    heroCopy:
      "Browse UIL trumpet quartets, search titles, composers, and publishers, and review the current trumpet ensemble literature.",
  },
  "horn-quartet": {
    slug: "horn-quartet",
    label: "Horn Quartets",
    shortLabel: "horn quartet",
    songsUrl: "./data/horn-quartet.json",
    statsUrl: "./data/horn-quartet-stats.json",
    titlePlaceholder: "Try Quartet, Horn, or Ensemble",
    heroCopy:
      "Browse UIL horn quartets, search titles, composers, and publishers, and review the current horn ensemble literature.",
  },
  "euphonium-baritone-quartet": {
    slug: "euphonium-baritone-quartet",
    label: "Euphonium and Baritone Horn Quartets",
    shortLabel: "euphonium quartet",
    songsUrl: "./data/euphonium-baritone-quartet.json",
    statsUrl: "./data/euphonium-baritone-quartet-stats.json",
    titlePlaceholder: "Try Quartet, Baritone, or Ensemble",
    heroCopy:
      "Browse UIL euphonium and baritone horn quartets, search titles, composers, and publishers, and review the current low-brass ensemble literature.",
  },
  "brass-quartet": {
    slug: "brass-quartet",
    label: "Brass Quartets",
    shortLabel: "brass quartet",
    songsUrl: "./data/brass-quartet.json",
    statsUrl: "./data/brass-quartet-stats.json",
    titlePlaceholder: "Try Quartet, Brass, or Ensemble",
    heroCopy:
      "Browse UIL brass quartets, search titles, composers, and publishers, and review the current brass chamber literature.",
  },
  "trombone-quartet": {
    slug: "trombone-quartet",
    label: "Trombone Quartets",
    shortLabel: "trombone quartet",
    songsUrl: "./data/trombone-quartet.json",
    statsUrl: "./data/trombone-quartet-stats.json",
    titlePlaceholder: "Try Quartet, Trombone, or Ensemble",
    heroCopy:
      "Browse UIL trombone quartets, search titles, composers, and publishers, and review the current trombone ensemble literature.",
  },
  "tuba-euphonium-quartet": {
    slug: "tuba-euphonium-quartet",
    label: "Tuba and Euphonium Quartets",
    shortLabel: "tuba/euphonium quartet",
    songsUrl: "./data/tuba-euphonium-quartet.json",
    statsUrl: "./data/tuba-euphonium-quartet-stats.json",
    titlePlaceholder: "Try Quartet, Tuba, or Euphonium",
    heroCopy:
      "Browse UIL tuba and euphonium quartets, search titles, composers, and publishers, and review the current low-brass ensemble literature.",
  },
  "brass-quintet": {
    slug: "brass-quintet",
    label: "Brass Quintets",
    shortLabel: "brass quintet",
    songsUrl: "./data/brass-quintet.json",
    statsUrl: "./data/brass-quintet-stats.json",
    titlePlaceholder: "Try Quintet, Brass, or Ensemble",
    heroCopy:
      "Browse UIL brass quintets, search titles, composers, and publishers, and review the current brass chamber literature.",
  },
  "brass-sextet": {
    slug: "brass-sextet",
    label: "Brass Sextets",
    shortLabel: "brass sextet",
    songsUrl: "./data/brass-sextet.json",
    statsUrl: "./data/brass-sextet-stats.json",
    titlePlaceholder: "Try Sextet, Brass, or Ensemble",
    heroCopy:
      "Browse UIL brass sextets, search titles, composers, and publishers, and review the current brass ensemble literature.",
  },
  "six-or-more-brass": {
    slug: "six-or-more-brass",
    label: "Six or More Brass Ensembles",
    shortLabel: "brass ensemble",
    songsUrl: "./data/six-or-more-brass.json",
    statsUrl: "./data/six-or-more-brass-stats.json",
    titlePlaceholder: "Try Brass, Ensemble, or Collection",
    heroCopy:
      "Browse UIL six-or-more-brass literature, search titles, composers, and publishers, and review the current larger brass ensemble list.",
  },
  "trumpet-choir": {
    slug: "trumpet-choir",
    label: "Trumpet Choirs",
    shortLabel: "trumpet choir work",
    songsUrl: "./data/trumpet-choir.json",
    statsUrl: "./data/trumpet-choir-stats.json",
    titlePlaceholder: "Try Choir, Trumpet, or Ensemble",
    heroCopy:
      "Browse UIL trumpet choir literature, search titles, composers, and publishers, and review the current trumpet choir list.",
  },
  "misc-horn-ensemble": {
    slug: "misc-horn-ensemble",
    label: "Miscellaneous Horn Ensembles",
    shortLabel: "horn ensemble",
    songsUrl: "./data/misc-horn-ensemble.json",
    statsUrl: "./data/misc-horn-ensemble-stats.json",
    titlePlaceholder: "Try Ensemble, Horn, or Collection",
    heroCopy:
      "Browse UIL miscellaneous horn ensembles, search titles, composers, and publishers, and review the current horn ensemble literature.",
  },
  "trombone-choir": {
    slug: "trombone-choir",
    label: "Trombone Choirs",
    shortLabel: "trombone choir work",
    songsUrl: "./data/trombone-choir.json",
    statsUrl: "./data/trombone-choir-stats.json",
    titlePlaceholder: "Try Choir, Trombone, or Ensemble",
    heroCopy:
      "Browse UIL trombone choir literature, search titles, composers, and publishers, and review the current trombone choir list.",
  },
  "percussion-ensemble": {
    slug: "percussion-ensemble",
    label: "Percussion Ensembles",
    shortLabel: "percussion ensemble",
    songsUrl: "./data/percussion-ensemble.json",
    statsUrl: "./data/percussion-ensemble-stats.json",
    titlePlaceholder: "Try Ensemble, Percussion, or Collection",
    heroCopy:
      "Browse UIL percussion ensembles, search titles, composers, and publishers, and review the current percussion ensemble literature.",
  },
  "steel-band": {
    slug: "steel-band",
    label: "Steel Bands",
    shortLabel: "steel band work",
    songsUrl: "./data/steel-band.json",
    statsUrl: "./data/steel-band-stats.json",
    titlePlaceholder: "Try Band, Steel, or Pan",
    heroCopy:
      "Browse UIL steel band literature, search titles, composers, and publishers, and review the current steel band list.",
  },
  "misc-mixed-ensemble": {
    slug: "misc-mixed-ensemble",
    label: "Miscellaneous Mixed Ensembles",
    shortLabel: "mixed ensemble",
    songsUrl: "./data/misc-mixed-ensemble.json",
    statsUrl: "./data/misc-mixed-ensemble-stats.json",
    titlePlaceholder: "Try Ensemble, Mixed, or Collection",
    heroCopy:
      "Browse UIL miscellaneous mixed ensembles, search titles, composers, and publishers, and review the current mixed-instrument literature list.",
  },
};

const state = {
  activeInstrument: "piano",
  activeFilter: "all",
  query: "",
  songs: [],
  stats: null,
};

const themes = {
  "midnight-lone-star": {
    pageGlowLeft: "rgba(179, 25, 45, 0.22)",
    pageGlowRight: "rgba(25, 59, 106, 0.26)",
    pageStart: "#171c26",
    pageMid: "#11161e",
    pageEnd: "#19130f",
    heroStart: "rgba(25, 59, 106, 0.96)",
    heroMid: "rgba(25, 59, 106, 0.9)",
    heroEnd: "rgba(179, 25, 45, 0.94)",
    heroOrb: "rgba(255, 255, 255, 0.1)",
    panel: "rgba(20, 26, 38, 0.88)",
    inputBg: "rgba(14, 20, 31, 0.9)",
    border: "rgba(143, 170, 214, 0.18)",
    accentSoft: "rgba(107, 132, 176, 0.18)",
    accentSoftText: "#dbe7fb",
    activeChipBg: "#b3192d",
    activeChipText: "#ffffff",
    nmrPillBg: "rgba(179, 25, 45, 0.22)",
    nmrPillText: "#ffd8de",
    composerAccent: "#ff8f9f",
    controlLabel: "#cad5ea",
    ink: "#edf2fb",
    muted: "#9ba7bd",
    placeholder: "#7d899d",
    cardStart: "rgba(24, 31, 44, 0.98)",
    cardEnd: "rgba(16, 22, 34, 0.94)",
    statCardBg: "rgba(255, 255, 255, 0.12)",
    selectBg: "rgba(10, 15, 23, 0.42)",
    linkColor: "#ff8f9f",
  },
  "neon-rodeo": {
    pageGlowLeft: "rgba(255, 86, 34, 0.25)",
    pageGlowRight: "rgba(25, 201, 255, 0.22)",
    pageStart: "#0e1120",
    pageMid: "#120d1d",
    pageEnd: "#1a1412",
    heroStart: "#112f62",
    heroMid: "#422d77",
    heroEnd: "#ff5c39",
    heroOrb: "rgba(255, 157, 120, 0.18)",
    panel: "rgba(18, 21, 35, 0.9)",
    inputBg: "rgba(10, 14, 24, 0.94)",
    border: "rgba(127, 214, 255, 0.2)",
    accentSoft: "rgba(45, 211, 255, 0.18)",
    accentSoftText: "#d8f8ff",
    activeChipBg: "#ff5c39",
    activeChipText: "#fff4ef",
    nmrPillBg: "rgba(255, 92, 57, 0.22)",
    nmrPillText: "#ffe0d8",
    composerAccent: "#ff9b7d",
    controlLabel: "#d9ebff",
    ink: "#f0f7ff",
    muted: "#a2b3d1",
    placeholder: "#7f91ad",
    cardStart: "rgba(28, 20, 46, 0.97)",
    cardEnd: "rgba(15, 24, 48, 0.94)",
    statCardBg: "rgba(255, 255, 255, 0.1)",
    selectBg: "rgba(20, 16, 36, 0.5)",
    linkColor: "#72d9ff",
  },
  "desert-ember": {
    pageGlowLeft: "rgba(255, 110, 64, 0.24)",
    pageGlowRight: "rgba(255, 205, 96, 0.18)",
    pageStart: "#1d140f",
    pageMid: "#18110f",
    pageEnd: "#120e13",
    heroStart: "#4f2f20",
    heroMid: "#8d472b",
    heroEnd: "#d46f3b",
    heroOrb: "rgba(255, 214, 155, 0.14)",
    panel: "rgba(34, 24, 19, 0.88)",
    inputBg: "rgba(26, 18, 15, 0.92)",
    border: "rgba(231, 181, 130, 0.16)",
    accentSoft: "rgba(208, 138, 87, 0.24)",
    accentSoftText: "#ffe6cf",
    activeChipBg: "#d46f3b",
    activeChipText: "#fff7ef",
    nmrPillBg: "rgba(255, 120, 80, 0.22)",
    nmrPillText: "#ffe0d6",
    composerAccent: "#ffb28d",
    controlLabel: "#f1d8c5",
    ink: "#fff3e8",
    muted: "#c0a794",
    placeholder: "#9d8372",
    cardStart: "rgba(46, 28, 19, 0.97)",
    cardEnd: "rgba(26, 16, 14, 0.94)",
    statCardBg: "rgba(255, 226, 196, 0.1)",
    selectBg: "rgba(44, 25, 15, 0.5)",
    linkColor: "#ffbf89",
  },
  "bluebonnet-dusk": {
    pageGlowLeft: "rgba(110, 118, 255, 0.25)",
    pageGlowRight: "rgba(107, 60, 255, 0.22)",
    pageStart: "#12132a",
    pageMid: "#11101f",
    pageEnd: "#0c1523",
    heroStart: "#163a6f",
    heroMid: "#3d3e92",
    heroEnd: "#7758f6",
    heroOrb: "rgba(181, 175, 255, 0.16)",
    panel: "rgba(18, 20, 43, 0.88)",
    inputBg: "rgba(11, 14, 31, 0.92)",
    border: "rgba(161, 163, 255, 0.18)",
    accentSoft: "rgba(111, 122, 255, 0.2)",
    accentSoftText: "#ebeeff",
    activeChipBg: "#7758f6",
    activeChipText: "#f7f5ff",
    nmrPillBg: "rgba(145, 121, 255, 0.24)",
    nmrPillText: "#efe9ff",
    composerAccent: "#b8a5ff",
    controlLabel: "#dadfff",
    ink: "#eff3ff",
    muted: "#a4add9",
    placeholder: "#7e87b7",
    cardStart: "rgba(28, 24, 58, 0.97)",
    cardEnd: "rgba(16, 18, 40, 0.94)",
    statCardBg: "rgba(201, 196, 255, 0.1)",
    selectBg: "rgba(18, 18, 54, 0.48)",
    linkColor: "#b8a5ff",
  },
  "vintage-marquee": {
    pageGlowLeft: "rgba(255, 80, 72, 0.22)",
    pageGlowRight: "rgba(255, 208, 90, 0.2)",
    pageStart: "#1a1413",
    pageMid: "#151010",
    pageEnd: "#1d1811",
    heroStart: "#5a1735",
    heroMid: "#9b2e44",
    heroEnd: "#e0a12a",
    heroOrb: "rgba(255, 216, 120, 0.18)",
    panel: "rgba(30, 21, 20, 0.9)",
    inputBg: "rgba(20, 15, 14, 0.94)",
    border: "rgba(236, 176, 98, 0.18)",
    accentSoft: "rgba(224, 161, 42, 0.2)",
    accentSoftText: "#ffefc7",
    activeChipBg: "#e0a12a",
    activeChipText: "#2b170e",
    nmrPillBg: "rgba(255, 102, 86, 0.24)",
    nmrPillText: "#ffe2db",
    composerAccent: "#ffbb77",
    controlLabel: "#f8e3bc",
    ink: "#fff4df",
    muted: "#c8ae8d",
    placeholder: "#a1866c",
    cardStart: "rgba(51, 24, 29, 0.97)",
    cardEnd: "rgba(27, 19, 17, 0.94)",
    statCardBg: "rgba(255, 220, 141, 0.12)",
    selectBg: "rgba(45, 19, 23, 0.52)",
    linkColor: "#ffd16e",
  },
  "crimson-steel": {
    pageGlowLeft: "rgba(194, 46, 78, 0.24)",
    pageGlowRight: "rgba(88, 108, 141, 0.18)",
    pageStart: "#141519",
    pageMid: "#111216",
    pageEnd: "#191215",
    heroStart: "#2b3443",
    heroMid: "#5b2439",
    heroEnd: "#bf314d",
    heroOrb: "rgba(255, 170, 170, 0.12)",
    panel: "rgba(23, 24, 30, 0.9)",
    inputBg: "rgba(15, 16, 20, 0.94)",
    border: "rgba(151, 161, 179, 0.18)",
    accentSoft: "rgba(116, 130, 154, 0.22)",
    accentSoftText: "#e5ebf6",
    activeChipBg: "#bf314d",
    activeChipText: "#fff0f4",
    nmrPillBg: "rgba(194, 46, 78, 0.24)",
    nmrPillText: "#ffdbe3",
    composerAccent: "#ff8ca1",
    controlLabel: "#d2dae6",
    ink: "#eef3f9",
    muted: "#99a6b8",
    placeholder: "#7f8998",
    cardStart: "rgba(33, 27, 35, 0.97)",
    cardEnd: "rgba(18, 18, 22, 0.94)",
    statCardBg: "rgba(255, 219, 228, 0.08)",
    selectBg: "rgba(26, 21, 29, 0.5)",
    linkColor: "#ff8ca1",
  },
  "electric-teal": {
    pageGlowLeft: "rgba(18, 227, 195, 0.22)",
    pageGlowRight: "rgba(48, 116, 255, 0.2)",
    pageStart: "#0d1719",
    pageMid: "#0c1418",
    pageEnd: "#0d1020",
    heroStart: "#0e4459",
    heroMid: "#06697a",
    heroEnd: "#1a96b2",
    heroOrb: "rgba(126, 255, 244, 0.15)",
    panel: "rgba(11, 23, 28, 0.9)",
    inputBg: "rgba(8, 16, 20, 0.94)",
    border: "rgba(118, 226, 233, 0.18)",
    accentSoft: "rgba(27, 181, 196, 0.22)",
    accentSoftText: "#dbffff",
    activeChipBg: "#1a96b2",
    activeChipText: "#efffff",
    nmrPillBg: "rgba(0, 204, 170, 0.24)",
    nmrPillText: "#d9fffb",
    composerAccent: "#7af5e8",
    controlLabel: "#cff8f7",
    ink: "#ecfefd",
    muted: "#93bfc3",
    placeholder: "#709498",
    cardStart: "rgba(13, 36, 41, 0.97)",
    cardEnd: "rgba(8, 19, 24, 0.94)",
    statCardBg: "rgba(173, 255, 247, 0.08)",
    selectBg: "rgba(9, 31, 35, 0.5)",
    linkColor: "#7af5e8",
  },
  "copper-night": {
    pageGlowLeft: "rgba(203, 113, 66, 0.24)",
    pageGlowRight: "rgba(61, 96, 143, 0.2)",
    pageStart: "#16120f",
    pageMid: "#100f13",
    pageEnd: "#151922",
    heroStart: "#3b2f46",
    heroMid: "#674054",
    heroEnd: "#bd6a43",
    heroOrb: "rgba(255, 185, 144, 0.14)",
    panel: "rgba(26, 21, 23, 0.9)",
    inputBg: "rgba(18, 14, 15, 0.94)",
    border: "rgba(214, 148, 112, 0.17)",
    accentSoft: "rgba(195, 120, 84, 0.22)",
    accentSoftText: "#ffe6da",
    activeChipBg: "#bd6a43",
    activeChipText: "#fff5f0",
    nmrPillBg: "rgba(230, 126, 90, 0.24)",
    nmrPillText: "#ffe3d8",
    composerAccent: "#ffb391",
    controlLabel: "#ecd1c5",
    ink: "#faf0ea",
    muted: "#b79f98",
    placeholder: "#8e7b75",
    cardStart: "rgba(41, 27, 28, 0.97)",
    cardEnd: "rgba(22, 18, 24, 0.94)",
    statCardBg: "rgba(255, 209, 186, 0.08)",
    selectBg: "rgba(31, 18, 21, 0.5)",
    linkColor: "#ffb391",
  },
};

function setTheme(themeName) {
  const theme = themes[themeName] || themes["midnight-lone-star"];
  const root = document.documentElement;
  const body = document.body;
  root.dataset.theme = themeName;
  root.style.colorScheme = "dark";
  body.style.setProperty("--page-glow-left", theme.pageGlowLeft);
  body.style.setProperty("--page-glow-right", theme.pageGlowRight);
  body.style.setProperty("--page-start", theme.pageStart);
  body.style.setProperty("--page-mid", theme.pageMid);
  body.style.setProperty("--page-end", theme.pageEnd);
  root.style.setProperty("--hero-start", theme.heroStart);
  root.style.setProperty("--hero-mid", theme.heroMid);
  root.style.setProperty("--hero-end", theme.heroEnd);
  root.style.setProperty("--hero-orb", theme.heroOrb);
  root.style.setProperty("--panel", theme.panel);
  root.style.setProperty("--input-bg", theme.inputBg);
  root.style.setProperty("--border", theme.border);
  root.style.setProperty("--accent-soft", theme.accentSoft);
  root.style.setProperty("--accent-soft-text", theme.accentSoftText);
  root.style.setProperty("--active-chip-bg", theme.activeChipBg);
  root.style.setProperty("--active-chip-text", theme.activeChipText);
  root.style.setProperty("--nmr-pill-bg", theme.nmrPillBg);
  root.style.setProperty("--nmr-pill-text", theme.nmrPillText);
  root.style.setProperty("--composer-accent", theme.composerAccent);
  root.style.setProperty("--control-label", theme.controlLabel);
  root.style.setProperty("--ink", theme.ink);
  root.style.setProperty("--muted", theme.muted);
  root.style.setProperty("--placeholder", theme.placeholder);
  root.style.setProperty("--card-start", theme.cardStart);
  root.style.setProperty("--card-end", theme.cardEnd);
  root.style.setProperty("--stat-card-bg", theme.statCardBg);
  root.style.setProperty("--select-bg", theme.selectBg);
  root.style.setProperty("--link-color", theme.linkColor);

  body.style.background = `
    radial-gradient(circle at top left, ${theme.pageGlowLeft}, transparent 28%),
    radial-gradient(circle at top right, ${theme.pageGlowRight}, transparent 34%),
    linear-gradient(180deg, ${theme.pageStart} 0%, ${theme.pageMid} 48%, ${theme.pageEnd} 100%)
  `;

  document.querySelectorAll(".hero").forEach((element) => {
    element.style.background = `linear-gradient(120deg, ${theme.heroStart} 0%, ${theme.heroMid} 48%, ${theme.heroEnd} 100%)`;
  });

  document.querySelectorAll(".controls").forEach((element) => {
    element.style.background = theme.panel;
    element.style.borderColor = theme.border;
  });

  document.querySelectorAll(".stat-card").forEach((element) => {
    element.style.background = theme.statCardBg;
  });

  document.querySelectorAll(".song-card").forEach((element) => {
    element.style.background = `linear-gradient(180deg, ${theme.cardStart}, ${theme.cardEnd})`;
    element.style.borderColor = theme.border;
  });

  document.querySelectorAll(".uil-link").forEach((element) => {
    element.style.color = theme.linkColor;
  });

  document.querySelectorAll(".filter-chip.is-active").forEach((element) => {
    element.style.background = theme.activeChipBg;
    element.style.color = theme.activeChipText;
  });

  document.querySelectorAll(".filter-chip:not(.is-active)").forEach((element) => {
    if (element.classList.contains("filter-chip-nmr")) {
      element.style.background = theme.nmrPillBg;
      element.style.color = theme.nmrPillText;
      return;
    }
    element.style.background = theme.accentSoft;
    element.style.color = theme.accentSoftText;
  });

  document.querySelectorAll(".song-composer").forEach((element) => {
    element.style.color = theme.composerAccent;
  });

  document.querySelectorAll(".nmr-badge").forEach((element) => {
    element.style.background = theme.nmrPillBg;
    element.style.color = theme.nmrPillText;
  });

  if (themeSelect) {
    themeSelect.style.background = theme.selectBg;
  }

  if (searchInput) {
    searchInput.style.background = theme.inputBg;
    searchInput.style.color = theme.ink;
    searchInput.style.borderColor = theme.border;
  }

  localStorage.setItem("uil-pml-theme", themeName);
}

window.__uilSetTheme = (themeName) => {
  if (themeSelect) {
    themeSelect.value = themeName;
  }
  setTheme(themeName);
};

async function loadDataset(instrumentSlug) {
  const instrument = instruments[instrumentSlug] || instruments.piano;
  const [statsResponse, songsResponse] = await Promise.all([
    fetch(instrument.statsUrl),
    fetch(instrument.songsUrl),
  ]);
  const [stats, songs] = await Promise.all([
    statsResponse.json(),
    songsResponse.json(),
  ]);
  state.stats = stats;
  state.songs = songs;
}

function getFilteredSongs() {
  return state.songs.filter((song) => {
    const filterMatches =
      state.activeFilter === "all" ||
      (state.activeFilter === "nmr" && song.noMemoryRequired) ||
      String(song.classLevel) === state.activeFilter;

    const query = state.query.toLowerCase();
    const searchMatches =
      !query ||
      song.title.toLowerCase().includes(query) ||
      song.composer.toLowerCase().includes(query) ||
      song.publisherText.toLowerCase().includes(query);

    return filterMatches && searchMatches;
  });
}

function renderSongs(songs) {
  songGrid.innerHTML = "";

  if (!songs.length) {
    songGrid.innerHTML = `
      <article class="song-card">
        <h2 class="song-title">No matches found</h2>
        <p class="song-specification">Try a different class filter or search term.</p>
      </article>
    `;
    return;
  }

  const fragment = document.createDocumentFragment();

  songs.forEach((song) => {
    const card = cardTemplate.content.cloneNode(true);
    card.querySelector(".class-badge").textContent = `Class ${song.classLevel}`;
    card.querySelector(".event-badge").textContent = song.eventName;
    const nmrBadge = card.querySelector(".nmr-badge");
    nmrBadge.hidden = !song.noMemoryRequired;
    card.querySelector(".uil-code").textContent = song.uilCode;
    card.querySelector(".song-title").textContent = song.title;
    card.querySelector(".song-composer").textContent = song.composer;
    card.querySelector(".song-specification").textContent =
      song.specification || "No additional UIL specification listed.";
    const downloadButton = card.querySelector(".download-button");
    if (song.publicDomainPdfUrl) {
      downloadButton.hidden = false;
      downloadButton.href = song.publicDomainPdfUrl;
    }

    const publisherList = card.querySelector(".publisher-list");
    song.publishers.forEach((publisher) => {
      const item = document.createElement("li");
      item.textContent = publisher;
      publisherList.appendChild(item);
    });

    fragment.appendChild(card);
  });

  songGrid.appendChild(fragment);
}

function updateSummary(songs) {
  let filterLabel = "all classes";
  if (state.activeFilter === "nmr") {
    filterLabel = "the No Memory Required category";
  } else if (state.activeFilter !== "all") {
    filterLabel = `Class ${state.activeFilter}`;
  }
  const searchLabel = state.query ? ` matching "${state.query}"` : "";
  const instrument = instruments[state.activeInstrument] || instruments.piano;
  resultSummary.textContent = `Showing ${songs.length} ${instrument.shortLabel} titles for ${filterLabel}${searchLabel}.`;
}

async function refreshSongs() {
  const songs = getFilteredSongs();
  renderSongs(songs);
  updateSummary(songs);
}

function applyActiveFilter(nextFilter) {
  state.activeFilter = nextFilter;
  filterButtons.forEach((button) => {
    button.classList.toggle("is-active", button.dataset.filter === nextFilter);
  });
  refreshSongs();
  setTheme(themeSelect.value);
}

function applyActiveInstrument(nextInstrument) {
  state.activeInstrument = nextInstrument;
  state.activeFilter = "all";
  state.query = "";
  searchInput.value = "";
  instrumentButtons.forEach((button) => {
    button.classList.toggle("is-active", button.dataset.instrument === nextInstrument);
  });
  filterButtons.forEach((button) => {
    button.classList.toggle("is-active", button.dataset.filter === "all");
  });
  localStorage.setItem("uil-pml-instrument", nextInstrument);
}

function updateInstrumentLabels(stats) {
  const instrument = instruments[state.activeInstrument] || instruments.piano;
  document.title = `UIL ${instrument.label} ${stats.schoolYear}`;
  heroTitle.textContent = `${stats.schoolYear} ${instrument.label}`;
  heroCopy.textContent = instrument.heroCopy;
  searchInput.placeholder = instrument.titlePlaceholder;
}

async function init() {
  const savedTheme = localStorage.getItem("uil-pml-theme") || "midnight-lone-star";
  const savedInstrument =
    localStorage.getItem("uil-pml-instrument") || state.activeInstrument;
  applyActiveInstrument(savedInstrument in instruments ? savedInstrument : "piano");
  themeSelect.value = savedTheme;
  setTheme(savedTheme);

  const handleThemeChange = (event) => {
    setTheme(event.target.value);
  };
  themeSelect.addEventListener("change", handleThemeChange);
  themeSelect.addEventListener("input", handleThemeChange);

  instrumentButtons.forEach((button) => {
    button.addEventListener("click", async () => {
      applyActiveInstrument(button.dataset.instrument);
      await loadDataset(state.activeInstrument);
      updateInstrumentLabels(state.stats);
      songCount.textContent = state.stats.songCount;
      databaseRecordCount.textContent = state.stats.databaseRecordCount;
      classBreakdown.textContent = `Class 3: ${state.stats.classBreakdown["3"]} | Class 2: ${state.stats.classBreakdown["2"]} | Class 1: ${state.stats.classBreakdown["1"]}`;
      nmrCount.textContent = state.stats.noMemoryRequiredCount;
      pdfCount.textContent = state.stats.publicDomainPdfCount;
      datasetNote.textContent = state.stats.notes.dataset_audit;
      await refreshSongs();
      setTheme(themeSelect.value);
    });
  });

  await loadDataset(state.activeInstrument);
  const stats = state.stats;
  updateInstrumentLabels(stats);
  songCount.textContent = stats.songCount;
  databaseRecordCount.textContent = stats.databaseRecordCount;
  classBreakdown.textContent = `Class 3: ${stats.classBreakdown["3"]} | Class 2: ${stats.classBreakdown["2"]} | Class 1: ${stats.classBreakdown["1"]}`;
  nmrCount.textContent = stats.noMemoryRequiredCount;
  pdfCount.textContent = stats.publicDomainPdfCount;
  datasetNote.textContent = stats.notes.dataset_audit;

  filterButtons.forEach((button) => {
    button.addEventListener("click", () => applyActiveFilter(button.dataset.filter));
  });

  let searchTimer;
  searchInput.addEventListener("input", (event) => {
    window.clearTimeout(searchTimer);
    searchTimer = window.setTimeout(() => {
      state.query = event.target.value.trim();
      refreshSongs();
    }, 180);
  });

  await refreshSongs();
  setTheme(themeSelect.value);
}

init().catch((error) => {
  resultSummary.textContent = "The UIL solo data could not be loaded.";
  datasetNote.textContent = error.message;
});
