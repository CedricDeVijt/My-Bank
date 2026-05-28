from datetime import UTC, datetime, timedelta
from hashlib import sha256
from typing import Any

import jwt
from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return str(password_hash.hash(password))


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bool(password_hash.verify(plain_password, hashed_password))


class TokenError(ValueError):
    pass


class TokenExpiredError(TokenError):
    pass


class InvalidTokenError(TokenError):
    pass


def _create_token(
    data: dict[str, Any],
    secret_key: str,
    expires_in: int,
    token_use: str,
    algorithm: str = "HS256",
) -> str:
    now = datetime.now(UTC)
    payload = {
        **data,
        "token_use": token_use,
        "iat": now,
        "exp": now + timedelta(seconds=expires_in),
    }
    return str(jwt.encode(payload, secret_key, algorithm=algorithm))


def create_access_token(
    data: dict[str, Any], secret_key: str, expires_in: int, algorithm: str = "HS256"
) -> str:
    return _create_token(
        data, secret_key, expires_in, token_use="access", algorithm=algorithm
    )


def create_refresh_token(
    data: dict[str, Any], secret_key: str, expires_in: int, algorithm: str = "HS256"
) -> str:
    return _create_token(
        data, secret_key, expires_in, token_use="refresh", algorithm=algorithm
    )


def hash_token(token: str) -> str:
    return sha256(token.encode("utf-8")).hexdigest()


def decode_token(
    token: str, secret_key: str, algorithm: str = "HS256"
) -> dict[str, Any]:
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        return payload
    except jwt.ExpiredSignatureError:
        raise TokenExpiredError("Token has expired") from None
    except jwt.InvalidTokenError:
        raise InvalidTokenError("Invalid token") from None
