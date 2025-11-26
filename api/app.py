import os
import smtplib
from email.message import EmailMessage

def handler(request):
    try:
        form = request.form
        files = request.files

        if files is None or "file" not in files:
            return {
                "statusCode": 400,
                "body": "No file sent"
            }

        file = files["file"]
        to_email = form.get("email")

        if not to_email:
            return {
                "statusCode": 400,
                "body": "Email is required"
            }

        # ✅ HARDCODED EMAIL (FOR NOW)
        SENDER_EMAIL = "shreeshpitambare084@gmail.com"
        SENDER_PASSWORD = "fsyo gokf lnqh yywy"

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

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(SENDER_EMAIL, SENDER_PASSWORD)
            smtp.send_message(msg)

        return {
            "statusCode": 200,
            "body": "File sent to email successfully"
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": str(e)
        }
