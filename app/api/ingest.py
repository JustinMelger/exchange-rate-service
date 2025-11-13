from typing import Annotated

from fastapi import APIRouter, Depends, Query
from app.external_clients.open_exchange import OpenExchangeClient
from app.database.bigquery import BigQueryClient
from app.services.ingest_service import ExchangeRateIngestService
from app.core.config import settings


router = APIRouter()


def get_exchange_client() -> OpenExchangeClient:
    return OpenExchangeClient(
        base_url=settings.OPEN_EXCHANGE_URL,
        api_key=settings.OPEN_EXCHANGE_API_KEY,
        symbols=settings.OPEN_EXCHANGE_SYMBOLS,
    )


def get_bigquery_client() -> BigQueryClient:
    return BigQueryClient(
        credential_file=settings.GOOGLE_APPLICATION_CREDENTIALS,
        project_id=settings.GOOGLE_PROJECT_ID,
        dataset=settings.BIGQUERY_DATASET,
        staging_table=settings.STAGING_TABLE,
        prod_table=settings.PROD_TABLE,
    )


def get_ingest_service(
    exchange_client: OpenExchangeClient = Depends(get_exchange_client),
    bigquery_client: BigQueryClient = Depends(get_bigquery_client),
) -> ExchangeRateIngestService:
    return ExchangeRateIngestService(exchange_client=exchange_client, bigquery_client=bigquery_client)


@router.post("/exchange_rates/ingest")
async def ingest_exchange_rates(
    days: Annotated[int, Query(ge=0, le=31)] = 30,
    ingest_service: ExchangeRateIngestService = Depends(get_ingest_service),
) -> dict:
    return await ingest_service.ingest_historical_rates(number_of_days=days)
