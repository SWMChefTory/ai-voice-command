from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class AuthConfig(BaseSettings):
    api_base: str = Field(default="", alias="AUTH_API_BASE")

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        validate_assignment=True,
        extra="ignore",
    )

auth_config = AuthConfig()