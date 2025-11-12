# Architecture

## Ingestion Sequence

```mermaid
sequenceDiagram
    participant User as User
    participant CloudRun as Cloud Run (FastAPI)
    participant Ingest as ExchangeRateIngestService
    participant OpenFX as OpenExchange API
    participant BQ as BigQuery
    participant Looker as Looker Studio

    User->>CloudRun: POST /exchange_rates/ingest
    CloudRun->>Ingest: ingest_historical_rates()
    Ingest->>OpenFX: fetch_historical_exchange_rates()
    OpenFX-->>Ingest: exchange_rates_data
    Ingest->>BQ: load staging rows
    Ingest->>BQ: merge staging into prod
    Ingest->>BQ: truncate staging
    CloudRun-->>User: {status: success, inserted_rows}
    Looker ->> BQ: query prod table
    BQ -->> Looker: latest exchange rates
```

## Domain Overview

```mermaid
classDiagram
    class OpenExchangeClient {
        -base_url: str
        -api_key: str
        -symbols: str
        +fetch_historical_exchange_rates(days:int): list[ExchangeRate]
        +convert_to_euro_base(euro_rate: float, rates: dict): dict
    }

    class ExchangeRate {
        day: str
        rates: dict[str, float]
    }

    class BigQueryClient {
        -project_id: str
        -dataset: str
        -staging_table: str
        -prod_table: str
        +insert_rows(table, rows): int
        +insert_into_staging(rows): int
        +execute_query(query): RowIterator
    }

    class ExchangeRateIngestService {
        exchange_client: OpenExchangeClient
        bigquery_client: BigQueryClient
        +ingest_historical_rates(): dict
        -_build_staging_rows(rates): list[dict]
    }

    class ExchangeRateRouter {
        POST /exchange_rates/ingest
    }

    ExchangeRateIngestService --> OpenExchangeClient
    ExchangeRateIngestService --> BigQueryClient
    OpenExchangeClient --> ExchangeRate
    ExchangeRateRouter --> ExchangeRateIngestService : trigger ingest
```

## Data Model

```mermaid
erDiagram
    STAGING ||--|| PROD : "merge on rate_date + currency"
    STAGING {
        DATE rate_date
        STRING currency
        NUMERIC rate_eur
        TIMESTAMP ingested_at
    }
    PROD {
        DATE rate_date
        STRING currency
        NUMERIC rate_eur
        TIMESTAMP last_updated_at
    }
```

## Update Strategy

This pipeline uses a `MERGE` to keep the production table synchronized with the latest rates:
- Daily payloads are small, so merging a few rows is operationally cheap.
- `MERGE` statements update changed currencies and insert new ones in a single job, keeping the table current without extra deduplication steps.
- A single prod table stays query-ready for Looker, instead of maintaining an additional self-updating view over append-only history.

After each merge, the staging table is truncated to keep the next ingest run clean:
- Clearing staging avoids accidentally reprocessing stale rows or inflating merge windows.
- Truncate operations in BigQuery are metadata-only, so they finish quickly even for large tables.
- Keeping staging empty between loads simplifies monitoring and makes it obvious if a run fails before merge.
