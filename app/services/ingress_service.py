from app.external_clients.open_exchange import OpenExchangeClient
from app.database.bigquery import BigQueryClient


class ExchangeRateIngressService:

    def __init__(
        self,
        exchange_client: OpenExchangeClient,
        bigquery_client: BigQueryClient,
    ) -> None:
        self.exchange_client = exchange_client
        self.bigquery_client = bigquery_client

    def ingest_historical_rates(self) -> dict:

        self.exchange_client.fetch_historical_exchange_rates()
        status = self.bigquery_client.execute_query()

        return status
