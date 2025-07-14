from functools import lru_cache
import json
import pysrt

from src.intent.exceptions import _CaptionLoaderException, _StepsLoaderException, IntentErrorCode
from src.intent.models import RecipeCaption, RecipeStep

class CaptionLoader:
    def __init__(self):
        pass

    @lru_cache(maxsize=1)
    def load_caption(self) -> list[RecipeCaption]:
        try:
            subs = pysrt.open("assets/test.srt", encoding="utf-8")
            return [
                RecipeCaption(int(sub.start.ordinal / 1000), int(sub.end.ordinal / 1000), sub.text)
                for sub in subs
            ]
        except Exception as e:
            raise _CaptionLoaderException(IntentErrorCode.CAPTION_LOAD_ERROR, e)

class StepsLoader:
    def __init__(self):
        pass

    @lru_cache(maxsize=1)
    def load_steps(self) -> list[RecipeStep]:
        try:
            with open("assets/steps.json", "r") as steps_json:
                steps = json.load(steps_json)
                result = []
                for i in range(len(steps)):
                    # subtitle과 details를 조합해서 텍스트 생성
                    text_parts = [steps[i]["subtitle"]]
                    if "details" in steps[i] and steps[i]["details"]:
                        text_parts.extend(steps[i]["details"])
                    combined_text = " | ".join(text_parts)
                    
                    result.append(
                        RecipeStep(i, int(steps[i]["start"]), int(steps[i]["end"]), combined_text)
                    )
                return result
        except Exception as e:
            raise _StepsLoaderException(IntentErrorCode.STEPS_LOAD_ERROR, e)