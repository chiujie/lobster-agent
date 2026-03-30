from flask import Flask, request, jsonify, render_template
from transformers import pipeline

app = Flask(__name__)

# 使用 HuggingFace 小型模型 (完全免費)
chatbot = pipeline("text-generation", model="distilgpt2")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_msg = request.json.get("message")
    
    # 生成回答，限制字數避免卡
    response = chatbot(user_msg, max_length=50, do_sample=True)[0]["generated_text"]
    
    return jsonify({
        "reply": response
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
