const DATA_URL = "data/characters.json";

document.addEventListener("DOMContentLoaded", async () => {
  try {
    const response = await fetch(DATA_URL, { cache: "no-store" });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);

    const characters = await response.json();
    if (!Array.isArray(characters)) throw new Error("Character data must be an array");

    if (document.body.dataset.page === "home") renderCharacterList(characters);
    if (document.body.dataset.page === "detail") renderCharacterDetail(characters);
  } catch (error) {
    console.error("Failed to load character data:", error);
    showLoadError();
  }
});

function renderCharacterList(characters) {
  const grid = document.querySelector("#character-grid");
  const count = document.querySelector("#character-count");
  count.textContent = `${characters.length}名を掲載中。`;

  const gradeFilter = document.querySelector("#grade-filter");
  const clubFilter = document.querySelector("#club-filter");
  const factionFilter = document.querySelector("#faction-filter");
  const resetButton = document.querySelector("#reset-filters");
  const result = document.querySelector("#filter-result");

  const grades = uniqueFactValues(characters, "Grade").sort(compareGrades);
  const clubs = [...new Set(characters.map(clubValue).filter(Boolean))].sort((a, b) =>
    a.localeCompare(b, "ja")
  );
  addOptions(gradeFilter, grades, (grade) => `Grade ${grade}`);
  addOptions(clubFilter, clubs);

  const applyFilters = () => {
    const selectedGrade = gradeFilter.value;
    const selectedClub = clubFilter.value;
    const selectedFaction = factionFilter.value;
    const filtered = characters.filter((character) => {
      return (
        (!selectedGrade || factValue(character, "Grade") === selectedGrade) &&
        (!selectedClub || clubValue(character) === selectedClub) &&
        (!selectedFaction || characterFactions(character).includes(selectedFaction))
      );
    });

    renderCharacterCards(grid, filtered);
    const hasFilters = Boolean(selectedGrade || selectedClub || selectedFaction);
    result.textContent = hasFilters
      ? `${characters.length}名中 ${filtered.length}名を表示しています。`
      : `全${characters.length}名を表示しています。`;
    resetButton.disabled = !hasFilters;
  };

  [gradeFilter, clubFilter, factionFilter].forEach((filter) => {
    filter.addEventListener("change", applyFilters);
  });
  resetButton.addEventListener("click", () => {
    gradeFilter.value = "";
    clubFilter.value = "";
    factionFilter.value = "";
    applyFilters();
    gradeFilter.focus();
  });

  setupBackToTop();
  applyFilters();
}

function renderCharacterCards(grid, characters) {
  grid.replaceChildren();

  if (!characters.length) {
    grid.append(
      element("p", "no-results", "条件に一致するキャラクターはいません。")
    );
    return;
  }

  characters.forEach((character) => {
    const card = element("a", "character-card");
    card.href = `character.html?id=${encodeURIComponent(character.id)}`;

    const image = element("img");
    image.src = character.images.portrait;
    image.alt = `${character.name}の立ち絵`;
    image.loading = "lazy";
    image.decoding = "async";

    card.append(
      element("span", "card-kicker", character.kicker),
      image,
      element("strong", "", character.name),
      element("span", "", `本名：${character.realName}`),
      element("p", "", character.summary)
    );
    grid.append(card);
  });
}

function factValue(character, label) {
  return character.facts.find((fact) => fact.label === label)?.value ?? "";
}

function uniqueFactValues(characters, label) {
  return [...new Set(characters.map((character) => factValue(character, label)).filter(Boolean))];
}

function clubValue(character) {
  const club = factValue(character, "所属");
  return club === "未所属" ? "無所属" : club;
}

function compareGrades(a, b) {
  const aNumber = Number(a);
  const bNumber = Number(b);
  if (Number.isFinite(aNumber) && Number.isFinite(bNumber)) return aNumber - bNumber;
  if (Number.isFinite(aNumber)) return -1;
  if (Number.isFinite(bNumber)) return 1;
  return a.localeCompare(b, "ja");
}

function addOptions(select, values, labelFor = (value) => value) {
  values.forEach((value) => {
    const option = document.createElement("option");
    option.value = value;
    option.textContent = labelFor(value);
    select.append(option);
  });
}

function characterFactions(character) {
  if (Array.isArray(character.factions)) {
    return character.factions.filter((faction) =>
      ["student-council", "anti-council", "pacifist"].includes(faction)
    );
  }

  const role = [factValue(character, "立場"), factValue(character, "役職")].join("／");
  const roleTitles = role
    .split(/[／・]/)
    .map((title) => title.trim())
    .filter(Boolean);
  const factions = [];

  if (role.includes("反生徒会")) factions.push("anti-council");
  else if (
    roleTitles.some((title) => /^生徒会(?:役員|長代理|長|副会長)?$/.test(title))
  ) {
    factions.push("student-council");
  }

  if (role.includes("パシフィスタ") || role.includes("平和主義者")) {
    factions.push("pacifist");
  }
  return factions;
}

function setupBackToTop() {
  const button = document.querySelector("#back-to-top");
  if (!button) return;

  const updateVisibility = () => {
    button.classList.toggle("is-visible", window.scrollY > 480);
  };
  button.addEventListener("click", () => {
    window.scrollTo({
      top: 0,
      behavior: window.matchMedia("(prefers-reduced-motion: reduce)").matches
        ? "auto"
        : "smooth",
    });
  });
  window.addEventListener("scroll", updateVisibility, { passive: true });
  updateVisibility();
}

function renderCharacterDetail(characters) {
  const id = new URLSearchParams(location.search).get("id");
  const character = characters.find((item) => item.id === id);
  const container = document.querySelector("#character-detail");

  if (!character) {
    document.title = "キャラクターが見つかりません | カス高 キャラクター名鑑";
    container.replaceChildren(
      element("section", "not-found", "指定されたキャラクターは見つかりませんでした。")
    );
    return;
  }

  document.title = `${character.name} | カス高 キャラクター名鑑`;
  document.querySelector('meta[name="description"]').content = character.summary;

  const head = element("section", "character-head");
  const introduction = element("div");
  introduction.append(
    element("p", "eyebrow", character.kicker),
    element("h1", "", character.name),
    element("p", "realname", `本名：${character.realName}`)
  );

  const quote = element("p", "quote");
  character.quotes.forEach((line, index) => {
    if (index) quote.append(document.createElement("br"));
    quote.append(document.createTextNode(line));
  });
  introduction.append(quote);

  const facts = element("div", "facts");
  character.facts.forEach(({ label, value }) => {
    const fact = element("div", "fact");
    fact.append(element("b", "", label), document.createTextNode(value));
    facts.append(fact);
  });
  head.append(introduction, facts);

  const bio = element("section", "bio");
  character.bio.forEach((paragraph) => bio.append(element("p", "", paragraph)));

  const gallery = element("section", "gallery");
  gallery.append(element("h2", "", "Character Art"));
  const imageGrid = element("div", "image-grid");
  imageGrid.append(
    artCard(character.images.portrait, `${character.name}のAI立ち絵`, "AI standing illustration", "art-card--portrait"),
    artCard(character.images.original, `${character.name}の元手書き資料`, "Original sketch", "art-card--sketch")
  );
  gallery.append(imageGrid);

  container.replaceChildren(head, bio, gallery);
}

function artCard(src, alt, caption, modifier) {
  const figure = element("figure", `art-card ${modifier}`);
  const image = element("img");
  image.src = src;
  image.alt = alt;
  image.loading = "lazy";
  image.decoding = "async";
  figure.append(image, element("figcaption", "", caption));
  return figure;
}

function element(tag, className = "", text = "") {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text) node.textContent = text;
  return node;
}

function showLoadError() {
  const target = document.querySelector("#character-grid, #character-detail");
  if (target) {
    target.replaceChildren(
      element("p", "error-message", "キャラクター情報を読み込めませんでした。時間をおいて再読み込みしてください。")
    );
  }
  const count = document.querySelector("#character-count");
  if (count) count.textContent = "";
}
