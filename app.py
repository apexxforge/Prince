import base64
import json
from flask import Flask, jsonify, request

app = Flask(__name__)


# Helper function to decode JWT token without external heavy dependencies if needed,
# or we can just extract the payload section.
def decode_jwt_payload(auth_header):
  try:
    if not auth_header or not auth_header.startswith("Bearer "):
      return None
    token = auth_header.split(" ")[1]
    # JWT format: header.payload.signature
    parts = token.split(".")
    if len(parts) >= 2:
      # Fix base64 padding if needed
      payload_part = parts[1]
      padding = len(payload_part) % 4
      if padding:
        payload_part += "=" * (4 - padding)
      decoded_bytes = base64.urlsafe_b64decode(payload_part)
      return json.loads(decoded_bytes.decode("utf-8"))
  except Exception as e:
    print(f"JWT Decode Error: {e}")
  return None


@app.route("/", methods=["GET"])
def home():
  return jsonify(
      {
        "status": "online",
        "message": "Free Fire Custom Backend is running successfully!",
      }
  )


# 1. GetLoginData Endpoint (Proxyman log #173 ke mutabiq)
@app.route("/GetLoginData", methods=["POST"])
def get_login_data():
  auth_header = request.headers.get("Authorization")
  jwt_data = decode_jwt_payload(auth_header)

  account_id = jwt_data.get("account_id", 16121612027) if jwt_data else 16121612027
  nickname = jwt_data.get("nickname", "cVEpkVjNkWEZ3ST0=") if jwt_data else "cVEpkVjNkWEZ3ST0="
  region = jwt_data.get("noti_region", "IND") if jwt_data else "IND"

  print(f"[GET_LOGIN_DATA] Request received for Account ID: {account_id}, Region: {region}")

  # Yahan hum game ko wahi exact structure bhej rahe hain jo response log #173 mein tha
  # Note: Kyunki game binary Protobuf expect karta hai, production mein isko protobuf builder se serialize karna padta hai.
  # Filhal hum basic JSON/binary placeholder response set kar rahe hain.
  
  response_payload = {
      "1": account_id,
      "2": 1,
      "3": region,
      "4": nickname,
      "5": 1782049211,
      "6": 2,
      "7": 48,
      "8": 2,
      "9": 1000,
      "14": "34.126.115.57:39698",
      "15": 8,
      "16": "https://indevent.ggblueshark.com/",
      "39": "https://indnetwork.ggblueshark.com/",
      "79": "https://indgigateway.ggblueshark.com/",
      "92": "https://vodka.freefiremobile.com",
      "98": "CS_IND"
  }
  
  # Note: Agar game direct raw protobuf mang raha hai, toh ise protobuf object mein pack karna hoga.
  return app.response_class(
      response.content if 'response' in locals() else b"", # placeholder
      status=200,
      mimetype="application/octet-stream"
  )


# 2. Ping Endpoint (Proxyman log #174)
@app.route("/Ping", methods=["POST"])
def ping():
  print("[PING] Ping request received from game.")
  return "", 200, {"Content-Type": "application/octet-stream"}


# 3. LoginGetDesc Endpoint (Proxyman log #175)
@app.route("/LoginGetDesc", methods=["POST"])
def login_get_desc():
  print("[LOGIN_GET_DESC] Fetching configuration/descriptions...")
  # Yeh lamba data hota hai, isko binary stream ke roop mein bhejna hota hai.
  return app.response_class(b"", status=200, mimetype="application/octet-stream")


if __name__ == "__main__":
  # Render ya local testing ke liye port configuration
  import os
  port = int(os.environ.get("PORT", 5000))
  app.run(host="0.0.0.0", port=port, debug=True)
  
