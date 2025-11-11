from typing import Any

from app.external_clients.open_exchange import ExchangeRate, OpenExchangeClient
from app.database.bigquery import BigQueryClient
from datetime import datetime, timezone


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

    async def ingest_historical_rates(self, number_of_days: int = 1) -> dict:
        """Fetch historical rates and insert them into the staging table.

         Args:
            number_of_days (int):  Number of consecutive days (including today) to retrieve.

        Returns:
            dict: Contains the inserted row count and raw rate snapshots.
        """
        rates = await self.exchange_client.fetch_historical_exchange_rates(days=number_of_days)
        rows = self._build_staging_rows(rates)
        inserted_rows = 0
        if rows:
            inserted_rows = self.bigquery_client.insert_into_staging(rows)
            self.bigquery_client.merge_staging_into_prod()
            self.bigquery_client.truncate_staging()

        return {"inserted_rows": inserted_rows, "rates": rates}

    def _build_staging_rows(self, rates: list[ExchangeRate]) -> list[dict[str, Any]]:
        """Convert API snapshots into BigQuery staging rows.

        Args:
            rates (list[ExchangeRate]): Snapshots pulled from OpenExchange.

        Returns:
            list[dict[str, Any]]: Row payloads ready for BigQuery.
        """
        ingested_at = datetime.now(timezone.utc).isoformat()
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
                        "ingested_at": ingested_at,
                    }
                )
        return staging_rows
