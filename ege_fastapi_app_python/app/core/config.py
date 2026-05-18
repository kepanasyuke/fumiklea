from pathlib import Path
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parents[2]
DEFAULT_DB_PATH = BASE_DIR / "data" / "ege_math.db"

class Settings(BaseSettings):
    DATABASE_URL: str = f"sqlite+aiosqlite:///{DEFAULT_DB_PATH}"
    OPENROUTER_API_KEY: str = ""
    SECRET_KEY: str = "supersecretkey"
    API_TOKEN: str = "ege-token-2026"

    class Config:
        env_file = ".env"

settings = Settings()