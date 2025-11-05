from abc import ABC, abstractmethod
from openai import AzureOpenAI, APIError, APITimeoutError, RateLimitError
from openai.types.chat import ChatCompletionToolParam, ChatCompletionMessageParam
import json
from typing import Optional, List, Iterable
from uvicorn.main import logger
from src.intent.llm_segment_match.utils import build_time_intent_tool
from .config import azure_config
from src.intent.llm_segment_match.models import LLMSegmentMatchLabel, LLMSegmentMatchResult


class IntentTimeMatchClient(ABC):

    @abstractmethod
    def request_intent(self, user_prompt: str, system_prompt: str) -> LLMSegmentMatchResult:
        pass

class AzureIntentTimeMatchClient(IntentTimeMatchClient):
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
    ) -> Optional[LLMSegmentMatchResult]:
        try:
            response = self.client.chat.completions.create(
                messages=messages,
                model=model,
                tools=tools,
                tool_choice="required",
                timeout=30,
            )

            message = response.choices[0].message
            if message.tool_calls:
                tool_call = message.tool_calls[0]
                function_args = json.loads(tool_call.function.arguments)
                label = function_args.get("label")

                logger.info(f"[AzureTimeMatch] Success with {model}: {label}")

                if label == LLMSegmentMatchLabel.TIMESTAMP.value:
                    timestamp = function_args.get("timestamp")
                    return LLMSegmentMatchResult(label, timestamp)
                else:
                    return LLMSegmentMatchResult(label)
            else:
                logger.warning(f"[AzureTimeMatch] No tool_calls with {model}")
                return None

        except (APIError, APITimeoutError, RateLimitError) as e:
            logger.warning(f"[AzureTimeMatch] {model} failed: {type(e).__name__} - {e}")
            return None
        except Exception as e:
            logger.error(f"[AzureTimeMatch] {model} unexpected error: {e}")
            return None

    def request_intent(self, user_prompt: str, system_prompt: str) -> LLMSegmentMatchResult:
        try:
            messages: List[ChatCompletionMessageParam] = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ]
            tools: List[ChatCompletionToolParam] = [build_time_intent_tool()]

            for i, model in enumerate(self.models):
                is_fallback = i > 0
                if is_fallback:
                    logger.info(f"[AzureTimeMatch] Falling back to: {model}")

                result = self._try_request(messages, tools, model)

                if result:
                    if is_fallback:
                        logger.warning(f"[AzureTimeMatch] Primary model failed, used fallback: {model}")
                    return result

            logger.error(f"[AzureTimeMatch] All models failed: {self.models}, returning EXTRA")
            return LLMSegmentMatchResult(LLMSegmentMatchLabel.EXTRA.value)

        except Exception as e:
            logger.error(f"[AzureTimeMatch] Fatal error: {e}", exc_info=True)
            return LLMSegmentMatchResult(LLMSegmentMatchLabel.EXTRA.value)