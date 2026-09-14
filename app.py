import base64
import json
from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():
    return jsonify({"status": "active", "message": "Proxy is running successfully"})

@app.route("/GetLoginData", methods=["POST", "GET"])
@app.route("/<path:subpath>/GetLoginData", methods=["POST", "GET"])
def get_login_data(subpath=None):
    try:
        # Print incoming headers/data for debugging on Render logs
        print("Incoming Headers:", dict(request.headers))
        print("Incoming Data:", request.get_data())
        
        # Free Fire login response structure
        response_data = {
            "account_id": 16121612027,
            "is_banned": False,
            "nickname": "Player",
            "region": "IND",
            "status": 0
        }
        return jsonify(response_data), 200
    except Exception as e:
        print(f"Error in GetLoginData: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/Ping", methods=["POST", "GET"])
@app.route("/<path:subpath>/Ping", methods=["POST", "GET"])
def ping(subpath=None):
    return "", 200

@app.route("/LoginGetDesc", methods=["POST", "GET"])
@app.route("/<path:subpath>/LoginGetDesc", methods=["POST", "GET"])
def login_get_desc(subpath=None):
    return jsonify({"desc": "Server Online"}), 200

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
  
