const songGrid = document.getElementById("song-grid");
const resultSummary = document.getElementById("result-summary");
const datasetNote = document.getElementById("dataset-note");
const searchInput = document.getElementById("search-input");
const songCount = document.getElementById("song-count");
const databaseRecordCount = document.getElementById("database-record-count");
const classBreakdown = document.getElementById("class-breakdown");
const nmrCount = document.getElementById("nmr-count");
const themeSelect = document.getElementById("theme-select");
const filterButtons = [...document.querySelectorAll(".filter-chip")];
const cardTemplate = document.getElementById("song-card-template");

const state = {
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

  localStorage.setItem("uil-piano-theme", themeName);
}

window.__uilSetTheme = (themeName) => {
  if (themeSelect) {
    themeSelect.value = themeName;
  }
  setTheme(themeName);
};

async function loadDataset() {
  const [statsResponse, songsResponse] = await Promise.all([
    fetch("./data/stats.json"),
    fetch("./data/piano-solos.json"),
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
    const nmrBadge = card.querySelector(".nmr-badge");
    nmrBadge.hidden = !song.noMemoryRequired;
    card.querySelector(".uil-code").textContent = song.uilCode;
    card.querySelector(".song-title").textContent = song.title;
    card.querySelector(".song-composer").textContent = song.composer;
    card.querySelector(".song-specification").textContent =
      song.specification || "No additional UIL specification listed.";

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
  resultSummary.textContent = `Showing ${songs.length} piano solo titles for ${filterLabel}${searchLabel}.`;
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

async function init() {
  const savedTheme = localStorage.getItem("uil-piano-theme") || "midnight-lone-star";
  themeSelect.value = savedTheme;
  setTheme(savedTheme);

  const handleThemeChange = (event) => {
    setTheme(event.target.value);
  };
  themeSelect.addEventListener("change", handleThemeChange);
  themeSelect.addEventListener("input", handleThemeChange);

  await loadDataset();
  const stats = state.stats;
  songCount.textContent = stats.songCount;
  databaseRecordCount.textContent = stats.databaseRecordCount;
  classBreakdown.textContent = `Class 3: ${stats.classBreakdown["3"]} | Class 2: ${stats.classBreakdown["2"]} | Class 1: ${stats.classBreakdown["1"]}`;
  nmrCount.textContent = stats.noMemoryRequiredCount;
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
  resultSummary.textContent = "The piano solo data could not be loaded.";
  datasetNote.textContent = error.message;
});
