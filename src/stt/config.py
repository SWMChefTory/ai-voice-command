from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

COMMAND_KEYWORDS = [
    "다음", "다음 단계", "다음 스텝", "다음 순서", "다음으로", "넘어가", "계속", "계속해", "진행", "진행해",
    "이전", "전 단계", "이전 스텝", "이전 순서", "되돌아가", "되돌려", "뒤로", "뒤로 가", "처음으로",
    "타이머", "타이머 시작", "타이머 멈춰", "타이머 정지", "타이머 종료", "타이머 체크", "스톱워치",
    "시간 재", "시간 재줘", "5분 타이머", "타이머 꺼"
]


class VitoConfig(BaseSettings):
    client_id: str = Field(default="", alias="RTZR_CLIENT_ID")
    client_secret: str = Field(default="", alias="RTZR_CLIENT_SECRET")
    api_base: str = "https://openapi.vito.ai"
    model_name: str = "sommers_ko"
    sample_rate: int = 16000
    encoding: str = "LINEAR16"
    use_itn: str = "False"
    use_disfluency_filter: str = "True"
    use_profanity_filter: str = "False"
    keywords: str = ",".join(COMMAND_KEYWORDS)
    keywords_boost: int = 16
    domain: str = "MEETING"

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        validate_assignment=True,
        extra="ignore",
    )


class NaverClovaConfig(BaseSettings):
    access_token: str = Field(default="", alias="CLOVA_ACCESS_TOKEN")
    grpc_server: str = "clovaspeech-gw.ncloud.com:50051"
    language: str = "ko"
    skip_empty_text: bool = True
    use_word_epd: bool = False
    use_period_epd: bool = True
    gap_threshold: int = 500
    duration_threshold: int = 5000

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        validate_assignment=True,
        extra="ignore",
    )


class OpenAIConfig(BaseSettings):
    api_key: str = Field(default="", alias="OPENAI_API_KEY")
    api_base: str = "wss://api.openai.com/v1/realtime?intent=transcription"
    input_audio_format: str = "pcm16"
    model: str = "gpt-4o-transcribe"
    language: str = "ko"
    vad_threshold: float = 0.5
    prefix_padding_ms: int = 300
    silence_duration_ms: int = 500
    noise_reduction_type: str = "far_field"

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        validate_assignment=True,
        extra="ignore",
    )


vito_config = VitoConfig()
naver_clova_config = NaverClovaConfig()
openai_config = OpenAIConfig()