from contextvars import ContextVar


def normalize_country_code(raw: str | None) -> str:
    if raw and raw.upper() == "KR":
        return "KR"
    return "US"


country_code_ctx: ContextVar[str] = ContextVar("country_code_ctx", default="US")
