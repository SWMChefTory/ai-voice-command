import httpx
from abc import ABC, abstractmethod
from src.user_session.recipe.config import recipe_config
from .models import RecipeStep
from .schema import RecipeStepsResponse
from uuid import UUID
from typing import List

class RecipeClient(ABC):
    @abstractmethod
    async def get_recipe_steps(self, recipe_id: UUID) -> List[RecipeStep]:
        pass

class RecipeCheftoryClient(RecipeClient):
    def __init__(self):
        self.api_base = recipe_config.api_base

    async def get_recipe_steps(self, recipe_id: UUID) -> List[RecipeStep]:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.api_base}/papi/v1/recipes/{recipe_id}/steps")
            response.raise_for_status()
            recipe_step_response = RecipeStepsResponse.model_validate(response.json())
            return [RecipeStep.from_response(step) for step in recipe_step_response.steps]