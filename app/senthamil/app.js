const questionInput = document.getElementById("question");
const messages = document.getElementById("messages");
const stopWords = new Set([
  "அது", "அதில்", "அந்த", "என்ன", "என்னும்", "எது", "எதை", "எவை", "எங்கே",
  "எங்கு", "எப்போது", "ஏன்", "எப்படி", "எவ்வாறு", "எதனால்", "எதற்கு", "யார்",
  "யாது", "பற்றி", "குறித்து", "சொல்", "சொல்லுங்கள்", "சொல்கிறது", "கூறு",
  "கூறுங்கள்", "கூறுகிறது", "விளக்கு", "விளக்குங்கள்", "விளக்குகிறது", "குறிக்கிறது",
  "என்பது", "என்று", "என", "ஆகிய", "மற்றும்", "ஒரு", "நூல்", "நூலில்",
  "தொல்காப்பியம்", "தொல்காப்பியத்தில்", "the", "what", "which", "who", "where",
  "when", "why", "how", "does", "do", "is", "are", "about", "tell", "explain"
]);
const suffixes = ["களுக்கு","களினால்","களிலிருந்து","களுக்குள்","களிடம்","களோடு","களில்","களால்","களின்","களை","த்திற்கு","த்திலிருந்து","த்தினால்","த்தில்","த்தால்","த்துக்கு","உடைய","இருந்து","உடன்","ஆனது","ஆகிய","ஆல்","இல்","இன்","க்கு","ஐ","ஓடு","ஆக","கள்","உம்","ப்"];

function addMessage(name, text) {
  const p = document.createElement("p");
  p.className = "message";
  const title = document.createElement("strong");
  title.textContent = name;
  p.append(title, document.createTextNode(text));
  messages.append(p);
  messages.scrollTop = messages.scrollHeight;
}

function addEvidence(record, matchedTerms) {
  const data = SenthamilApp.renderRecord(record.id);
  const card = document.createElement("article");
  card.className = "result";
  const heading = document.createElement("h2");
  heading.textContent = data.header;
  card.append(heading);
  for (const layer of data.layers) {
    if (!layer.body || !["நூற்பா", "காண்டிகை", "உரை (649)", "துணிவு (650)"].includes(layer.name)) continue;
    const p = document.createElement("p");
    const label = document.createElement("b");
    label.textContent = layer.name + ": ";
    p.append(label, document.createTextNode(layer.body));
    card.append(p);
  }
  const source = document.createElement("p");
  source.className = "source";
  source.textContent = "பொருந்திய சொற்கள்: " + matchedTerms.join(", ");
  card.append(source);
  messages.append(card);
}

function queryGroups(text) {
  const raw = text.toLowerCase().match(/[a-z]+|[\u0b80-\u0bff]+/g) || [];
  const groups = [];
  for (const original of raw) {
    if (stopWords.has(original) || original.length < 2) continue;
    const forms = [original];
    let stem = original;
    for (let i = 0; i < 2; i++) {
      const suffix = suffixes.find(s => stem.endsWith(s) && stem.length - s.length >= 3);
      if (!suffix) break;
      stem = stem.slice(0, -suffix.length);
      if (!stopWords.has(stem) && !forms.includes(stem)) forms.push(stem);
    }
    groups.push(forms);
  }
  return groups;
}

function showRecord(record) {
  addMessage("செந்தமிழ் AI", "நூலில் உள்ள நூற்பா:");
  addEvidence(record, [record.id]);
}

function answerFromBook(query) {
  const id = query.replace(/\s+/g, "").toLowerCase();
  const idMatch = id.match(/^(ezhu|ezhuthu|sol|porul)\.?(\d+)$/);
  if (idMatch) {
    const prefix = idMatch[1] === "ezhuthu" ? "ezhu" : idMatch[1];
    const record = SenthamilApp.get(prefix + "." + Number(idMatch[2]));
    if (record) { showRecord(record); return; }
    addMessage("செந்தமிழ் AI", "அந்த நூற்பா எண் இந்த நூலில் இல்லை.");
    return;
  }

  let searchText = query.trim();
  if (searchText.startsWith("தேடு:")) searchText = searchText.slice(4).trim();
  const groups = queryGroups(searchText);
  const results = new Map();
  for (const forms of groups) {
    const found = new Map();
    for (const form of forms) {
      for (const record of SenthamilApp.search(form)) {
        if (!found.has(record.id)) found.set(record.id, form);
      }
    }
    for (const [recordId, matchedForm] of found) {
      if (!results.has(recordId)) results.set(recordId, { record: SenthamilApp.get(recordId), terms: [] });
      results.get(recordId).terms.push(matchedForm);
    }
  }
  const ranked = [...results.values()]
    .filter(item => item.terms.length >= Math.min(2, groups.length))
    .sort((a, b) => b.terms.length - a.terms.length)
    .slice(0, 5);
  if (!ranked.length) {
    addMessage("செந்தமிழ் AI", "இந்த வினாவுக்கு நூலில் பொருந்தும் பகுதியைக் கண்டுபிடிக்க முடியவில்லை. இது நூலில் இல்லை என்று உறுதி செய்யாது; வேறு முக்கியச் சொல்லால் மீண்டும் கேளுங்கள்.");
    return;
  }
  addMessage("செந்தமிழ் AI", "நூலில் தொடர்புடைய பகுதிகள் (சொல் பொருத்தம்):");
  ranked.forEach(item => addEvidence(item.record, [...new Set(item.terms)]));
  addMessage("குறிப்பு", "இவை நூலில் உள்ள நேரடிப் பகுதிகள்; முழுச் சூழலைப் படித்து பொருளை உறுதிப்படுத்துங்கள்.");
}

async function ask(text) {
  const value = (text || questionInput.value).trim();
  if (!value) { questionInput.focus(); return; }
  questionInput.value = "";
  addMessage("நீங்கள்", value);
  try {
    const loading = document.createElement("p");
    loading.className = "message";
    loading.textContent = "நூலில் தேடுகிறது…";
    messages.append(loading);
    if (!SenthamilApp.bundle) await SenthamilApp.init("./bundle_v2.json");
    loading.remove();
    answerFromBook(value);
  } catch (error) {
    addMessage("சிக்கல்", "நூல் தரவை ஏற்ற முடியவில்லை. இணைய இணைப்பைச் சரிபார்த்து மீண்டும் முயலுங்கள்.");
    console.error(error);
  }
}

document.getElementById("ask-form").addEventListener("submit", event => {
  event.preventDefault();
  ask();
});
document.querySelectorAll("[data-query]").forEach(button =>
  button.addEventListener("click", () => ask(button.dataset.query))
);
const tabs = [
  [document.getElementById("ai-tab"), document.getElementById("ai")],
  [document.getElementById("write-tab"), document.getElementById("write")]
];
tabs.forEach(([button, panel]) => button.addEventListener("click", () => {
  tabs.forEach(([otherButton, otherPanel]) => {
    const active = otherButton === button;
    otherButton.setAttribute("aria-selected", String(active));
    otherPanel.hidden = !active;
  });
  if (panel.id === "ai") questionInput.focus();
}));
window.addEventListener("load", () => questionInput.focus());
