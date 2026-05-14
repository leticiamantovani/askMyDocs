import mailtrap as mt

from app.core.config import settings

SENDER = mt.Address(email="hello@demomailtrap.co", name="AskMyDocs")


def _client() -> mt.MailtrapClient:
    return mt.MailtrapClient(token=settings.mailtrap_api_key)


def send_password_reset_email(to_email: str, reset_link: str) -> None:
    mail = mt.Mail(
        sender=SENDER,
        to=[mt.Address(email=to_email)],
        subject="Reset your password",
        html=f"""
        <p>You requested a password reset.</p>
        <p>Click the link below to set a new password. The link expires in {settings.reset_token_expire_minutes} minutes.</p>
        <p><a href="{reset_link}">Reset password</a></p>
        <p>If you did not request this, you can safely ignore this email.</p>
        """,
    )
    _client().send(mail)


def send_bug_report_email(reporter_email: str, reporter_name: str, title: str, description: str) -> None:
    mail = mt.Mail(
        sender=SENDER,
        to=[mt.Address(email=settings.bug_report_email)],
        subject=f"[Bug Report] {title}",
        html=f"""
        <h2 style="margin:0 0 12px">Bug Report</h2>
        <p><strong>From:</strong> {reporter_name} ({reporter_email})</p>
        <p><strong>Title:</strong> {title}</p>
        <hr style="border:none;border-top:1px solid #eee;margin:12px 0"/>
        <p><strong>Description:</strong></p>
        <p style="white-space:pre-wrap">{description}</p>
        """,
    )
    _client().send(mail)
