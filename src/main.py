from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from src.config import get_settings, Settings
from src.router import router

def create_app() -> FastAPI:
    settings = get_settings()
    
    app = FastAPI(
        title=settings.app_name,
        description="WebSocket 기반 실시간 STT(Speech-to-Text) 서비스",
        version=settings.version,
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