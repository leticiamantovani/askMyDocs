from sqlalchemy import Column, DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4

from app.db.session import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    reset_token = Column(String, nullable=True)
    reset_token_expires = Column(DateTime, nullable=True)
