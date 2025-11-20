from enum import Enum
from typing import Optional

class LLMSegmentMatchLabel(str, Enum):
    TIMESTAMP = "TIMESTAMP"
    EXTRA = "EXTRA"
    ERROR = "ERROR"

class LLMSegmentMatchResult:
    def __init__(self, raw_label: str, timestamp: Optional[float] = None):
        self.label: LLMSegmentMatchLabel
        self.timestamp: Optional[float] = None

        if raw_label == LLMSegmentMatchLabel.TIMESTAMP.value:
            if timestamp is not None and timestamp >= 0:
                self.label = LLMSegmentMatchLabel.TIMESTAMP
                self.timestamp = timestamp
                return
            else:
                self.label = LLMSegmentMatchLabel.ERROR
                return

        if raw_label == LLMSegmentMatchLabel.EXTRA.value:
            self.label = LLMSegmentMatchLabel.EXTRA
            return

        self.label = LLMSegmentMatchLabel.ERROR

    def as_string(self) -> str:
        if self.label == LLMSegmentMatchLabel.TIMESTAMP and self.timestamp is not None:
            return f"{self.label.value} {self.timestamp}"
        return self.label.value