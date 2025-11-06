from uuid import UUID
from fastapi import WebSocket
from src.intent.service import IntentService
from src.enums import STTProvider
from src.stt.service import STTService
from src.user_session.service import UserSessionService
from uuid import uuid4
from src.auth.service import AuthService
from src.client import VoiceCommandClient
from src.objectstore.service import ObjectStoreService
class VoiceCommandService:
    def __init__(self, stt_service: STTService, intent_service: IntentService, user_session_service: UserSessionService, auth_service: AuthService, voice_command_client: VoiceCommandClient, object_store_service: ObjectStoreService):
        self.stt_service = stt_service
        self.intent_service = intent_service
        self.user_session_service = user_session_service
        self.auth_service = auth_service
        self.voice_command_client = voice_command_client
        self.object_store_service = object_store_service
        
    async def validate_auth_token(self, auth_token: str) -> UUID:
        return await self.auth_service.validate_auth_token(auth_token)
    
    async def start_session(self, client_websocket: WebSocket, provider: STTProvider, user_id: UUID, recipe_id: UUID) -> UUID:
        session_id = uuid4()
        await self.user_session_service.add(session_id, client_websocket, provider, user_id, recipe_id)
        await self.stt_service.add(session_id, provider)
        return session_id
        
    async def stream_audio(self, session_id: UUID, chunk: bytes, is_final: bool):
        user_session = self.user_session_service.get_session(session_id)
        provider = user_session.get_stt_provider()
        
        user_session.get_audio_buffer().add_audio(chunk)
        #10초 160000샘플 이상 저장
        if user_session.get_audio_buffer().get_audio_sample_count() > 160000:
            audio = user_session.get_audio_buffer().pop_audio()
            await self.object_store_service.upload_audio(session_id, bytes(audio))
            
        await self.stt_service.send(session_id, chunk, provider, is_final)
    
    async def stream_intents(self, session_id: UUID):
        user_session = self.user_session_service.get_session(session_id)
        async for stt_result, start, end in self.stt_service.receive(session_id, user_session.get_stt_provider()):
            intent = await self.intent_service.analyze(stt_result, user_session.get_recipe_steps(), user_session.get_recipe_ingredients())
            await self.user_session_service.send_result(session_id, intent)
            await self.voice_command_client.send_result(user_session.get_stt_provider(), intent, user_session.get_user_id(), str(session_id), start, end)

    async def end_session(self, session_id: UUID):
        user_session = self.user_session_service.get_session(session_id)
        audio = user_session.get_audio_buffer().pop_audio()
        await self.object_store_service.upload_audio(session_id, bytes(audio))
        provider = user_session.get_stt_provider()
        await self.stt_service.remove(session_id, provider)
        await self.user_session_service.remove(session_id)