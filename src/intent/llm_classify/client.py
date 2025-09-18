
from abc import ABC, abstractmethod
from asyncio.log import logger
from groq.types.chat import ChatCompletionMessageParam
from openai import AzureOpenAI
import json
from src.intent.llm_classify.utils import build_intent_classification_tool
from src.intent.exceptions import AzureClientException, IntentErrorCode
from .config import azure_config
from src.intent.llm_classify.models import LLMClassifyResult


class IntentClient(ABC):

    @abstractmethod
    def request_intent(self, user_prompt: str, system_prompt: str, total_steps: int) -> LLMClassifyResult:
        pass

class AzureIntentClient(IntentClient):
    def __init__(self):
        self.client = AzureOpenAI(
            api_key=azure_config.api_key,
            azure_endpoint="https://hwangkyo.openai.azure.com/",
            api_version="2024-12-01-preview"
            )  

    def request_intent(self, user_prompt: str, system_prompt: str, total_steps: int) -> LLMClassifyResult:
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
            if message.tool_calls:
                tool_call = message.tool_calls[0]
                function_args = json.loads(tool_call.function.arguments)
                intent = function_args.get("intent", "ERROR")
                return LLMClassifyResult(intent)
            else:
                raise AzureClientException(IntentErrorCode.AZURE_REQUEST_SEND_ERROR)
                
        except Exception as e:
            logger.error(e)
            raise AzureClientException(IntentErrorCode.AZURE_REQUEST_SEND_ERROR)