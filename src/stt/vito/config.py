import os
from pydantic import BaseModel


API_BASE = "https://openapi.vito.ai"


class VitoConfig(BaseModel):
    client_id: str = os.getenv("RTZR_CLIENT_ID") or ""
    client_secret: str = os.getenv("RTZR_CLIENT_SECRET") or ""
    api_base: str = "https://openapi.vito.ai"
    sample_rate: int = 16000
    encoding: str = "LINEAR16"
    use_itn: str = "true"
    use_disfluency_filter: str = "false"
    use_profanity_filter: str = "false"


vito_config = VitoConfig()