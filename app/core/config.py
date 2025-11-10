from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    OPEN_EXCHANGE_API_KEY: str
    OPEN_EXCHANGE_URL: str
    OPEN_EXCHANGE_SYMBOLS: str

    class Config:
        env_file = "app/core/.env"


settings = Settings()
