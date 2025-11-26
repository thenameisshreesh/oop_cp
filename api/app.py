# api/app.py
import os
import smtplib
from email.message import EmailMessage

def handler(request, response):
    # check file upload
    if not hasattr(request, "files") or "file" not in request.files:
        response.status_code = 400
        return {"error": "No file sent"}

    file = request.files["file"]
    to_email = request.form.get("email")
    if not to_email:
        response.status_code = 400
        return {"error": "Email is required"}

    # Environment variables from Vercel dashboard
    SENDER_EMAIL = os.environ.get("SENDER_EMAIL")
    SENDER_PASSWORD = os.environ.get("SENDER_PASSWORD")

    # Compose email
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
        response.status_code = 500
        return {"error": str(e)}

    return {"status": "success", "message": "File sent"}
