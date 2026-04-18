from dataclasses import dataclass

@dataclass
class EndpointProfile:
    name: str
    base_latency_ms: float
    jitter_ms: float
    cpu_weight: float
    io_weight: float
    payload_factor: float
    error_base_prob: float


ENDPOINT_PROFILES = {
    "/api/users": EndpointProfile(
        name="users",
        base_latency_ms=80,
        jitter_ms=20,
        cpu_weight=0.6,
        io_weight=0.5,
        payload_factor=0.02,
        error_base_prob=0.005
    ),
    "/api/orders": EndpointProfile(
        name="orders",
        base_latency_ms=120,
        jitter_ms=35,
        cpu_weight=0.9,
        io_weight=0.8,
        payload_factor=0.03,
        error_base_prob=0.010
    ),
    "/api/search": EndpointProfile(
        name="search",
        base_latency_ms=180,
        jitter_ms=60,
        cpu_weight=1.2,
        io_weight=0.6,
        payload_factor=0.05,
        error_base_prob=0.015
    ),
    "/api/reports": EndpointProfile(
        name="reports",
        base_latency_ms=260,
        jitter_ms=80,
        cpu_weight=1.4,
        io_weight=1.1,
        payload_factor=0.08,
        error_base_prob=0.020
    ),
}

WINDOW_SECONDS = 10
MAX_QUEUE_PRESSURE = 100