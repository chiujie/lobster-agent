import os
import requests
import smtplib
from email.mime.text import MIMEText
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# 1. 環境變數
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY")
SENDER_EMAIL = os.getenv("SENDER_EMAIL")     
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD") 

# 2. 寄信功能
def send_lobster_email(to_email, subject, content):
    try:
        print(f"🦞 [寄信中] 連線至 Gmail...")
        msg = MIMEText(content)
        msg['Subject'] = subject
        msg['From'] = SENDER_EMAIL
        msg['To'] = to_email

        with smtplib.SMTP('smtp.gmail.com', 587, timeout=20) as server:
            server.starttls() 
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, [to_email], msg.as_string())
        print(f"🦞 [成功] 已寄給 {to_email}")
        return True
    except Exception as e:
        print(f"❌ [失敗] {e}")
        return False

# 3. 網頁介面
HTML_PAGE = """
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>🦞 龍蝦助理</title></head>
<body style="text-align:center; padding:50px; background:#0f172a; color:white; font-family:sans-serif;">
    <h1>🦞 萬能龍蝦 Agent</h1>
    <div id="chat-box" style="background:#1e293b; height:300px; overflow-y:auto; padding:20px; border-radius:10px; margin-bottom:20px; text-align:left;"></div>
    <input id="msg" style="width:70%; padding:15px; border-radius:5px;" placeholder="對龍蝦下令... (例如: 幫我寄信給 xxx@gmail.com)" onkeypress="if(event.keyCode==13) send()"/>
    <button onclick="send()" style="padding:15px; background:#38bdf8; border:none; cursor:pointer; font-weight:bold;">執行</button>
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
            document.getElementById('loading').innerText = "❌ 出錯了，請查看 Logs。";
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
    print(f"📬 收到任務：{user_msg}")
    
    system_prompt = "你是一隻萬能龍蝦。若使用者要寄信，請回覆格式：SEND_EMAIL|信箱|主旨|內容。否則正常聊天。"
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
                mail_to = parts[1].strip()
                mail_sub = parts[2].strip()
                mail_con = parts[3].strip()
                if send_lobster_email(mail_to, mail_sub, mail_con):
                    return jsonify({"reply": f"✅ 任務完成！信已寄給 **{mail_to}**。"})
                else:
                    return jsonify({"reply": "❌ 寄信失敗，請檢查密碼。
