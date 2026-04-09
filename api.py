import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

ALLOWED_ORIGINS = [
    "http://127.0.0.1:5500",
    "http://localhost:5500",
    "http://127.0.0.1:3000",
    "http://localhost:3000",
    # "https://your-username.github.io",   # ← uncomment & replace with your GitHub Pages URL
    "https://sri-vani-kalai-mandram.netlify.app",  # ← replace with your Netlify URL
    # "https://your-site.vercel.app",      # ← uncomment & replace with your Vercel URL
]

CORS(app, resources={
    r"/send-whatsapp": {
        "origins": ALLOWED_ORIGINS,
        "methods": ["POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

ACCOUNT_SID  = os.getenv("ACCOUNT_SID")
AUTH_TOKEN   = os.getenv("AUTH_TOKEN")
TWILIO_NUMBER = os.getenv("TWILIO_NUMBER")   # e.g. whatsapp:+14155238886
MY_NUMBER    = os.getenv("MY_NUMBER")         # e.g. whatsapp:+91XXXXXXXXXX

missing = [k for k, v in {
    "ACCOUNT_SID":   ACCOUNT_SID,
    "AUTH_TOKEN":    AUTH_TOKEN,
    "TWILIO_NUMBER": TWILIO_NUMBER,
    "MY_NUMBER":     MY_NUMBER,
}.items() if not v]

if missing:
    print(f"⚠️  WARNING: Missing environment variables: {', '.join(missing)}")
    print("   Set them in your .env file (local) or Render dashboard (production).")

client = Client(ACCOUNT_SID, AUTH_TOKEN) if not missing else None

@app.route("/")
def index():
    status = "✅ Ready" if not missing else f"⚠️ Missing env vars: {', '.join(missing)}"
    return jsonify({
        "app":    "Dance Class API",
        "status": status
    })

@app.route("/health")
def health():
    return jsonify({"status": "ok"}), 200

@app.route("/send-whatsapp", methods=["POST", "OPTIONS"])
def send_whatsapp():
    if request.method == "OPTIONS":
        return "", 204

    if missing:
        return jsonify({
            "status":  "error",
            "message": f"Server misconfiguration: Missing env vars: {', '.join(missing)}"
        }), 500

    data = request.get_json(silent=True)
    if not data:
        return jsonify({
            "status":  "error",
            "message": "No JSON data received. Send Content-Type: application/json."
        }), 400

    required_fields = ["name", "email", "message"]
    missing_fields = [f for f in required_fields if not data.get(f, "").strip()]
    if missing_fields:
        return jsonify({
            "status":  "error",
            "message": f"Missing required fields: {', '.join(missing_fields)}"
        }), 400

    content = (
        f"💃 New Dance Class Enquiry!\n\n"
        f"Name:    {data.get('name', 'N/A')}\n"
        f"Email:   {data.get('email', 'N/A')}\n"
        f"Phone:   {data.get('phone', 'N/A') or 'Not provided'}\n"
        f"Message: {data.get('message', 'N/A')}"
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