from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn

# FastAPI 인스턴스 생성
app = FastAPI(
    title="My FastAPI App",
    description="FastAPI 초기 설정 예제",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 개발 환경에서만 사용, 프로덕션에서는 구체적인 도메인 지정
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic 모델 정의
class Item(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    is_available: bool = True

class User(BaseModel):
    id: int
    name: str
    email: str

# 기본 라우트
@app.get("/")
async def read_root():
    return {"message": "Hello World!", "status": "FastAPI is running"}

# 헬스 체크 엔드포인트
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# 아이템 관련 엔드포인트
@app.get("/items/{item_id}")
async def read_item(item_id: int, q: Optional[str] = None):
    return {"item_id": item_id, "q": q}

@app.post("/items/")
async def create_item(item: Item):
    return {"message": "Item created successfully", "item": item}

# 사용자 관련 엔드포인트
@app.get("/users/{user_id}")
async def read_user(user_id: int):
    return {"user_id": user_id, "name": f"User {user_id}"}

@app.post("/users/")
async def create_user(user: User):
    return {"message": "User created successfully", "user": user}

# 개발 환경에서 직접 실행할 때 사용
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 