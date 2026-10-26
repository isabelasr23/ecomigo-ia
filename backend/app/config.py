from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=Path(__file__).resolve().parents[2] / '.env', extra='ignore')
    database_url: str = 'postgresql+psycopg://ecomigo:ecomigo@localhost:55432/ecomigo'
    ai_provider: str = 'gemini'
    gemini_api_key: str = ''
    gemini_model: str = 'gemini-3.8-flash'
    openai_api_key: str = ''
    openai_model: str = 'gpt-4.1-mini'
    ai_timeout_seconds: float = 45
    cors_origins: str = 'http://localhost:5173,http://127.0.0.1:5173'

settings = Settings()
