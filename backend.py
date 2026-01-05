from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import requests
import os

app = Flask(__name__, static_folder='.')
CORS(app)

# HuggingFace Router API
API_URL = "https://router.huggingface.co/models/meta-llama/Llama-3.2-1B-Instruct"
API_KEY = os.environ.get("HF_TOKEN")  # HF_TOKEN already set in Render

@app.route('/')
def index():
    return send_file('chatbot.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json(silent=True)

    if not data or 'message' not in data:
        return jsonify({"reply": "Message missing 😶"}), 400

    try:
        response = requests.post(
            API_URL,
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "inputs": data["message"],
                "parameters": {
                    "max_new_tokens": 200,
                    "temperature": 0.7
                }
            },
            timeout=60
        )

        # 👀 Debug (Render logs)
        print("STATUS:", response.status_code)
        print("RAW:", response.text)

        # ❌ Empty or failed response
        if response.status_code != 200 or not response.text.strip():
            return jsonify({
                "reply": "Model thoda busy hai baby 🥺 thodi der baad try karo"
            }), 503

        # 🧠 SAFE JSON handling
        try:
            output = response.json()

            if isinstance(output, list) and len(output) > 0:
                reply = output[0].get("generated_text", "")
            else:
                reply = str(output)

            return jsonify({"reply": reply})

        except Exception:
            # Router kabhi plain text bhejta hai
            return jsonify({"reply": response.text})

    except Exception as e:
        return jsonify({
            "reply": "Server side thoda issue aa gaya 😔",
            "error": str(e)
        }), 500


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
