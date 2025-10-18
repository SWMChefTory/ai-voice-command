import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
import uvicorn

from src.config import get_settings, Settings
from src.router import router
from src.stt.client import NaverClovaStreamingClient

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("STT 서비스 시작")
    
    yield 
    
    print("STT 서비스 종료 중...")
    await NaverClovaStreamingClient.shutdown()
    print("STT 서비스 종료 완료")

def create_app() -> FastAPI:
    settings = get_settings()
    
    app = FastAPI(
        title=settings.app_name,
        description="WebSocket 기반 실시간 STT(Speech-to-Text) 서비스",
        version=settings.version,
        lifespan=lifespan
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=settings.allowed_methods,
        allow_headers=settings.allowed_headers,
    )

    app.include_router(router, prefix=settings.api_v1_str)
    
    return app

app = create_app()

class UvicornMetricsFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        request_line = getattr(record, "request_line", "")
        if isinstance(request_line, str) and " /metrics" in request_line:
            return False
        try:
            message = record.getMessage()
        except Exception:
            message = ""
        return "/metrics" not in message

logging.getLogger("uvicorn.access").addFilter(UvicornMetricsFilter())
Instrumentator().instrument(app).expose(app)
@app.get("/health")
async def health_check(settings: Settings = Depends(get_settings)):
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.version,
        "env": settings.env,
    }

if __name__ == "__main__":
    settings = get_settings()
    uvicorn.run(
        "src.main:app",
        reload=settings.debug,
        host=settings.host,
        port=settings.port,
    ) 