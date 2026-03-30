import os
import requests
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# 從環境變數讀 OpenRouter API Key
API_KEY = os.getenv("OPENROUTER_API_KEY")
API_URL = "https://openrouter.ai/api/v1/chat/completions"

# 簡單前端 HTML
HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>🦞 AI 龍蝦 Agent</title>
</head>
<body>
<h1>🦞 AI 龍蝦 Agent</h1>
<input id="msg" placeholder="問龍蝦任何問題..." />
<button onclick="send()">送出</button>
<div id="chat"></div>

<script>
async function send() {
    let input = document.getElementById("msg");
    let chat = document.getElementById("chat");
    let userText = input.value;
    if(!userText) return;
    chat.innerHTML += `<div>👤 ${userText}</div>`;
    input.value = "";

    let res = await fetch("/chat", {
        method:"POST",
        headers: {"Content-Type":"application/json"},
        body: JSON.stringify({message: userText})
    });
    let data = await res.json();
    chat.innerHTML += `<div>🦞 ${data.reply}</div>`;
}
</script>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML_PAGE)

@app.route("/chat", methods=["POST"])
def chat():
    user_msg = request.json.get("message", "")
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": user_msg}]
    }
    try:
        resp = requests.post(API_URL, headers=headers, json=payload, timeout=10)
        resp.raise_for_status()
        reply = resp.json()["choices"][0]["message"]["content"]
    except Exception as e:
        reply = "🦞 龍蝦暫時思考中，請稍後再試..."
    return jsonify({"reply": reply})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
