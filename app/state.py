import time
from collections import deque
from threading import Lock


class SimulationState:
    def __init__(self):
        self.active_requests = 0
        self.request_timestamps = deque()
        self.lock = Lock()

    def request_started(self):
        now = time.time()
        with self.lock:
            self.active_requests += 1
            self.request_timestamps.append(now)
            self._cleanup(now)

    def request_finished(self):
        with self.lock:
            self.active_requests = max(0, self.active_requests - 1)

    def _cleanup(self, now: float, window_seconds: int = 60):
        while self.request_timestamps and (now - self.request_timestamps[0]) > window_seconds:
            self.request_timestamps.popleft()

    def get_metrics(self):
        now = time.time()
        with self.lock:
            self._cleanup(now)
            last_10_sec = sum(1 for ts in self.request_timestamps if now - ts <= 10)
            last_60_sec = len(self.request_timestamps)
            rps_10s = last_10_sec / 10
            rps_60s = last_60_sec / 60
            return {
                "active_requests": self.active_requests,
                "requests_last_10s": last_10_sec,
                "requests_last_60s": last_60_sec,
                "rps_10s": round(rps_10s, 3),
                "rps_60s": round(rps_60s, 3),
            }


simulation_state = SimulationState()