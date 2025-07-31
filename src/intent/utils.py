from functools import lru_cache
import json
import pysrt # type: ignore
from uvicorn.main import logger

from src.intent.exceptions import CaptionLoaderException, StepsLoaderException, IntentErrorCode
from src.user_session.recipe.models import RecipeCaption, RecipeStep

class CaptionLoader:
    def __init__(self):
        pass

    @lru_cache(maxsize=1)
    def load_caption(self) -> list[RecipeCaption]:
        try:
            subs = pysrt.open("assets/test.srt", encoding="utf-8") # type: ignore
            return [
                RecipeCaption(int(sub.start.ordinal / 1000), int(sub.end.ordinal / 1000), sub.text) # type: ignore
                for sub in subs # type: ignore
            ]
        except Exception as e:
            logger.error(e)
            raise CaptionLoaderException(IntentErrorCode.CAPTION_LOAD_ERROR)

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
                    
                    result.append( # type: ignore
                        RecipeStep(i, int(steps[i]["start"]), int(steps[i]["end"]), combined_text) # type: ignore
                    )
                return result # type: ignore
        except Exception as e:
            logger.error(e)
            raise StepsLoaderException(IntentErrorCode.STEPS_LOAD_ERROR)