from fastapi import WebSocket
from src.exceptions import VoiceCommandErrorCode, VoiceCommandException
from src.intent.service import IntentService
from src.client_session.service import ClientSessionService
from src.stt.service import STTService


class VoiceCommandService:
    def __init__(self, stt_service: STTService, client_session_service: ClientSessionService, intent_service: IntentService):
        self.stt_service = stt_service
        self.client_session_service = client_session_service
        self.intent_service = intent_service

    async def create_session(self, websocket: WebSocket):
        session_id = await self.client_session_service.create_session(websocket)
        try:
            await self.stt_service.connect(session_id)
        except Exception as e:
            await self.client_session_service.send_error(session_id, e)
            raise VoiceCommandException(VoiceCommandErrorCode.VOICE_COMMAND_SERVICE_ERROR, e)
        return session_id

    async def create_recognition(self, session_id: str, chunk: bytes):
        try:
            await self.stt_service.stream_audio_chunk(session_id, chunk)
        except Exception as e:
            await self.client_session_service.send_error(session_id, e)
            raise VoiceCommandException(VoiceCommandErrorCode.VOICE_COMMAND_SERVICE_ERROR, e)
    
    async def create_intent(self, session_id: str):
        try:
            async for stt_result in self.stt_service.get_result(session_id):
                intent = await self.intent_service.get_intent(session_id, stt_result)
                await self.intent_service.send_intent(session_id, intent, stt_result)
        except VoiceCommandException as e:
            await self.client_session_service.send_error(session_id, e)
            raise VoiceCommandException(VoiceCommandErrorCode.VOICE_COMMAND_SERVICE_ERROR, e)
        except Exception as e:
            await self.client_session_service.send_error(session_id, e)
            raise VoiceCommandException(VoiceCommandErrorCode.VOICE_COMMAND_SERVICE_ERROR, e)

    async def disconnect(self, session_id: str):
        await self.client_session_service.remove_session(session_id)
        await self.stt_service.disconnect(session_id)