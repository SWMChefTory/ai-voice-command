from enum import Enum


class STTProvider(Enum):
    VITO = "VITO"
    CLOVA = "CLOVA"
    OPENAI = "OPENAI"

class IntentProvider(Enum):
    GPT4_1 = "GPT4.1"
    NLU = "NLU"