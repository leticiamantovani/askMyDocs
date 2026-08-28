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

    # Upload limits. Bytes bound the file; pages and chars bound what it
    # expands into, since a small compressed PDF can hold a huge text payload.
    max_pdf_bytes: int = int(os.getenv("MAX_PDF_BYTES", str(20 * 1024 * 1024)))
    max_pdf_pages: int = int(os.getenv("MAX_PDF_PAGES", "500"))
    max_pdf_chars: int = int(os.getenv("MAX_PDF_CHARS", str(2_000_000)))

    # Chunks embedded per round-trip; also the ceiling on indexing memory.
    index_batch_size: int = int(os.getenv("INDEX_BATCH_SIZE", "128"))

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