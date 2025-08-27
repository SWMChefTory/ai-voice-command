from enum import Enum
from typing import Optional

class TimerIntentLabel(str, Enum):
   TIMER_START = "TIMER START"
   TIMER_STOP = "TIMER STOP"
   TIMER_CHECK = "TIMER CHECK"
   TIMER_SET = "TIMER SET"
   EXTRA = "EXTRA"
   ERROR = "ERROR"

class TimerIntentResult:
   def __init__(self, raw_label: str, duration: Optional[int] = None):
       self.label: TimerIntentLabel
       self.duration: Optional[int] = None
       
       if raw_label == TimerIntentLabel.TIMER_SET:
           if duration is not None and duration >= 1:
               self.label = TimerIntentLabel.TIMER_SET
               self.duration = duration
               return
           else:
               self.label = TimerIntentLabel.ERROR
               return
       
       try:
           self.label = TimerIntentLabel(raw_label)
       except ValueError:
           self.label = TimerIntentLabel.ERROR
   
   def as_string(self) -> str:
       if self.label == TimerIntentLabel.TIMER_SET and self.duration is not None:
           return f"{self.label.value} {self.duration}"
       return self.label.value