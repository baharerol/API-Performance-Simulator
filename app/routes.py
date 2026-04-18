import asyncio
import random
from datetime import datetime
from fastapi import APIRouter, Query
from app.state import simulation_state
from app.simulator import calculate_latency_and_status

router = APIRouter()

AVAILABLE_ENDPOINTS = [
    "/api/users",
    "/api/orders",
    "/api/search",
    "/api/reports",
]


async def process_request(endpoint: str, payload_size: int):
    simulation_state.request_started()
    metrics_before = simulation_state.get_metrics()

    active_requests = metrics_before["active_requests"]
    rps_10s = metrics_before["rps_10s"]

    latency_ms, status_code = calculate_latency_and_status(
        endpoint=endpoint,
        active_requests=active_requests,
        rps_10s=rps_10s,
        payload_size=payload_size,
    )

    await asyncio.sleep(latency_ms / 1000.0)

    simulation_state.request_finished()
    metrics_after = simulation_state.get_metrics()

    return {
        "timestamp": datetime.now().isoformat(),
        "endpoint": endpoint,
        "payload_size": payload_size,
        "response_time_ms": latency_ms,
        "status_code": status_code,
        "active_requests": active_requests,
        "rps_10s": rps_10s,
        "requests_last_60s": metrics_before["requests_last_60s"],
        "active_requests_after": metrics_after["active_requests"],
    }


@router.get("/api/users")
async def get_users(size: int = Query(default=50, ge=1, le=2000)):
    return await process_request("/api/users", size)


@router.get("/api/orders")
async def get_orders(size: int = Query(default=80, ge=1, le=3000)):
    return await process_request("/api/orders", size)


@router.get("/api/search")
async def search(q_len: int = Query(default=20, ge=1, le=500)):
    payload_size = q_len * random.randint(5, 20)
    return await process_request("/api/search", payload_size)


@router.get("/api/reports")
async def get_reports(size: int = Query(default=120, ge=1, le=5000)):
    return await process_request("/api/reports", size)


@router.get("/health")
async def health():
    return {"status": "ok", "timestamp": datetime.now().isoformat()}