# api/send_log.py

import os
import smtplib
from email.message import EmailMessage
from werkzeug.datastructures import FileStorage

def send_email_with_attachment(to_email, file: FileStorage):
    msg = EmailMessage()
    msg["Subject"] = "Tracker Log File"
    msg["From"] = os.environ.get("SENDER_EMAIL")
    msg["To"] = to_email
    msg.set_content("Tracker log attached.")

    file_data = file.read()
    file_name = file.filename

    msg.add_attachment(
        file_data,
        maintype="application",
        subtype="octet-stream",
        filename=file_name
    )

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login("shreeshpitambare084@gmail.com", "fsyo gokf lnqh yywy")
        smtp.send_message(msg)

# ====== Vercel entry point ======
def handler(request, response):
    if "file" not in request.files:
        response.status_code = 400
        return response.json({"error": "No file sent"})

    to_email = request.form.get("email")
    if not to_email:
        response.status_code = 400
        return response.json({"error": "Email is required"})

    file = request.files["file"]
    try:
        send_email_with_attachment(to_email, file)
    except Exception as e:
        response.status_code = 500
        return response.json({"error": str(e)})

    return response.json({"status": "success", "message": "File sent"})
