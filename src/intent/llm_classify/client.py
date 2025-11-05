from abc import ABC, abstractmethod
from openai import AzureOpenAI, APIError, APITimeoutError, RateLimitError
from openai.types.chat import ChatCompletionToolParam, ChatCompletionMessageParam
import json
from src.intent.llm_classify.utils import build_intent_classification_tool
from src.intent.exceptions import AzureClientException, IntentErrorCode
from .config import azure_config
from src.intent.llm_classify.models import LLMClassifyResult
from uvicorn.main import logger
from typing import Optional, List, Iterable


class IntentClient(ABC):

    @abstractmethod
    def request_intent(self, user_prompt: str, system_prompt: str, total_steps: int) -> LLMClassifyResult:
        pass

class AzureIntentClient(IntentClient):
    def __init__(self):
        self.client = AzureOpenAI(
            api_key=azure_config.api_key,
            azure_endpoint=azure_config.endpoint,
            api_version=azure_config.api_version
        )

        self.models = [azure_config.model, azure_config.fallback_model]

    def _try_request(
            self,
            messages: List[ChatCompletionMessageParam],
            tools: Iterable[ChatCompletionToolParam],
            model: str
    ) -> Optional[LLMClassifyResult]:
        """단일 모델로 요청 시도"""
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
                intent = function_args.get("intent", "ERROR")
                return LLMClassifyResult(intent)
            else:
                logger.warning(f"[Azure] No tool_calls with {model}")
                return None

        except (APIError, APITimeoutError, RateLimitError) as e:
            logger.warning(f"[Azure] {model} failed: {type(e).__name__} - {e}")
            return None
        except Exception as e:
            logger.error(f"[Azure] {model} unexpected error: {e}")
            return None

    def request_intent(self, user_prompt: str, system_prompt: str, total_steps: int) -> LLMClassifyResult:
        """Fallback 로직이 포함된 요청"""
        try:
            messages: list[ChatCompletionMessageParam] = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ]

            tools: List[ChatCompletionToolParam] = [build_intent_classification_tool(total_steps)]

            for i, model in enumerate(self.models):
                is_fallback = i > 0
                if is_fallback:
                    logger.info(f"[Azure] Falling back to: {model}")

                result = self._try_request(messages, tools, model)

                if result:
                    if is_fallback:
                        logger.warning(f"[Azure] Primary model failed, used fallback: {model}")
                    return result

            logger.error(f"[Azure] All models failed: {self.models}")
            raise AzureClientException(IntentErrorCode.AZURE_REQUEST_SEND_ERROR)

        except AzureClientException:
            raise
        except Exception as e:
            logger.error(f"[Azure] Fatal error: {e}", exc_info=True)
            raise AzureClientException(IntentErrorCode.AZURE_REQUEST_SEND_ERROR)