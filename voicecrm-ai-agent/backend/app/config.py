from functools import lru_cache
from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_env: str = Field(default="local", alias="APP_ENV")
    database_path: str = Field(default="data/voicecrm.db", alias="DATABASE_PATH")
    crm_provider: str = Field(default="mock", alias="CRM_PROVIDER")
    hubspot_private_app_token: str = Field(default="", alias="HUBSPOT_PRIVATE_APP_TOKEN")
    hubspot_base_url: str = Field(default="https://api.hubapi.com", alias="HUBSPOT_BASE_URL")
    public_base_url: str = Field(default="http://127.0.0.1:8000", alias="PUBLIC_BASE_URL")
    business_name: str = Field(default="Demo Business", alias="BUSINESS_NAME")
    make_webhook_url: str = Field(default="", alias="MAKE_WEBHOOK_URL")
    make_webhook_secret: str = Field(default="", alias="MAKE_WEBHOOK_SECRET")
    ai_provider: str = Field(default="rules", alias="AI_PROVIDER")
    hf_token: str = Field(default="", alias="HF_TOKEN")
    hf_model: str = Field(default="openai/gpt-oss-120b:fastest", alias="HF_MODEL")
    hf_base_url: str = Field(default="https://router.huggingface.co/v1", alias="HF_BASE_URL")

    class Config:
        env_file = ".env"
        populate_by_name = True
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    Path(settings.database_path).parent.mkdir(parents=True, exist_ok=True)
    Path("data").mkdir(parents=True, exist_ok=True)
    return settings
