from functools import lru_cache
import json
import pysrt

from src.intent.exceptions import _CaptionLoaderException, _StepsLoaderException, IntentErrorCode


class CaptionLoader:
    def __init__(self):
        pass

    def load_caption(self):
        try:
            subs = pysrt.open("assets/test.srt", encoding="utf-8")
            lines = []
            for sub in subs:
                lines.append(f"{sub.start} --> {sub.end}")
                lines.append(sub.text.replace("\n", " "))
                lines.append("")     
            return "\n".join(lines)
        except Exception as e:
            raise _CaptionLoaderException(IntentErrorCode.CAPTION_LOAD_ERROR, e)



class StepsLoader:
    def __init__(self):
        pass

    def _convertTotimeFormat(self, seconds: int) -> str:
        hours  = seconds//3600
        minutes = (seconds%3600)//60
        seconds = (seconds%60)
        return f'{hours}:{minutes}:{seconds}'

    @lru_cache(maxsize=1)
    def load_steps(self):
        try:
            with open("assets/steps.json", "r") as stepsJson:
                steps = json.load(stepsJson)

                result = ''
                for i in range(0,len(steps)):
                    result+= f"""
                        step {i}
                        timeline: {self._convertTotimeFormat(int(steps[i]["start"]))} --> {self._convertTotimeFormat(int(steps[i]["end"]))}
                        content: {steps[i]["text"]}
                        """
            return result
        except Exception as e:
            raise _StepsLoaderException(IntentErrorCode.STEPS_LOAD_ERROR, e)

class PromptGenerator:
    def __init__(self):
        pass
        
    def generate_prompt(self, caption: str, recipeSteps: str) -> str:
        prompt = f"""
                    You MUST respond with ONLY ONE of these exact words: NEXT, PREV, STEPn, or EXTRA.
                    DO NOT write any explanations, greetings, or additional text.

                    **Available Recipe Steps:**
                    {recipeSteps}
                    
                    **Video Captions:**
                    {caption}

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