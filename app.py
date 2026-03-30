from flask import Flask, request, jsonify, render_template
import requests

app = Flask(__name__)

API_URL = "https://api-inference.huggingface.co/models/google/flan-t5-base"

def query(payload):
    response = requests.post(API_URL, json=payload)
    return response.json()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_msg = request.json.get("message")

    output = query({
        "inputs": f"請用可愛的AI龍蝦語氣回答：{user_msg}"
    })

    try:
        reply = output[0]["generated_text"]
    except:
        reply = "🦞 龍蝦暫時思考中，請稍後再試..."

    return jsonify({"reply": reply})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
