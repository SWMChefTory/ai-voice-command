from enum import Enum
from typing import Optional

class LLMIngredientMatchLabel(str, Enum):
    INGREDIENT = "INGREDIENT"
    EXTRA = "EXTRA"
    ERROR = "ERROR"

class LLMIngredientMatchResult:
    def __init__(self, raw_label: str, ingredient: Optional[str] = None):
        self.label: LLMIngredientMatchLabel
        self.ingredient: Optional[str] = ingredient

        if raw_label == LLMIngredientMatchLabel.INGREDIENT.value:
            if ingredient is not None and ingredient.strip():
                self.label = LLMIngredientMatchLabel.INGREDIENT
                self.ingredient = ingredient.strip()
                return
            else:
                self.label = LLMIngredientMatchLabel.ERROR
                return

        if raw_label == LLMIngredientMatchLabel.EXTRA.value:
            self.label = LLMIngredientMatchLabel.EXTRA
            return

        self.label = LLMIngredientMatchLabel.ERROR

    def as_string(self) -> str:
        if self.label == LLMIngredientMatchLabel.INGREDIENT and self.ingredient is not None:
            return f"{self.label.value} {self.ingredient}"
        return self.label.value