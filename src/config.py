import os
from typing import List
from dotenv import load_dotenv
from pydantic import BaseModel

class BaseSettings(BaseModel):
    app_name: str = "STT FastAPI Service"
    version: str = "1.0.0"
    api_v1_str: str = "/papi/v1"
    
    debug: bool = False
    environment: str = "base"
    host: str = "0.0.0.0"
    port: int = 8000
    log_level: str = "INFO"
    
    allowed_origins: List[str] = ["*"]
    allowed_methods: List[str] = ["*"]
    allowed_headers: List[str] = ["*"]
    
    class Config:
        case_sensitive = False


class LocalSettings(BaseSettings):
    debug: bool = True
    environment: str = "local"
    log_level: str = "DEBUG"
    host: str = "127.0.0.1"
    port: int = 8000
    
    allowed_origins: List[str] = ["*"]


class DevelopmentSettings(BaseSettings):
    debug: bool = True
    environment: str = "development"
    log_level: str = "DEBUG"
    host: str = "0.0.0.0"
    port: int = 8000
    
    allowed_origins: List[str] = ["*"]


class ProductionSettings(BaseSettings):
    debug: bool = False
    environment: str = "production"
    log_level: str = "INFO"
    host: str = "0.0.0.0"
    port: int = 8000
    
    allowed_origins: List[str] = []


def get_settings() -> BaseSettings:
    env = os.getenv("APP_ENV", "local").lower()
    
    # 환경별 .env 파일 로드
    env_file = f".env.{env}"
    if os.path.exists(env_file):
        load_dotenv(dotenv_path=env_file)
    
    # 환경에 따른 설정 클래스 반환
    if env == "prod":
        return ProductionSettings()
    elif env == "dev":
        return DevelopmentSettings()
    elif env == "local":
        return LocalSettings()
    else:
        return LocalSettings()


settings = get_settings()