import secrets
from datetime import datetime, timedelta, timezone

import bcrypt
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import DomainError
from app.db.models.users import User


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def create_access_token(user_id: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expire_minutes)
    return jwt.encode({"sub": user_id, "exp": expire}, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> str:
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        user_id: str | None = payload.get("sub")
        if user_id is None:
            raise DomainError("Invalid token", 401)
        return user_id
    except JWTError:
        raise DomainError("Invalid token", 401)


async def register_user(email: str, password: str, name: str, db: AsyncSession) -> User:
    result = await db.execute(select(User).where(User.email == email))
    if result.scalar_one_or_none():
        raise DomainError("Email already registered", 409)

    user = User(email=email, name=name, hashed_password=hash_password(password))
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def update_user(user_id: str, name: str, email: str, db: AsyncSession) -> User:
    from uuid import UUID
    result = await db.execute(select(User).where(User.id == UUID(user_id)))
    user = result.scalar_one_or_none()
    if not user:
        raise DomainError("User not found", 404)

    if email != user.email:
        existing = await db.execute(select(User).where(User.email == email))
        if existing.scalar_one_or_none():
            raise DomainError("Email already in use", 409)

    user.name = name
    user.email = email
    await db.commit()
    await db.refresh(user)
    return user


async def update_user_password(user_id: str, current_password: str, new_password: str, db: AsyncSession) -> None:
    from uuid import UUID
    result = await db.execute(select(User).where(User.id == UUID(user_id)))
    user = result.scalar_one_or_none()
    if not user:
        raise DomainError("User not found", 404)
    if not verify_password(current_password, user.hashed_password):
        raise DomainError("Current password is incorrect", 400)

    user.hashed_password = hash_password(new_password)
    await db.commit()


async def get_user_by_id(user_id: str, db: AsyncSession) -> User:
    from uuid import UUID
    result = await db.execute(select(User).where(User.id == UUID(user_id)))
    user = result.scalar_one_or_none()
    if not user:
        raise DomainError("User not found", 404)
    return user


async def login_user(email: str, password: str, db: AsyncSession) -> str:
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(password, user.hashed_password):
        raise DomainError("Invalid credentials", 401)

    return create_access_token(str(user.id))


async def request_password_reset(email: str, db: AsyncSession) -> str | None:
    """Returns the reset token if user exists, None otherwise (caller decides whether to send email)."""
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if not user:
        return None

    token = secrets.token_urlsafe(32)
    user.reset_token = token
    user.reset_token_expires = datetime.utcnow() + timedelta(minutes=settings.reset_token_expire_minutes)
    await db.commit()
    return token


async def reset_password(token: str, new_password: str, db: AsyncSession) -> None:
    result = await db.execute(select(User).where(User.reset_token == token))
    user = result.scalar_one_or_none()

    if not user or not user.reset_token_expires:
        raise DomainError("Invalid or expired reset token", 400)

    if datetime.utcnow() > user.reset_token_expires:
        raise DomainError("Invalid or expired reset token", 400)

    user.hashed_password = hash_password(new_password)
    user.reset_token = None
    user.reset_token_expires = None
    await db.commit()
