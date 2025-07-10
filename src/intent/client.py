
from abc import ABC, abstractmethod
from groq import Groq
from groq.types.chat import ChatCompletionMessageParam

from src.intent.exceptions import _GroqClientException, _SpringIntentClientException, IntentErrorCode
from .config import groq_config


class IntentClient(ABC):

    @abstractmethod
    def request_intent(self, user_prompt: str, system_prompt: str) -> str:
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