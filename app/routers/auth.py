from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.dependencies import get_db
from app.core.exceptions import DomainError
from app.core.dependencies import get_current_user_id
from app.schema.auth import ForgotPasswordRequest, LoginRequest, RegisterRequest, ResetPasswordRequest, TokenResponse, UserResponse
from app.services.auth_service import get_user_by_id, login_user, register_user, request_password_reset, reset_password
from app.services.email_service import send_password_reset_email

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", status_code=201)
async def register(body: RegisterRequest, db: AsyncSession = Depends(get_db)):
    user = await register_user(body.email, body.password, body.name, db)
    return {"id": str(user.id), "email": user.email, "name": user.name}


@router.get("/me", response_model=UserResponse)
async def me(user_id: str = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    user = await get_user_by_id(user_id, db)
    return UserResponse(id=str(user.id), email=user.email, name=user.name)


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    token = await login_user(body.email, body.password, db)
    return TokenResponse(access_token=token)


@router.post("/forgot-password", status_code=200)
async def forgot_password(body: ForgotPasswordRequest, db: AsyncSession = Depends(get_db)):
    token = await request_password_reset(body.email, db)
    if not token:
        raise DomainError("Email not found.", 404)

    reset_link = f"{settings.frontend_url}/reset-password?token={token}"
    send_password_reset_email(body.email, reset_link)
    return {"message": "Reset link sent to your email."}


@router.post("/reset-password", status_code=200)
async def do_reset_password(body: ResetPasswordRequest, db: AsyncSession = Depends(get_db)):
    await reset_password(body.token, body.new_password, db)
    return {"message": "Password updated successfully."}
