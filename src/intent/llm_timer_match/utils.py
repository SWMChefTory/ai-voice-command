import textwrap
from openai.types.chat import ChatCompletionToolParam

class PromptGenerator:
    def __init__(self):
        pass
        
    def generate_secondary_system_prompt(self) -> str:
        """2차 분류용 시스템 프롬프트 생성 (타이머 분류)"""
        return textwrap.dedent("""당신은 요리 영상의 타이머 분류기입니다.

### 가능한 액션
- TIMER START: 타이머 시작
- TIMER STOP: 타이머 중지/정지
- TIMER CHECK: 타이머 상태 확인
- TIMER SET: 특정 시간으로 타이머 설정

### 2차 분류 규칙

**1. 액션 분류(예시):**
- TIMER START: "타이머 시작", "시간 재줘", "타이머 켜줘", "스톱워치 시작"
- TIMER STOP: "타이머 멈춰", "시간 그만", "타이머 꺼줘", "정지", "타이머 끄기"
- TIMER CHECK: "시간 얼마나 됐어", "타이머 확인", "몇 분 지났어", "시간 체크", "남은 시간"
- TIMER SET: "5분 타이머", "10분 타이머 설정", "3분으로 맞춰줘", "30초 타이머 만들어줘", "1시간 20분"

**2. 우선순위(충돌 해소):**
- 발화에 **명시적 시간(duration)** 이 포함되면 **TIMER SET**으로 분류한다.
- TIMER START/TIMER STOP/TIMER CHECK는 **항상 duration=null**이어야 한다.

**3. 시간 duration 계산 (초 단위 변환):**
- 기본: "30초"→30, "5분"→300, "1시간"→3600, "2시간 30분"→9000, "1시간 20분 30초"→4830
- 콜론 표기: "MM:SS"(예: "01:30"→90), "HH:MM:SS"(예: "01:02:03"→3723)
- 관용/복합: "한 시간 반"→5400, "1분 반"→90, "두 시간 십오 분"→8100
- 해석 불가 시 상위 단계에서 제거되었다고 가정한다.

**4. duration 설정 규칙:**
- TIMER SET 액션: duration **반드시 포함**(초 단위, 1 이상 정수)
- TIMER START/TIMER STOP/TIMER CHECK 액션: duration은 **항상 null**

**중요: 스키마 검증 규칙**
- TIMER SET 액션일 때: duration은 1 이상의 정수여야 함
- TIMER START/TIMER STOP/TIMER CHECK 액션일 때: duration은 반드시 null이어야 함

**출력 형식:**
반드시 classify_timer 함수만 호출하여 JSON 형태로 응답하라. 다른 텍스트나 설명 금지.

**예시:**
- 입력: "10분 타이머 시작해" → {"action":"TIMER SET","duration":600}
- 입력: "타이머 멈춰" → {"action":"TIMER STOP","duration":null}
- 입력: "얼마나 남았어?" → {"action":"TIMER CHECK","duration":null}
""").strip()

def build_intent_timer_match_tool() -> ChatCompletionToolParam:
    return {
        "type": "function", 
        "function": {
            "name": "classify_timer",
            "description": "Classify cooking timer input into action and duration. TIMER SET action requires positive integer duration in seconds. TIMER START/TIMER STOP/TIMER CHECK actions must have null duration.",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["TIMER START", "TIMER STOP", "TIMER CHECK", "TIMER SET"],
                        "description": "The timer action to perform"
                    },
                    "duration": {
                        "type": ["integer", "null"],
                        "description": "Duration in seconds. Must be positive integer for TIMER SET action, null for TIMER START/TIMER STOP/TIMER CHECK actions",
                        "minimum": 1
                    }
                },
                "required": ["action", "duration"],
                "additionalProperties": False
            }
        }
    }