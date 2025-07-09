from fastapi import WebSocket
from src.exceptions import VoiceCommandErrorCode, VoiceCommandException
from src.intent.service import IntentService
from src.user_session.service import UserSessionService
from src.stt.service import STTService


class VoiceCommandService:
    def __init__(self, stt_service: STTService, user_session_service: UserSessionService, intent_service: IntentService):
        self.stt_service = stt_service
        self.user_session_service = user_session_service
        self.intent_service = intent_service

    async def start_session(self, client_websocket: WebSocket):
        session_id = await self.user_session_service.create(client_websocket)
        try:
            await self.stt_service.connect(session_id)
        except Exception as e:
            await self.user_session_service.send_error(session_id, e)
            raise VoiceCommandException(VoiceCommandErrorCode.VOICE_COMMAND_SERVICE_ERROR, e)
        return session_id

    async def stream_audio(self, session_id: str, chunk: bytes):
        try:
            await self.stt_service.stream_audio(session_id, chunk)
        except Exception as e:
            await self.user_session_service.send_error(session_id, e)
            raise VoiceCommandException(VoiceCommandErrorCode.VOICE_COMMAND_SERVICE_ERROR, e)
    
    async def stream_intents(self, session_id: str):
        try:
            async for stt_result in self.stt_service.get_result(session_id):
                intent = await self.intent_service.analyze(session_id, stt_result)
                await self.intent_service.send_result(session_id, intent)
        except VoiceCommandException as e:
            await self.user_session_service.send_error(session_id, e)
            raise VoiceCommandException(VoiceCommandErrorCode.VOICE_COMMAND_SERVICE_ERROR, e)
        except Exception as e:
            await self.user_session_service.send_error(session_id, e)
            raise VoiceCommandException(VoiceCommandErrorCode.VOICE_COMMAND_SERVICE_ERROR, e)

    async def end_session(self, session_id: str):
        await self.user_session_service.remove(session_id)
        await self.stt_service.disconnect(session_id)