import smtplib, os
from email.message import EmailMessage
from Blueprint_app.models import User

def send_notification(user_id, subject, message):
    user = User.query.get(user_id)
    if not user or not user.notifications_enabled or not user.notification_email:
        return False
    msg = EmailMessage()
    msg.set_content(message)
    msg['Subject'] = subject
    msg['From'] = 'no-reply@example.com'
    msg['To'] = user.notification_email
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as s:
            sender_mail = os.getenv('EMAIL_USER', '')
            sender_pass = os.getenv('EMAIL_PASS', '')
            s.login(sender_mail, sender_pass)
            s.send_message(msg)
        return True
    except Exception:
        return False
