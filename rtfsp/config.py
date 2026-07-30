import os
from pydantic import BaseModel

class PipelineConfig(BaseModel):
    # SLA & Performance Targets
    TARGET_P95_LATENCY_MS: float = 180.0
    DAILY_TRANSACTION_VOLUME: int = 1_200_000
    DYNAMIC_BATCH_MAX_SIZE: int = 64
    DYNAMIC_BATCH_TIMEOUT_MS: float = 15.0

    # Model Performance Benchmarks
    BASELINE_FPR: float = 0.140      # 14.0%
    TARGET_FPR: float = 0.035        # 3.5%
    SECONDARY_TRIGGER_THRESHOLD: float = 0.45 # Trigger ensemble if primary score in uncertain band [0.45, 0.80]
    FRAUD_CONFIRM_THRESHOLD: float = 0.80

    # Drift & Retraining
    PSI_WARNING_THRESHOLD: float = 0.15
    PSI_CRITICAL_THRESHOLD: float = 0.25
    ADJUDICATION_SET_SIZE: int = 50_000

    # Feature Store Configuration
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    FEATURE_CACHE_TTL_SEC: int = 86400  # 24 hours

    # Canary & Deployment SLAs
    CANARY_TRAFFIC_PCT: float = 10.0
    ERROR_RATE_ROLLBACK_THRESHOLD: float = 0.02  # 2% error rate triggers auto-rollback
    TARGET_MTTR_MINUTES: float = 8.0

config = PipelineConfig()
