import textwrap
from typing import List

from src.user_session.recipe.models import RecipeStep
from openai.types.chat import ChatCompletionToolParam

class PromptGenerator:
    def __init__(self):
        pass
        
    def generate_secondary_system_prompt(self, steps: List[RecipeStep]) -> str:
        return textwrap.dedent(f"""
        당신은 요리 영상의 **시간 구간 질의 분류기**입니다.

        ### 가능한 라벨
        - TIMESTAMP  : 레시피 시간 구간을 찾을 수 있음 (정확한 타임스탬프를 반환)
        - EXTRA      : 시간 구간을 찾을 수 없음(매칭 실패/요리 무관/모호)

        ### 분류 규칙
        - 사용자가 특정 장면/행동/시간을 묻거나 “언제/어디/어느 부분/다시” 류의 요청이면 TIMESTAMP 후보로 판단하되,
          레시피 자막/시간 구간과 매칭이 불가하면 EXTRA로 분류합니다.
        - 라벨이 TIMESTAMP라면 반드시 가장 적절한 초 단위 timestamp를 함께 반환하세요.
        - 라벨이 EXTRA라면 timestamp를 절대 포함하지 마세요.

        ### 반드시 아래 함수 형식으로만 응답하세요:
        classify_recipe_time_intent(label="<TIMESTAMP|EXTRA>", timestamp=<정수, TIMESTAMP일 때만>)

        ### 현재 요리 영상의 시간 구간 목록:
        {chr(10).join(map(str, steps))}
        """).strip()


def build_time_intent_tool() -> ChatCompletionToolParam:
    return {
        "type": "function",
        "function": {
            "name": "classify_recipe_time_intent",
            "description": "사용자 입력을 시간 구간 질의(TIMESTAMP) 또는 EXTRA로 분류하고, TIMESTAMP일 때 timestamp를 함께 반환",
            "parameters": {
                "type": "object",
                "properties": {
                    "label": {
                        "type": "string",
                        "enum": ["TIMESTAMP", "EXTRA"],
                        "description": "시간 구간 매칭이면 TIMESTAMP, 아니면 EXTRA",
                    },
                    "timestamp": {
                        "type": "integer",
                        "minimum": 0,
                        "description": "가장 적절한 레시피 타임스탬프(초). label == TIMESTAMP일 때만 사용",
                    },
                },
                "required": ["label"],
                "additionalProperties": False,
            },
        },
    }