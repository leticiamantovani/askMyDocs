from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db
from app.services.email_service import send_bug_report_email

router = APIRouter(prefix="/feedback", tags=["feedback"])


class BugReportRequest(BaseModel):
    title: str
    description: str


@router.post("/bug", status_code=204)
async def report_bug(
    body: BugReportRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    reporter_email = "anonymous"
    reporter_name = "Anonymous"

    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        try:
            from app.services.auth_service import decode_token, get_user_by_id
            user_id = decode_token(auth_header.removeprefix("Bearer ").strip())
            user = await get_user_by_id(user_id, db)
            reporter_email = user.email
            reporter_name = user.name or user.email
        except Exception:
            pass

    send_bug_report_email(
        reporter_email=reporter_email,
        reporter_name=reporter_name,
        title=body.title,
        description=body.description,
    )
