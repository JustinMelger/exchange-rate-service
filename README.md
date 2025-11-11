# exchange-rate-service
service for updating exchange rates in google cloud

## Getting Started

```bash
# Install dependencies with uv (installs into an isolated environment)
uv sync

# Run the FastAPI app locally (default port 8000)
uv run fastapi dev app/main.py --host 0.0.0.0 --port 8000
```

### Design

#### Ingestion Sequence

```mermaid
sequenceDiagram
    participant User as User
    participant CloudRun as Cloud Run (FastAPI)
    participant Ingress as ExchangeRateIngressService
    participant OpenFX as OpenExchange API
    participant BQ as BigQuery
    participant Looker as Looker Studio

    User->>CloudRun: POST /exchange_rates/ingest
    CloudRun->>Ingress: ingest_historical_rates()
    Ingress->>OpenFX: fetch_historical_exchange_rates()
    OpenFX-->>Ingress: exchange_rates_data
    Ingress->>BQ: load staging rows
    Ingress->>BQ: merge staging into prod
    Ingress->>BQ: truncate staging
    CloudRun-->>User: {status: success, inserted_rows}
    Looker ->> BQ: query prod table
    BQ -->> Looker: latest exchange rates

```

#### Domain Overview idea --> will be updated

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

    class ExchangeRateIngressService {
        exchange_client: OpenExchangeClient
        bigquery_client: BigQueryClient
        +ingest_historical_rates(): dict
        -_build_staging_rows(rates): list[dict]

    }

    class ExchangeRateRouter {
        POST /exchange_rates/ingest
    }

    ExchangeRateIngressService --> OpenExchangeClient
    ExchangeRateIngressService --> BigQueryClient
    OpenExchangeClient --> ExchangeRate
    ExchangeRateRouter --> ExchangeRateIngressService : trigger ingest
```
