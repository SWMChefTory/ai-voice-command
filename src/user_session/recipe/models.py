from textwrap import dedent
from typing import List
from src.user_session.recipe.schema import RecipeStepResponse, RecipeStepDetailResponse

class RecipeStepDetail:
    def __init__(self, start: float, text: str):
        self.start = start
        self.text = text

    def __str__(self):
            return f"{self._format_time(self.start)}: {self.text}"
    
    def _format_time(self, seconds: float) -> str:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f'{hours:02d}:{minutes:02d}:{secs:02d}'

    @classmethod
    def from_response(cls, response: RecipeStepDetailResponse) -> 'RecipeStepDetail':
        return cls(response.start, response.text)

class RecipeStep:
    def __init__(self, id: str, step: int, subtitle: str, start_time: float, details: List[RecipeStepDetail]):
        self.id = id
        self.step = step
        self.subtitle = subtitle
        self.start_time = start_time
        self.details = details

    def __str__(self):
        details_str = "\n  ".join([str(detail) for detail in self.details])
        return dedent(f"""\
            step {self.step}: {self.subtitle}
            details:
              {details_str}
        """)


    @classmethod
    def from_response(cls, response: RecipeStepResponse) -> 'RecipeStep':
        return cls(
            id=str(response.id),
            step=response.step_order,
            subtitle=response.subtitle,
            start_time=response.start,
            details=[RecipeStepDetail.from_response(detail) for detail in response.details]
        )
    
