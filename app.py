from flask import Flask, request, jsonify
import requests
import random

app = Flask(__name__)

HF_API_KEY = "PASTE_YOUR_TOKEN_HERE"
MODEL_URL = "https://api-inference.huggingface.co/models/google/flan-t5-large"

headers = {
    "Authorization": f"Bearer {HF_API_KEY}"
}

def generate_odds(question):
    base = random.randint(25, 75)

    prompt = f"""
Question: {question}
Give a logical probability in percentage and explain shortly why.
Format:
Percentage: XX%
Explanation: ...
"""

    response = requests.post(
        MODEL_URL,
        headers=headers,
        json={"inputs": prompt}
    )

    if response.status_code != 200:
        return base, "Logic based on common patterns and probability."

    text = response.json()[0]["generated_text"]

    return base, text

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
    app.run()
