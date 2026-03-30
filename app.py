from flask import Flask, request, jsonify, render_template
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

app = Flask(__name__)

# 使用免費 HuggingFace 模型
MODEL_NAME = "tiiuae/falcon-7b-instruct"  # 或選小一點的免費模型如 "gpt2"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(MODEL_NAME)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_msg = request.json.get("message")

    inputs = tokenizer.encode(user_msg + tokenizer.eos_token, return_tensors="pt")
    outputs = model.generate(inputs, max_length=200, do_sample=True, top_p=0.95, top_k=50)
    reply = tokenizer.decode(outputs[0], skip_special_tokens=True)

    return jsonify({
        "reply": reply
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
