
from abc import ABC, abstractmethod
from groq.types.chat import ChatCompletionMessageParam
from openai import AzureOpenAI
import json

from uvicorn.main import logger
from src.intent.llm_segment_match.utils import build_time_intent_tool
from .config import azure_config
from src.intent.llm_segment_match.models import TimeIntentLabel, TimeIntentResult

class IntentTimeMatchClient(ABC):

    @abstractmethod
    def request_intent(self, user_prompt: str, system_prompt: str) -> TimeIntentResult:
        pass
class AzureIntentTimeMatchClient(IntentTimeMatchClient):
    def __init__(self):
        self.client = AzureOpenAI(
            api_key=azure_config.api_key,
            azure_endpoint=azure_config.endpoint,
            api_version=azure_config.api_version    
            )
        

    def request_intent(self, user_prompt: str, system_prompt: str) -> TimeIntentResult:
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
                if label == TimeIntentLabel.TIMESTAMP.value:
                    timestamp = function_args.get("timestamp")
                    return TimeIntentResult(label, timestamp)
                else:
                    return TimeIntentResult(label)
            else:
                return TimeIntentResult(TimeIntentLabel.EXTRA.value)
                
        except Exception as e:
            logger.error(f"[IntentTimeMatchClient] {e}", exc_info=True)
            return TimeIntentResult(TimeIntentLabel.EXTRA.value)
