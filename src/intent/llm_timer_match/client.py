from abc import ABC, abstractmethod
from openai import AzureOpenAI, APIError, APITimeoutError, RateLimitError
from openai.types.chat import ChatCompletionToolParam, ChatCompletionMessageParam
import json
from typing import Optional, List, Iterable
from uvicorn.main import logger
from src.intent.llm_timer_match.utils import build_intent_timer_match_tool
from .config import azure_config
from src.intent.llm_timer_match.models import LLMTimerMatchLabel, LLMTimerMatchResult


class IntentTimerMatchClient(ABC):

    @abstractmethod
    def request_intent(self, user_prompt: str, system_prompt: str) -> LLMTimerMatchResult:
        pass

class AzureIntentTimerMatchClient(IntentTimerMatchClient):

    def __init__(self) -> None:
        self.client = AzureOpenAI(
            api_key=azure_config.api_key,
            azure_endpoint=azure_config.endpoint,
            api_version=azure_config.api_version
        )
        self.models: List[str] = [azure_config.model, azure_config.fallback_model]

    def _try_request(
            self,
            messages: List[ChatCompletionMessageParam],
            tools: Iterable[ChatCompletionToolParam],
            model: str
    ) -> Optional[LLMTimerMatchResult]:
        try:
            response = self.client.chat.completions.create(
                messages=messages,
                model=model,
                tools=tools,
                tool_choice="required",
                timeout=azure_config.request_timeout,
            )

            message = response.choices[0].message
            if message.tool_calls:
                tool_call = message.tool_calls[0]
                function_args = json.loads(tool_call.function.arguments)
                action = function_args.get("action", "ERROR")

                if action == LLMTimerMatchLabel.TIMER_SET.value:
                    duration = function_args.get("duration", "ERROR")
                    logger.info(f"[AzureTimerMatch] Success with {model}: {action} {duration}")
                    return LLMTimerMatchResult(action, duration)
                else:
                    logger.info(f"[AzureTimerMatch] Success with {model}: {action}")
                    return LLMTimerMatchResult(action)
            else:
                logger.warning(f"[AzureTimerMatch] No tool_calls with {model}")
                return None

        except (APIError, APITimeoutError, RateLimitError) as e:
            logger.warning(f"[AzureTimerMatch] {model} failed: {type(e).__name__} - {e}")
            return None
        except Exception as e:
            logger.error(f"[AzureTimerMatch] {model} unexpected error: {e}")
            return None

    def request_intent(self, user_prompt: str, system_prompt: str) -> LLMTimerMatchResult:
        try:
            messages: List[ChatCompletionMessageParam] = [
                {"role": "system", "content": system_prompt},  # type: ignore
                {"role": "user", "content": user_prompt},  # type: ignore
            ]
            tools: List[ChatCompletionToolParam] = [build_intent_timer_match_tool()]

            for i, model in enumerate(self.models):
                is_fallback = i > 0
                if is_fallback:
                    logger.info(f"[AzureTimerMatch] Falling back to: {model}")

                result = self._try_request(messages, tools, model)

                if result:
                    if is_fallback:
                        logger.warning(f"[AzureTimerMatch] Primary model failed, used fallback: {model}")
                    return result

            logger.error(f"[AzureTimerMatch] All models failed: {self.models}, returning EXTRA")
            return LLMTimerMatchResult(LLMTimerMatchLabel.EXTRA.value)

        except Exception as e:
            logger.error(f"[AzureTimerMatch] Fatal error: {e}", exc_info=True)
            return LLMTimerMatchResult(LLMTimerMatchLabel.EXTRA.value)