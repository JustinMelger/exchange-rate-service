from unittest.mock import AsyncMock, MagicMock

import pytest

from app.external_clients.open_exchange import ExchangeRate
from app.services.ingest_service import ExchangeRateIngestService


def build_service(rates: list[ExchangeRate]) -> ExchangeRateIngestService:
    exchange_client = MagicMock()
    exchange_client.fetch_historical_exchange_rates = AsyncMock(return_value=rates)

    bigquery_client = MagicMock()
    bigquery_client.insert_into_staging.return_value = len(
        [1 for snapshot in rates for currency in snapshot.rates if currency != "EUR"]
    )

    return ExchangeRateIngestService(exchange_client=exchange_client, bigquery_client=bigquery_client)


def test_build_staging_rows_skips_eur_currency():
    """Ensure staging rows exclude EUR entries and keep other fields."""
    service = build_service([])
    rates = [
        ExchangeRate(day="2024-01-01", rates={"EUR": 1.0, "USD": 1.08, "GBP": 0.86}),
    ]

    rows = service._build_staging_rows(rates)

    assert len(rows) == 2
    currencies = {row["currency"] for row in rows}
    assert currencies == {"USD", "GBP"}
    assert all(row["rate_date"] == "2024-01-01" for row in rows)


@pytest.mark.asyncio
async def test_ingest_historical_rates_inserts_and_merges():
    """Verify a successful ingest stages, merges, and truncates once."""
    rates = [
        ExchangeRate(day="2024-01-02", rates={"USD": 1.07}),
        ExchangeRate(day="2024-01-03", rates={"JPY": 160.0}),
    ]
    service = build_service(rates)

    result = await service.ingest_historical_rates(number_of_days=1)

    service.bigquery_client.insert_into_staging.assert_called_once()
    service.bigquery_client.merge_staging_into_prod.assert_called_once()
    service.bigquery_client.truncate_staging.assert_called_once()
    assert result["inserted_rows"] == 2
    assert result["days_requested"] == 1
    assert result["staging_merged"] is True
    assert result["staging_truncated"] is True
    assert "ingested_at" in result


@pytest.mark.asyncio
async def test_ingest_historical_rates_skips_bigquery_when_no_rows():
    """No BigQuery calls should run when all currencies were filtered out."""
    rates = [
        ExchangeRate(day="2024-01-04", rates={"EUR": 1.0}),
    ]
    service = build_service(rates)

    result = await service.ingest_historical_rates(number_of_days=1)

    service.bigquery_client.insert_into_staging.assert_not_called()
    service.bigquery_client.merge_staging_into_prod.assert_not_called()
    service.bigquery_client.truncate_staging.assert_not_called()
    assert result["inserted_rows"] == 0
    assert result["staging_merged"] is False
    assert result["staging_truncated"] is False
