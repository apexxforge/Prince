import base64
import json
from flask import Flask, jsonify, request

app = Flask(__name__)


def decode_jwt_payload(auth_header):
  try:
    if not auth_header or not auth_header.startswith("Bearer "):
      return None
    token = auth_header.split(" ")[1]
    parts = token.split(".")
    if len(parts) >= 2:
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


# Support both with or without prefix routes
@app.route("/GetLoginData", methods=["POST"])
@app.route("/<path:subpath>/GetLoginData", methods=["POST"])
def get_login_data(subpath=None):
  auth_header = request.headers.get("Authorization")
  jwt_data = decode_jwt_payload(auth_header)

  account_id = jwt_data.get("account_id", 16121612027) if jwt_data else 16121612027
  nickname = jwt_data.get("nickname", "cVEpkVjNkWEZ3ST0=") if jwt_data else "cVEpkVjNkWEZ3ST0="
  region = jwt_data.get("noti_region", "IND") if jwt_data else "IND"

  print(f"[GET_LOGIN_DATA] Account ID: {account_id}, Region: {region}")

  # Dummy valid binary response structure to prevent crash/error (2)
  # Game expects proper binary stream, returning minimal payload wrapper
  return app.response_class(
      b"\x08\x96\x01\x12\x0b" + str(account_id).encode(),
      status=200,
      mimetype="application/octet-stream"
  )


@app.route("/Ping", methods=["POST"])
@app.route("/<path:subpath>/Ping", methods=["POST"])
def ping(subpath=None):
  return "", 200, {"Content-Type": "application/octet-stream"}


@app.route("/LoginGetDesc", methods=["POST"])
@app.route("/<path:subpath>/LoginGetDesc", methods=["POST"])
def login_get_desc(subpath=None):
  return "", 200, {"Content-Type": "application/octet-stream"}


if __name__ == "__main__":
  import os
  port = int(os.environ.get("PORT", 5000))
  app.run(host="0.0.0.0", port=port, debug=True)
  
