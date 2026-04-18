import os
import pandas as pd

RAW_FILE = "data/raw/request_level_data.csv"
PROCESSED_FILE = "data/processed/window_level_data.csv"

WINDOW = "30S"  # 30 saniyelik pencere


def main():
    os.makedirs("data/processed", exist_ok=True)

    df = pd.read_csv(RAW_FILE)

    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df = df.dropna(subset=["timestamp"])

    df["is_error"] = df["status_code"].apply(lambda x: 1 if x >= 500 else 0)
    df["is_success"] = df["status_code"].apply(lambda x: 1 if x == 200 else 0)

    agg = (
        df.set_index("timestamp")
        .groupby("scenario")
        .resample(WINDOW)
        .agg(
            total_requests=("request_id", "count"),
            avg_response_time_ms=("response_time_ms", "mean"),
            median_response_time_ms=("response_time_ms", "median"),
            max_response_time_ms=("response_time_ms", "max"),
            min_response_time_ms=("response_time_ms", "min"),
            std_response_time_ms=("response_time_ms", "std"),
            avg_payload_size=("payload_size", "mean"),
            avg_active_requests=("active_requests", "mean"),
            avg_rps_10s=("rps_10s", "mean"),
            avg_requests_last_60s=("requests_last_60s", "mean"),
            error_count=("is_error", "sum"),
            success_count=("is_success", "sum"),
        )
        .reset_index()
    )

    agg["error_rate"] = agg["error_count"] / agg["total_requests"]
    agg["success_rate"] = agg["success_count"] / agg["total_requests"]

    agg.to_csv(PROCESSED_FILE, index=False, encoding="utf-8")
    print(f"[INFO] Saved: {PROCESSED_FILE}")


if __name__ == "__main__":
    main()