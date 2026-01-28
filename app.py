from flask import Flask, request, jsonify, send_from_directory
import hashlib
import re

app = Flask(__name__)

# ---------- HELPERS ----------

def stable_percent(text, low, high):
    h = hashlib.sha256(text.encode()).hexdigest()
    return low + (int(h[:6], 16) % (high - low + 1))


def classify(question):
    q = question.lower()

    if any(x in q for x in ["anime", "waifu", "fiction", "magic", "teleport", "superpower"]):
        return "impossible"

    if any(x in q for x in ["die today", "plane crash", "meteor", "lottery"]):
        return "extremely_rare"

    if any(x in q for x in ["marry tomorrow", "become rich overnight"]):
        return "rare"

    if any(x in q for x in ["pass exam", "get job", "relationship", "learn", "improve"]):
        return "common"

    return "uncertain"


def calculate_probability(question, category):
    if category == "impossible":
        return stable_percent(question, 0, 2)

    if category == "extremely_rare":
        return stable_percent(question, 1, 5)

    if category == "rare":
        return stable_percent(question, 5, 20)

    if category == "common":
        return stable_percent(question, 40, 75)

    return stable_percent(question, 20, 50)


def explain(question, category, percent):
    if category == "impossible":
        return (
            f"This scenario involves fictional or physically impossible elements. "
            f"In real-world conditions, such events cannot occur, which is why the probability is around {percent}%."
        )

    if category == "extremely_rare":
        return (
            f"Events like this are statistically possible but extremely uncommon. "
            f"They depend on rare circumstances aligning, which keeps the odds low at about {percent}%."
        )

    if category == "rare":
        return (
            f"This could technically happen, but only under very specific conditions and timing. "
            f"Because those factors are unlikely to align quickly, the chance is estimated at {percent}%."
        )

    if category == "common":
        return (
            f"This outcome depends on personal actions, environment, and opportunity. "
            f"Since it is influenced by controllable factors, the probability is relatively higher at {percent}%."
        )

    return (
        f"There isn’t enough concrete information to be certain. "
        f"Based on general uncertainty, the probability is estimated at {percent}%."
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
            "explanation": "Ask a question to calculate realistic odds."
        })

    category = classify(question)
    percent = calculate_probability(question, category)
    explanation = explain(question, category, percent)

    return jsonify({
        "percentage": f"{percent}%",
        "explanation": explanation
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
