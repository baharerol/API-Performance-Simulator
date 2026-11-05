# API Performance Simulator

A FastAPI service and traffic generator that produce synthetic API performance data under controlled load scenarios. Built as the data-generation companion to [microservice-latency-prediction](https://github.com/baharerol/microservice-latency-prediction) - the predictive-analytics and explainable-AI graduation project that consumes this data.

## Why

Real production API traffic was out of reach due to privacy and access constraints. This simulator instead produces controlled, reproducible synthetic data with a known scenario structure, so the downstream models can be validated against clearly defined load conditions.

## What it does

- Exposes a REST API with multiple endpoints modeling different workload costs (user, order, search and reporting operations).
- Generates each request's response time dynamically from concurrent active requests, requests-per-second, payload size, time-based load variation, and random spikes - mimicking realistic low- and high-load behavior.
- Drives the API with a traffic generator across 5 scenarios: low, medium, high, spike and mixed.
- Logs, per request: timestamp, endpoint, payload size, response time, status code, concurrent request count and traffic intensity.
- Produces a CSV of ~29,000 records used for modeling in the related project.

## Related project

The generated dataset feeds [microservice-latency-prediction](https://github.com/baharerol/microservice-latency-prediction), which predicts API response times, classifies load into risk levels, and explains predictions with SHAP.

## Tech stack

- **Language:** Python
- **API:** FastAPI (served with uvicorn)
- **Traffic generation:** httpx (async)
- **Data:** pandas

## Setup

```bash
git clone https://github.com/baharerol/API-Performance-Simulator.git
cd API-Performance-Simulator
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS / Linux
pip install -r requirements.txt
```

## Usage

The traffic generator sends requests to the running API, so start the API first, then run the generator in a second terminal.

```bash
# Terminal 1 — start the API
uvicorn main:app --reload
```

```bash
# Terminal 2 — generate the dataset
python generate_traffic.py
```

## Author

Bahar Erol

