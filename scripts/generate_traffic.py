import os
import csv
import time
import math
import random
import asyncio
from datetime import datetime
import httpx


BASE_URL = "http://127.0.0.1:8000"

OUTPUT_FILE = "data/raw/request_level_data.csv"

ENDPOINTS = [
    ("users", "/api/users"),
    ("orders", "/api/orders"),
    ("search", "/api/search"),
    ("reports", "/api/reports"),
]


SCENARIOS = {
    "low": {
        "duration_sec": 600,
        "base_rps": 3,
        "burstiness": 0.10,
    },
    "medium": {
        "duration_sec": 240,
        "base_rps": 8,
        "burstiness": 0.20,
    },
    "high": {
        "duration_sec": 240,
        "base_rps": 18,
        "burstiness": 0.30,
    },
    "burst": {
        "duration_sec": 180,
        "base_rps": 10,
        "burstiness": 0.80,
    },
    "mixed_day": {
        "duration_sec": 420,
        "base_rps": 12,
        "burstiness": 0.40,
    }
}


def ensure_output_dir():
    os.makedirs("data/raw", exist_ok=True)


def init_csv():
    ensure_output_dir()
    if not os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "request_id",
                "timestamp",
                "scenario",
                "endpoint_name",
                "endpoint_path",
                "payload_size",
                "response_time_ms",
                "status_code",
                "active_requests",
                "rps_10s",
                "requests_last_60s",
                "client_send_ts",
                "client_receive_ts",
                "client_observed_latency_ms"
            ])


def scenario_rps(scenario_name: str, elapsed_sec: int) -> int:
    config = SCENARIOS[scenario_name]
    base_rps = config["base_rps"]
    burstiness = config["burstiness"]

    # Zaman içinde dalgalı trafik
    wave = 1 + 0.35 * math.sin(elapsed_sec / 15.0) + 0.20 * math.sin(elapsed_sec / 5.0)

    # Burst etkisi
    burst_multiplier = 1.0
    if random.random() < burstiness * 0.08:
        burst_multiplier = random.uniform(1.5, 3.5)

    rps = max(1, int(base_rps * wave * burst_multiplier))
    return rps


def choose_endpoint():
    # Daha gerçekçi dağılım
    roll = random.random()
    if roll < 0.35:
        return ENDPOINTS[0]  # users
    elif roll < 0.60:
        return ENDPOINTS[1]  # orders
    elif roll < 0.85:
        return ENDPOINTS[2]  # search
    return ENDPOINTS[3]      # reports


def generate_payload(endpoint_name: str):
    if endpoint_name == "users":
        return random.randint(20, 400)
    elif endpoint_name == "orders":
        return random.randint(50, 900)
    elif endpoint_name == "search":
        return random.randint(10, 250)
    return random.randint(80, 2000)  # reports


async def send_request(client: httpx.AsyncClient, request_id: int, scenario: str):
    endpoint_name, endpoint_path = choose_endpoint()
    payload_size = generate_payload(endpoint_name)

    if endpoint_name in ["users", "orders", "reports"]:
        params = {"size": payload_size}
    else:
        params = {"q_len": max(1, payload_size // 5)}

    client_send_ts = datetime.now().isoformat()
    start = time.perf_counter()

    try:
        response = await client.get(f"{BASE_URL}{endpoint_path}", params=params, timeout=30.0)
        end = time.perf_counter()

        data = response.json()
        client_observed_latency_ms = round((end - start) * 1000, 2)

        return [
            request_id,
            data.get("timestamp"),
            scenario,
            endpoint_name,
            endpoint_path,
            data.get("payload_size"),
            data.get("response_time_ms"),
            data.get("status_code"),
            data.get("active_requests"),
            data.get("rps_10s"),
            data.get("requests_last_60s"),
            client_send_ts,
            datetime.now().isoformat(),
            client_observed_latency_ms,
        ]
    except Exception:
        end = time.perf_counter()
        client_observed_latency_ms = round((end - start) * 1000, 2)

        return [
            request_id,
            datetime.now().isoformat(),
            scenario,
            endpoint_name,
            endpoint_path,
            payload_size,
            None,
            599,
            None,
            None,
            None,
            client_send_ts,
            datetime.now().isoformat(),
            client_observed_latency_ms,
        ]


async def run_scenario(scenario_name: str, start_request_id: int):
    duration = SCENARIOS[scenario_name]["duration_sec"]
    request_id = start_request_id
    rows = []

    async with httpx.AsyncClient() as client:
        for second in range(duration):
            current_rps = scenario_rps(scenario_name, second)
            tasks = []

            for _ in range(current_rps):
                tasks.append(send_request(client, request_id, scenario_name))
                request_id += 1

            second_rows = await asyncio.gather(*tasks)
            rows.extend(second_rows)

            # her saniye ritmini koruyalım
            await asyncio.sleep(1)

    return rows, request_id


def append_rows(rows):
    with open(OUTPUT_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(rows)


async def main():
    init_csv()

    request_id = 1

    ordered_scenarios = [
        "low",
        "medium",
        "high",
        "burst",
        "mixed_day",
    ]

    for scenario in ordered_scenarios:
        print(f"[INFO] Scenario started: {scenario}")
        rows, request_id = await run_scenario(scenario, request_id)
        append_rows(rows)
        print(f"[INFO] Scenario completed: {scenario}, rows={len(rows)}")

    print("[INFO] Traffic generation finished.")


if __name__ == "__main__":
    asyncio.run(main())