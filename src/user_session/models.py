from uuid import UUID
from fastapi import WebSocket
from src.models import STTProvider
from src.user_session.recipe.models import RecipeCaption, RecipeStep
from typing import List

class UserSession:
    def __init__(self, session_id: UUID, websocket: WebSocket, user_id: UUID, provider: STTProvider, recipe_captions: List[RecipeCaption], recipe_steps: List[RecipeStep]):
        self.session_id = session_id
        self.websocket = websocket
        self.user_id = user_id
        self.stt_provider = provider    
        self.recipe_captions = recipe_captions
        self.recipe_steps = recipe_steps
        
    def get_session_id(self) -> UUID:
        return self.session_id

    def get_websocket(self) -> WebSocket:
        return self.websocket

    def get_user_id(self) -> UUID:
        return self.user_id
    
    def get_stt_provider(self) -> STTProvider:
        return self.stt_provider
    
    def get_recipe_captions(self) -> List[RecipeCaption]:
        return self.recipe_captions
    
    def get_recipe_steps(self) -> List[RecipeStep]:
        return self.recipe_steps