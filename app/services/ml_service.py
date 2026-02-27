import httpx
from app.config import ML_SERVICE_URL

async def call_ml_service(resume_json):
    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(ML_SERVICE_URL, json=resume_json)
        response.raise_for_status()
        return response.json()