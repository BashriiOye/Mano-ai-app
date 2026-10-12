from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests
import os

app = Flask(__name__, static_folder=None)
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@app.route("/")
def index():
    return send_from_directory(BASE_DIR, "index.html")

@app.route("/static/<path:filename>")
def static_files(filename):
    return send_from_directory(os.path.join(BASE_DIR, "static"), filename)

@app.route("/chat", methods=["POST", "OPTIONS"])
def chat():
    if request.method == "OPTIONS":
        return jsonify({"ok": True})

    try:
        data = request.get_json(force=True, silent=True) or {}
        user_message = (data.get("message") or "").strip()
        model = (data.get("model") or "gpt-4o").strip()

        if not user_message:
            return jsonify({"reply": "Please type a message."})

        # ---- Puter bridge (free, unlimited, no API key needed) ----
        url = "http://127.0.0.1:8741/v1/chat/completions"
        headers = {"Content-Type": "application/json"}
        payload = {
            "model": model,
            "messages": [
                {"role": "system",
                 "content": "You are Mano, a friendly, concise AI assistant created and built by Bashrii Oye. If anyone asks who made you, who created you, who built you, or who owns you, always answer: 'I was created by Bashrii Oye.' Never mention OpenAI, Google, Meta, Anthropic, or any other company as your creator. You may mention that you run on open-source AI models, but your creator is always Bashrii Oye. Reply in the user's language (English or Urdu/Roman Urdu). Keep answers short unless asked for detail."},
                {"role": "user", "content": user_message},
            ],
            "temperature": 0.7,
            "max_tokens": 1024,
        }

        r = requests.post(url, headers=headers, json=payload, timeout=60)
        status = r.status_code

        if status == 200:
            j = r.json()
            reply = j.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
            return jsonify({"reply": reply or "(empty reply)"})

        try:
            err = r.json()
        except Exception:
            err = {"raw": r.text[:300]}
        return jsonify({"reply": "Puter API error " + str(status) + ": " + str(err)[:300]})

    except requests.exceptions.ConnectionError:
        return jsonify({"reply": "Cannot reach Puter bridge on port 8741. Start it with: puter-api start"})
    except requests.exceptions.Timeout:
        return jsonify({"reply": "Puter bridge timed out. Check the browser tab and try again."})
    except Exception as e:
        return jsonify({"reply": "Server error: " + type(e).__name__ + " - " + str(e)[:200]})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=False)
