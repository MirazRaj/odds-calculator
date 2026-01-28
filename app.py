from flask import Flask, request, jsonify, send_from_directory
import requests
import os
import hashlib

app = Flask(__name__)

HF_API_KEY = os.environ.get("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")
MODEL_URL = "https://api-inference.huggingface.co/models/google/flan-t5-large"

headers = {
    "Authorization": f"Bearer {HF_API_KEY}"
}

# -----------------------------
# REALITY-BASED PROBABILITY LOGIC
# -----------------------------
def determine_probability(question):
    q = question.lower()

    # HARD IMPOSSIBLE EVENTS
    impossible_keywords = [
        "anime", "waifu", "come out of the screen", "time travel",
        "revive", "dead person", "magic", "teleport", "fictional",
        "superpower", "immortal"
    ]

    if any(word in q for word in impossible_keywords):
        return 0, (
            "This event is physically impossible because it violates known laws "
            "of reality and involves fictional or non-existent phenomena."
        )

    # EXTREMELY SHORT TIME EVENTS
    short_time_keywords = ["tomorrow", "today", "next 24 hours", "3 days"]

    if any(word in q for word in short_time_keywords):
        return 5, (
            "The timeframe is extremely short, making the probability very low "
            "due to practical and social constraints."
        )

    # RELATIONSHIP / LIFE OUTCOMES
    life_keywords = ["girlfriend", "boyfriend", "marriage", "love", "relationship"]

    if any(word in q for word in life_keywords):
        percent = stable_hash_percentage(question, 20, 50)
        return percent, (
            "Human relationships depend on time, interaction, mutual interest, "
            "and circumstances, which makes outcomes uncertain but possible."
        )

    # DEFAULT REALISTIC UNCERTAINTY
    percent = stable_hash_percentage(question, 25, 65)
    return percent, (
        "The outcome depends on multiple real-world factors, effort, chance, "
        "and conditions beyond full control."
    )


def stable_hash_percentage(text, min_p, max_p):
    h = int(hashlib.sha256(text.encode()).hexdigest(), 16)
    return min_p + (h % (max_p - min_p))


# -----------------------------
# AI EXPLANATION (NO BULLSHIT)
# -----------------------------
def explain_with_ai(question, percentage, core_reason):
    prompt = f"""
Question: {question}
Probability: {percentage}%

Core reasoning:
{core_reason}

Explain this clearly and logically in simple human language.
Do NOT invent fantasy or unrealistic logic.
Keep it short.
"""

    try:
        r = requests.post(
            MODEL_URL,
            headers=headers,
            json={"inputs": prompt},
            timeout=20
        )
        return r.json()[0]["generated_text"]
    except:
        return core_reason


# -----------------------------
# ROUTES
# -----------------------------
@app.route("/")
def home():
    return send_from_directory(".", "index.html")


@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    question = data.get("question", "").strip()

    if not question:
        return jsonify({
            "error": "Please enter a question before calculating odds."
        }), 400

    percent, core_reason = determine_probability(question)
    explanation = explain_with_ai(question, percent, core_reason)

    return jsonify({
        "percentage": f"{percent}%",
        "explanation": explanation
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
