from abc import ABC, abstractmethod
from uuid import UUID
from typing import Dict
from fastapi import WebSocket
from src.models import STTProvider
from .models import UserSession

class UserSessionRepository(ABC):
    @abstractmethod
    def create_session(self, session_id: UUID, websocket: WebSocket, provider: STTProvider, user_id: UUID):
        pass

    @abstractmethod
    def remove_session(self, session_id: UUID):
        pass

    @abstractmethod
    def get_user_session(self, session_id: UUID) -> UserSession:
        pass

    @abstractmethod
    def is_session_exists(self, session_id: UUID) -> bool:
        pass

class UserSessionRepositoryImpl(UserSessionRepository):
    def __init__(self):
        self.sessions: Dict[UUID, UserSession] = {}

    def create_session(self, session_id: UUID, websocket: WebSocket, provider: STTProvider, user_id: UUID):
        self.sessions[session_id] = UserSession(session_id, websocket, user_id, provider)

    def remove_session(self, session_id: UUID):
        self.sessions.pop(session_id, None)
    
    def get_user_session(self, session_id: UUID) -> UserSession:
        if session_id not in self.sessions:
            raise KeyError(f"Session {session_id} not found")
        session = self.sessions[session_id]
        return session

    def is_session_exists(self, session_id: UUID) -> bool:
        return session_id in self.sessions