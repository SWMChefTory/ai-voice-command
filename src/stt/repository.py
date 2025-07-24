from abc import ABC, abstractmethod
from typing import Any, Dict
from uuid import UUID
class STTSessionRepository(ABC):
    @abstractmethod
    def create_session(self, session_id: UUID, connection: Any):
        pass
    
    @abstractmethod
    def remove_session(self, session_id: UUID):
        pass

    @abstractmethod
    def get_session(self, session_id: UUID) -> Any:
        pass

    @abstractmethod
    def is_session_exists(self, session_id: UUID) -> bool:
        pass


class STTSessionRepositoryImpl(STTSessionRepository):
    def __init__(self):
        self.sessions : Dict[UUID, Any] = {}

    def create_session(self, session_id: UUID, connection: Any):
        self.sessions[session_id] = connection

    def remove_session(self, session_id: UUID):
        self.sessions.pop(session_id, None)

    def is_session_exists(self, session_id: UUID) -> bool:
        return session_id in self.sessions
    
    def get_session(self, session_id: UUID) -> Any:
        return self.sessions[session_id]

