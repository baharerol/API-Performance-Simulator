import math
import random
from datetime import datetime
from app.config import ENDPOINT_PROFILES


def get_time_of_day_factor(ts: datetime) -> float:
    """
    Günün saatine göre yoğunluk etkisi.
    Öğlen ve akşam üstü yoğunluğu biraz artırıyoruz.
    """
    hour = ts.hour + ts.minute / 60
    peak1 = math.exp(-((hour - 13) ** 2) / 8)   # öğlen piki
    peak2 = math.exp(-((hour - 18) ** 2) / 10)  # akşamüstü piki
    return 1 + 0.25 * peak1 + 0.20 * peak2


def get_spike_factor() -> float:
    """
    Bazen sistemde kısa süreli beklenmeyen gecikmeler oluşsun.
    """
    p = random.random()
    if p < 0.02:
        return random.uniform(1.8, 3.2)  # güçlü spike
    elif p < 0.08:
        return random.uniform(1.2, 1.7)  # hafif spike
    return 1.0


def calculate_latency_and_status(
    endpoint: str,
    active_requests: int,
    rps_10s: float,
    payload_size: int,
):
    profile = ENDPOINT_PROFILES[endpoint]
    now = datetime.now()

    base = profile.base_latency_ms
    jitter = random.gauss(0, profile.jitter_ms)

    # eşzamanlı istek arttıkça kuyruk etkisi
    concurrency_factor = 1 + (active_requests / 40.0) ** 1.35

    # son 10 saniyedeki yük etkisi
    traffic_factor = 1 + (rps_10s / 25.0) ** 1.20

    # payload etkisi
    payload_effect = payload_size * profile.payload_factor

    # gün içi etki
    tod_factor = get_time_of_day_factor(now)

    # ani dalgalanmalar
    spike_factor = get_spike_factor()

    raw_latency = (
        (base + payload_effect + jitter)
        * concurrency_factor
        * traffic_factor
        * tod_factor
        * spike_factor
    )

    latency_ms = max(20, raw_latency)

    # Hata olasılığı da yük arttıkça artsın
    error_prob = (
        profile.error_base_prob
        + min(0.10, active_requests / 1500)
        + min(0.08, rps_10s / 1200)
    )

    roll = random.random()
    if roll < error_prob * 0.35:
        status_code = 500
    elif roll < error_prob:
        status_code = 503
    else:
        status_code = 200

    return round(latency_ms, 2), status_code