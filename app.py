import os
import requests
import smtplib
import re
from email.mime.text import MIMEText
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# 1. 環境變數
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY")
SENDER_EMAIL = os.getenv("SENDER_EMAIL")     
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD") 

# 2. 通用寄信功能
def send_lobster_email(to_email, subject, content):
    try:
        msg = MIMEText(content)
        msg['Subject'] = subject
        msg['From'] = SENDER_EMAIL
        msg['To'] = to_email
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, [to_email], msg.as_string())
        return True
    except Exception as e:
        print(f"寄信報錯: {e}")
        return False

# 3. 前端網頁 (加入一點點龍蝦動畫感覺)
HTML_PAGE = """
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>🦞 龍蝦自動執行員</title></head>
<body style="text-align:center; padding:50px; background:#0f172a; color:white; font-family:sans-serif;">
    <h1>🦞 萬能龍蝦 Agent</h1>
    <p>範例：寄信給 test@gmail.com，主旨是開會，內容是明天下午三點。</p>
    <div id="chat-box" style="background:#1e293b; height:300px; overflow-y:auto; padding:20px; border-radius:10px; margin-bottom:20px; text-align:left;"></div>
    <input id="msg" style="width:70%; padding:15px; border-radius:5px; border:none;" placeholder="對龍蝦下令..." onkeypress="if(event.keyCode==13) send()"/>
    <button onclick="send()" style="padding:15px 30px; background:#38bdf8; border:none; cursor:pointer; font-weight:bold;">執行</button>

    <script>
    async function send() {
        let input = document.getElementById("msg");
        let box = document.getElementById("chat-box");
        let text = input.value;
        if(!text) return;

        box.innerHTML += `<div>👤 你：${text}</div>`;
        box.innerHTML += `<div id='loading'>🦞 龍蝦正在揮動鉗子...</div>`;
        input.value = "";

        let res = await fetch("/task", {
            method:"POST",
            headers: {"Content-Type":"application/json"},
            body: JSON.stringify({message: text})
        });
        let data = await res.json();
        document.getElementById('loading').remove();
        box.innerHTML += `<div style="color:#38bdf8;">🦞 龍蝦：${data.reply}</div>`;
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
    
    system_prompt = (
        "你是一隻萬能的 AI 龍蝦。如果使用者想要寄信，請嚴格按照以下格式回覆："
        "SEND_EMAIL|收件人信箱|郵件主旨|郵件內容。"
        "如果使用者沒有提供信箱、主旨或內容，請詢問他們。"
        "如果只是普通聊天，請正常回覆。"
    )

    headers = {
        "Authorization": f"Bearer {OPENROUTER_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        # 將原本的 gemini-2.0-flash-exp:free 換成下面其中一個
        "model": "google/gemini-2.0-flash-001", 
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_msg}
        ]
    }
    
    try:
        resp = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
        data = resp.json()

        # 如果 OpenRouter 回傳錯誤，這裡會抓到並顯示出來
        if "error" in data:
            return jsonify({"reply": f"🦞 龍蝦的大腦報錯了：{data['error'].get('message', '未知錯誤')}"})

        ai_reply = data["choices"][0]["message"]["content"]
        
        # 檢查是否為寄信指令
        if ai_reply.startswith("SEND_EMAIL|"):
            parts = ai_reply.split("|")
            if len(parts) >= 4:
                # 這裡統一把變數改成 to_email (跟下面呼叫的一樣)
                to_email = parts[1].strip() 
                subject = parts[2].strip()
                content = parts[3].strip()
                
                # 檢查權限
                if not SENDER_EMAIL or not SENDER_PASSWORD:
                    return jsonify({"reply": "🦞 我還沒有寄信的權限！請去 Render 設定 SENDER_EMAIL 和 SENDER_PASSWORD。"})
                
                # 執行寄信 (這裡呼叫的名稱也是 to_email)
                success = send_lobster_email(to_email, subject, content)
                if success:
                    return jsonify({"reply": f"任務完成！我已經把信寄給了 **{to_email}**。<br>主旨：{subject}<br>內容：{content}"})
                else:
                    return jsonify({"reply": "🦞 寄信失敗了... 請確認你的應用程式密碼是否正確。"})
        
        return jsonify({"reply": ai_reply})
    except Exception as e:
        return jsonify({"reply": f"🦞 龍蝦發生意外錯誤：{str(e)}"})
