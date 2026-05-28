from pathlib import Path

from pydantic import Field, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str = Field(..., alias="DATABASE_URL")

    jwt_secret_key: str = Field(..., alias="JWT_SECRET_KEY")
    jwt_algorithm: str = Field("HS256", alias="JWT_ALGORITHM")
    jwt_access_token_expires_in: int = Field(900, alias="JWT_ACCESS_TOKEN_EXPIRES_IN")
    jwt_refresh_token_expires_in: int = Field(
        2592000, alias="JWT_REFRESH_TOKEN_EXPIRES_IN"
    )


try:
    settings = Settings()  # type: ignore[call-arg]
except ValidationError as e:
    env_file = Path(".env")
    if not env_file.exists():
        raise FileNotFoundError(
            "Configuration Error: The required '.env' file was not found at "
            f"{env_file.resolve()}\n\n"
        ) from e
    else:
        raise
