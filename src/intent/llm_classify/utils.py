import textwrap
from openai.types.chat import ChatCompletionToolParam


class PromptGenerator:
    def __init__(self):
        pass
        
    def generate_prompt(self,total_steps: int) -> str:
        return textwrap.dedent(f"""
        당신은 요리 영상 제어 시스템의 **인텐트 단일 분류기**입니다.

        ### 가능한 라벨
        - NEXT
        - PREV
        - STEP 1 … STEP {total_steps}
        - TIMER
        - TIMESTAMP
        - EXTRA

        ### 분류 규칙:
        - NEXT: 다음 단계로 이동 요청. 예) "다음", "계속해", "넘겨"
        - PREV: 이전 단계로 이동 요청. 예) "뒤로", "전 단계", "되돌려"
        - STEP n: 특정 단계 요청. 예) "1단계", "두 번째 단계", "마지막 단계"
        - TIMER: 타이머 관련 요청. 예) "5분 타이머 맞춰", "10분 재워"
        - **TIMESTAMP:** 특정 장면/행동/시간 요청
            - 장면이나 동작을 언급하며 “언제/어디/어느 부분/다시” 같은 질문 포함
            - 예) "야채 써는 거 뭐야?", "고기 굽는 장면 다시 보여줘", "계란 푸는 부분 언제 나와?", "양파 넣는 부분 어디야?"
        - EXTRA: 요리와 무관하거나 일반 대화/인사. 예) "안녕하세요", "이 레시피 맛있나요?"

        ### 주의
        - 항상 아래 함수 형식으로 응답:
        classify_cooking_intent(intent="<위 라벨 중 하나>")
        """).strip()

def _build_label_enum(total_steps: int) -> list[str]:
    return ["NEXT", "PREV", "EXTRA", "TIMESTAMP", "TIMER"] + [f"STEP {i+1}" for i in range(total_steps)]

def build_intent_classification_tool(total_steps: int) -> ChatCompletionToolParam:
    labels = _build_label_enum(total_steps)

    return {
        "type": "function",
        "function": {
            "name": "classify_cooking_intent",
            "description": "Classify user input into cooking video control intents",
            "strict": True,
            "parameters": {
                "type": "object",
                "properties": {
                    "intent": {
                        "type": "string",
                        "enum": labels,
                        "description": "The classified intent"
                    }
                },
                "required": ["intent"],
                "additionalProperties": False
            }
        }
    }