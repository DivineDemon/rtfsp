from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from rtfsp.api.routes import router

app = FastAPI(
    title="Real-Time Fraud Scoring Pipeline (RTFSP)",
    description="High-throughput streaming fraud detection pipeline with sub-180ms p95 latency, feature store, and canary deployment.",
    version="0.1.0"
)

# Enable CORS for dashboard visualizer
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1")

@app.get("/health")
async def health_check():
    return {
        "status": "HEALTHY",
        "service": "rtfsp-scoring-engine",
        "version": "0.1.0"
    }
