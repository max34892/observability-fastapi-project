from fastapi import FastAPI, Request
from prometheus_client import Counter, Histogram, generate_latest
from starlette.responses import Response
from fastapi import HTTPException
import time

app = FastAPI()

REQUEST_COUNT = Counter(
    "api_requests_total", "Total API Requests", ["method", "endpoint" "status_code"]
)

REQUEST_LATENCY = Histogram(
    "api_request_duration_seconds", "API Latency", ["endpoint"]
)

@app.middleware("http")
async def track_metrics(request: Request, call_next):
    start_time = time.time()

    response = await call_next(request)

    process_time = time.time() - start_time
    status_code = response.status_code

    REQUEST_COUNT.labels(
        request.method,
        request.url.path,
        str(status_code)
    ).inc()
    REQUEST_LATENCY.labels(request.url.path).observe(process_time)

    return response

@app.get("/")
def read_root():
    return {"message": "Hello Observability"}

@app.get("/slow")
def slow_api():
    time.sleep(2)
    return {"message": "Slow endpoint"}

@app.get("/error")
def error_api():
    raise HTTPException(status_code=500, detail="Something went wrong")

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type="text/plain")