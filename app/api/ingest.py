from fastapi import APIRouter, Depends
from app.external_clients.open_exchange import OpenExchangeClient
from app.database.bigquery import BigQueryClient
from app.services.ingress_service import ExchangeRateIngressService
from app.core.config import settings


router = APIRouter()


def get_exchange_client() -> OpenExchangeClient:
    return OpenExchangeClient(
        base_url=settings.OPEN_EXCHANGE_URL,
        api_key=settings.OPEN_EXCHANGE_API_KEY,
        symbols=settings.OPEN_EXCHANGE_SYMBOLS,
    )


def get_bigquery_client() -> BigQueryClient:
    return BigQueryClient()


def get_ingress_service(
    exchange_client: OpenExchangeClient = Depends(get_exchange_client),
    bigquery_client: BigQueryClient = Depends(get_bigquery_client),
) -> ExchangeRateIngressService:
    return ExchangeRateIngressService(exchange_client=exchange_client, bigquery_client=bigquery_client)


@router.post("/exchange_rates/ingest")
async def ingest_exchange_rates():
    open_exchange_client = OpenExchangeClient(
        base_url=settings.OPEN_EXCHANGE_URL, api_key=settings.OPEN_EXCHANGE_API_KEY, symbols=settings.OPEN_EXCHANGE_SYMBOLS
    )
    database_client = BigQueryClient()
    exchange_rates = ExchangeRateIngressService(exchange_client=open_exchange_client, bigquery_client=database_client)
    return await exchange_rates.ingest_historical_rates()
