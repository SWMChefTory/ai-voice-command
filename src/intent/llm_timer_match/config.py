
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class AzureConfig(BaseSettings):
    api_key: str = Field(default="", alias="AZURE_OPENAI_API_KEY")
    endpoint: str = Field(default="", alias="AZURE_OPENAI_ENDPOINT")
    api_version: str = Field(default="", alias="AZURE_OPENAI_API_VERSION")
    model: str = Field(default="gpt-4.1", alias="AZURE_PRIMARY_MODEL")
    fallback_model: str = Field(default="gpt-4.1-mini", alias="AZURE_FALLBACK_MODEL")
    max_retries: int = 2

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        validate_assignment=True,
        extra="ignore",
    )

azure_config = AzureConfig()