import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import Config

SMTP_SERVER = Config.SMTP_SERVER
SMTP_PORT = Config.SMTP_PORT
SMTP_USERNAME = Config.SMTP_USERNAME
SMTP_PASSWORD = Config.SMTP_PASSWORD

def send_email(to, subject, body_html):
    if not SMTP_SERVER or not SMTP_USERNAME or not SMTP_PASSWORD:
        print("Email settings not configured. Skipping email send.")
        return False
    
    msg = MIMEMultipart()
    msg['From'] = SMTP_USERNAME
    msg['To'] = to
    msg['Subject'] = subject
    msg.attach(MIMEText(body_html, 'html'))
    
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Email sending failed: {e}")
        return False
