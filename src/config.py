import pathlib
from pydantic_settings import BaseSettings, SettingsConfigDict

env_path = pathlib.Path(__file__).parent.resolve() / ".env"


class Settings(BaseSettings):
    DATABASE_URL: str
    ALGORITHM: str
    SECRET_KEY: str
    REDIS_URL: str = "redis://localhost:6379/0"

    model_config = SettingsConfigDict(env_file=env_path, extra="ignore")


settings = Settings()
