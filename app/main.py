from fastapi import FastAPI
from app.routes import router

app = FastAPI(
    title="API Performance Simulator",
    version="1.0.0",
    description="Synthetic REST API environment for performance data generation"
)

app.include_router(router)