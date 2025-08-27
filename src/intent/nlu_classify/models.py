from enum import Enum

class NLUIntentLabel(str, Enum):
    NEXT = "NEXT"
    PREV = "PREV"
    TIMER_SET = "TIMER SET"
    TIMER_STOP = "TIMER STOP"
    TIMER_CHECK = "TIMER CHECK"
    EXTRA = "EXTRA"
    WRONG = "WRONG"

class NLUIntentResult:
    def __init__(self, raw_label: str):
        try:
            self.label = NLUIntentLabel(raw_label)
        except ValueError:
            self.label = NLUIntentLabel.WRONG

    def as_string(self) -> str:
        return self.label.value