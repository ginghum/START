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
  grid.replaceChildren();
  count.textContent = `${characters.length}名を掲載中。`;

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
