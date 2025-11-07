from abc import ABC, abstractmethod
from openai import AzureOpenAI, APIError, APITimeoutError, RateLimitError
from openai.types.chat import ChatCompletionToolParam, ChatCompletionMessageParam
import json
from typing import Optional, List, Iterable
from uvicorn.main import logger
from src.intent.llm_ingredient_match.utils import build_ingredient_intent_tool
from .config import azure_config
from .models import LLMIngredientMatchResult, LLMIngredientMatchLabel


class IntentIngredientMatchClient(ABC):

    @abstractmethod
    def request_intent(self, user_prompt: str, system_prompt: str) -> LLMIngredientMatchResult:
        pass

class AzureIntentIngredientClient(IntentIngredientMatchClient):
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
    ) -> Optional[LLMIngredientMatchResult]:
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
                label = function_args.get("label")

                if label == LLMIngredientMatchLabel.INGREDIENT.value:
                    ingredient = function_args.get("ingredient")
                    logger.info(f"[AzureIngredientMatch] Success with {model}: {label} {ingredient}")
                    return LLMIngredientMatchResult(label, ingredient)
                else:
                    logger.info(f"[AzureIngredientMatch] Success with {model}: {label}")
                    return LLMIngredientMatchResult(label)
            else:
                return None

        except (APIError, APITimeoutError, RateLimitError) as e:
            logger.warning(f"[AzureIngredientMatch] {model} failed: {type(e).__name__} - {e}")
            return None
        except Exception as e:
            logger.error(f"[AzureIngredientMatch] {model} unexpected error: {e}")
            return None

    def request_intent(self, user_prompt: str, system_prompt: str) -> LLMIngredientMatchResult:
        try:
            messages: List[ChatCompletionMessageParam] = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ]
            tools: List[ChatCompletionToolParam] = [build_ingredient_intent_tool()]

            for i, model in enumerate(self.models):
                is_fallback = i > 0
                if is_fallback:
                    logger.info(f"[AzureIngredientMatch] Falling back to: {model}")

                result = self._try_request(messages, tools, model)

                if result:
                    if is_fallback:
                        logger.warning(f"[AzureIngredientMatch] Primary model failed, used fallback: {model}")
                    return result

            logger.error(f"[AzureIngredientMatch] All models failed: {self.models}, returning EXTRA")
            return LLMIngredientMatchResult(LLMIngredientMatchLabel.EXTRA.value)

        except Exception as e:
            logger.error(f"[AzureIngredientMatch] Fatal error: {e}", exc_info=True)
            return LLMIngredientMatchResult(LLMIngredientMatchLabel.EXTRA.value)