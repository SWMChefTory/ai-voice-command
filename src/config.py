from typing import List
from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = "STT FastAPI Service"
    version: str = "1.0.0"
    debug: bool = True
    environment: str = "development"
    
    host: str = "0.0.0.0"
    port: int = 8000
    
    api_v1_str: str = "/api/v1"
    
    allowed_origins: List[str] = ["*"]
    allowed_methods: List[str] = ["*"]
    allowed_headers: List[str] = ["*"]
        
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings() 