from typing import AsyncIterator
from uvicorn.main import logger
import websockets

from src.stt.client import VitoStreamingClient
from src.stt.exceptions import STTErrorCode, STTException
from src.stt.repository import STTSessionRepository


class STTService:
    def __init__(self, repository: STTSessionRepository, client: VitoStreamingClient):
        self.repository = repository
        self.client = client

    async def connect(self, session_id: str):
        try:
            ws : websockets.ClientConnection = await self.client.connect()
            self.repository.create_session(session_id, ws)
        except STTException as e:
            logger.error(f"[STTService] {e.code.value}: {e.original_exception}", exc_info=True)
            raise STTException(STTErrorCode.STT_SERVICE_ERROR, e)

    async def stream_audio_chunk(self, session_id: str, chunk: bytes):
        try:
            if not self.repository.is_session_exists(session_id):
                logger.info(f"[STTService] 세션 {session_id}이 연결되지 않았거나 종료됨. 재연결 시도.")
                ws = await self.client.connect()
                self.repository.create_session(session_id, ws)

            ws = self.repository.find_session(session_id)
            await self.client.send_chunk(ws, chunk)

        except STTException as e:
            logger.error(f"[STTService] {e.code.value}: {e.original_exception}", exc_info=True)
            raise STTException(STTErrorCode.STT_SERVICE_ERROR, e)

        except Exception as e:
            logger.error(f"[STTService]: {e}", exc_info=True)
            raise STTException(STTErrorCode.STT_SERVICE_ERROR, e)

    async def disconnect(self, session_id: str):
        if self.repository.is_session_exists(session_id):
            ws = self.repository.find_session(session_id)
            await self.client.close(ws)
            self.repository.remove_session(session_id)
    
    async def get_result(self, session_id: str) -> AsyncIterator[str]:
        if self.repository.is_session_exists(session_id):
            ws = self.repository.find_session(session_id)
            try:
                async for text in self.client.get_result(ws):
                    yield text
            except websockets.ConnectionClosed as e:
                logger.info(f"[STTService]: 세션 {session_id} 연결이 끊어졌습니다.")
            finally:
                await self.client.close(ws)
                self.repository.remove_session(session_id)