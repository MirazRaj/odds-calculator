from flask import Flask, request, jsonify, send_from_directory
import requests, os, hashlib

app = Flask(__name__)

HF_API_KEY = os.environ.get("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")
MODEL_URL = "https://api-inference.huggingface.co/models/google/flan-t5-large"

headers = {
    "Authorization": f"Bearer {HF_API_KEY}"
}

def stable_percentage(question):
    q = question.lower()

    if any(word in q for word in ["tomorrow", "today", "next day"]):
        min_p, max_p = 5, 30
    elif any(word in q for word in ["impossible", "time travel", "dead"]):
        min_p, max_p = 1, 10
    elif any(word in q for word in ["marry", "rich", "successful"]):
        min_p, max_p = 20, 70
    else:
        min_p, max_p = 25, 75

    h = int(hashlib.sha256(question.encode()).hexdigest(), 16)
    return min_p + (h % (max_p - min_p))

def explain_with_ai(question, percentage):
    prompt = f"""
Question: {question}
Calculated probability: {percentage}%

Explain logically and realistically why the probability is around this value.
Keep it short and grounded in real life.
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
        return "The probability is based on time constraints, real-world limitations, and typical outcomes."

@app.route("/")
def home():
    return send_from_directory(".", "index.html")

@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    question = data.get("question", "").strip()

    if not question:
        return jsonify({
            "error": "Please ask a question first."
        }), 400

    percent = stable_percentage(question)
    explanation = explain_with_ai(question, percent)

    return jsonify({
        "percentage": f"{percent}%",
        "explanation": explanation
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
