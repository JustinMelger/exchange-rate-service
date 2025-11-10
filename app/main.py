from fastapi import FastAPI
from app.api import ingest

app = FastAPI()


# Register routes
app.include_router(ingest.router)
