import pytest
from jose import jwt

from app.core.config import settings
from app.services.auth_service import (
    TokenData,
    create_access_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.core.exceptions import DomainError


def test_hash_and_verify_password():
    hashed = hash_password("secret123")
    assert verify_password("secret123", hashed)


def test_wrong_password_fails():
    hashed = hash_password("secret123")
    assert not verify_password("wrong", hashed)


def test_create_and_decode_token():
    token = create_access_token("user-id-123", "Alice")
    data = decode_token(token)
    assert data.id == "user-id-123"
    assert data.name == "Alice"


def test_decode_invalid_token_raises():
    with pytest.raises(DomainError) as exc_info:
        decode_token("not.a.valid.token")
    assert exc_info.value.status_code == 401


def test_decode_token_missing_sub_raises():
    token = jwt.encode({"name": "Alice"}, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    with pytest.raises(DomainError) as exc_info:
        decode_token(token)
    assert exc_info.value.status_code == 401
