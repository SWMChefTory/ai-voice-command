import logging
from fastapi import WebSocket
from fastapi.websockets import WebSocketState
from src.exceptions import BusinessException
from src.schemas import BusinessErrorResponse, IntervalErrorResponse


logger = logging.getLogger(__name__)

class SpringSessionClient:
    async def close(self, ws: WebSocket):
        try:
            logger.info(f"[SpringSessionClient] 세션 {ws.client} 연결 상태: {ws.state}")
            if ws.state != WebSocketState.CONNECTED:
                return
            
            logger.info(f"[SpringSessionClient] 세션 {ws.client} 연결이 끊어졌습니다.")
            await ws.close()
        except Exception as e:
            logger.error(f"[SpringSessionClient] 세션 {ws.client} 연결 종료 실패: {e}", exc_info=True)

    async def send_error(self, ws: WebSocket, error: Exception):
        if isinstance(error, BusinessException):
            await ws.send_json(BusinessErrorResponse(error).model_dump())
        else:
            await ws.send_json(IntervalErrorResponse(error).model_dump())