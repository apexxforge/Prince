from flask import Flask, request

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():
    return "Proxy is running successfully", 200

@app.route("/GetLoginData", methods=["POST", "GET"])
@app.route("/<path:subpath>/GetLoginData", methods=["POST", "GET"])
def get_login_data(subpath=None):
    # Game expects a raw binary octet-stream response, not JSON!
    # Returning a valid minimal binary packet structure that Free Fire accepts
    dummy_binary_response = b"\x08\x96\x01\x12\x15\x0a\x0b16121612027\x10\x01"
    return app.response_class(dummy_binary_response, status=200, mimetype="application/octet-stream")

@app.route("/Ping", methods=["POST", "GET"])
@app.route("/<path:subpath>/Ping", methods=["POST", "GET"])
def ping(subpath=None):
    return b"", 200, {"Content-Type": "application/octet-stream"}

@app.route("/LoginGetDesc", methods=["POST", "GET"])
@app.route("/<path:subpath>/LoginGetDesc", methods=["POST", "GET"])
def login_get_desc(subpath=None):
    return b"", 200, {"Content-Type": "application/octet-stream"}

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
    
