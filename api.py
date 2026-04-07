# import os
# from flask import Flask, request, jsonify
# from flask.cli import load_dotenv
# from flask_cors import CORS
# from twilio.rest import Client

# app = Flask(__name__)
# CORS(app) 

# load_dotenv()

# ACCOUNT_SID = os.getenv('ACCOUNT_SID')
# print(ACCOUNT_SID)
# AUTH_TOKEN = os.getenv('AUTH_TOKEN')
# print(AUTH_TOKEN)
# TWILIO_NUMBER = os.getenv('TWILIO_NUMBER')
# print(TWILIO_NUMBER)
# MY_NUMBER = os.getenv('MY_NUMBER')
# print(MY_NUMBER)


# client = Client(ACCOUNT_SID, AUTH_TOKEN)

# @app.route('/send-whatsapp', methods=['POST'])
# def send_whatsapp():
#     try:
#         data = request.json
#         print(f"Received data: {data}") # This will show in your terminal

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
#         print(f"Success! SID: {message.sid}")
#         return jsonify({"status": "success", "sid": message.sid}), 200

#     except Exception as e:
#         print(f"ERROR OCCURRED: {e}") # CHECK YOUR TERMINAL FOR THIS LINE
#         return jsonify({"status": "error", "message": str(e)}), 500

# if __name__ == '__main__':
#     app.run(port=5000) # Runs on http://127.0.0.1:5000


import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)   # Enable CORS

ACCOUNT_SID = os.getenv('ACCOUNT_SID')
AUTH_TOKEN = os.getenv('AUTH_TOKEN')
TWILIO_NUMBER = os.getenv('TWILIO_NUMBER')
MY_NUMBER = os.getenv('MY_NUMBER')

client = Client(ACCOUNT_SID, AUTH_TOKEN)

@app.route('/send-whatsapp', methods=['POST'])
def send_whatsapp():
    try:
        data = request.get_json()

        content = (
            f"New Enquiry!\n"
            f"Name: {data.get('name')}\n"
            f"Email: {data.get('email')}\n"
            f"Phone: {data.get('phone')}\n"
            f"Message: {data.get('message')}"
        )

        message = client.messages.create(
            from_=TWILIO_NUMBER,
            body=content,
            to=MY_NUMBER
        )

        return jsonify({"status": "success", "sid": message.sid})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})
        

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)