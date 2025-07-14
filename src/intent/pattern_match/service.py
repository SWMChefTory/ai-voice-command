from typing import Optional
import re

_NAV_PATTERNS = {
    re.compile(r"(다음(\s*단계)?|계속|넘어가|그\s*다음)"): "NEXT",
    re.compile(r"(이전|뒤로|돌아가|되돌려|전\s*단계)"): "PREV",
}


class IntentPatternMatchService:
    def __init__(self):
        pass

    def match_intent(self, text: str) -> Optional[str]:
        text = text.lower()
        for rx, label in _NAV_PATTERNS.items():
            if rx.search(text):
                return label
        return None