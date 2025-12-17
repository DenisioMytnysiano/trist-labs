from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from prometheus_client import make_asgi_app, Counter, Histogram
import time

app = FastAPI()

REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total number of HTTP requests',
    ['method', 'endpoint', 'http_status']
)

REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency in seconds',
    ['method', 'endpoint']
)

metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

@app.middleware("http")
async def track_metrics(request: Request, call_next):
    start_time = time.time()
    method = request.method
    endpoint = request.url.path
    
    try:
        response = await call_next(request)
        status_code = response.status_code
    except Exception as e:
        status_code = 500
        response = JSONResponse(
            content={"error": str(e)},
            status_code=status_code
        )
    
    REQUEST_COUNT.labels(method, endpoint, status_code).inc()
    REQUEST_LATENCY.labels(method, endpoint).observe(time.time() - start_time)
    
    return response

@app.get("/")
async def healthcheck():
    return {"status": "ok"}


@app.get("/ping")
async def ping():
    return {"message": "pong"}
