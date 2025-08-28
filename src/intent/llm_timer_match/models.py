from enum import Enum
from typing import Optional

class LLMTimerMatchLabel(str, Enum):
   TIMER_START = "TIMER START"
   TIMER_STOP = "TIMER STOP"
   TIMER_CHECK = "TIMER CHECK"
   TIMER_SET = "TIMER SET"
   EXTRA = "EXTRA"
   ERROR = "ERROR"

class LLMTimerMatchResult:
   def __init__(self, raw_label: str, duration: Optional[int] = None):
       self.label: LLMTimerMatchLabel
       self.duration: Optional[int] = None
       
       if raw_label == LLMTimerMatchLabel.TIMER_SET:
           if duration is not None and duration >= 1:
               self.label = LLMTimerMatchLabel.TIMER_SET
               self.duration = duration
               return
           else:
               self.label = LLMTimerMatchLabel.ERROR
               return
       
       try:
           self.label = LLMTimerMatchLabel(raw_label)
       except ValueError:
           self.label = LLMTimerMatchLabel.ERROR
   
   def as_string(self) -> str:
       if self.label == LLMTimerMatchLabel.TIMER_SET and self.duration is not None:
           return f"{self.label.value} {self.duration}"
       return self.label.value