from fastapi import WebSocket

from src.intent.models import Intent
from src.models import STTProvider
from .models import UserSession
from .repository import UserSessionRepository

from .client import UserSessionClient
from uuid import UUID
from .recipe.service import RecipeService

class UserSessionService:
    def __init__(self, repository: UserSessionRepository, client: UserSessionClient, recipe_service: RecipeService):
        self.repository = repository
        self.client = client
        self.recipe_service = recipe_service

    async def create(self,session_id: UUID, client_websocket: WebSocket, provider: STTProvider, user_id: UUID, recipe_id: UUID) -> UUID:
        recipe_captions = await self.recipe_service.get_recipe_caption(recipe_id)
        recipe_steps = await self.recipe_service.get_recipe_steps(recipe_id)
        user_session = UserSession(session_id, client_websocket, user_id, provider, recipe_captions, recipe_steps)
        self.repository.create_session(session_id, user_session)
        return session_id

    async def remove(self, session_id: UUID):
        if self.repository.is_session_exists(session_id):
            user_session = self.repository.get_user_session(session_id)
            await self.client.close_session(user_session.get_websocket())
            self.repository.remove_session(session_id)

    async def send_error(self, session_id: UUID, error: Exception):
        user_session = self.repository.get_user_session(session_id)
        await self.client.send_error(user_session.get_websocket(), error)

    async def send_result(self, session_id: UUID, result: Intent):
        user_session = self.repository.get_user_session(session_id)
        await self.client.send_result(user_session.get_websocket(), result)

    def get_session(self, session_id: UUID) -> UserSession:
        return self.repository.get_user_session(session_id)