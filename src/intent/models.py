from enum import Enum
from textwrap import dedent
import re

class Intent:
    def __init__(self, intent: str, base_intent: str):
        self.intent = self._validate_intent(intent)
        self.base_intent = base_intent

    def _validate_intent(self, intent: str) -> str:
        if intent in ["NEXT", "PREV", "EXTRA"]:
            return intent
        elif intent.startswith("STEP") or intent.startswith("TIMESTAMP"):
            return intent
        else:
            return "EXTRA"
    


class RecipeStep:
    def __init__(self, step: int, start_time: int, end_time: int, content: str):
        self.step = step
        self.start_time = start_time
        self.end_time = end_time
        self.content = content

    def __str__(self):
        return dedent(f"""\
            step {self.step}
            timeline: {self._format_time(self.start_time)} → {self._format_time(self.end_time)}
            content: {self.content}
        """)

    def _format_time(self, seconds: int) -> str:
        hours  = seconds//3600
        minutes = (seconds%3600)//60
        seconds = (seconds%60)
        return f'{hours}:{minutes}:{seconds}'

class RecipeCaption:
    def __init__(self, start: int, end: int, text: str):
        self.start = start
        self.end = end
        self.text = text

    def __str__(self):
        return dedent(f"""\
            timeline: {self._format_time(self.start)} → {self._format_time(self.end)}
            content: {self.text.replace("\n", " ")}
        """)

    def _format_time(self, seconds: int) -> str:
        hours  = seconds//3600
        minutes = (seconds%3600)//60
        seconds = (seconds%60)
        return f'{hours}:{minutes}:{seconds}'