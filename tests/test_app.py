import unittest

from app import app, predict_emotion


class EmotionPredictionTests(unittest.TestCase):
    def test_detects_joy(self):
        self.assertEqual(predict_emotion("I feel happy and excited today!")["emotion"], "Joy")

    def test_detects_sadness(self):
        self.assertEqual(predict_emotion("I feel lonely and heartbroken.")["emotion"], "Sadness")

    def test_negated_emotion_is_not_counted_as_strong_evidence(self):
        result = predict_emotion("I am not happy.")
        self.assertEqual(result["emotion"], "Neutral")

    def test_unmatched_text_is_neutral(self):
        result = predict_emotion("The package arrived on Tuesday.")
        self.assertEqual(result["emotion"], "Neutral")
        self.assertGreater(result["confidence"], 0)

    def test_prediction_endpoint_validates_text(self):
        client = app.test_client()
        response = client.post("/api/predict", json={"text": "I adore this!"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["emotion"], "Love")
        self.assertIn("confidence", response.get_json())

        empty_response = client.post("/api/predict", json={"text": "   "})
        self.assertEqual(empty_response.status_code, 400)

    def test_prediction_endpoint_enforces_character_limit(self):
        client = app.test_client()
        response = client.post("/api/predict", json={"text": "a" * 501})
        self.assertEqual(response.status_code, 400)


if __name__ == "__main__":
    unittest.main()
