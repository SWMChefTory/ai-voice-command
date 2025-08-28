from abc import ABC, abstractmethod
from uuid import UUID
from typing import Dict

from .exceptions import SessionException, SessionErrorCode
from .models import UserSession

class UserSessionRepository(ABC):
    @abstractmethod
    def add_session(self, session_id: UUID, user_session: UserSession):
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

    def add_session(self, session_id: UUID, user_session: UserSession):
        self.sessions[session_id] = user_session

    def remove_session(self, session_id: UUID):
        self.sessions.pop(session_id, None)
    
    def get_user_session(self, session_id: UUID) -> UserSession:
        if self.is_session_exists(session_id):
            return self.sessions[session_id]
        raise SessionException(SessionErrorCode.SESSION_NOT_FOUND)

    def is_session_exists(self, session_id: UUID) -> bool:
        return session_id in self.sessions