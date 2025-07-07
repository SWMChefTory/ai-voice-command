from fastapi import WebSocket
from fastapi.websockets import WebSocketState
from uvicorn.main import logger
from src.exceptions import BusinessException
from src.schemas import BusinessErrorResponse, IntervalErrorResponse

class SpringSessionClient:
    async def close(self, client_websocket: WebSocket):
        try:
            logger.info(f"[SpringSessionClient] 세션 {client_websocket.client} 연결 상태: {client_websocket.state}")
            if client_websocket.state != WebSocketState.CONNECTED:
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