from pydantic import BaseModel
from typing import List
from uuid import UUID

class SegmentResponse(BaseModel):
    start: float
    end: float
    text: str

class RecipeCaptionsResponse(BaseModel):
    lang_code: str
    captions: List[SegmentResponse]

class RecipeStepResponse(BaseModel):
    id: UUID
    step_order: int
    subtitle: str
    details: List[str]
    start: float
    end: float

class RecipeStepsResponse(BaseModel):
    steps: List[RecipeStepResponse]