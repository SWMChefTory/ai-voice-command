import uuid
from fastapi import WebSocket
from uvicorn.main import logger
from .exceptions import SessionErrorCode, SessionException
from .repository import UserSessionRepository

from .client import UserSessionClient


class UserSessionService:
    def __init__(self, repository: UserSessionRepository, client: UserSessionClient):
        self.repository = repository
        self.client = client

    async def create(self, client_websocket: WebSocket):
        session_id = uuid.uuid4().hex
        try:
            self.repository.create_session(session_id, client_websocket)
            return session_id
        except SessionException as e:
            logger.error(f"[ClientSessionService] {e.code.value}: {e.original_exception}", exc_info=True)
            raise SessionException(SessionErrorCode.SESSION_SERVICE_ERROR, e)
        except Exception as e:
            logger.error(f"[ClientSessionService]: {e}", exc_info=True)
            raise SessionException(SessionErrorCode.SESSION_SERVICE_ERROR, e)
            
    async def remove(self, session_id: str):
        client_websocket = self.repository.get_user_session(session_id)
        await self.client.close(client_websocket)
        self.repository.remove_session(session_id)

    async def send_error(self, session_id: str, error: Exception):
        client_websocket = self.repository.get_user_session(session_id)
        await self.client.send_error(client_websocket, error)