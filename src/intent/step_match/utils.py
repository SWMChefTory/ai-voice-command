from typing import List, Dict, Any
from src.user_session.recipe.models import RecipeCaption
import textwrap

class PromptGenerator:
    def __init__(self):
        pass
        
    def generate_secondary_system_prompt(self, recipe_captions: List[RecipeCaption]) -> str:
        """2차 분류용 시스템 프롬프트 생성 (구체적인 단계 분류)"""
        return textwrap.dedent(f"""
            당신은 요리 영상의 구체적인 단계 분류기입니다.

            **2차 분류 규칙:**
            사용자가 요리 관련 특정 내용을 언급했을 때, 위의 단계들 중 가장 적절한 시간을 찾아 timestamp로 분류하세요.


            **중요 지침:**
            1. 사용자 입력과 레시피 단계를 매칭하여 가장 적절한 시간을 찾으세요.
            2. 애매한 경우는 가장 유사한 시간을 선택하세요.

            **반드시 classify_specific_step 함수를 호출하여 응답하세요.**
            **절대 다른 형식으로 응답하지 마세요.**

            **현재 요리 영상의 시간:**
            {chr(10).join(map(str, recipe_captions))}
    """).strip()

def build_intent_step_match_tool() -> Dict[str, Any]:
    return {
            "type": "function",
            "function": {
                "name": "classify_specific_step",
                "description": "Classify cooking input into specific recipe steps",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "timestamp": {
                            "type": "integer",
                            "description": "The specific recipe timestamp"
                        },
                    },
                    "required": ["timestamp"]
                }
            }
    }