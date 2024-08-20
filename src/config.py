import pathlib
from pydantic_settings import BaseSettings, SettingsConfigDict

env_path = pathlib.Path(__file__).parent.resolve() / ".env"


class Settings(BaseSettings):
    DATABASE_URL: str

    model_config = SettingsConfigDict(env_file=env_path, extra="ignore")


settings = Settings()
