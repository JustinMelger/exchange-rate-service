from fastapi import APIRouter
from app.external_clients.open_exchange import OpenExchangeClient
from app.database.bigquery import BigQueryClient
from app.services.ingress_service import ExchangeRateIngressService

router = APIRouter()


@router.post("/exchange_rates/ingest")
async def ingest_exchange_rates():
    open_exchange_client = OpenExchangeClient()
    database_client = BigQueryClient()
    exchange_rates = ExchangeRateIngressService(exchange_client=open_exchange_client, bigquery_client=database_client)
    return exchange_rates.ingest_historical_rates()
