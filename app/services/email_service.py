import mailtrap as mt

from app.core.config import settings


def send_password_reset_email(to_email: str, reset_link: str) -> None:
    mail = mt.Mail(
        sender=mt.Address(email="hello@demomailtrap.co", name="AskMyDocs"),
        to=[mt.Address(email=to_email)],
        subject="Reset your password",
        html=f"""
        <p>You requested a password reset.</p>
        <p>Click the link below to set a new password. The link expires in {settings.reset_token_expire_minutes} minutes.</p>
        <p><a href="{reset_link}">Reset password</a></p>
        <p>If you did not request this, you can safely ignore this email.</p>
        """,
    )

    client = mt.MailtrapClient(token=settings.mailtrap_api_key)
    client.send(mail)
