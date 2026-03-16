import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from uuid import uuid4


def send_via_smtp(sender: str, password: str, to_email: str, subject: str, body: str) -> tuple[str, str]:
    msg = MIMEMultipart()
    msg["From"] = sender
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain", "utf-8"))
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender, password)
        server.sendmail(sender, to_email, msg.as_string())
    message_id = uuid4().hex
    return message_id, ""
