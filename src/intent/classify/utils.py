class PromptGenerator:
    def __init__(self):
        pass
        
    def generate_prompt(self, total_steps: int) -> str:

        return f"""
        당신은 요리 영상 제어 시스템의 **음성/텍스트 인텐트 단일 분류기**입니다.

        ### 가능한 라벨
        - NEXT
        - PREV
        - STEP1 … STEP{total_steps}
        - TIMER
        - TIMESTAMP
        - EXTRA

        **분류 규칙:**
        - NEXT: "다음", "다음 단계", "넘어가", "계속", "진행" 등의 다음 단계 진행 요청
        - PREV: "이전", "뒤로", "전 단계", "돌아가", "되돌려" 등의 이전 단계 이동 요청
        - STEPn: 숫자·순서·“첫/두/마지막” 등이 명시된 단계 요청
        - 예) "1단계 보여줘" → `{{"intent":"STEP1"}}`  
        - 예) "마지막 단계"  → `{{"intent":"STEP{total_steps}"}}` 
        - TIMESTAMP: 특정 장면을 찾으라는 요청 ("파 넣는 장면", "물 살짝 부은 부분", "먹는 장면", "불 줄인 화면" 등)
        - TIMER: 모든 타이머 관련 요청 ("타이머 시작", "시간 재줘", "타이머 멈춰", "시간 얼마나 됐어", "5분 타이머", "스톱워치" 등)
        - EXTRA: 명확하지 않은 입력, 인사, 일반 대화, 기술 문제, 거부 표현 등

        **반드시 `classify_cooking_intent` 함수를 호출해 위 JSON 형식으로만 응답하세요.**
        """

def build_label_enum(total_steps: int) -> list[str]:
    return ["NEXT", "PREV", "EXTRA", "TIMESTAMP", "TIMER"] + [f"STEP{i+1}" for i in range(total_steps)]

from typing import Dict, Any

def build_intent_classification_tool(total_steps: int) -> Dict[str, Any]:
    return {
    "type": "function",
    "function": {
        "name": "classify_cooking_intent",
        "description": "Classify user input into cooking video control intents",
        "parameters": {
            "type": "object",
            "properties": {
                "intent": {
                    "type": "string",
                    "enum": build_label_enum(total_steps),
                    "description": "The classified intent"
                },
            },
            "required": ["intent"]
        }
    }
}