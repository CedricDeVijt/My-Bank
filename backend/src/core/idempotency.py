import json
import uuid
from collections.abc import Callable
from functools import wraps
from typing import Any

from fastapi import Request
from sqlalchemy.orm import Session

from src.repositories import idempotency_key_repository


def idempotent(
    user_id_attr: str = "id",
    ttl_seconds: int = 3600,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Decorator to make an endpoint idempotent.

    Args:
        user_id_attr: The attribute name to extract user_id from current_user parameter
        ttl_seconds: Time-to-live for cached responses (default: 1 hour)

    Returns:
        Decorated function that handles idempotency
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Extract request and db from kwargs
            request: Request | None = kwargs.get("request")
            db: Session | None = kwargs.get("db")
            current_user = kwargs.get("current_user")

            if not request or not db:
                # If required dependencies are missing, just execute the function
                return func(*args, **kwargs)

            # Extract idempotency key from headers
            idempotency_key = request.headers.get("Idempotency-Key")

            if not idempotency_key:
                # If no idempotency key, just execute the function
                return func(*args, **kwargs)

            # For unauthenticated endpoints (like registration), use a hash of the
            # request path and key as the user identifier.
            if current_user:
                user_id: uuid.UUID = getattr(current_user, user_id_attr)
            else:
                # For unauthenticated endpoints, generate a deterministic UUID from
                # the path and key.
                import hashlib

                path_key = f"{request.method}:{request.url.path}"
                hash_obj = hashlib.sha256(path_key.encode())
                user_id = uuid.UUID(hash_obj.hexdigest()[:32])

            # Check if this request has already been processed
            existing = idempotency_key_repository.get_by_key(
                db=db,
                user_id=user_id,
                idempotency_key=idempotency_key,
                method=request.method,
                path=request.url.path,
            )

            if existing:
                # Return cached response
                from fastapi.responses import JSONResponse

                return JSONResponse(
                    content=json.loads(existing.response_data),
                    status_code=existing.status_code,
                )

            # Execute the function
            result = func(*args, **kwargs)

            # Cache the response
            try:
                # Serialize response data
                if hasattr(result, "model_dump"):
                    response_data = json.dumps(result.model_dump())
                elif isinstance(result, dict):
                    response_data = json.dumps(result)
                else:
                    response_data = json.dumps(result, default=str)

                status_code = 200  # Default status code
                # For POST requests, default to 201 (Created)
                if request.method == "POST":
                    status_code = 201

                idempotency_key_repository.create(
                    db=db,
                    user_id=user_id,
                    idempotency_key=idempotency_key,
                    method=request.method,
                    path=request.url.path,
                    response_data=response_data,
                    status_code=status_code,
                    ttl_seconds=ttl_seconds,
                )
                db.commit()
            except Exception:
                # If caching fails, don't crash the response
                pass

            return result

        return wrapper

    return decorator
