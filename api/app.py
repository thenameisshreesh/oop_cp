from flask import Flask, request, jsonify
import smtplib
from email.message import EmailMessage

app = Flask(__name__)  # ✅ This is required by Vercel

@app.route("/send-log", methods=["POST"])
def send_log():
    if "file" not in request.files:
        return jsonify({"error": "No file sent"}), 400

    file = request.files["file"]
    to_email = request.form.get("email")

    if not to_email:
        return jsonify({"error": "Email is required"}), 400

    # ✅ USE ENV VARIABLES (NOT HARDCODE)
    SENDER_EMAIL = "shreeshpitambare084@gmail.com"
    SENDER_PASSWORD = "fsyo gokf lnqh yywy"

    if not SENDER_EMAIL or not SENDER_PASSWORD:
        return jsonify({"error": "Email credentials not set in Vercel"}), 500

    msg = EmailMessage()
    msg["Subject"] = "Tracker Log File"
    msg["From"] = SENDER_EMAIL
    msg["To"] = to_email
    msg.set_content("Tracker log attached.")

    msg.add_attachment(
        file.read(),
        maintype="application",
        subtype="octet-stream",
        filename=file.filename
    )

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(SENDER_EMAIL, SENDER_PASSWORD)
            smtp.send_message(msg)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({"status": "success", "message": "File sent to email"})
