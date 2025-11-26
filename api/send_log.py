# api/send_log.py

import os
import smtplib
from email.message import EmailMessage

def send_email_with_attachment(to_email, file_data, file_name):
    msg = EmailMessage()
    msg["Subject"] = "Tracker Log File"
    msg["From"] = os.environ.get("SENDER_EMAIL")
    msg["To"] = to_email
    msg.set_content("Tracker log attached.")

    msg.add_attachment(
        file_data,
        maintype="application",
        subtype="octet-stream",
        filename=file_name
    )

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(os.environ.get("SENDER_EMAIL"), os.environ.get("SENDER_PASSWORD"))
        smtp.send_message(msg)

def handler(request, response):
    if "file" not in request.files:
        response.status_code = 400
        return response.json({"error": "No file sent"})

    file = request.files["file"]
    to_email = request.form.get("email")
    if not to_email:
        response.status_code = 400
        return response.json({"error": "Email is required"})

    try:
        send_email_with_attachment(to_email, file.read(), file.filename)
    except Exception as e:
        response.status_code = 500
        return response.json({"error": str(e)})

    return response.json({"status": "success", "message": "File sent"})
