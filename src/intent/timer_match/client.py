
from abc import ABC, abstractmethod
from groq.types.chat import ChatCompletionMessageParam
from openai import AzureOpenAI
import json

from uvicorn.main import logger
from src.intent.timer_match.utils import build_intent_timer_match_tool
from .config import azure_config


class IntentTimerMatchClient(ABC):

    @abstractmethod
    def request_intent(self, user_prompt: str, system_prompt: str) -> str:
        pass
class AzureIntentTimerMatchClient(IntentTimerMatchClient):
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
            tools = [build_intent_timer_match_tool()]
            response = self.client.chat.completions.create(
                messages=messages,  # type: ignore
                model=azure_config.model,
                temperature=0.0,
                max_tokens=20,
                tools=tools,  # type: ignore
                tool_choice="required",
            )

            message = response.choices[0].message
            logger.info(f"[IntentTimerMatchClient] {message}")
            if message.tool_calls:
                tool_call = message.tool_calls[0]
                function_args = json.loads(tool_call.function.arguments)
                action = function_args.get("action", "ERROR")
                if action == "SET":
                    duration = function_args.get("duration", "ERROR")
                    logger.info(f"[IntentTimerMatchClient] TIMER {action} {duration}")
                    return f"TIMER {action} {duration}"
                else:
                    logger.info(f"[IntentTimerMatchClient] TIMER {action}")
                    return f"TIMER {action}"
            else:
                return "ERROR"
                
        except Exception as e:
            logger.error(f"[IntentTimerMatchClient] {e}", exc_info=True)
            return "EXTRA"
