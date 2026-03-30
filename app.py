import os
from flask import Flask, request, jsonify, render_template
from openai import OpenAI

app = Flask(__name__)


def get_client():
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set")
    return OpenAI(api_key=api_key)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    if not data or "message" not in data:
        return jsonify({"error": "No message provided"}), 400

    user_message = data["message"].strip()
    if not user_message:
        return jsonify({"error": "Message cannot be empty"}), 400

    try:
        client = get_client()
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are Lobster, a helpful and friendly AI assistant.",
                },
                {"role": "user", "content": user_message},
            ],
        )
        reply = response.choices[0].message.content
        return jsonify({"reply": reply})
    except ValueError as e:
        app.logger.error("Configuration error: %s", e)
        return jsonify({"error": "Server configuration error. Please contact the administrator."}), 500
    except Exception as e:
        app.logger.error("Unexpected error during chat: %s", e)
        return jsonify({"error": "An unexpected error occurred. Please try again later."}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
