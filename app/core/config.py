import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    jwt_secret: str = os.getenv("JWT_SECRET", "change-me-in-production")
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24 * 7  # 7 days

    mailtrap_api_key: str = os.getenv("MAILTRAP_API_KEY", "")
    reset_token_expire_minutes: int = int(os.getenv("RESET_TOKEN_EXPIRE_MINUTES", "30"))
    frontend_url: str = os.getenv("FRONTEND_URL", "http://localhost:5173")
    bug_report_email: str = os.getenv("BUG_REPORT_EMAIL", "")


settings = Settings()