
from fastapi import WebSocket
from groq import Groq
from groq.types.chat import ChatCompletionMessageParam

from src.exceptions import BusinessException
from src.intent.exceptions import _GroqClientException, _SpringIntentClientException, IntentErrorCode
from src.intent.schemas import IntentResponse
from src.schemas import BusinessErrorResponse, IntervalErrorResponse, SuccessResponse
from .config import groq_config


class GroqClient:
    def __init__(self):
        self.client = Groq(api_key=groq_config.api_key)

    def send_prompt(self, user_prompt: str, system_prompt: str) -> str:
        try:
            messages: list[ChatCompletionMessageParam] = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ]
            response = self.client.chat.completions.create(
                messages=messages,
                model=groq_config.model
            )
            content = response.choices[0].message.content
            if content is None:
                raise ValueError("API 응답에서 content를 가져올 수 없습니다.")
            return content
        except Exception as e:
            raise _GroqClientException(IntentErrorCode.GROQ_REQUEST_SEND_ERROR, e)

class SpringIntentClient:
    async def send_intent(self, ws: WebSocket, text: str, base_intent : str):
        try:
            intent_response = IntentResponse(intent=text, base_intent=base_intent)
            await ws.send_json(SuccessResponse(intent_response).model_dump())
        except Exception as e:
            raise _SpringIntentClientException(IntentErrorCode.SPRING_INTENT_SEND_ERROR, e)
    
    async def send_error(self, ws: WebSocket, error: Exception):
        if isinstance(error, BusinessException):
            await ws.send_json(BusinessErrorResponse(error).model_dump())
        else:
            await ws.send_json(IntervalErrorResponse(error).model_dump())
