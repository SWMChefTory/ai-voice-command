from pydantic import BaseModel
from typing import List
from uuid import UUID


class RecipeStepDetailResponse(BaseModel):
    text: str
    start: float

class RecipeStepResponse(BaseModel):
    id: UUID
    step_order: int
    subtitle: str
    details: List[RecipeStepDetailResponse]
    start: float

class RecipeStepsResponse(BaseModel):
    steps: List[RecipeStepResponse]

class RecipeIngredientResponse(BaseModel):
    name: str
    unit: str
    amount: int

class RecipeIngredientsResponse(BaseModel):
    ingredients: List[RecipeIngredientResponse]