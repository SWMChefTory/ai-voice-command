from functools import lru_cache
import json
import pysrt

from src.intent.exceptions import _CaptionLoaderException, _StepsLoaderException, IntentErrorCode
from src.intent.models import RecipeCaption, RecipeStep

class CaptionLoader:
    def __init__(self):
        pass

    @lru_cache(maxsize=1)
    def load_caption(self):
        try:
            subs = pysrt.open("assets/test.srt", encoding="utf-8")
            return [
                RecipeCaption(int(sub.start.ordinal), int(sub.end.ordinal), sub.text)
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
                return [
                    RecipeStep(i, int(steps[i]["start"]), int(steps[i]["end"]), steps[i]["text"])
                    for i in range(0,len(steps))
                ]
        except Exception as e:
            raise _StepsLoaderException(IntentErrorCode.STEPS_LOAD_ERROR, e)

class PromptGenerator:
    def __init__(self):
        pass
        
    def generate_prompt(self, captions: list[RecipeCaption], recipe_steps: list[RecipeStep]) -> str:
        prompt = f"""
                    You MUST respond with ONLY ONE of these exact words: NEXT, PREV, STEPn, or EXTRA.
                    DO NOT write any explanations, greetings, or additional text.

                    **Available Recipe Steps:**
                    {'\n'.join(map(str, recipe_steps))}
                    
                    **Video Captions:**
                    {'\n'.join(map(str, captions))}

                    **RESPONSE RULES:**
                    - NEXT: for "다음", "다음 단계", "넘어가", "계속"
                    - PREV: for "이전", "뒤로", "전 단계", "돌아가"
                    - STEPn: for specific cooking requests (n = step number 1-10)
                    - EXTRA: for unclear/meaningless input, greetings, errors

                    **CRITICAL CONSTRAINTS:**
                    - Your response must be EXACTLY one of: NEXT, PREV, STEP1, STEP2, STEP3, STEP4, STEP5, STEP6, STEP7, STEP8, STEP9, STEP10, or EXTRA
                    - NO other text allowed
                    - NO explanations 
                    - NO greetings
                    - NO sentences
                    - JUST the command word

                    **Examples:**
                    User: "다음 단계로 가줘" → Response: NEXT
                    User: "이전 단계 보여줘" → Response: PREV  
                    User: "양파 볶는 부분" → Response: STEP3
                    User: "안녕하세요" → Response: EXTRA
                    User: "알어" → Response: EXTRA

                    RESPOND WITH ONLY ONE WORD FROM THE ALLOWED LIST.
                """
        return prompt