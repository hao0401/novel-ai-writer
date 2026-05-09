from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "基于大模型的网络小说创作与投稿辅助系统"
    secret_key: str = "dev-secret"
    access_token_expire_minutes: int = 60 * 24 * 7
    database_url: str = "mysql+pymysql://root:123456@localhost:3306/novel_ai_writer?charset=utf8mb4"
    ai_provider: str = "openai"
    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"
    openai_base_url: str | None = None

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()
