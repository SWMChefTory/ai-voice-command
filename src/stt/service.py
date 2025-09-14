from typing import AsyncIterator, Dict
from uuid import UUID
from uvicorn.main import logger
import websockets
from src.stt.client import NaverClovaStreamingClient, OpenAIStreamingClient, STTClient, VitoStreamingClient
from src.enums import STTProvider

from src.stt.exceptions import STTErrorCode, STTException
from src.stt.repository import STTSessionRepository 


class STTService:
    def __init__(self, repository: STTSessionRepository, naver_clova_client: NaverClovaStreamingClient, openai_client: OpenAIStreamingClient, vito_client: VitoStreamingClient):
        self.repository = repository
        self.clients: Dict[STTProvider, STTClient] = {
            STTProvider.CLOVA: naver_clova_client,
            STTProvider.OPENAI: openai_client,
            STTProvider.VITO: vito_client,
        }

    async def add(self, session_id: UUID, provider: STTProvider):
        stt_connection = await self.clients[provider].connect_session()
        self.repository.add_session(session_id, stt_connection)

    async def send(self, session_id: UUID, chunk: bytes, provider: STTProvider, is_final: bool = False):
        try:
            if not self.repository.is_session_exists(session_id):
                logger.info(f"[STTService] 세션 {session_id}이 연결되지 않았거나 종료됨. 재연결 시도.")
                stt_connection = await self.clients[provider].connect_session()
                self.repository.add_session(session_id, stt_connection)

            stt_connection = self.repository.get_session(session_id)
            await self.clients[provider].send_chunk(stt_connection, chunk, is_final)
            
        except STTException:
            raise STTException(STTErrorCode.STT_SERVICE_ERROR)

        except Exception:
            raise STTException(STTErrorCode.STT_SERVICE_ERROR)

    async def remove(self, session_id: UUID, provider: STTProvider):
        if self.repository.is_session_exists(session_id):
            stt_connection = self.repository.get_session(session_id)
            await self.clients[provider].close_session(stt_connection)
            self.repository.remove_session(session_id)
    
    async def receive(self, session_id: UUID, provider: STTProvider) -> AsyncIterator[str]:
        if self.repository.is_session_exists(session_id):
            stt_connection = self.repository.get_session(session_id)
            try:
                async for text in self.clients[provider].receive_result(stt_connection):
                    logger.info(f"[STTService]: 음성 인식 결과: {text}")
                    yield text
            except websockets.ConnectionClosed:
                logger.info(f"[STTService]: 세션 {session_id} 연결이 끊어졌습니다.")