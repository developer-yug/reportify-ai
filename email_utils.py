# import os
# import smtplib
# from email.mime.text import MIMEText
# from dotenv import load_dotenv

# load_dotenv()

# def send_email(subject, body):
#     sender = os.getenv("SENDER_EMAIL")
#     password = os.getenv("SENDER_PASSWORD")
#     receiver = os.getenv("RECEIVER_EMAIL")

#     msg = MIMEText(body, "plain")
#     msg["Subject"] = subject
#     msg["From"] = sender
#     msg["To"] = receiver

#     with smtplib.SMTP("smtp.gmail.com", 587) as server:
#         server.starttls()
#         server.login(sender, password)
#         server.send_message(msg)
#         print("✅ Email sent successfully!")
