from typing import Any

from app.external_clients.open_exchange import ExchangeRate, OpenExchangeClient
from app.database.bigquery import BigQueryClient


class ExchangeRateIngressService:
    """Coordinate fetching exchange rates and loading them into BigQuery."""

    def __init__(
        self,
        exchange_client: OpenExchangeClient,
        bigquery_client: BigQueryClient,
    ) -> None:
        """Initialize the service.

        Args:
            exchange_client (OpenExchangeClient): OpenExchange data source.
            bigquery_client (BigQueryClient): BigQuery data access object.
        """
        self.exchange_client = exchange_client
        self.bigquery_client = bigquery_client

    async def ingest_historical_rates(self) -> dict:
        """Fetch historical rates and insert them into the staging table.

        Returns:
            dict: Contains the inserted row count and raw rate snapshots.
        """
        rates = await self.exchange_client.fetch_historical_exchange_rates()
        rows = self._build_staging_rows(rates)
        inserted_rows = 0
        if rows:
            inserted_rows = self.bigquery_client.insert_into_staging(rows)

        return {"inserted_rows": inserted_rows, "rates": rates}

    def _build_staging_rows(self, rates: list[ExchangeRate]) -> list[dict[str, Any]]:
        """Convert API snapshots into BigQuery staging rows.

        Args:
            rates (list[ExchangeRate]): Snapshots pulled from OpenExchange.

        Returns:
            list[dict[str, Any]]: Row payloads ready for BigQuery.
        """
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
