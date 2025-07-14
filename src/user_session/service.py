import uuid
from fastapi import WebSocket

from src.intent.models import Intent
from .repository import UserSessionRepository

from .client import UserSessionClient


class UserSessionService:
    def __init__(self, repository: UserSessionRepository, client: UserSessionClient):
        self.repository = repository
        self.client = client

    async def create(self, client_websocket: WebSocket) -> str:
        session_id = uuid.uuid4().hex
        self.repository.create_session(session_id, client_websocket)
        return session_id

    async def remove(self, session_id: str):
        if self.repository.is_session_exists(session_id):
            client_websocket = self.repository.get_user_session(session_id)
            await self.client.close_session(client_websocket)
            self.repository.remove_session(session_id)

    async def send_error(self, session_id: str, error: Exception):
        client_websocket = self.repository.get_user_session(session_id)
        await self.client.send_error(client_websocket, error)

    async def send_result(self, session_id: str, result: Intent):
        client_websocket = self.repository.get_user_session(session_id)
        await self.client.send_result(client_websocket, result)