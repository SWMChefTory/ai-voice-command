
from abc import ABC, abstractmethod
from groq.types.chat import ChatCompletionMessageParam
from openai import AzureOpenAI
import json

from uvicorn.main import logger
from src.intent.time_match.utils import build_time_intent_tool
from .config import azure_config


class IntentTimeMatchClient(ABC):

    @abstractmethod
    def request_intent(self, user_prompt: str, system_prompt: str) -> str:
        pass
class AzureIntentTimeMatchClient(IntentTimeMatchClient):
    def __init__(self):
        self.client = AzureOpenAI(
            api_key=azure_config.api_key,
            azure_endpoint=azure_config.endpoint,
            api_version=azure_config.api_version    
            )
        

    def request_intent(self, user_prompt: str, system_prompt: str) -> str:
        try:
            messages: list[ChatCompletionMessageParam] = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ]
            tools = [build_time_intent_tool()]
            response = self.client.chat.completions.create(
                messages=messages,  # type: ignore
                model=azure_config.model,
                temperature=0.0,
                max_tokens=50,
                tools=tools,  # type: ignore
                tool_choice="required",
            )

            message = response.choices[0].message
            if message.tool_calls:
                tool_call = message.tool_calls[0]
                function_args = json.loads(tool_call.function.arguments)
                label = function_args.get("label")
                if label == "TIMESTAMP":
                    timestamp = function_args.get("timestamp")
                    return f"TIMESTAMP {timestamp}"
                else:
                    return "EXTRA"
            else:
                return "EXTRA"
                
        except Exception as e:
            logger.error(f"[IntentTimeMatchClient] {e}", exc_info=True)
            return "EXTRA"
