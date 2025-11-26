# api/app.py
from flask import Flask, request, jsonify
import smtplib
from email.message import EmailMessage
import os

app = Flask(__name__)  # <-- This is what Vercel requires

SENDER_EMAIL = "shreeshpitambare084@gmail.com"
SENDER_PASSWORD = "fsyo gokf lnqh yywy"

def send_email_with_attachment(to_email, file_data, file_name):
    msg = EmailMessage()
    msg["Subject"] = "File Received"
    msg["From"] = SENDER_EMAIL
    msg["To"] = to_email
    msg.set_content("File received successfully. See attachment.")
    msg.add_attachment(file_data, maintype="application", subtype="octet-stream", filename=file_name)
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(SENDER_EMAIL, SENDER_PASSWORD)
        smtp.send_message(msg)

@app.route("/send-log", methods=["POST"])
def send_log():
    if "file" not in request.files:
        return jsonify({"error": "No file sent"}), 400
    to_email = request.form.get("email")
    if not to_email:
        return jsonify({"error": "Email is required"}), 400
    file = request.files["file"]
    try:
        send_email_with_attachment(to_email, file.read(), file.filename)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    return jsonify({"status": "success", "message": "File sent"})
