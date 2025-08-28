
from abc import ABC, abstractmethod
from groq.types.chat import ChatCompletionMessageParam
from openai import AzureOpenAI
import json

from uvicorn.main import logger
from src.intent.llm_timer_match.utils import build_intent_timer_match_tool
from .config import azure_config
from src.intent.llm_timer_match.models import LLMTimerMatchLabel, LLMTimerMatchResult

class IntentTimerMatchClient(ABC):

    @abstractmethod
    def request_intent(self, user_prompt: str, system_prompt: str) -> LLMTimerMatchResult:
        pass
class AzureIntentTimerMatchClient(IntentTimerMatchClient):
    def __init__(self):
        self.client = AzureOpenAI(
            api_key=azure_config.api_key,
            azure_endpoint=azure_config.endpoint,
            api_version=azure_config.api_version    
            )
        

    def request_intent(self, user_prompt: str, system_prompt: str) -> LLMTimerMatchResult:
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
                max_tokens=50,
                tools=tools,  # type: ignore
                tool_choice="required",
            )

            message = response.choices[0].message
            if message.tool_calls:
                tool_call = message.tool_calls[0]
                function_args = json.loads(tool_call.function.arguments)
                action = function_args.get("action", "ERROR")
                if action == LLMTimerMatchLabel.TIMER_SET.value:
                    duration = function_args.get("duration", "ERROR")
                    logger.info(f"[IntentTimerMatchClient] {action} {duration}")
                    return LLMTimerMatchResult(action, duration)
                else:
                    logger.info(f"[IntentTimerMatchClient] {action}")
                    return LLMTimerMatchResult(action)
            else:
                return LLMTimerMatchResult(LLMTimerMatchLabel.EXTRA)
                
        except Exception as e:
            logger.error(f"[IntentTimerMatchClient] {e}", exc_info=True)
            return LLMTimerMatchResult(LLMTimerMatchLabel.EXTRA)
