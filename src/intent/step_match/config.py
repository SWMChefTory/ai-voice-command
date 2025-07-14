import os
from pydantic import BaseModel

class AzureConfig(BaseModel):
    api_key: str = os.getenv("AZURE_OPENAI_API_KEY") or ""
    endpoint: str = os.getenv("AZURE_OPENAI_ENDPOINT") or ""
    api_version: str = os.getenv("AZURE_OPENAI_API_VERSION") or ""
    model: str = os.getenv("AZURE_OPENAI_MODEL") or ""

azure_config = AzureConfig()