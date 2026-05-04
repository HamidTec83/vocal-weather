from pydantic import BaseModel
from dotenv import load_dotenv
import os

# Charger .env
load_dotenv()


class Settings(BaseModel):
    # Application
    app_name: str = os.getenv("APP_NAME", "Vocal Weather")
    app_version: str = os.getenv("APP_VERSION", "1.0.0")
    env: str = os.getenv("ENV", "development")

    # API
    api_prefix: str = os.getenv("API_PREFIX", "/api/v1")

    # Serveur
    app_host: str = os.getenv("APP_HOST", "127.0.0.1")
    app_port: int = int(os.getenv("APP_PORT", "8000"))

    # Base de données
    db_path: str = os.getenv("DB_PATH", "data/vocal_weather.db")

    # OpenAI
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY")
    stt_provider: str = os.getenv("STT_PROVIDER", "mock")


settings = Settings()