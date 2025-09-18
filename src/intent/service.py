from src.intent.exceptions import IntentErrorCode, IntentException
from src.intent.nlu_classify.models import NLUClassifyLabel
from src.intent.llm_classify.models import LLMClassifyLabel
from src.intent.models import Intent
from src.intent.llm_segment_match.service import IntentSegmentMatchService
from src.intent.nlu_classify.service import IntentNLUClassifyService
from src.intent.llm_classify.service import IntentLLMClassifyService
from src.intent.llm_timer_match.service import IntentTimerMatchService
from src.enums import IntentProvider
from src.user_session.recipe.models import RecipeStep
from typing import List, Optional
from src.intent.nlu_timer_extract.service import IntentNLUTimerExtractService
from uvicorn.main import logger
from src.intent.regex_keyword_spotting.service import RegexKeywordSpottingService

class NLUService:
    """NLU 기반 인텐트 분석 서비스"""
    
    def __init__(self,
                 nlu_classify_service: IntentNLUClassifyService,
                 nlu_timer_parse_service: IntentNLUTimerExtractService,
                 ):
        self.nlu_classify_service = nlu_classify_service
        self.nlu_timer_parse_service = nlu_timer_parse_service
    
    def analyze_intent(self, text: str) -> Optional[Intent]:
        matched_intent = self.nlu_classify_service.match_intent(text)
        
        if not matched_intent:
            return None
            
        if matched_intent.label == NLUClassifyLabel.TIMER_SET:
            timer_time = self.nlu_timer_parse_service.extract_time(text)
            if timer_time:
                return Intent(f"{matched_intent.as_string()} {timer_time}", text, IntentProvider.NLU)
            return None
        
        if matched_intent.label == NLUClassifyLabel.WRONG:
            return Intent(NLUClassifyLabel.EXTRA.value, text, IntentProvider.NLU)
        
        if matched_intent.label not in [NLUClassifyLabel.EXTRA, NLUClassifyLabel.TIMER_SET]:
            return Intent(matched_intent.as_string(), text, IntentProvider.NLU)
        
        return None


class LLMService:
    """LLM 기반 인텐트 분석 서비스"""
    
    def __init__(self,
                 classify_service: IntentLLMClassifyService,
                 time_match_service: IntentSegmentMatchService,
                 timer_match_service: IntentTimerMatchService):
        self.classify_service = classify_service
        self.time_match_service = time_match_service
        self.timer_match_service = timer_match_service
    
    def analyze_intent(self, text: str, recipe_steps: List[RecipeStep]) -> Intent:
        classify_intent = self.classify_service.classify_intent(text, len(recipe_steps))
        
        if classify_intent.label == LLMClassifyLabel.TIMESTAMP:
            timestamp_intent = self.time_match_service.time_match(text, recipe_steps)
            return Intent(timestamp_intent.as_string(), text, IntentProvider.GPT4_1)
        
        elif classify_intent.label == LLMClassifyLabel.TIMER:
            timer_intent = self.timer_match_service.timer_match(text)
            return Intent(timer_intent.as_string(), text, IntentProvider.GPT4_1)
        elif classify_intent.label == LLMClassifyLabel.ERROR:
            logger.error(f"[LLMService]: LLM 인텐트 분류 실패: {classify_intent.as_string()}")
            return Intent(LLMClassifyLabel.EXTRA, text, IntentProvider.GPT4_1)
        else:
            return Intent(classify_intent.as_string(), text, IntentProvider.GPT4_1)

class RegexService:
    """정규식 기반 인텐트 분석 서비스"""
    
    def __init__(self, regex_keyword_spotting_service: RegexKeywordSpottingService):
        self.regex_keyword_spotting_service = regex_keyword_spotting_service
    
    def analyze_intent(self, text: str) -> Intent | None:
        return self.regex_keyword_spotting_service.detect(text)


class IntentService:
    """인텐트 분석 서비스"""
    
    def __init__(self,
                 nlu_service: NLUService,
                 llm_service: LLMService,
                 regex_service: RegexService
                 ):
        self.nlu_service = nlu_service
        self.llm_service = llm_service
        self.regex_service = regex_service
    async def analyze(self, base_intent: str, recipe_steps: List[RecipeStep]) -> Intent:
        try:

            regex_result = self.regex_service.analyze_intent(base_intent)
            if regex_result:
                logger.info(f"[IntentService]: Regex 결과: {regex_result.intent}")
                return regex_result

            nlu_result = self.nlu_service.analyze_intent(base_intent)
            if nlu_result:
                logger.info(f"[IntentService]: NLU 결과: {nlu_result.intent}")
                return nlu_result
            
            llm_result = self.llm_service.analyze_intent(base_intent, recipe_steps)
            logger.info(f"[IntentService]: LLM 결과: {llm_result.intent}")
            return llm_result
            
        except IntentException as e:
            logger.error(f"[IntentService]: IntentException 발생 - {e.code.message}")
            raise e
        except Exception as e:
            logger.error(f"[IntentService]: 예상치 못한 오류 발생 - {str(e)}")
            raise IntentException(IntentErrorCode.INTENT_SERVICE_ERROR)