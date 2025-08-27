from enum import Enum
from typing import Optional


class ClassifyIntentLabel(str, Enum):
    NEXT = "NEXT"
    PREV = "PREV"
    STEP = "STEP"
    TIMESTAMP = "TIMESTAMP"
    TIMER = "TIMER"
    EXTRA = "EXTRA"
    ERROR = "ERROR"

class IntentResult:
    def __init__(self, raw: str):
        self.label: ClassifyIntentLabel
        self.step: Optional[int] = None

        if not raw:
            self.label = ClassifyIntentLabel.ERROR
            return

        if raw.startswith("STEP"):
            parts = raw.split()
            if len(parts) == 2 and parts[1].isdigit():
                self.label = ClassifyIntentLabel.STEP
                self.step = int(parts[1])
                return

        try:
            self.label = ClassifyIntentLabel(raw)
        except ValueError:
            self.label = ClassifyIntentLabel.ERROR
    def as_string(self) -> str:
        """STEP은 'STEP n', 나머지는 Enum value로 반환"""
        if self.label == ClassifyIntentLabel.STEP and self.step is not None:
            return f"STEP {self.step}"
        return self.label.value
