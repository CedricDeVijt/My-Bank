from pydantic import BaseModel, ConfigDict, Field


class TokenResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    token_type: str = "Bearer"
    access_token: str
    refresh_token: str
    access_token_expires_in: int = Field(gt=0)
    refresh_token_expires_in: int = Field(gt=0)


class RefreshTokenRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    refresh_token: str = Field(min_length=16)


class LogoutRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    refresh_token: str = Field(min_length=16)
