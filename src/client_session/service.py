import uuid
from fastapi import WebSocket
from uvicorn.main import logger
from .exceptions import SessionErrorCode, SessionException
from .repository import SessionRepository

from .client import SpringSessionClient


class ClientSessionService:
    def __init__(self, repository: SessionRepository, spring_client: SpringSessionClient):
        self.repository = repository
        self.spring_client = spring_client

    async def create_session(self, ws: WebSocket):
        session_id = uuid.uuid4().hex
        try:
            self.repository.create_session(session_id, ws)
            return session_id
        except SessionException as e:
            logger.error(f"[ClientSessionService] {e.code.value}: {e.original_exception}", exc_info=True)
            raise SessionException(SessionErrorCode.SESSION_SERVICE_ERROR, e)
        except Exception as e:
            logger.error(f"[ClientSessionService]: {e}", exc_info=True)
            raise SessionException(SessionErrorCode.SESSION_SERVICE_ERROR, e)
            
    async def remove_session(self, session_id: str):
        spring_ws = self.repository.get_user_session(session_id)
        await self.spring_client.close(spring_ws)
        self.repository.remove_session(session_id)

    async def send_error(self, session_id: str, error: Exception):
        spring_ws = self.repository.get_user_session(session_id)
        await self.spring_client.send_error(spring_ws, error)