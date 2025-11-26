# api/send_log.py

from flask import Flask, request, jsonify
import smtplib
from email.message import EmailMessage
import os

app = Flask(__name__)

# ✅ Environment variables
SENDER_EMAIL = "shreeshpitambare084@gmail.com"
SENDER_PASSWORD = "fsyo gokf lnqh yywy"

def send_email_with_attachment(to_email, file_path):
    msg = EmailMessage()
    msg["Subject"] = "Tracker Log File"
    msg["From"] = SENDER_EMAIL
    msg["To"] = to_email
    msg.set_content("Tracker log attached.")

    with open(file_path, "rb") as f:
        file_data = f.read()
        file_name = os.path.basename(file_path)

    msg.add_attachment(
        file_data,
        maintype="application",
        subtype="octet-stream",
        filename=file_name
    )

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(SENDER_EMAIL, SENDER_PASSWORD)
        smtp.send_message(msg)

@app.route("/api/send-log", methods=["POST"])
def send_log():
    if "file" not in request.files:
        return jsonify({"error": "No file sent"}), 400

    to_email = request.form.get("email")
    if not to_email:
        return jsonify({"error": "Email is required"}), 400

    file = request.files["file"]
    os.makedirs("/tmp/uploads", exist_ok=True)  # Vercel serverless temp dir
    file_path = os.path.join("/tmp/uploads", file.filename)
    file.save(file_path)

    try:
        send_email_with_attachment(to_email, file_path)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({"status": "success", "message": "File sent"})
