import pytest

from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


def test_password_hashing():
    password = "TestPassword123"

    hashed_password = hash_password(password)

    assert hashed_password != password
    assert verify_password(password, hashed_password)


def test_wrong_password_fails():
    password = "TestPassword123"
    wrong_password = "wrongpassword"

    hashed_password = hash_password(password)

    assert not verify_password(wrong_password, hashed_password)


def test_create_access_token():
    token = create_access_token("1")

    assert isinstance(token, str)
    assert len(token) > 0


def test_decode_access_token():
    token = create_access_token("1")

    payload = decode_access_token(token)

    assert payload["sub"] == "1"
    assert "exp" in payload


def test_invalid_access_token():
    invalid_token = "invalid.token.value"

    with pytest.raises(ValueError, match="Invalid or expired token"):
        decode_access_token(invalid_token)
