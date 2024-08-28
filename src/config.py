import pathlib
from pydantic_settings import BaseSettings, SettingsConfigDict

env_path = pathlib.Path(__file__).parent.resolve() / ".env"


class Settings(BaseSettings):
    DATABASE_URL: str
    ALGORITHM: str
    SECRET_KEY: str
    REDIS_URL: str = "redis://localhost:6379/0"
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_SERVER: str
    MAIL_PORT: int
    MAIL_FROM: str
    MAIL_FROM_NAME: str
    MAIL_STARTTLS: bool = False
    MAIL_SSL_TLS: bool = False
    USE_CREDENTIALS: bool = False
    VALIDATE_CERTS: bool = False
    DOMAIN: str

    model_config = SettingsConfigDict(env_file=env_path, extra="ignore")


settings = Settings()
