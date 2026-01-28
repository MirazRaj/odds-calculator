from flask import Flask, request, jsonify, send_from_directory
import hashlib
import requests
import os

app = Flask(__name__)

HF_API_KEY = os.environ.get("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")
HF_MODEL = "google/flan-t5-small"
HF_URL = f"https://api-inference.huggingface.co/models/{HF_MODEL}"
HF_HEADERS = {"Authorization": f"Bearer {HF_API_KEY}"}


# ---------- LOGIC ----------

def stable_percent(text, low, high):
    h = hashlib.sha256(text.encode()).hexdigest()
    return low + (int(h[:8], 16) % (high - low + 1))


def classify(question):
    q = question.lower()

    if any(x in q for x in ["anime", "waifu", "fiction", "magic", "superpower", "reincarnated", "flying", "raining money", "toji", "anime character", "anime power", "super hero", "super physics", "time travel"]):
        return "impossible"

    if any(x in q for x in ["die today", "plane crash", "meteor", "car crash", "billionear", "money", "millionear", "cash", "femboy", "free money", "famous", "killing", "dying", "crime", "buying"]):
        return "extremely_rare"

    if any(x in q for x in ["tomorrow", "overnight", "yesterday", "right now", "gym", "body", "girlfriend", "gf", "movie", "coffee", "bonk", "bonked", "filian", "kanna", "kazeki", "shil", "youtuber", "viral", "money", "cash", "playing", "games"]):
        return "rare"

    if any(x in q for x in ["job", "exam", "relationship", "learn", "improve", "eating", "food", "walking", "sleeping", "having", "family", "getting", "passing", "having", "eeping", "roblox", "sitting"]):
        return "common"

    return "uncertain"


def probability(question, category):
    if category == "impossible":
        return stable_percent(question, 0, 2)
    if category == "extremely_rare":
        return stable_percent(question, 1, 5)
    if category == "rare":
        return stable_percent(question, 5, 25)
    if category == "common":
        return stable_percent(question, 40, 75)
    return stable_percent(question, 20, 50)


# ---------- AI EXPLANATION ----------

def ai_explanation(question, percent):
    prompt = (
        f"Question: {question}\n"
        f"Estimated probability: {percent}%.\n\n"
        "Explain logically why this probability makes sense, "
        "based on real-world constraints, likelihood, and common sense. "
        "Do not mention AI or probability models."
    )

    payload = {
        "inputs": prompt,
        "parameters": {"max_new_tokens": 80}
    }

    try:
        res = requests.post(HF_URL, headers=HF_HEADERS, json=payload, timeout=10)
        data = res.json()

        if isinstance(data, list) and "generated_text" in data[0]:
            return data[0]["generated_text"].strip()

    except:
        pass

    # Fallback (only if AI fails)
    return (
        f"This estimate considers real-world limitations, timing, and likelihood. "
        f"Based on common circumstances, a probability of {percent}% is reasonable."
    )


# ---------- ROUTES ----------

@app.route("/")
def home():
    return send_from_directory(".", "index.html")


@app.route("/ask", methods=["POST"])
def ask():
    data = request.json or {}
    question = data.get("question", "").strip()

    if not question:
        return jsonify({
            "percentage": "--",
            "explanation": "Ask a question to calculate the odds."
        })

    category = classify(question)
    percent = probability(question, category)
    explanation = ai_explanation(question, percent)

    return jsonify({
        "percentage": f"{percent}%",
        "explanation": explanation
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
