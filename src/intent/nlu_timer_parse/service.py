from typing import cast, Any
from transformers import AutoTokenizer, AutoModelForTokenClassification, PreTrainedTokenizerBase, PreTrainedModel, pipeline # type: ignore
import torch
from torch.nn import Module
import os
from uvicorn.main import logger

class IntentNLUTimerParseService:
    """요리 음성 명령 의도 분류기"""

    def __init__(self, model_path: str = "./assets/ner-model") -> None:
        self.model_path: str = model_path
        self.device: torch.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.tens = {
            "십": 10, "열": 10,
            "이십": 20, "스무": 20,
            "삼십": 30, "서른": 30,
            "사십": 40, "마흔": 40,
            "오십": 50, "쉰": 50,
            "육십": 60, "예순": 60,
            "칠십": 70, "일흔": 70,
            "팔십": 80, "여든": 80,
            "구십": 90, "아흔": 90
        }
        self.ones = {
            "일": 1, "한": 1,
            "이": 2, "두": 2,
            "삼": 3, "세": 3,
            "사": 4, "네": 4,
            "오": 5, "다섯": 5,
            "육": 6, "여섯": 6,
            "칠": 7, "일곱": 7,
            "팔": 8, "여덟": 8,
            "구": 9, "아홉": 9
        }
        self.tokenizer = cast(PreTrainedTokenizerBase, None)
        self.model = cast(PreTrainedModel, None)

        self.ner: Any = None
        self._load_model()

    def _load_model(self) -> None:
        """모델과 토크나이저 로드"""
        try:
            if not os.path.exists(self.model_path):
                raise FileNotFoundError(f"모델 경로를 찾을 수 없습니다: {self.model_path}")

            self.tokenizer = cast(PreTrainedTokenizerBase, AutoTokenizer.from_pretrained(self.model_path))  # type: ignore[reportUnknownMemberType]
            self.model = cast(PreTrainedModel, AutoModelForTokenClassification.from_pretrained(self.model_path))  # type: ignore[reportUnknownMemberType]
            cast(Module, self.model).to(self.device)
            cast(Module, self.model).eval()

            self.ner = pipeline("ner",  # type: ignore
                                model=self.model,
                                tokenizer=self.tokenizer,  # type: ignore
                                aggregation_strategy="simple")

        except Exception as e:
            logger.error(f"모델 로딩 실패: {e}")
            raise

    def korean_to_arabic(self, text: str) -> str:
        result = text

        for ten_name, ten_val in self.tens.items():
            for one_name, one_val in self.ones.items():
                compound = ten_name + one_name
                compound_val = str(ten_val + one_val)
                result = result.replace(compound, compound_val)

        all_numbers = {**self.tens, **self.ones}
        sorted_numbers = sorted(all_numbers.items(),
                                key=lambda x: len(x[0]),
                                reverse=True)

        for korean, arabic in sorted_numbers:
            result = result.replace(korean, str(arabic))

        return result


    def parse_time_to_seconds(self, text: str) -> int:
        converted_text = self.korean_to_arabic(text)

        total_seconds = 0

        time_patterns = [
            (r'(\d+)\s*시간', 3600),
            (r'(\d+)\s*분', 60),
            (r'(\d+)\s*초', 1)
        ]

        for pattern, multiplier in time_patterns:
            import re
            matches = re.findall(pattern, converted_text)
            total_seconds += sum(int(m) * multiplier for m in matches)

        return total_seconds

    def extract_time(self, text: str) -> int | None:
        try:
            entities = self.ner(text)  # type: ignore
        except Exception as e:
            logger.error(f"NER 파이프라인 초기화 실패: {e}")
            raise

        time_entities = [str(entity["word"]) for entity in entities  # type: ignore
                         if entity["entity_group"] == "TI"]  # type: ignore
        if not time_entities:
            return None

        total_seconds = sum(self.parse_time_to_seconds(entity) for entity in time_entities)

        return total_seconds