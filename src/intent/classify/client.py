from uvicorn.main import logger
from abc import ABC, abstractmethod
from groq.types.chat import ChatCompletionMessageParam
from openai import AzureOpenAI
import json
from src.intent.classify.utils import build_intent_classification_tool
from src.intent.exceptions import _AzureClientException, IntentErrorCode
from .config import azure_config


class IntentClient(ABC):

    @abstractmethod
    def request_intent(self, user_prompt: str, system_prompt: str, total_steps: int) -> str:
        pass

class AzureIntentClient(IntentClient):
    def __init__(self):
        self.client = AzureOpenAI(
            api_key=azure_config.api_key,
            azure_endpoint=azure_config.endpoint,
            api_version=azure_config.api_version
            )  

    def request_intent(self, user_prompt: str, system_prompt: str, total_steps: int) -> str:
        try:
            messages: list[ChatCompletionMessageParam] = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ]
            tools = [build_intent_classification_tool(total_steps)]
            response = self.client.chat.completions.create(
                messages=messages,  # type: ignore
                model=azure_config.model,
                temperature=0.0,
                max_tokens=20,
                tools=tools,  # type: ignore
                tool_choice="required",
            )

            message = response.choices[0].message
            logger.info(f"[IntentClient] {message}")
            if message.tool_calls:
                tool_call = message.tool_calls[0]
                function_args = json.loads(tool_call.function.arguments)
                intent = function_args.get("intent", "ERROR")
                logger.info(f"[IntentClient] {intent}")
                return intent
            else:
                raise _AzureClientException(IntentErrorCode.AZURE_REQUEST_SEND_ERROR, ValueError("No tool call found"))
                
        except Exception as e:
            raise _AzureClientException(IntentErrorCode.AZURE_REQUEST_SEND_ERROR, e)