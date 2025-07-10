from abc import ABC, abstractmethod
from typing import Dict
from websockets import ClientConnection

class STTSessionRepository(ABC):
    @abstractmethod
    def create_session(self, session_id: str, websocket: ClientConnection):
        pass
    
    @abstractmethod
    def remove_session(self, session_id: str):
        pass

    @abstractmethod
    def get_session(self, session_id: str) -> ClientConnection:
        pass

    @abstractmethod
    def is_session_exists(self, session_id: str) -> bool:
        pass


class STTSessionRepositoryImpl(STTSessionRepository):
    def __init__(self):
        self.sessions : Dict[str, ClientConnection] = {}

    def create_session(self, session_id: str, websocket: ClientConnection):
        self.sessions[session_id] = websocket

    def remove_session(self, session_id: str):
        self.sessions.pop(session_id, None)

    def is_session_exists(self, session_id: str) -> bool:
        return session_id in self.sessions
    
    def get_session(self, session_id: str) -> ClientConnection:
        return self.sessions[session_id]

