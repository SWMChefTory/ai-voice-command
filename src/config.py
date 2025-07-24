from typing import List
from enum import Enum
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from functools import lru_cache

class AppEnv(str, Enum):
    local = "local"
    dev   = "dev"
    prod  = "prod"


class VoiceCommandConfig(BaseSettings):
    api_base: str = Field(default="", alias="VOICE_COMMAND_API_BASE")

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        validate_assignment=True,
        extra="ignore",
    )

voice_command_config = VoiceCommandConfig()

class Settings(BaseSettings):
    app_name: str = "Voice Command FastAPI Service"
    version: str  = "1.0.0"
    api_v1_str: str = "/api/v1"

    env: AppEnv = Field(default=AppEnv.dev, alias="APP_ENV")
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000
    log_level: str = "INFO"

    allowed_origins: List[str] = Field(default_factory=lambda: ["*"])
    allowed_methods: List[str] = Field(default_factory=lambda: ["*"])
    allowed_headers: List[str] = Field(default_factory=lambda: ["*"])

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        validate_assignment=True,
        extra="ignore",
    )

    @property
    def is_prod(self) -> bool:
        return self.env is AppEnv.prod


@lru_cache()
def get_settings() -> Settings:
    s = Settings()
    
    # 환경별 오버라이드 예시
    if s.env is AppEnv.local:
        s.debug = True
        s.log_level = "DEBUG"
        s.host = "0.0.0.0"
    elif s.env is AppEnv.dev:
        s.debug = True
        s.log_level = "DEBUG"
    elif s.env is AppEnv.prod:
        s.allowed_origins = [] 

    return s