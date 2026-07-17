import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
from config import settings


def _build_reminder_html(client_name: str, session_title: str, start_time: datetime, location: str) -> str:
    time_str = start_time.strftime("%H:%M")
    date_str = start_time.strftime("%d/%m/%Y")
    loc = location or ""
    return f"""
    <div dir="rtl" style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; padding: 24px; border: 1px solid #e0e0e0; border-radius: 8px;">
        <h2 style="color: #6c63ff;">תזכורת לשיעור מחר 💪</h2>
        <p>שלום <strong>{client_name}</strong>,</p>
        <p>רצינו להזכיר לך שיש לך שיעור מחר:</p>
        <table style="width:100%; border-collapse: collapse; margin: 16px 0;">
            <tr style="background: #f5f5f5;">
                <td style="padding: 10px; font-weight: bold;">שיעור</td>
                <td style="padding: 10px;">{session_title}</td>
            </tr>
            <tr>
                <td style="padding: 10px; font-weight: bold;">תאריך</td>
                <td style="padding: 10px;">{date_str}</td>
            </tr>
            <tr style="background: #f5f5f5;">
                <td style="padding: 10px; font-weight: bold;">שעה</td>
                <td style="padding: 10px;">{time_str}</td>
            </tr>
            {"<tr><td style='padding: 10px; font-weight: bold;'>מיקום</td><td style='padding: 10px;'>" + loc + "</td></tr>" if loc else ""}
        </table>
        <p style="color: #777; font-size: 13px;">מכון כושר לנשים 🌸</p>
    </div>
    """


def send_reminder_email(to_email: str, client_name: str, session_title: str, start_time: datetime, location: str = ""):
    if not settings.mail_username or not settings.mail_password:
        print(f"[EMAIL SKIP] No credentials configured. Would send to {to_email}")
        return

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"תזכורת לשיעור מחר: {session_title}"
    msg["From"] = f"{settings.mail_from_name} <{settings.mail_from}>"
    msg["To"] = to_email

    html = _build_reminder_html(client_name, session_title, start_time, location)
    msg.attach(MIMEText(html, "html", "utf-8"))

    try:
        with smtplib.SMTP(settings.mail_server, settings.mail_port) as server:
            server.starttls()
            server.login(settings.mail_username, settings.mail_password)
            server.sendmail(settings.mail_from, to_email, msg.as_string())
        print(f"[EMAIL OK] Sent reminder to {to_email}")
    except Exception as e:
        print(f"[EMAIL ERROR] Failed to send to {to_email}: {e}")
