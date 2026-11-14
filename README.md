# Emotion Prediction Web App 🎭

A lightweight Flask-based web application that uses a lexicon-based rule engine to analyze and detect emotions from text (such as Joy, Sadness, Anger, Fear, Surprise, and Love), complete with negation handling, intensifier weights, and confidence scoring.

## Features ✨
- **Emotion Detection:** Analyzes input sentences and identifies core emotions.
- **Context-Aware Rules:** Handles token negations (e.g., "not happy") and intensifiers (e.g., "very excited").
- **REST API Endpoint:** `/api/predict` handles JSON requests with validation and character limits.
- **Unit Tested:** Built-in test suite using Python's `unittest`.
.
  
