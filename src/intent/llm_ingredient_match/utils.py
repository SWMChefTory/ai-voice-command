import textwrap
from typing import List

from src.user_session.recipe.models import RecipeIngredient
from openai.types.chat import ChatCompletionToolParam

class IngredientMatchPromptGenerator:
    def __init__(self):
        pass
        
    def generate_secondary_system_prompt(self, ingredients: List[RecipeIngredient]) -> str:
        return textwrap.dedent(f"""
        당신은 요리 레시피의 **재료 질의 분류기**입니다.

        ### 가능한 라벨
        - INGREDIENT : 레시피 재료를 찾을 수 있음 (정확한 재료 정보를 반환)
        - EXTRA      : 재료를 찾을 수 없음(매칭 실패/요리 무관/모호)

        ### 분류 규칙
        - 사용자가 특정 재료에 대해 묻거나 "무엇/어떤 재료/몇 개/얼마나" 류의 요청이면 INGREDIENT 후보로 판단하되,
          레시피 재료 목록과 매칭이 불가하면 EXTRA로 분류합니다.
        - 라벨이 INGREDIENT라면 반드시 아래 재료 목록에서 가장 적절한 재료의 **전체 문자열**을 그대로 반환하세요.
        - 라벨이 EXTRA라면 ingredient를 절대 포함하지 마세요.

        ### 반드시 아래 함수 형식으로만 응답하세요:
        classify_recipe_ingredient_intent(label="<INGREDIENT|EXTRA>", ingredient="<재료 전체 문자열, INGREDIENT일 때만>")

        ### 현재 레시피의 재료 목록 (정확히 이 형태로 반환하세요):
        {chr(10).join(map(str, ingredients))}
        """).strip()


def build_ingredient_intent_tool() -> ChatCompletionToolParam:
    return {
        "type": "function",
        "function": {
            "name": "classify_recipe_ingredient_intent",
            "description": "사용자 입력을 재료 질의(INGREDIENT) 또는 EXTRA로 분류하고, INGREDIENT일 때 재료 전체 문자열을 함께 반환",
            "parameters": {
                "type": "object",
                "properties": {
                    "label": {
                        "type": "string",
                        "enum": ["INGREDIENT", "EXTRA"],
                        "description": "재료 매칭이면 INGREDIENT, 아니면 EXTRA",
                    },
                    "ingredient": {
                        "type": "string",
                        "description": "가장 적절한 재료의 전체 문자열 (예: '양파 1 개'). label == INGREDIENT일 때만 사용",
                    },
                },
                "required": ["label"],
                "additionalProperties": False,
            },
        },
    }