import json
import os
import time
import smtplib
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from dateutil import parser as dateparser
from groq import Groq

client = Groq()

tools = [
    {
        "type": "function",
        "function": {
            "name": "schedule_email",
            "description": "Schedule an email to be sent at a specific time",
            "parameters": {
                "type": "object",
                "properties": {
                    "to": {"type": "string", "description": "Recipient email address"},
                    "send_time": {"type": "string", "description": "Time to send, e.g. '17:00', '5pm', or 'now'"},
                    "body": {"type": "string", "description": "The email message content"}
                },
                "required": ["to", "send_time", "body"]
            }
        }
    }
]

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

    print(f"Email sent to {to} at {datetime.now().strftime('%H:%M:%S')}")

def resolve_send_time(send_time_str):
    """Turn whatever the model gave us into an actual future datetime."""
    now = datetime.now()

    if send_time_str.strip().lower() == "now":
        return now

    target_time = dateparser.parse(send_time_str, fuzzy=True)

    # dateutil defaults to today's date if none given — but if that
    # time has already passed today, assume they mean tomorrow.
    target_time = target_time.replace(year=now.year, month=now.month, day=now.day)
    if target_time <= now:
        target_time += timedelta(days=1)

    return target_time

def schedule_email(to, send_time, body):
    target = resolve_send_time(send_time)
    now = datetime.now()
    delay_seconds = (target - now).total_seconds()

    print(f"Email to {to} scheduled for {target.strftime('%H:%M:%S')} "
          f"(waiting {int(delay_seconds)} seconds)")

    if delay_seconds > 0:
        time.sleep(delay_seconds)

    send_email(to, body)

user_message = "Schedule an email to usama.aslam@nayatel.com to be sent at 5pm. The message body should say: Hello Sir, if you are reading this message, congrats, my code worked! I will see you at 4:59:59 :)"
response = client.chat.completions.create(
    model="openai/gpt-oss-120b",
    messages=[{"role": "user", "content": user_message}],
    tools=tools
)

message = response.choices[0].message

if message.tool_calls:
    for call in message.tool_calls:
        args = json.loads(call.function.arguments)
        print("Tool called:", call.function.name)
        print("Arguments:", args)
        schedule_email(to=args["to"], send_time=args["send_time"], body=args["body"])
else:
    print("No tool was called. Model said:", message.content)