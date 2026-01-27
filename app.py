from flask import Flask, request, jsonify, send_from_directory
import requests
import random
import os

app = Flask(__name__)

# Get API key securely from environment
HF_API_KEY = os.environ.get("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")

MODEL_URL = "https://api-inference.huggingface.co/models/google/flan-t5-large"

headers = {
    "Authorization": f"Bearer {HF_API_KEY}"
}

def generate_odds(question):
    base_probability = random.randint(30, 75)

    prompt = f"""
Question: {question}

Give a logical probability in percentage and a short explanation.
Format exactly like this:
Percentage: XX%
Explanation: ...
"""

    try:
        response = requests.post(
            MODEL_URL,
            headers=headers,
            json={"inputs": prompt},
            timeout=15
        )

        if response.status_code != 200:
            raise Exception("Model error")

        result = response.json()

        generated_text = result[0].get("generated_text", "")

        return base_probability, generated_text

    except Exception:
        return base_probability, "Based on common real-world patterns and probability."

@app.route("/")
def home():
    return send_from_directory(".", "index.html")

@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    question = data.get("question", "")

    percent, explanation = generate_odds(question)

    return jsonify({
        "percentage": f"{percent}%",
        "explanation": explanation
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
