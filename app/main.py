from fastapi import FastAPI
from app.api import ingest
from app.core.logger import create_logger
from app.core.config import settings

create_logger()

app = FastAPI(title=settings.PROJECT_NAME)


# Register routes
app.include_router(ingest.router, tags=["Ingest"])
