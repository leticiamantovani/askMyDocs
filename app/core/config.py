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
    conversation_history_window: int = 20

    @property
    def allowed_origins(self) -> list[str]:
        """CORS origins: local dev plus every URL in FRONTEND_URL.

        FRONTEND_URL accepts a comma-separated list (prod + preview deploys).
        Trailing slashes are stripped because the browser's Origin header
        never has one, and CORSMiddleware compares the strings exactly.
        """
        configured = [u.strip().rstrip("/") for u in self.frontend_url.split(",")]
        origins = ["http://localhost:5173", *filter(None, configured)]
        return list(dict.fromkeys(origins))


settings = Settings()