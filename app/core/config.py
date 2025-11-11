from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    OPEN_EXCHANGE_API_KEY: str
    OPEN_EXCHANGE_URL: str
    OPEN_EXCHANGE_SYMBOLS: str
    GOOGLE_PROJECT_ID: str
    BIGQUERY_DATASET: str
    PROJECT_NAME: str = "Exchange Rate Ingress Service"
    GOOGLE_APPLICATION_CREDENTIALS: str = "app/core/gcp.json"
    STAGING_TABLE: str = "stg_exchange_rates"
    PROD_TABLE: str = "exchange_rates"

    class Config:
        env_file = "app/core/.env"


settings = Settings()
