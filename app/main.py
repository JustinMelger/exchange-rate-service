from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.api import ingest
from app.core.logger import create_logger
from app.core.config import settings
from app.core.errors import IngestServiceError
from datetime import datetime, timezone


create_logger()

app = FastAPI(title=settings.PROJECT_NAME)


@app.exception_handler(IngestServiceError)
async def ingest_service_exception_handler(request: Request, exc: IngestServiceError):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "message": exc.detail,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )


# Register routes
app.include_router(ingest.router, tags=["Ingest"])
