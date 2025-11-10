from fastapi import APIRouter

router = APIRouter()


@router.post("/exchange_rates/ingest")
async def ingest_exchange_rates():
    return {"status": "success"}
