# import os
# from flask import Flask, request, jsonify
# from flask_cors import CORS
# from twilio.rest import Client
# from dotenv import load_dotenv

# # Load environment variables from .env
# load_dotenv()

# # Flask app
# app = Flask(__name__)

# # CORS configuration
# CORS(app, resources={
#     r"/send-whatsapp": {
#         "origins": [
#             "http://127.0.0.1:5500",
#             "http://localhost:5500",
#             "https://dance-class-api.onrender.com"
#         ],
#         "methods": ["POST"],
#         "allow_headers": ["Content-Type"]
#     }
# })

# # Twilio credentials
# ACCOUNT_SID = os.getenv('ACCOUNT_SID')
# AUTH_TOKEN = os.getenv('AUTH_TOKEN')
# TWILIO_NUMBER = os.getenv('TWILIO_NUMBER')
# MY_NUMBER = os.getenv('MY_NUMBER')

# # Twilio client
# client = Client(ACCOUNT_SID, AUTH_TOKEN)

# # Root route
# @app.route("/")
# def index():
#     return "Welcome to Dance Class API!"

# # WhatsApp API route
# @app.route('/send-whatsapp', methods=['POST'])
# def send_whatsapp():
#     try:
#         data = request.get_json()
#         if not data:
#             return jsonify({"status": "error", "message": "No JSON data received"}), 400

#         # Construct message content
#         content = (
#             f"New Enquiry!\n"
#             f"Name: {data.get('name')}\n"
#             f"Email: {data.get('email')}\n"
#             f"Phone: {data.get('phone')}\n"
#             f"Message: {data.get('message')}"
#         )

#         # Send WhatsApp message via Twilio
#         message = client.messages.create(
#             from_=TWILIO_NUMBER,
#             body=content,
#             to=MY_NUMBER
#         )

#         print(f"Message sent! SID: {message.sid}")
#         return jsonify({"status": "success", "sid": message.sid}), 200

#     except Exception as e:
#         print(f"ERROR: {e}")
#         return jsonify({"status": "error", "message": str(e)}), 500

# # Run Flask app
# if __name__ == "__main__":
#     port = int(os.environ.get("PORT", 5000))
#     app.run(host="0.0.0.0", port=port)



import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from twilio.rest import Client
from dotenv import load_dotenv

# Load environment variables from .env (for local dev)
load_dotenv()

# Flask app
app = Flask(__name__)

# ── CORS CONFIGURATION ──
# Add your frontend URLs here (GitHub Pages, Netlify, Vercel, etc.)
ALLOWED_ORIGINS = [
    "http://127.0.0.1:5500",
    "http://localhost:5500",
    "http://127.0.0.1:3000",
    "http://localhost:3000",
    # "https://your-username.github.io",   # ← uncomment & replace with your GitHub Pages URL
    # "https://your-site.netlify.app",     # ← uncomment & replace with your Netlify URL
    # "https://your-site.vercel.app",      # ← uncomment & replace with your Vercel URL
]

CORS(app, resources={
    r"/send-whatsapp": {
        "origins": ALLOWED_ORIGINS,
        "methods": ["POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# ── TWILIO CREDENTIALS (loaded from environment variables) ──
ACCOUNT_SID  = os.getenv("ACCOUNT_SID")
AUTH_TOKEN   = os.getenv("AUTH_TOKEN")
TWILIO_NUMBER = os.getenv("TWILIO_NUMBER")   # e.g. whatsapp:+14155238886
MY_NUMBER    = os.getenv("MY_NUMBER")         # e.g. whatsapp:+91XXXXXXXXXX

# ── VALIDATE ENV VARS ON STARTUP ──
missing = [k for k, v in {
    "ACCOUNT_SID":   ACCOUNT_SID,
    "AUTH_TOKEN":    AUTH_TOKEN,
    "TWILIO_NUMBER": TWILIO_NUMBER,
    "MY_NUMBER":     MY_NUMBER,
}.items() if not v]

if missing:
    print(f"⚠️  WARNING: Missing environment variables: {', '.join(missing)}")
    print("   Set them in your .env file (local) or Render dashboard (production).")

# ── TWILIO CLIENT ──
client = Client(ACCOUNT_SID, AUTH_TOKEN) if not missing else None


# ── ROOT ROUTE ──
@app.route("/")
def index():
    status = "✅ Ready" if not missing else f"⚠️ Missing env vars: {', '.join(missing)}"
    return jsonify({
        "app":    "Dance Class API",
        "status": status
    })


# ── HEALTH CHECK ──
@app.route("/health")
def health():
    return jsonify({"status": "ok"}), 200


# ── WHATSAPP ROUTE ──
@app.route("/send-whatsapp", methods=["POST", "OPTIONS"])
def send_whatsapp():
    # Handle CORS preflight
    if request.method == "OPTIONS":
        return "", 204

    # Check credentials are loaded
    if missing:
        return jsonify({
            "status":  "error",
            "message": f"Server misconfiguration: Missing env vars: {', '.join(missing)}"
        }), 500

    # Parse request body
    data = request.get_json(silent=True)
    if not data:
        return jsonify({
            "status":  "error",
            "message": "No JSON data received. Send Content-Type: application/json."
        }), 400

    # Validate required fields
    required_fields = ["name", "email", "message"]
    missing_fields = [f for f in required_fields if not data.get(f, "").strip()]
    if missing_fields:
        return jsonify({
            "status":  "error",
            "message": f"Missing required fields: {', '.join(missing_fields)}"
        }), 400

    # Build WhatsApp message
    content = (
        f"💃 New Dance Class Enquiry!\n\n"
        f"👤 Name:    {data.get('name', 'N/A')}\n"
        f"📧 Email:   {data.get('email', 'N/A')}\n"
        f"📞 Phone:   {data.get('phone', 'N/A') or 'Not provided'}\n"
        f"💬 Message: {data.get('message', 'N/A')}"
    )

    try:
        message = client.messages.create(
            from_=TWILIO_NUMBER,
            body=content,
            to=MY_NUMBER
        )
        print(f"✅ Message sent! SID: {message.sid}")
        return jsonify({
            "status":  "success",
            "message": "WhatsApp message sent successfully.",
            "sid":     message.sid
        }), 200

    except Exception as e:
        print(f"❌ Twilio ERROR: {e}")
        return jsonify({
            "status":  "error",
            "message": str(e)
        }), 500


# ── RUN ──
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 Starting Dance Class API on port {port}...")
    app.run(host="0.0.0.0", port=port, debug=False)