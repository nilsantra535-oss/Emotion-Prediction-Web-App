import re
from typing import Dict, List

from flask import Flask, jsonify, render_template, request

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024

MAX_TEXT_LENGTH = 500
EMOTION_WORDS = {
    "Joy": {
        "happy", "joyful", "delighted", "excited", "amazing", "wonderful",
        "great", "good", "glad", "smile", "laugh", "proud", "awesome",
        "fantastic", "fun", "enjoy", "celebrate", "success", "cheerful",
        "thrilled", "hopeful", "pleased",
    },
    "Sadness": {
        "sad", "unhappy", "lonely", "depressed", "down", "heartbroken",
        "miserable", "grief", "crying", "miss", "disappointed", "hopeless",
        "hurt", "upset", "gloomy", "empty", "devastated", "loss",
    },
    "Anger": {
        "angry", "mad", "furious", "annoyed", "frustrated", "hate", "rage",
        "irritated", "outraged", "resentful", "infuriated", "bitter",
    },
    "Fear": {
        "afraid", "scared", "fearful", "worried", "anxious", "nervous",
        "panic", "terrified", "dread", "unsafe", "frightened", "alarmed",
        "uneasy", "uncertain",
    },
    "Surprise": {
        "surprised", "astonished", "shocked", "unbelievable", "wow",
        "unexpected", "suddenly", "incredible", "startled", "speechless",
        "amazed",
    },
    "Love": {
        "love", "adore", "cherish", "affection", "caring", "sweetheart",
        "beloved", "appreciate", "devoted", "tender", "romantic",
    },
}
NEGATIONS = {"no", "not", "never", "neither", "nor", "without", "hardly"}
INTENSIFIERS = {"very", "really", "so", "extremely", "incredibly", "too"}
TOKEN_PATTERN = re.compile(r"\b[\w']+\b", re.UNICODE)


def predict_emotion(text: str) -> Dict[str, object]:
    """Return a lexicon-based emotion and an evidence-based heuristic score."""
    tokens = TOKEN_PATTERN.findall(text.lower())
    scores = {emotion: 0.0 for emotion in EMOTION_WORDS}
    matched_words: List[str] = []

    for index, token in enumerate(tokens):
        matching_emotions = [
            emotion for emotion, words in EMOTION_WORDS.items() if token in words
        ]
        if not matching_emotions:
            continue

        context = tokens[max(0, index - 3):index]
        if any(word in NEGATIONS for word in context):
            continue

        weight = 1.0
        if any(word in INTENSIFIERS for word in context):
            weight *= 1.35

        matched_words.append(token)
        for emotion in matching_emotions:
            scores[emotion] += weight

    ranked_emotions = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    emotion, top_score = ranked_emotions[0]
    second_score = ranked_emotions[1][1]

    if top_score == 0:
        emotion = "Neutral"
        confidence = 62
    else:
        evidence = min(top_score, 3.0)
        margin = (top_score - second_score) / top_score
        confidence = round(min(96, 58 + 9 * evidence + 12 * margin))

    return {
        "emotion": emotion,
        "confidence": confidence,
        "matched_words": list(dict.fromkeys(matched_words)),
    }


@app.get("/")
def home():
    return render_template("index.html")


@app.post("/api/predict")
def predict():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"error": "Send your text as JSON."}), 400

    text = payload.get("text")
    if not isinstance(text, str) or not text.strip():
        return jsonify({"error": "Enter a sentence before predicting."}), 400
    if len(text) > MAX_TEXT_LENGTH:
        return jsonify({"error": f"Keep your text under {MAX_TEXT_LENGTH} characters."}), 400

    return jsonify(predict_emotion(text.strip()))


if __name__ == "__main__":
    app.run(debug=True)
