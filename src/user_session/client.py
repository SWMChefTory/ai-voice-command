from abc import ABC, abstractmethod
from fastapi import WebSocket
from fastapi.websockets import WebSocketState
from uvicorn.main import logger
from src.exceptions import BusinessException
from src.intent.models import Intent
from .schemas import UserSessionResponse
from src.schemas import BusinessErrorResponse, IntervalErrorResponse, SuccessResponse

class UserSessionClient(ABC):

    @abstractmethod
    async def close_session(self, client_websocket: WebSocket):
        pass

    @abstractmethod
    async def send_error(self, client_websocket: WebSocket, error: Exception):
        pass

    @abstractmethod
    async def send_result(self, client_websocket: WebSocket, result: Intent, start: int, end: int):
        pass

class UserSessionClientImpl(UserSessionClient):
    async def close_session(self, client_websocket: WebSocket):
        try:
            if client_websocket.client_state != WebSocketState.CONNECTED:
                return
            
            logger.info(f"[SpringSessionClient] 세션 {client_websocket.client} 연결이 끊어졌습니다.")
            await client_websocket.close()
        except Exception as e:
            logger.error(f"[SpringSessionClient] 세션 {client_websocket.client} 연결 종료 실패: {e}", exc_info=True)

    async def send_error(self, client_websocket: WebSocket, error: Exception):
        if isinstance(error, BusinessException):
            await client_websocket.send_json(BusinessErrorResponse(error).model_dump())
        else:
            await client_websocket.send_json(IntervalErrorResponse(error).model_dump())
            
    async def send_result(self, client_websocket: WebSocket, result : Intent, start: int, end: int):
        response = UserSessionResponse.from_result(result, start, end)
        await client_websocket.send_json(SuccessResponse(response).model_dump())