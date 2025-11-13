# exchange-rate-service
FastAPI service that fetches Open Exchange Rates data, normalizes it to a EUR base, and writes both staging and production tables in Google BigQuery on demand.

## Requirements

- Python 3.13+
- [uv](https://github.com/astral-sh/uv) for dependency management
- Access to a Google Cloud project with BigQuery enabled
- Open Exchange API key

## Getting Started

```bash
# Install dependencies with uv (installs into an isolated environment)
uv sync

# Run the FastAPI app locally (default port 8000)
uv run fastapi dev app/main.py --host 0.0.0.0 --port 8000

# Build and run with Docker
docker build -t exchange-rate-service .
docker run --rm -p 8000:8000 exchange-rate-service
```

Copy `app/core/.env.example` to `app/core/.env` and fill in the required API keys and BigQuery settings before running locally.

### Triggering an ingest run
- **HTTP**: `POST http://localhost:8000/exchange_rates/ingest?days=30` triggers a fetch/merge for the most recent 30 days (0–31 days allowed). The response includes inserted row count and timestamps.
- **Docs/Swagger**: browse to `http://localhost:8000/docs` (Swagger UI) or `http://localhost:8000/redoc` to trigger the endpoint interactively and inspect request/response schemas.


### `.env` quick reference

Add the values that the service needs in `app/core/.env`. Example values shown below:

```
OPEN_EXCHANGE_API_KEY=pk_test_replace_me
OPEN_EXCHANGE_URL=https://openexchangerates.org/api
OPEN_EXCHANGE_SYMBOLS=EUR,USD,GBP
GOOGLE_PROJECT_ID=my-gcp-project
BIGQUERY_DATASET=exchange_rates
GOOGLE_APPLICATION_CREDENTIALS=/abs/path/to/service-account.json
STAGING_TABLE=exchange_rates.staging_rates
PROD_TABLE=exchange_rates.rates
```

`OPEN_EXCHANGE_SYMBOLS` must include `EUR` (the service converts other currencies relative to EUR), otherwise ingestion fails.

See the [Open Exchange Rates currency list](https://openexchangerates.org/currencies) for the full set of supported codes you can include.

### Creating a Google Cloud service account

1. In the GCP console, go to **IAM & Admin → Service Accounts** and create an account with `BigQuery Data Editor` (or a restricted custom role that can insert/merge rows in your target dataset).
2. Generate a JSON key for that account and download it locally.
3. Point `GOOGLE_APPLICATION_CREDENTIALS` in `.env` to the absolute path of the downloaded JSON file so that the BigQuery client can authenticate.

### BigQuery tables

- Create the dataset referenced by `BIGQUERY_DATASET` and two tables that match `STAGING_TABLE` and `PROD_TABLE`.
- Both tables use the same schema: `rate_date DATE`, `currency STRING`, `rate_eur NUMERIC`, plus `ingested_at TIMESTAMP` in staging and `last_updated_at TIMESTAMP` in prod.
- The app does **not** auto-create these tables; provision them manually or through IaC before running ingestion. See the “Data Model” section in [architecture.md](architecture.md) for a diagram.

## Testing

```bash
# Run the entire suite
uv run -m pytest tests

# Run a specific module
uv run -m pytest tests/test_services/test_ingest_service.py
```

## Linting & Style

```bash
# Static analysis and formatting checks
uv run ruff check .
uv run ruff format --check .
```

Use `uv run ruff format .` before committing if formatting changes are needed.

## Commit Guidelines

Follow [Conventional Commits](https://www.conventionalcommits.org/) so that CI/CD automation can generate clean change logs. Example prefixes: `feat:`, `fix:`, `chore:`, `docs:`, `refactor:`.

## Architecture

For sequence diagrams, class relationships, and data-flow details see [architecture.md](architecture.md).

## Limitations

- Async throttling: there is currently no `asyncio.Semaphore` or request throttling in the Open Exchange client, so a large backfill will issue many concurrent HTTP calls and may hit rate limits. Add a semaphore or exponential backoff before running extremely large batches.
- Large historical backfills: the merge job is tuned for ≤30 days of rates and a moderate currency list. Requesting more history or hundreds of symbols in one run leads to very large payloads, which can exceed Open Exchange payload limits and BigQuery merge memory quotas. Break up long ranges or large symbol sets into smaller batches.
- Authentication: the ingest endpoint has no authentication/authorization yet. Do not expose it publicly until you add API keys, IAM, or some other access control (e.g., Cloud Run IAM + IAP).

## Open Exchange

- Open Exchange counts each historical day fetch as a request. Large backfills can quickly consume your monthly quota; consider caching or running incremental jobs instead of full history reloads.
- The free (Developer) plan allows about 1,000 requests per month and caps bursts at roughly 60 requests per minute. 
- Review the latest plan specifics at [openexchangerates.org/signup](https://openexchangerates.org/signup)
