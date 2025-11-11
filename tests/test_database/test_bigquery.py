from unittest.mock import MagicMock

import pytest

from app.database.bigquery import BigQueryClient


@pytest.fixture()
def mocked_bq(monkeypatch) -> MagicMock:
    credentials = MagicMock(name="credentials")
    monkeypatch.setattr(
        "app.database.bigquery.service_account.Credentials.from_service_account_file",
        MagicMock(return_value=credentials),
    )

    client = MagicMock(name="bigquery_client")
    monkeypatch.setattr(
        "app.database.bigquery.bigquery.Client",
        MagicMock(return_value=client),
    )
    return client


def _build_client() -> BigQueryClient:
    return BigQueryClient(
        credential_file="creds.json",
        project_id="demo-project",
        dataset="fx",
        staging_table="stg_exchange_rates",
        prod_table="exchange_rates",
    )


def test_insert_rows_returns_count(mocked_bq: MagicMock) -> None:
    """Inserting rows returns the row count and builds the table ref correctly."""
    mocked_bq.insert_rows_json.return_value = []
    client = _build_client()

    rows = [{"currency": "USD", "rate_eur": 0.92}]
    inserted = client.insert_rows("custom_table", rows)

    assert inserted == 1
    mocked_bq.insert_rows_json.assert_called_once_with("demo-project.fx.custom_table", rows)


def test_insert_rows_short_circuits_empty_payload(mocked_bq: MagicMock) -> None:
    """Empty payload should skip the BigQuery call entirely."""
    client = _build_client()

    assert client.insert_rows("custom_table", []) == 0
    mocked_bq.insert_rows_json.assert_not_called()


def test_insert_into_staging_uses_configured_table(mocked_bq: MagicMock) -> None:
    """Staging helper must forward rows to the configured staging table."""
    mocked_bq.insert_rows_json.return_value = []
    client = _build_client()

    rows = [{"currency": "USD", "rate_eur": 0.93}]
    client.insert_into_staging(rows)

    mocked_bq.insert_rows_json.assert_called_once_with("demo-project.fx.stg_exchange_rates", rows)
