import os
from pydantic import BaseModel

COMMAND_KEYWORDS = [
    "다음", "다음 단계", "넘어가", "계속",
    "이전", "전 단계", "뒤로",
]

class VitoConfig(BaseModel):
    client_id: str = os.getenv("RTZR_CLIENT_ID") or ""
    client_secret: str = os.getenv("RTZR_CLIENT_SECRET") or ""
    api_base: str = "https://openapi.vito.ai"
    model_name: str = "sommers_ko"
    sample_rate: int = 16000
    encoding: str = "LINEAR16"
    use_itn: str = "false"
    use_disfluency_filter: str = "true"
    use_profanity_filter: str = "false"
    keywords: str = ",".join(COMMAND_KEYWORDS)
    keywords_boost: int = 16
    domain: str = "CALL"


vito_config = VitoConfig()