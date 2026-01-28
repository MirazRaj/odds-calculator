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

# ---------- UTILITIES ----------

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
        return r.json()[0]["generated_text"].strip()
    except:
        return ""


# ---------- CORE LOGIC ----------

def analyze_question(question):
    prompt = f"""
Analyze this question realistically:

"{question}"

Answer in ONE sentence:
- Is this event common, rare, extremely rare, or impossible?
- Mention real-world constraints if any.
"""
    analysis = ask_ai(prompt)

    if not analysis:
        analysis = "This event depends on real-world conditions and limitations."

    return analysis


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
Probability: {percentage}%

Analysis:
{analysis}

Explain clearly and logically why the probability is around this value.
Keep it grounded in reality.
"""
    explanation = ask_ai(prompt)

    if not explanation:
        explanation = analysis

    return explanation


# ---------- ROUTES ----------

@app.route("/")
def index():
    return send_from_directory(".", "index.html")


@app.route("/calculate", methods=["POST"])
def calculate():
    data = request.json
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

