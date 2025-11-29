from fastapi import FastAPI
from app.api.routes import router as agent_router

app = FastAPI(title="Reperi AI Agent Backend")

app.include_router(agent_router, prefix="/v1/agent", tags=["agent"])

@app.get("/")
async def root():
    return {"message": "Reperi AI Backend is running"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}
