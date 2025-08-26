from src.intent.exceptions import IntentErrorCode, IntentException
from src.intent.models import Intent
from src.intent.utils import CaptionLoader, StepsLoader
from src.intent.time_match.service import IntentTimeMatchService
from src.intent.pattern_match.service import IntentPatternMatchService
from src.intent.classify.service import IntentClassifyService
from src.intent.timer_match.service import IntentTimerMatchService
from src.models import IntentProvider
from src.user_session.recipe.models import RecipeCaption, RecipeStep
from typing import List


class IntentService:
    def __init__(self,
                 caption_loader: CaptionLoader,
                 steps_loader: StepsLoader,
                 intent_time_match_service: IntentTimeMatchService,
                 intent_pattern_match_service: IntentPatternMatchService,
                 intent_classify_service: IntentClassifyService,
                 intent_timer_match_service: IntentTimerMatchService
                 ):
        self.caption_loader = caption_loader
        self.steps_loader = steps_loader
        self.intent_time_match_service = intent_time_match_service
        self.intent_pattern_match_service = intent_pattern_match_service
        self.intent_classify_service = intent_classify_service
        self.intent_timer_match_service = intent_timer_match_service

    async def analyze(self, base_intent: str, recipe_captions: List[RecipeCaption],
                      recipe_steps: List[RecipeStep]) -> Intent:
        try:
            matched_intent = self.intent_pattern_match_service.match_intent(base_intent)

            if matched_intent and matched_intent != "EXTRA":
                if matched_intent == "WRONG":
                    return Intent("EXTRA", base_intent, IntentProvider.REGEX)
                return Intent(matched_intent, base_intent, IntentProvider.REGEX)

            filtered_intent = self.intent_classify_service.classify_intent(base_intent, len(recipe_steps))
            if filtered_intent == "TIMESTAMP":
                timestamp_intent = self.intent_time_match_service.time_match(base_intent, recipe_captions)
                return Intent(timestamp_intent, base_intent, IntentProvider.GPT4_1)
            elif filtered_intent == "TIMER":
                timer_intent = self.intent_timer_match_service.timer_match(base_intent)
                return Intent(timer_intent, base_intent, IntentProvider.GPT4_1)
            else:
                return Intent(filtered_intent, base_intent, IntentProvider.GPT4_1)

        except IntentException:
            raise IntentException(IntentErrorCode.INTENT_SERVICE_ERROR)
        except Exception:
            raise IntentException(IntentErrorCode.INTENT_SERVICE_ERROR)