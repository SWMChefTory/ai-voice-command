from typing import Dict, Mapping, Optional, cast
from transformers import AutoTokenizer, AutoModelForSequenceClassification, PreTrainedTokenizerBase, PreTrainedModel
from transformers.modeling_outputs import SequenceClassifierOutput
import torch
from torch.nn import Module
import os
from uvicorn.main import logger


class IntentPatternMatchService:
    """요리 음성 명령 의도 분류기"""

    def __init__(self, model_path: str = "./assets/pattern-match-intent-model") -> None:
        self.model_path: str = model_path
        self.device: torch.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.label_map: Dict[int, str] = {
            0: "NEXT",
            1: "PREV",
            2: "TIMER START",
            3: "TIMER STOP",
            4: "TIMER CHECK",
            5: "EXTRA",
            6: "WRONG"
        }
        self.tokenizer = cast(PreTrainedTokenizerBase, None)
        self.model = cast(PreTrainedModel, None)

        # FastAPI 앱 시작 시 모델 로드
        self._load_model()

    def _load_model(self) -> None:
        """모델과 토크나이저 로드"""
        try:
            if not os.path.exists(self.model_path):
                raise FileNotFoundError(f"모델 경로를 찾을 수 없습니다: {self.model_path}")

            logger.info(f"📂 모델 로딩 중: {self.model_path}")
            self.tokenizer = cast(PreTrainedTokenizerBase, AutoTokenizer.from_pretrained(self.model_path))  # type: ignore[reportUnknownMemberType]
            self.model = cast(PreTrainedModel, AutoModelForSequenceClassification.from_pretrained(self.model_path))  # type: ignore[reportUnknownMemberType]
            cast(Module, self.model).to(self.device)
            cast(Module, self.model).eval()
            logger.info(f"모델 로딩 완료")

        except Exception as e:
            logger.error(f"모델 로딩 실패: {e}")
            raise

    def match_intent(self, text: str) -> Optional[str]:
        try:
            encoding = cast(Mapping[str, torch.Tensor], self.tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                padding=True,
                max_length=128
            ))
            inputs: Dict[str, torch.Tensor] = {k: v.to(self.device) for k, v in encoding.items()}

            with torch.no_grad():
                outputs = cast(SequenceClassifierOutput, self.model(**inputs))
                assert outputs.logits is not None
                probs: torch.Tensor = torch.nn.functional.softmax(outputs.logits, dim=-1)[0]
                predicted_idx: int = int(torch.argmax(probs).item())
                confidence: float = float(probs[predicted_idx])

            logger.info(f"의도 분류 결과: {self.label_map[predicted_idx]} (신뢰도: {confidence})")

            if confidence < 0.9:
                return "EXTRA"

            return self.label_map[predicted_idx]

        except Exception as e:
            logger.error(f"의도 분류 실패: {e}")
            return "EXTRA"