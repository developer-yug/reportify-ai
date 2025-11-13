import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

def send_email(subject, body, receiver_email=None, cc_emails=None):
    sender = os.getenv("SENDER_EMAIL")
    password = os.getenv("SENDER_PASSWORD")
    receiver = receiver_email or os.getenv("RECEIVER_EMAIL")

    # Prepare CC list
    cc_emails = cc_emails or []  # [] if None

    # Use MIMEMultipart for CC support
    msg = MIMEMultipart()
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = receiver
    if cc_emails:
        msg["Cc"] = ", ".join(cc_emails)

    msg.attach(MIMEText(body, "plain"))

    # Combined recipients (To + CC)
    all_recipients = [receiver] + cc_emails

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender, password)
        server.send_message(msg, from_addr=sender, to_addrs=all_recipients)

    print("✅ Email sent successfully!")
