import httpx
from abc import ABC, abstractmethod
from src.user_session.recipe.config import recipe_config
from .models import RecipeStep, RecipeIngredient
from .schema import RecipeStepsResponse, RecipeIngredientsResponse
from uuid import UUID
from typing import List
from src.context import country_code_ctx


class RecipeClient(ABC):
    @abstractmethod
    async def get_recipe_steps(self, recipe_id: UUID) -> List[RecipeStep]:
        pass

    @abstractmethod
    async def get_recipe_ingredients(self, recipe_id: UUID) -> List[RecipeIngredient]:
        pass

class RecipeCheftoryClient(RecipeClient):
    def __init__(self):
        self.api_base = recipe_config.api_base
        self.headers = {
            "X-Country-Code": "KR",
        }

    async def get_recipe_steps(self, recipe_id: UUID) -> List[RecipeStep]:
        headers = {
            "X-Country-Code": country_code_ctx.get(),
        }

        async with httpx.AsyncClient(headers=headers) as client:
            response = await client.get(f"{self.api_base}/papi/v1/recipes/{recipe_id}/steps")
            response.raise_for_status()
            recipe_step_response = RecipeStepsResponse.model_validate(response.json())
            return [RecipeStep.from_response(step) for step in recipe_step_response.steps]

    async def get_recipe_ingredients(self, recipe_id: UUID) -> List[RecipeIngredient]:

        headers = {
            "X-Country-Code": country_code_ctx.get(),
        }

        async with httpx.AsyncClient(headers=headers) as client:
            response = await client.get(f"{self.api_base}/papi/v1/recipes/{recipe_id}/ingredients")
            response.raise_for_status()
            recipe_ingredient_response = RecipeIngredientsResponse.model_validate(response.json())
            return [RecipeIngredient.from_response(ingredient) for ingredient in recipe_ingredient_response.ingredients]