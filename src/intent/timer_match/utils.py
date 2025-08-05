from typing import Dict, Any

class PromptGenerator:
    def __init__(self):
        pass
        
    def generate_secondary_system_prompt(self) -> str:
        """2차 분류용 시스템 프롬프트 생성 (타이머 분류)"""
        return """당신은 요리 영상의 타이머 분류기입니다.

### 가능한 액션
- START: 타이머 시작
- STOP: 타이머 중지/정지
- CHECK: 타이머 상태 확인
- SET: 특정 시간으로 타이머 설정

### 2차 분류 규칙

**1. 액션 분류(예시):**
- START: "타이머 시작", "시간 재줘", "타이머 켜줘", "스톱워치 시작"
- STOP: "타이머 멈춰", "시간 그만", "타이머 꺼줘", "정지", "타이머 끄기"
- CHECK: "시간 얼마나 됐어", "타이머 확인", "몇 분 지났어", "시간 체크", "남은 시간"
- SET: "5분 타이머", "10분 타이머 설정", "3분으로 맞춰줘", "30초 타이머 만들어줘", "1시간 20분"

**2. 우선순위(충돌 해소):**
- 발화에 **명시적 시간(duration)** 이 포함되면 **SET**으로 분류한다.
- START/STOP/CHECK는 **항상 duration=null**이어야 한다.

**3. 시간 duration 계산 (초 단위 변환):**
- 기본: "30초"→30, "5분"→300, "1시간"→3600, "2시간 30분"→9000, "1시간 20분 30초"→4830
- 콜론 표기: "MM:SS"(예: "01:30"→90), "HH:MM:SS"(예: "01:02:03"→3723)
- 관용/복합: "한 시간 반"→5400, "1분 반"→90, "두 시간 십오 분"→8100
- 해석 불가 시 상위 단계에서 제거되었다고 가정한다.

**4. duration 설정 규칙:**
- SET 액션: duration **반드시 포함**(초 단위, 1 이상 정수)
- START/STOP/CHECK 액션: duration은 **항상 null**

**출력 형식:**
반드시 classify_timer 함수만 호출하여 JSON 형태로 응답하라. 다른 텍스트나 설명 금지.

**예시:**
- 입력: "10분 타이머 시작해" → {"action":"SET","duration":600}
- 입력: "타이머 멈춰" → {"action":"STOP","duration":null}
- 입력: "얼마나 남았어?" → {"action":"CHECK","duration":null}
"""

def build_intent_timer_match_tool() -> Dict[str, Any]:
    """타이머 분류를 위한 함수 도구 정의"""
    return {
        "type": "function",
        "function": {
            "name": "classify_timer",
            "description": "Classify cooking timer input into action and duration (seconds). For SET, duration is required; otherwise it must be null.",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["START", "STOP", "CHECK", "SET"],
                        "description": "The timer action to perform"
                    },
                    "duration": {
                        "type": ["integer", "null"],
                        "description": "Duration in seconds. Required for SET; null for START/STOP/CHECK"
                    }
                },
                "required": ["action"],
                "additionalProperties": False,
                "allOf": [
                    {
                        "if": { "properties": { "action": { "const": "SET" } } },
                        "then": {
                            "required": ["duration"],
                            "properties": {
                                "duration": { "type": "integer", "minimum": 1 }
                            }
                        }
                    },
                    {
                        "if": { "properties": { "action": { "enum": ["START", "STOP", "CHECK"] } } },
                        "then": {
                            "properties": {
                                "duration": { "type": "null" }
                            }
                        }
                    }
                ]
            }
        }
    }