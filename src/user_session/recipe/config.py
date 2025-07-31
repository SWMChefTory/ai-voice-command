from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class RecipeConfig(BaseSettings):
    api_base: str = Field(default="", alias="RECIPE_API_BASE")

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        validate_assignment=True,
        extra="ignore",
    )

recipe_config = RecipeConfig()