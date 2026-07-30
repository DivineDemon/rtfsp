import time
from typing import Dict, Any, List
from pydantic import BaseModel, Field

from rtfsp.config import config
from rtfsp.generator.transaction_stream import TransactionEvent
from rtfsp.feature_store.store import FeatureStore
from rtfsp.models.primary_classifier import PrimaryFraudClassifier
from rtfsp.models.secondary_ensemble import SecondaryEnsembleClassifier

class ScoringResult(BaseModel):
    transaction_id: str
    user_id: str
    amount: float
    fraud_probability: float
    decision: str  # 'APPROVE', 'CHALLENGE', 'DECLINE'
    model_version: str
    primary_score: float
    secondary_score: float = 0.0
    escalated_to_ensemble: bool = False
    total_latency_ms: float
    feature_lookup_latency_ms: float
    inference_latency_ms: float

class FraudScoringEngine:
    """Core fraud scoring engine combining feature store lookup + primary/secondary classifier models."""

    def __init__(self, feature_store: FeatureStore = None):
        self.feature_store = feature_store or FeatureStore()
        self.primary_model = PrimaryFraudClassifier()
        self.secondary_ensemble = SecondaryEnsembleClassifier()
        self.model_version = "v2.4.1-ensemble"

    def score_transaction(self, event: TransactionEvent) -> ScoringResult:
        start_total = time.perf_counter()

        # 1. Fetch online features (sub-5ms)
        features = self.feature_store.get_online_features(
            user_id=event.user_id,
            device_id=event.device_id,
            current_amount=event.amount,
            distance_km=event.distance_from_home_km
        )
        feature_lookup_latency = features.get("_feature_lookup_latency_ms", 2.0)

        # Merge transaction event values into feature dictionary
        full_features = {
            "amount": event.amount,
            "merchant_category_code": event.merchant_category_code,
            "distance_from_home_km": event.distance_from_home_km,
            "is_international": 1.0 if event.is_international else 0.0,
            **features
        }

        # 2. Execute Primary Classifier (under 10ms)
        start_infer = time.perf_counter()
        primary_score = self.primary_model.predict_proba(full_features)
        
        final_score = primary_score
        escalated = False
        secondary_score = 0.0

        # 3. Check if score falls in ambiguous band [0.45, 0.80] -> Escalate to Secondary Ensemble
        if config.SECONDARY_TRIGGER_THRESHOLD <= primary_score <= config.FRAUD_CONFIRM_THRESHOLD:
            escalated = True
            secondary_score = self.secondary_ensemble.predict_proba(full_features, primary_score)
            final_score = secondary_score

        infer_latency = (time.perf_counter() - start_infer) * 1000.0

        # 4. Decision thresholding
        if final_score >= config.FRAUD_CONFIRM_THRESHOLD:
            decision = "DECLINE"
        elif final_score >= 0.45:
            decision = "CHALLENGE"
        else:
            decision = "APPROVE"

        # Update online feature store state
        self.feature_store.update_online_features(event.user_id, event.device_id, event.amount)

        total_latency = (time.perf_counter() - start_total) * 1000.0

        return ScoringResult(
            transaction_id=event.transaction_id,
            user_id=event.user_id,
            amount=event.amount,
            fraud_probability=round(final_score, 4),
            decision=decision,
            model_version=self.model_version,
            primary_score=round(primary_score, 4),
            secondary_score=round(secondary_score, 4),
            escalated_to_ensemble=escalated,
            total_latency_ms=round(total_latency, 2),
            feature_lookup_latency_ms=round(feature_lookup_latency, 2),
            inference_latency_ms=round(infer_latency, 2)
        )
