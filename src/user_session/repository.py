from abc import ABC, abstractmethod
from typing import Dict
from fastapi import WebSocket

class UserSessionRepository(ABC):
    @abstractmethod
    def create_session(self, session_id: str, websocket: WebSocket):
        pass
    
    @abstractmethod
    def remove_session(self, session_id: str):
        pass

    @abstractmethod
    def get_user_session(self, session_id: str) -> WebSocket:
        pass

    @abstractmethod
    def is_session_exists(self, session_id: str) -> bool:
        pass

class UserSessionRepositoryImpl(UserSessionRepository):
    def __init__(self):
        self.sessions : Dict[str, WebSocket] = {}

    def create_session(self, session_id: str, websocket: WebSocket):
        self.sessions[session_id] = websocket

    def remove_session(self, session_id: str):
        self.sessions.pop(session_id, None)
    
    def get_user_session(self, session_id: str) -> WebSocket:
        return self.sessions[session_id]

    def is_session_exists(self, session_id: str) -> bool:
        return session_id in self.sessions
