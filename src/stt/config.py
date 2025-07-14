import os
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

COMMAND_KEYWORDS = [
    "다음", "다음 단계", "넘어가", "계속",
    "이전", "전 단계", "뒤로",
]

class VitoConfig(BaseSettings):
    client_id: str = Field(default="", alias="RTZR_CLIENT_ID")
    client_secret: str = Field(default="", alias="RTZR_CLIENT_SECRET")
    api_base: str = "https://openapi.vito.ai"
    model_name: str = "sommers_ko"
    sample_rate: int = 16000
    encoding: str = "LINEAR16"
    use_itn: str = "false"
    use_disfluency_filter: str = "true"
    use_profanity_filter: str = "false"
    keywords: str = ",".join(COMMAND_KEYWORDS)
    keywords_boost: int = 16
    domain: str = "CALL"

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        validate_assignment=True,
        extra="ignore",
    )


vito_config = VitoConfig()