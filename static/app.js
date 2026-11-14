const textInput = document.querySelector("#text-input");
const predictButton = document.querySelector("#predict-button");
const charCount = document.querySelector("#char-count");
const errorMessage = document.querySelector("#error-message");
const resultCard = document.querySelector("#result-card");
const historyList = document.querySelector("#history-list");
const clearHistoryButton = document.querySelector("#clear-history");
const HISTORY_KEY = "emote-prediction-history";
const MAX_HISTORY = 5;

const emotionDetails = {
  Joy: { icon: "☀️", description: "There’s a bright, positive energy in these words." },
  Sadness: { icon: "🌧️", description: "These words carry a tender or heavy feeling." },
  Anger: { icon: "🔥", description: "A strong sense of frustration or anger comes through." },
  Fear: { icon: "🌫️", description: "There may be some worry or uncertainty here." },
  Surprise: { icon: "✨", description: "These words suggest something unexpected." },
  Love: { icon: "💜", description: "There’s warmth and affection in these words." },
  Neutral: { icon: "🍃", description: "No strong emotion stood out in the words." },
};

function readHistory() {
  try {
    const saved = JSON.parse(localStorage.getItem(HISTORY_KEY) || "[]");
    return Array.isArray(saved) ? saved.slice(0, MAX_HISTORY) : [];
  } catch {
    return [];
  }
}

function saveHistory(history) {
  try {
    localStorage.setItem(HISTORY_KEY, JSON.stringify(history));
  } catch {
    errorMessage.textContent = "Your browser could not save prediction history.";
    errorMessage.hidden = false;
  }
}

function renderHistory() {
  const history = readHistory();
  historyList.replaceChildren();
  clearHistoryButton.hidden = history.length === 0;

  if (history.length === 0) {
    const empty = document.createElement("p");
    empty.className = "empty-history";
    empty.textContent = "Your recent predictions will show up here.";
    historyList.append(empty);
    return;
  }

  for (const item of history) {
    const row = document.createElement("article");
    row.className = "history-item";
    const icon = document.createElement("span");
    icon.className = "history-icon";
    icon.setAttribute("aria-hidden", "true");
    icon.textContent = emotionDetails[item.emotion]?.icon || emotionDetails.Neutral.icon;

    const copy = document.createElement("div");
    copy.className = "history-copy";
    const emotion = document.createElement("span");
    emotion.className = "history-emotion";
    emotion.textContent = item.emotion;
    const text = document.createElement("div");
    text.className = "history-text";
    text.textContent = item.text;
    copy.append(emotion, text);

    const confidence = document.createElement("span");
    confidence.className = "history-confidence";
    confidence.textContent = `${item.confidence}%`;
    row.append(icon, copy, confidence);
    historyList.append(row);
  }
}

textInput.addEventListener("input", () => {
  charCount.textContent = `${textInput.value.length} / 500`;
});

predictButton.addEventListener("click", async () => {
  errorMessage.hidden = true;
  const text = textInput.value.trim();
  if (!text) {
    errorMessage.textContent = "Write a sentence first, then try again.";
    errorMessage.hidden = false;
    textInput.focus();
    return;
  }

  predictButton.disabled = true;
  predictButton.querySelector("span").textContent = "Reading your words…";

  try {
    const response = await fetch("/api/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text }),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "Something went wrong. Please try again.");

    const details = emotionDetails[data.emotion] || emotionDetails.Neutral;
    document.querySelector("#result-icon").textContent = details.icon;
    document.querySelector("#result-emotion").textContent = data.emotion;
    document.querySelector("#result-description").textContent = details.description;
    document.querySelector("#result-confidence").textContent = `${data.confidence}%`;
    document.querySelector("#confidence-bar").style.width = `${data.confidence}%`;
    resultCard.hidden = false;

    const history = [{ text, emotion: data.emotion, confidence: data.confidence }, ...readHistory()]
      .slice(0, MAX_HISTORY);
    saveHistory(history);
    renderHistory();
  } catch (error) {
    errorMessage.textContent = error.message || "Could not reach the prediction service. Is the app running?";
    errorMessage.hidden = false;
  } finally {
    predictButton.disabled = false;
    predictButton.querySelector("span").textContent = "Find the feeling";
  }
});

clearHistoryButton.addEventListener("click", () => {
  saveHistory([]);
  renderHistory();
});

renderHistory();
