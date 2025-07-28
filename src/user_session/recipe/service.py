from src.user_session.recipe.client import RecipeClient
from src.user_session.recipe.models import RecipeCaption, RecipeStep
from typing import List
from uuid import UUID

class RecipeService:
    def __init__(self, client: RecipeClient):
        self.client = client

    async def get_recipe_caption(self, recipe_id: UUID) -> List[RecipeCaption]:
        return await self.client.get_recipe_caption(recipe_id)

    async def get_recipe_steps(self, recipe_id: UUID) -> List[RecipeStep]:
        return await self.client.get_recipe_steps(recipe_id)