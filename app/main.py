import logging
from fastapi import FastAPI
from redis import Redis
from pymongo import MongoClient

from app.api.routes import router as agent_router
from app.core.config import settings
from app.core.logging import configure_logging
from app.services.celery_app import celery_app

app = FastAPI(title="Reperi AI Agent Backend")

configure_logging()

app.include_router(agent_router, prefix="/v1/agent", tags=["agent"])

@app.get("/")
async def root():
    return {"message": "Reperi AI Backend is running"}

@app.get("/health")
async def health_check():
    try:
        redis_client = Redis.from_url(settings.REDIS_URL)
        redis_client.ping()

        mongo_client = MongoClient(settings.MONGODB_URL, serverSelectionTimeoutMS=2000)
        mongo_client.server_info()

        celery_inspect = celery_app.control.inspect()
        workers = celery_inspect.ping() if celery_inspect else None
        if not workers:
            return {"status": "degraded", "error": "No Celery workers available"}

        return {"status": "ok", "redis": "connected", "mongodb": "connected", "celery": "connected"}
    except Exception as exc:
        logging.exception("Health check failed")
        return {"status": "degraded", "error": str(exc)}
