from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite+aiosqlite:///./data/ege_math.db"
    OPENROUTER_API_KEY: str = ""
    SECRET_KEY: str = "supersecretkey"
    API_TOKEN: str = "ege-token-2026"

    class Config:
        env_file = ".env"

settings = Settings()