from functools import wraps
from fastapi import WebSocket
from src.exceptions import VoiceCommandException, VoiceCommandErrorCode
from src.intent.service import IntentService
from src.stt.service import STTService
from src.user_session.service import UserSessionService
from src.utils import voice_command_error

class VoiceCommandService:
    def __init__(self, stt_service: STTService, intent_service: IntentService, user_session_service: UserSessionService):
        self.stt_service = stt_service
        self.intent_service = intent_service
        self.user_session_service = user_session_service

    @voice_command_error
    async def start_session(self, client_websocket: WebSocket) -> str:
        session_id = await self.user_session_service.create(client_websocket)
        await self.stt_service.create(session_id)
        return session_id

    @voice_command_error
    async def stream_audio(self, session_id: str, chunk: bytes):
        await self.stt_service.send(session_id, chunk)
    
    @voice_command_error
    async def stream_intents(self, session_id: str):
        async for stt_result in self.stt_service.recieve(session_id):
            intent = await self.intent_service.analyze(stt_result)
            await self.user_session_service.send(session_id, intent)

    async def end_session(self, session_id: str):
        await self.stt_service.remove(session_id)
        await self.user_session_service.remove(session_id)