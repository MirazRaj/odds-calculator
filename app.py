import os
import hashlib
import requests
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__)

HF_API_KEY = os.environ.get("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")
MODEL_URL = "https://api-inference.huggingface.co/models/google/flan-t5-base"

headers = {
    "Authorization": f"Bearer {HF_API_KEY}"
}

# ---------------- UTILITIES ----------------

def stable_hash_percentage(text, low, high):
    h = hashlib.sha256(text.encode()).hexdigest()
    num = int(h[:8], 16)
    return low + (num % (high - low + 1))


def ask_ai(prompt):
    try:
        r = requests.post(
            MODEL_URL,
            headers=headers,
            json={"inputs": prompt},
            timeout=20
        )
        data = r.json()
        if isinstance(data, list) and "generated_text" in data[0]:
            return data[0]["generated_text"].strip()
    except:
        pass
    return ""


# ---------------- CORE LOGIC ----------------

def analyze_question(question):
    prompt = f"""
Analyze this question realistically:

"{question}"

Classify it as common, rare, extremely rare, or impossible.
Mention real-world constraints briefly.
"""
    analysis = ask_ai(prompt)
    return analysis or "This event is constrained by real-world limitations."


def decide_probability(question, analysis):
    a = analysis.lower()

    if "impossible" in a:
        return 0
    if "extremely rare" in a:
        return stable_hash_percentage(question, 1, 5)
    if "rare" in a:
        return stable_hash_percentage(question, 5, 20)
    if "common" in a:
        return stable_hash_percentage(question, 40, 70)

    return stable_hash_percentage(question, 20, 50)


def explain_probability(question, percentage, analysis):
    prompt = f"""
Question: {question}
Estimated Probability: {percentage}%

Explain logically WHY the probability is around this value.
Base it on reality, constraints, and likelihood.
"""
    explanation = ask_ai(prompt)
    return explanation or analysis


# ---------------- ROUTES ----------------

@app.route("/")
def index():
    return send_from_directory(".", "index.html")


# 🔥 THIS MATCHES YOUR FRONTEND
@app.route("/ask", methods=["POST"])
def ask():
    data = request.json or {}
    question = data.get("question", "").strip()

    if not question:
        return jsonify({
            "percentage": "--",
            "explanation": "Ask a question to calculate realistic odds."
        })

    analysis = analyze_question(question)
    percentage = decide_probability(question, analysis)
    explanation = explain_probability(question, percentage, analysis)

    return jsonify({
        "percentage": f"{percentage}%",
        "explanation": explanation
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
