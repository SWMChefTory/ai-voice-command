from uuid import UUID
from fastapi import WebSocket
from src.models import STTProvider

class UserSession:
    def __init__(self, session_id: UUID, websocket: WebSocket, user_id: UUID, provider: STTProvider):
        self.session_id = session_id
        self.websocket = websocket
        self.user_id = user_id
        self.stt_provider = provider    
    def get_session_id(self) -> UUID:
        return self.session_id

    def get_websocket(self) -> WebSocket:
        return self.websocket

    def get_user_id(self) -> UUID:
        return self.user_id
    
    def get_stt_provider(self) -> STTProvider:
        return self.stt_provider