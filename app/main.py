from fastapi import FastAPI
from app.api import ingest
from app.core.logger import create_logger

create_logger()

app = FastAPI()


# Register routes
app.include_router(ingest.router)
