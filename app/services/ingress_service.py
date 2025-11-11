from typing import Any

from app.external_clients.open_exchange import ExchangeRate, OpenExchangeClient
from app.database.bigquery import BigQueryClient


class ExchangeRateIngressService:

    def __init__(
        self,
        exchange_client: OpenExchangeClient,
        bigquery_client: BigQueryClient,
    ) -> None:
        self.exchange_client = exchange_client
        self.bigquery_client = bigquery_client

    async def ingest_historical_rates(self) -> dict:
        rates = await self.exchange_client.fetch_historical_exchange_rates()
        rows = self._build_staging_rows(rates)
        inserted_rows = 0
        if rows:
            inserted_rows = self.bigquery_client.insert_into_staging(rows)

        return {"inserted_rows": inserted_rows, "rates": rates}

    def _build_staging_rows(self, rates: list[ExchangeRate]) -> list[dict[str, Any]]:
        staging_rows: list[dict[str, Any]] = []
        for snapshot in rates:
            for currency, rate_eur in snapshot.rates.items():
                if currency == "EUR":
                    continue
                staging_rows.append(
                    {
                        "rate_date": snapshot.day,
                        "currency": currency,
                        "rate_eur": rate_eur,
                    }
                )
        return staging_rows
