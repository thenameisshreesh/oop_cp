import os
import smtplib
from email.message import EmailMessage
from flask import Flask, request, jsonify

app = Flask(__name__)

# ✅ TEMP DIRECTORY FOR VERCEL (IMPORTANT)
UPLOAD_FOLDER = "/tmp/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ✅ USE HARD-CODED FOR NOW (ENV ALSO WORKS)
SENDER_EMAIL = "shreeshpitambare084@gmail.com"
SENDER_PASSWORD = "fsyo gokf lnqh yywy"   # Gmail App Password

def send_email_with_attachment(to_email, file_path):
    msg = EmailMessage()
    msg["Subject"] = "File Receivedd"
    msg["From"] = SENDER_EMAIL
    msg["To"] = to_email
    msg.set_content("File received successfully. See attachment.")

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

# ✅ VERCEL API ROUTE
@app.route("/api", methods=["POST"])
def upload_and_send():
    to_email = request.form.get("email")

    if not to_email:
        return jsonify({"error": "Email is required"}), 400

    if "file" not in request.files:
        return jsonify({"error": "No file sent"}), 400

    file = request.files["file"]
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    try:
        send_email_with_attachment(to_email, file_path)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({"status": "success", "message": "File sent to email"})
