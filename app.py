# app.py
import os
import requests
from flask import Flask, request, render_template_string

app = Flask(__name__)

# 從環境變數讀取 OpenRouter API Key 和城市
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY")
CITY = os.getenv("CITY", "Taipei")

# HTML 前端模板
HTML_TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>OpenRouter Chat</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 40px; }
    input, button { font-size: 1rem; padding: 8px; }
    #response { margin-top: 20px; white-space: pre-wrap; }
  </style>
</head>
<body>
  <h1>OpenRouter Chat - {{ city }}</h1>
  <form method="post">
    <input type="text" name="prompt" placeholder="輸入你的問題..." size="50" required>
    <button type="submit">送出</button>
  </form>
  {% if response %}
    <div id="response"><strong>回答：</strong>{{ response }}</div>
  {% endif %}
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    response_text = ""
    if request.method == "POST":
        prompt = request.form.get("prompt", "")
        if prompt:
            response_text = ask_openrouter(prompt)
    return render_template_string(HTML_TEMPLATE, response=response_text, city=CITY)

def ask_openrouter(prompt):
    """
    呼叫 OpenRouter API 取得回答
    """
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }
    try:
        r = requests.post(url, json=data, headers=headers, timeout=15)
        r.raise_for_status()
        result = r.json()
        # 取得 OpenRouter 回答
        return result["choices"][0]["message"]["content"]
    except Exception as e:
        return f"發生錯誤：{e}"

if __name__ == "__main__":
    # Render 會自動提供 PORT
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
