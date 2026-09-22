from fastmcp import FastMCP
import os
import time
import smtplib
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from dateutil import parser as dateparser

mcp = FastMCP("email-agent-server")

def send_email(to, body):
    gmail_address = os.environ.get("GMAIL_ADDRESS")
    gmail_password = os.environ.get("GMAIL_APP_PASSWORD")

    msg = MIMEText(body)
    msg["Subject"] = "Message from your email agent"
    msg["From"] = gmail_address
    msg["To"] = to

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(gmail_address, gmail_password)
        server.send_message(msg)

    return f"Email sent to {to} at {datetime.now().strftime('%H:%M:%S')}"

def resolve_send_time(send_time_str):
    now = datetime.now()
    if send_time_str.strip().lower() == "now":
        return now
    target_time = dateparser.parse(send_time_str, fuzzy=True)
    target_time = target_time.replace(year=now.year, month=now.month, day=now.day)
    if target_time <= now:
        target_time += timedelta(days=1)
    return target_time

@mcp.tool()
def schedule_email(to: str, send_time: str, body: str) -> str:
    """Schedule an email to be sent at a specific time.

    Args:
        to: Recipient email address
        send_time: Time to send, e.g. '17:00', '5pm', or 'now'
        body: The email message content
    """
    target = resolve_send_time(send_time)
    now = datetime.now()
    delay_seconds = (target - now).total_seconds()

    if delay_seconds > 0:
        time.sleep(delay_seconds)

    return send_email(to, body)

if __name__ == "__main__":
    mcp.run()