import os
import requests
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# 1. 環境變數
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY")
RESEND_API_KEY = os.getenv("RESEND_API_KEY")

# 2. 龍蝦 API 寄信功能 (這條路絕對通！)
def send_lobster_email(to_email, subject, content):
    try:
        print(f"🚀 [API 模式] 正在透過 Resend 隧道寄信...")
        response = requests.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {RESEND_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "from": "LobsterBot <onboarding@resend.dev>",
                "to": [to_email],
                "subject": subject,
                "html": f"<p>{content}</p>",
            }
        )
        if response.status_code in [200, 201, 202]:
            print(f"✅ 成功！信件已透過 API 送出。")
            return True
        else:
            print(f"❌ API 報錯：{response.text}")
            return False
    except Exception as e:
        print(f"💥 意外錯誤：{e}")
        return False

# 3. 前端網頁介面 (簡約穩定版)
HTML_PAGE = """
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>🦞 龍蝦助理</title></head>
<body style="text-align:center; padding:50px; background:#0f172a; color:white; font-family:sans-serif;">
    <h1>🦞 萬能龍蝦 Agent - API 版</h1>
    <div id="chat-box" style="background:#1e293b; height:300px; overflow-y:auto; padding:20px; border-radius:10px; margin-bottom:20px; text-align:left;"></div>
    <input id="msg" style="width:70%; padding:15px; border-radius:5px;" placeholder="例如：寄信給 xxx@mail.hwu.edu.tw，主旨是你好，內容是龍蝦進化了。" onkeypress="if(event.keyCode==13) send()"/>
    <button onclick="send()" style="padding:15px; background:#38bdf8; border:none; cursor:pointer; font-weight:bold;">執行任務</button>
    <script>
    async function send() {
        let input = document.getElementById("msg");
        let box = document.getElementById("chat-box");
        let text = input.value;
        if(!text) return;
        box.innerHTML += `<div>👤 你：${text}</div>`;
        box.innerHTML += `<div id='loading'>🦞 龍蝦正在揮動鉗子...</div>`;
        input.value = "";
        box.scrollTop = box.scrollHeight;
        try {
            let res = await fetch("/task", {
                method:"POST",
                headers: {"Content-Type":"application/json"},
                body: JSON.stringify({message: text})
            });
            let data = await res.json();
            document.getElementById('loading').remove();
            box.innerHTML += `<div style="color:#38bdf8;">🦞 龍蝦：${data.reply}</div>`;
        } catch (e) {
            document.getElementById('loading').innerText = "❌ 連線失敗，請查看 Render Logs。";
        }
        box.scrollTop = box.scrollHeight;
    }
    </script>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML_PAGE)

@app.route("/task", methods=["POST"])
def task():
    user_msg = request.json.get("message", "")
    print(f"📬 指令：{user_msg}")
    
    system_prompt = "你是龍蝦助理。若要寄信，格式：SEND_EMAIL|信箱|主旨|內容。否則正常聊天。"
    headers = {"Authorization": f"Bearer {OPENROUTER_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": "google/gemini-2.0-flash-001",
        "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_msg}]
    }
    
    try:
        resp = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload, timeout=25)
        data = resp.json()
        ai_reply = data["choices"][0]["message"]["content"]
        
        if "SEND_EMAIL|" in ai_reply:
            parts = ai_reply.split("|")
            if len(parts) >= 4:
                mail_to, mail_sub, mail_con = parts[1].strip(), parts[2].strip(), parts[3].strip()
                if send_lobster_email(mail_to, mail_sub, mail_con):
                    return jsonify({"reply": f"✅ 龍蝦成功把信送出去了！收件人：{mail_to}"})
                else:
                    return jsonify({"reply": "❌ 龍蝦遇到封鎖，請檢查 Resend API Key 設定。"})
        
        return jsonify({"reply": ai_reply})
    except Exception as e:
        return jsonify({"reply": f"龍蝦腦袋打結：{str(e)}"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
