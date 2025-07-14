import os
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class AzureConfig(BaseSettings):
    api_key: str = Field(default="", alias="AZURE_OPENAI_API_KEY")
    endpoint: str = Field(default="", alias="AZURE_OPENAI_ENDPOINT")
    api_version: str = Field(default="", alias="AZURE_OPENAI_API_VERSION")
    model: str = "gpt-4.1"

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        validate_assignment=True,
        extra="ignore",
    )

azure_config = AzureConfig()