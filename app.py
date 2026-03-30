from flask import Flask, request, jsonify, render_template
from transformers import pipeline

app = Flask(__name__)

# 免費模型（DistilGPT2）
chatbot = pipeline("text-generation", model="distilgpt2")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_msg = request.json.get("message")
    result = chatbot(user_msg, max_length=100, do_sample=True)[0]['generated_text']
    return jsonify({"reply": result})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
