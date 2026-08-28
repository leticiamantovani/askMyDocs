import logging
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.routers import auth, chat, conversations, documents, feedback, upload
from app.core.config import settings
from app.core.exceptions import DomainError
from app.core.middleware import UploadSizeLimit

logger = logging.getLogger(__name__)

app = FastAPI()


@app.exception_handler(DomainError)
def domain_error_handler(_request: Request, exc: DomainError):
    return JSONResponse(status_code=exc.status_code, content={"detail": str(exc)})


@app.exception_handler(Exception)
def unhandled_exception_handler(_request: Request, exc: Exception):
    logger.exception("Unhandled exception", exc_info=exc)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(upload.router)
app.include_router(documents.router)
app.include_router(conversations.router)
app.include_router(feedback.router)


# The guard has to match the route's real path, so it is resolved from the app
# instead of hardcoded: a prefix added at include_router time would otherwise
# leave uploads silently unprotected. An unknown name raises NoMatchFound here,
# at import, rather than failing quietly at request time.
app.add_middleware(
    UploadSizeLimit,
    path=app.url_path_for("upload_pdf"),
    max_bytes=settings.max_pdf_bytes,
)

# CORS goes on last so it wraps everything, including the 413 above: without it
# the browser reports a CORS failure and the dropzone never sees why the upload
# was refused.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Conversation-ID"],
)
