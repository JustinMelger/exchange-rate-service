from fastapi import APIRouter
from app.external_clients.open_exchange import OpenExchangeClient
from app.database.bigquery import BigQueryClient
from app.services.ingress_service import ExchangeRateIngressService
from app.core.config import settings


router = APIRouter()


@router.post("/exchange_rates/ingest")
async def ingest_exchange_rates():
    open_exchange_client = OpenExchangeClient(
        base_url=settings.OPEN_EXCHANGE_URL, api_key=settings.OPEN_EXCHANGE_API_KEY, symbols=settings.OPEN_EXCHANGE_SYMBOLS
    )
    database_client = BigQueryClient()
    exchange_rates = ExchangeRateIngressService(exchange_client=open_exchange_client, bigquery_client=database_client)
    return await exchange_rates.ingest_historical_rates()
