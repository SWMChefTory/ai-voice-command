from enum import Enum
from typing import Optional

class TimeIntentLabel(str, Enum):
    TIMESTAMP = "TIMESTAMP"
    EXTRA = "EXTRA"
    ERROR = "ERROR"

class TimeIntentResult:
    def __init__(self, raw_label: str, timestamp: Optional[int] = None):
        self.label: TimeIntentLabel
        self.timestamp: Optional[int] = None

        if raw_label == TimeIntentLabel.TIMESTAMP.value:
            if timestamp is not None and timestamp >= 0:
                self.label = TimeIntentLabel.TIMESTAMP
                self.timestamp = timestamp
                return
            else:
                self.label = TimeIntentLabel.ERROR
                return

        if raw_label == TimeIntentLabel.EXTRA.value:
            self.label = TimeIntentLabel.EXTRA
            return

        self.label = TimeIntentLabel.ERROR

    def as_string(self) -> str:
        if self.label == TimeIntentLabel.TIMESTAMP and self.timestamp is not None:
            return f"{self.label.value} {self.timestamp}"
        return self.label.value