from textwrap import dedent
from typing import List
from src.user_session.recipe.schema import RecipeStepResponse, SegmentResponse

class RecipeStep:
    def __init__(self, id: str, step: int, subtitle: str, start_time: float, end_time: float, details: List[str]):
        self.id = id
        self.step = step
        self.subtitle = subtitle
        self.start_time = start_time
        self.end_time = end_time
        self.details = details
        self.content = "\n".join(details)

    def __str__(self):
        return dedent(f"""\
            step {self.step}
            subtitle: {self.subtitle}
            timeline: {self._format_time(self.start_time)} → {self._format_time(self.end_time)}
            content: {self.content}
        """)

    def _format_time(self, seconds: float) -> str:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f'{hours:02d}:{minutes:02d}:{secs:02d}'

    @classmethod
    def from_response(cls, response: RecipeStepResponse) -> 'RecipeStep':
        return cls(
            id=str(response.id),
            step=response.step_order,
            subtitle=response.subtitle,
            start_time=response.start,
            end_time=response.end,
            details=response.details
        )

class RecipeCaption:
    def __init__(self, start: float, end: float, text: str):
        self.start = start
        self.end = end
        self.text = text

    def __str__(self):
        return dedent(f"""\
            timeline: {self._format_time(self.start)} → {self._format_time(self.end)}
            content: {self.text.replace("\n", " ")}
        """)

    def _format_time(self, seconds: float) -> str:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f'{hours:02d}:{minutes:02d}:{secs:02d}'
    
    @classmethod
    def from_response(cls, response: SegmentResponse) -> 'RecipeCaption':
        return cls(response.start, response.end, response.text)