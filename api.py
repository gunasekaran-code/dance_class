# import os
# from flask import Flask, request, jsonify
# from flask_cors import CORS
# from twilio.rest import Client
# from dotenv import load_dotenv

# load_dotenv()

# app = Flask(__name__)

# ALLOWED_ORIGINS = [
#     "http://127.0.0.1:5500",
#     "http://localhost:5500",
#     "http://127.0.0.1:3000",
#     "http://localhost:3000",
#     # "https://your-username.github.io",   # ← uncomment & replace with your GitHub Pages URL
#     # "https://sri-vani-kalai-mandram.netlify.app",  # ← replace with your Netlify URL
#     # "https://your-site.vercel.app",      # ← uncomment & replace with your Vercel URL
# ]

# CORS(app, resources={
#     r"/send-whatsapp": {
#         "origins": ALLOWED_ORIGINS,
#         "methods": ["POST", "OPTIONS"],
#         "allow_headers": ["Content-Type"]
#     }
# })

# ACCOUNT_SID  = os.getenv("ACCOUNT_SID")
# AUTH_TOKEN   = os.getenv("AUTH_TOKEN")
# TWILIO_NUMBER = os.getenv("TWILIO_NUMBER")   # e.g. whatsapp:+14155238886
# MY_NUMBER    = os.getenv("MY_NUMBER")         # e.g. whatsapp:+91XXXXXXXXXX

# missing = [k for k, v in {
#     "ACCOUNT_SID":   ACCOUNT_SID,
#     "AUTH_TOKEN":    AUTH_TOKEN,
#     "TWILIO_NUMBER": TWILIO_NUMBER,
#     "MY_NUMBER":     MY_NUMBER,
# }.items() if not v]

# if missing:
#     print(f"⚠️  WARNING: Missing environment variables: {', '.join(missing)}")
#     print("   Set them in your .env file (local) or Render dashboard (production).")

# client = Client(ACCOUNT_SID, AUTH_TOKEN) if not missing else None

# @app.route("/")
# def index():
#     status = "✅ Ready" if not missing else f"⚠️ Missing env vars: {', '.join(missing)}"
#     return jsonify({
#         "app":    "Dance Class API",
#         "status": status
#     })

# @app.route("/health")
# def health():
#     return jsonify({"status": "ok"}), 200

# @app.route("/send-whatsapp", methods=["POST", "OPTIONS"])
# def send_whatsapp():
#     if request.method == "OPTIONS":
#         return "", 204

#     if missing:
#         return jsonify({
#             "status":  "error",
#             "message": f"Server misconfiguration: Missing env vars: {', '.join(missing)}"
#         }), 500

#     data = request.get_json(silent=True)
#     if not data:
#         return jsonify({
#             "status":  "error",
#             "message": "No JSON data received. Send Content-Type: application/json."
#         }), 400

#     required_fields = ["name", "email", "message"]
#     missing_fields = [f for f in required_fields if not data.get(f, "").strip()]
#     if missing_fields:
#         return jsonify({
#             "status":  "error",
#             "message": f"Missing required fields: {', '.join(missing_fields)}"
#         }), 400

#     content = (
#         f"💃 New Dance Class Enquiry!\n\n"
#         f"Name:    {data.get('name', 'N/A')}\n"
#         f"Email:   {data.get('email', 'N/A')}\n"
#         f"Phone:   {data.get('phone', 'N/A') or 'Not provided'}\n"
#         f"Message: {data.get('message', 'N/A')}"
#     )

#     try:
#         message = client.messages.create(
#             from_=TWILIO_NUMBER,
#             body=content,
#             to=MY_NUMBER
#         )
#         print(f"✅ Message sent! SID: {message.sid}")
#         return jsonify({
#             "status":  "success",
#             "message": "WhatsApp message sent successfully.",
#             "sid":     message.sid
#         }), 200

#     except Exception as e:
#         print(f"❌ Twilio ERROR: {e}")
#         return jsonify({
#             "status":  "error",
#             "message": str(e)
#         }), 500


# # ── RUN ──
# if __name__ == "__main__":
#     port = int(os.environ.get("PORT", 5000))
#     print(f"🚀 Starting Dance Class API on port {port}...")
#     app.run(host="0.0.0.0", port=port, debug=False)


import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

ALLOWED_ORIGINS = [
    "http://127.0.0.1:5500",
    "http://localhost:5500",
    "http://127.0.0.1:3000",
    "http://localhost:3000",
    # "https://your-username.github.io",
    # "https://sri-vani-kalai-mandram.netlify.app",
]

CORS(app, resources={
    r"/send-whatsapp": {
        "origins": ALLOWED_ORIGINS,
        "methods": ["POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

ACCOUNT_SID   = os.getenv("ACCOUNT_SID")
AUTH_TOKEN    = os.getenv("AUTH_TOKEN")
TWILIO_NUMBER = os.getenv("TWILIO_NUMBER")   # e.g. whatsapp:+14155238886
MY_NUMBER     = os.getenv("MY_NUMBER")       # e.g. whatsapp:+91XXXXXXXXXX

missing = [k for k, v in {
    "ACCOUNT_SID":   ACCOUNT_SID,
    "AUTH_TOKEN":    AUTH_TOKEN,
    "TWILIO_NUMBER": TWILIO_NUMBER,
    "MY_NUMBER":     MY_NUMBER,
}.items() if not v]

if missing:
    print(f"⚠️  WARNING: Missing env vars: {', '.join(missing)}")

client = Client(ACCOUNT_SID, AUTH_TOKEN) if not missing else None

# ─────────────────────────────────────────────────────────────────
# In-memory store: maps customer WhatsApp number → enquiry details
# (Use a real DB like SQLite / Redis in production)
# ─────────────────────────────────────────────────────────────────
pending_orders = {}   # { "whatsapp:+91XXXXXXXXXX": { name, email, phone, message } }


# ════════════════════════════════════════════════════════════════
#  STEP 1 — Frontend posts enquiry → we notify business + send
#           a "Confirm / Cancel" prompt to the CUSTOMER
# ════════════════════════════════════════════════════════════════
@app.route("/send-whatsapp", methods=["POST", "OPTIONS"])
def send_whatsapp():
    if request.method == "OPTIONS":
        return "", 204

    if missing:
        return jsonify({
            "status": "error",
            "message": f"Server misconfiguration: missing env vars: {', '.join(missing)}"
        }), 500

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"status": "error",
                        "message": "No JSON data received."}), 400

    required_fields = ["name", "email", "message"]
    missing_fields = [f for f in required_fields if not data.get(f, "").strip()]
    if missing_fields:
        return jsonify({
            "status": "error",
            "message": f"Missing required fields: {', '.join(missing_fields)}"
        }), 400

    name    = data.get("name",    "N/A").strip()
    email   = data.get("email",   "N/A").strip()
    phone   = data.get("phone",   "").strip()
    message = data.get("message", "N/A").strip()

    # Build customer WhatsApp number
    customer_wa = None
    if phone.startswith("+"):
        customer_wa = f"whatsapp:{phone}"
    elif phone.isdigit() and len(phone) >= 10:
        # Auto-add India code if no + prefix
        customer_wa = f"whatsapp:+91{phone[-10:]}"

    sids = []

    try:
        # ── 1a. Notify BUSINESS number about new enquiry ──────────────
        biz_body = (
            f"💃 *New Dance Class Enquiry!*\n\n"
            f"👤 Name:    {name}\n"
            f"📧 Email:   {email}\n"
            f"📱 Phone:   {phone or 'Not provided'}\n"
            f"💬 Message: {message}\n\n"
            f"{'✅ Confirmation request sent to customer.' if customer_wa else '⚠️ No valid phone — cannot send confirmation to customer.'}"
        )
        biz_msg = client.messages.create(
            from_=TWILIO_NUMBER,
            body=biz_body,
            to=MY_NUMBER
        )
        sids.append(biz_msg.sid)
        print(f"✅ Business notified! SID: {biz_msg.sid}")

        # ── 1b. Send CONFIRM / CANCEL prompt to CUSTOMER ──────────────
        if customer_wa:
            # Save enquiry so the webhook can look it up
            pending_orders[customer_wa] = {
                "name": name, "email": email,
                "phone": phone, "message": message
            }

            # WhatsApp Sandbox supports quick-reply-style text buttons
            # Customer just needs to reply "1" or "2"
            cust_body = (
                f"🙏 Hi *{name}*!\n\n"
                f"Thank you for enquiring about *Sri Vani Kalai Mandram* dance class. "
                f"We've received your details.\n\n"
                f"━━━━━━━━━━━━━━━\n"
                f"📋 *Your Enquiry*\n"
                f"📧 {email}\n"
                f"💬 {message}\n"
                f"━━━━━━━━━━━━━━━\n\n"
                f"Please reply to *confirm or cancel* your registration:\n\n"
                f"✅  Reply *1* to *CONFIRM* your registration\n"
                f"❌  Reply *2* to *CANCEL* your enquiry"
            )
            cust_msg = client.messages.create(
                from_=TWILIO_NUMBER,
                body=cust_body,
                to=customer_wa
            )
            sids.append(cust_msg.sid)
            print(f"✅ Confirmation request sent to customer! SID: {cust_msg.sid}")

        return jsonify({
            "status":   "success",
            "message":  "Enquiry received. Confirmation request sent to customer via WhatsApp.",
            "sids":     sids,
            "customer": customer_wa or "No valid number provided"
        }), 200

    except Exception as e:
        print(f"❌ Twilio ERROR: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


# ════════════════════════════════════════════════════════════════
#  STEP 2 — Twilio webhook: customer replies "1" (confirm)
#           or "2" (cancel) → auto-respond + notify business
#
#  👉 Set this URL in your Twilio Sandbox settings:
#     https://YOUR-DOMAIN.com/whatsapp-reply
#     (use ngrok for local testing: ngrok http 5000)
# ════════════════════════════════════════════════════════════════
@app.route("/whatsapp-reply", methods=["POST"])
def whatsapp_reply():
    incoming_msg = request.form.get("Body", "").strip()
    from_number  = request.form.get("From", "").strip()   # e.g. whatsapp:+91XXXXXXXXXX

    resp = MessagingResponse()

    # Look up the pending order for this customer
    order = pending_orders.get(from_number)
    name  = order["name"] if order else "there"

    # ── CONFIRM (reply "1" or keywords) ──────────────────────────
    if incoming_msg in ["1", "yes", "confirm", "ok", "okay"]:
        # Reply to customer with green-style confirmation
        reply_text = (
            f"✅ *Registration Confirmed!*\n\n"
            f"Hi *{name}*, your registration for *Sri Vani Kalai Mandram* "
            f"dance class has been *confirmed*! 🎉💃\n\n"
            f"We will contact you shortly with class schedule and details.\n\n"
            f"Thank you for joining us! 🙏"
        )
        resp.message(reply_text)

        # Notify business about the confirmation
        if not missing and order:
            try:
                client.messages.create(
                    from_=TWILIO_NUMBER,
                    body=(
                        f"✅ *ORDER CONFIRMED*\n\n"
                        f"👤 {order['name']} has *confirmed* their registration!\n"
                        f"📧 {order['email']}\n"
                        f"📱 {order['phone']}\n"
                        f"💬 {order['message']}"
                    ),
                    to=MY_NUMBER
                )
                print(f"✅ Business notified: {name} confirmed.")
            except Exception as e:
                print(f"❌ Could not notify business: {e}")

        # Clean up
        pending_orders.pop(from_number, None)

    # ── CANCEL (reply "2" or keywords) ───────────────────────────
    elif incoming_msg in ["2", "no", "cancel", "stop"]:
        reply_text = (
            f"❌ *Enquiry Cancelled*\n\n"
            f"Hi *{name}*, your enquiry has been cancelled.\n\n"
            f"No worries! Feel free to reach out anytime if you'd like "
            f"to join our dance class in the future. 🙏\n\n"
            f"*Sri Vani Kalai Mandram* 💃"
        )
        resp.message(reply_text)

        # Notify business about the cancellation
        if not missing and order:
            try:
                client.messages.create(
                    from_=TWILIO_NUMBER,
                    body=(
                        f"❌ *ORDER CANCELLED*\n\n"
                        f"👤 {order['name']} has *cancelled* their enquiry.\n"
                        f"📧 {order['email']}\n"
                        f"📱 {order['phone']}"
                    ),
                    to=MY_NUMBER
                )
                print(f"❌ Business notified: {name} cancelled.")
            except Exception as e:
                print(f"❌ Could not notify business: {e}")

        # Clean up
        pending_orders.pop(from_number, None)

    # ── UNKNOWN REPLY ─────────────────────────────────────────────
    else:
        resp.message(
            f"👋 Hi! Please reply:\n\n"
            f"✅  *1*  to CONFIRM your registration\n"
            f"❌  *2*  to CANCEL your enquiry"
        )

    return str(resp), 200, {"Content-Type": "text/xml"}


# ── Utility routes ────────────────────────────────────────────────
@app.route("/")
def index():
    status = "✅ Ready" if not missing else f"⚠️ Missing: {', '.join(missing)}"
    return jsonify({
        "app": "Dance Class API",
        "status": status,
        "pending_orders": len(pending_orders)
    })

@app.route("/health")
def health():
    return jsonify({"status": "ok"}), 200


# ── RUN ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 Starting Dance Class API on port {port}...")
    print(f"📌 Webhook URL for Twilio Sandbox: http://localhost:{port}/whatsapp-reply")
    app.run(host="0.0.0.0", port=port, debug=False)