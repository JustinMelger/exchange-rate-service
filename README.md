# exchange-rate-service
Service for updating exchange rates with base euro in google bigquery.

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

## Testing

```bash
# Run the entire suite
uv run -m pytest tests

# Run a specific module
uv run -m pytest tests/test_services/test_ingest_service.py
```

## Architecture

For sequence diagrams, class relationships, and data-flow details see [architecture.md](architecture.md).
