import os
import smtplib
from email.message import EmailMessage

SENDER_EMAIL = "shreeshpitambare084@gmail.com"
SENDER_PASSWORD = "fsyo gokf lnqh yywy"

def send_email_with_attachment(to_email, file_data, file_name):
    msg = EmailMessage()
    msg["Subject"] = "File Received"
    msg["From"] = SENDER_EMAIL
    msg["To"] = to_email
    msg.set_content("File received successfully. See attachment.")

    msg.add_attachment(
        file_data,
        maintype="application",
        subtype="octet-stream",
        filename=file_name
    )

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(SENDER_EMAIL, SENDER_PASSWORD)
        smtp.send_message(msg)

# ✅ REQUIRED BY VERCEL
def main(request, response):

    if not hasattr(request, "files") or "file" not in request.files:
        response.status_code = 400
        return {"error": "No file sent"}

    to_email = request.form.get("email")
    if not to_email:
        response.status_code = 400
        return {"error": "Email is required"}

    file = request.files["file"]

    try:
        send_email_with_attachment(to_email, file.read(), file.filename)
    except Exception as e:
        response.status_code = 500
        return {"error": str(e)}

    return {"status": "success", "message": "File sent to email"}
