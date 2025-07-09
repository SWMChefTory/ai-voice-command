
from abc import ABC, abstractmethod
from fastapi import WebSocket
from groq import Groq
from groq.types.chat import ChatCompletionMessageParam

from src.exceptions import BusinessException
from src.intent.exceptions import _GroqClientException, _SpringIntentClientException, IntentErrorCode
from src.intent.models import Intent
from src.intent.schemas import IntentResponse
from src.schemas import BusinessErrorResponse, IntervalErrorResponse, SuccessResponse
from .config import groq_config


class IntentClient(ABC):

    @abstractmethod
    def request_intent(self, user_prompt: str, system_prompt: str) -> str:
        pass

class UserSessionClient(ABC):
    @abstractmethod
    async def send_intent(self, client_websocket: WebSocket, intent: Intent):
        pass

    @abstractmethod
    async def send_error(self, client_websocket: WebSocket, error: Exception):
        pass

class GroqIntentClient(IntentClient):
    def __init__(self):
        self.client = Groq(api_key=groq_config.api_key)

    def request_intent(self, user_prompt: str, system_prompt: str) -> str:
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

class SpringSessionClient(UserSessionClient):
    async def send_intent(self, client_websocket: WebSocket, intent: Intent):
        try:
            intent_response = IntentResponse.from_intent(intent)
            await client_websocket.send_json(SuccessResponse(intent_response).model_dump())
        except Exception as e:
            raise _SpringIntentClientException(IntentErrorCode.SPRING_INTENT_SEND_ERROR, e)
    
    async def send_error(self, client_websocket: WebSocket, error: Exception):
        if isinstance(error, BusinessException):
            await client_websocket.send_json(BusinessErrorResponse(error).model_dump())
        else:
            await client_websocket.send_json(IntervalErrorResponse(error).model_dump())