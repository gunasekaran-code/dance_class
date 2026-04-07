

# import os
# from flask import Flask, request, jsonify
# from flask_cors import CORS
# from twilio.rest import Client
# from dotenv import load_dotenv

# load_dotenv()

# app = Flask(__name__)
# CORS(app)   # Enable CORS

# ACCOUNT_SID = os.getenv('ACCOUNT_SID')
# AUTH_TOKEN = os.getenv('AUTH_TOKEN')
# TWILIO_NUMBER = os.getenv('TWILIO_NUMBER')
# MY_NUMBER = os.getenv('MY_NUMBER')

# client = Client(ACCOUNT_SID, AUTH_TOKEN)

# @app.route('/send-whatsapp', methods=['POST'])
# def send_whatsapp():
#     try:
#         data = request.get_json()

#         content = (
#             f"New Enquiry!\n"
#             f"Name: {data.get('name')}\n"
#             f"Email: {data.get('email')}\n"
#             f"Phone: {data.get('phone')}\n"
#             f"Message: {data.get('message')}"
#         )

#         message = client.messages.create(
#             from_=TWILIO_NUMBER,
#             body=content,
#             to=MY_NUMBER
#         )

#         return jsonify({"status": "success", "sid": message.sid})

#     except Exception as e:
#         return jsonify({"status": "error", "message": str(e)})
        

# if __name__ == "__main__":
#     port = int(os.environ.get("PORT", 5000))
#     app.run(host="0.0.0.0", port=port)


import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from twilio.rest import Client
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Flask app
app = Flask(__name__)

# CORS configuration
CORS(app, resources={
    r"/send-whatsapp": {
        "origins": [
            "http://127.0.0.1:5500",
            "http://localhost:5500",
            "https://dance-class-api.onrender.com"
        ],
        "methods": ["POST"],
        "allow_headers": ["Content-Type"]
    }
})

# Twilio credentials
ACCOUNT_SID = os.getenv('ACCOUNT_SID')
AUTH_TOKEN = os.getenv('AUTH_TOKEN')
TWILIO_NUMBER = os.getenv('TWILIO_NUMBER')
MY_NUMBER = os.getenv('MY_NUMBER')

# Twilio client
client = Client(ACCOUNT_SID, AUTH_TOKEN)

# Root route
@app.route("/")
def index():
    return "Welcome to Dance Class API!"

# WhatsApp API route
@app.route('/send-whatsapp', methods=['POST'])
def send_whatsapp():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "message": "No JSON data received"}), 400

        # Construct message content
        content = (
            f"New Enquiry!\n"
            f"Name: {data.get('name')}\n"
            f"Email: {data.get('email')}\n"
            f"Phone: {data.get('phone')}\n"
            f"Message: {data.get('message')}"
        )

        # Send WhatsApp message via Twilio
        message = client.messages.create(
            from_=TWILIO_NUMBER,
            body=content,
            to=MY_NUMBER
        )

        print(f"Message sent! SID: {message.sid}")
        return jsonify({"status": "success", "sid": message.sid}), 200

    except Exception as e:
        print(f"ERROR: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

# Run Flask app
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)