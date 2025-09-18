from enum import Enum

class NLUClassifyLabel(str, Enum):
    NEXT = "NEXT"
    PREV = "PREV"
    TIMER_SET = "TIMER SET"
    TIMER_STOP = "TIMER STOP"
    TIMER_CHECK = "TIMER CHECK"
    VIDEO_PLAY = "VIDEO PLAY"
    VIDEO_STOP = "VIDEO STOP"
    EXTRA = "EXTRA"
    WRONG = "WRONG"

class NLUClassifyResult:
    def __init__(self, raw_label: str):
        try:
            self.label = NLUClassifyLabel(raw_label)
        except ValueError:
            self.label = NLUClassifyLabel.WRONG

    def as_string(self) -> str:
        return self.label.value