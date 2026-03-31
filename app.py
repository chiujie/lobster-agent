import os
import requests
import smtplib
from email.mime.text import MIMEText
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# 1. 從環境變數讀取資料
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY")
SENDER_EMAIL = os.getenv("SENDER_EMAIL")     
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD") 

# 2. 寄信功能
def send_lobster_email(to_email, subject, content):
    try:
        print(f"🦞 [寄信中] 正在連線至 Gmail 伺服器...")
        msg = MIMEText(content)
        msg['Subject'] = subject
        msg['From'] = SENDER_EMAIL
        msg['To'] = to_email

        with smtplib.SMTP('smtp.gmail.com', 587, timeout=20) as server:
            server.starttls() 
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, [to_email], msg.as_string())
        print(f"🦞 [成功] 信件已飛向 {to_email}")
        return True
    except Exception as e:
        print(f"❌ [失敗] 錯誤原因：{e}")
        return False

# 3. 前端網頁介面
HTML_PAGE = """
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>🦞 龍蝦自動執行員</title></head>
<body style="text-align:center; padding:50px; background:#0f172a; color:white; font-family:sans-serif;">
    <h1>🦞 萬能龍蝦 Agent</h1>
    <p>指令範例：寄信給 1121410902@mail.hwu.edu.tw，主旨是你好，內容是龍蝦進化了。</p>
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
            document.getElementById('loading').innerText = "❌ 發生連線錯誤，請查看日誌。";
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
    print(f"--- 📬 新指令：{user_msg} ---")
    
    system_prompt = (
        "你是一隻萬能的 AI 龍蝦。如果使用者想要寄信，請嚴格按照以下格式回覆："
        "SEND_EMAIL|收件人信箱|郵件主旨|郵件內容。"
        "否則請正常聊天。"
    )

    # 加上 Referer 標頭，這是 OpenRouter 官方建議的
    headers = {
        "Authorization": f"Bearer {OPENROUTER_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://render.com", # 告訴 OpenRouter 你從哪來
        "X-Title": "Lobster Agent"
    }
    
    payload = {
        # 換一個更穩定的免費模型試試看
        "model": "meta-llama/llama-3.1-8b-instruct:free", 
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_msg}
        ]
    }
    
    try:
        print("🧠 [思考中] 呼叫 OpenRouter...")
        resp = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload, timeout=25)
        
        # 這是關鍵！如果不是 200，就印出錯誤碼
        if resp.status_code != 200:
            print(f"❌ 大腦連線失敗，狀態碼：{resp.status_code}，內容：{resp.text}")
            return jsonify({"reply": f"🦞 龍蝦大腦斷線了（錯誤碼：{resp.status_code}），請稍後再試。"})

        data = resp.json()
        ai_reply = data["choices"][0]["message"]["content"]
        print(f"🤖 [AI 回覆]：{ai_reply}")
        
        if "SEND_EMAIL|" in ai_reply:
            parts = ai_reply.split("|")
            if len(parts) >= 4:
                to_email = parts[1].strip()
                subject = parts[2].strip()
                content = parts[3].strip()
                
                success = send_lobster_email(to_email, subject, content)
                if success:
                    return jsonify({"reply": f"✅ 任務完成！信已寄給 **{to_email}**。"})
                else:
                    return jsonify({"reply": "❌ 寄信失敗，請檢查 Gmail 應用程式密碼。"})
        
        return jsonify({"reply": ai_reply})
    except Exception as e:
        print(f"💥 [意外錯誤]：{str(e)}")
        return jsonify({"reply": f"龍蝦發生意外：{str(e)}"})

if __name__ == "__main__":
    # Render 會自動指定 PORT
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
