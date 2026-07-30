import time
import random
from typing import Dict, Any, List, Optional

class FeatureStore:
    """Online & Offline Feature Store for low-latency (<5ms) feature retrieval."""

    def __init__(self, use_redis: bool = False):
        self.use_redis = use_redis
        # In-memory fast cache for user activity velocity
        self._online_user_state: Dict[str, Dict[str, Any]] = {}
        self._device_risk_scores: Dict[str, float] = {}

    def get_online_features(self, user_id: str, device_id: str, current_amount: float, distance_km: float) -> Dict[str, float]:
        """Fetch online entity features for scoring at sub-5ms latency."""
        start_time = time.perf_counter()

        state = self._online_user_state.get(user_id, {
            "txn_count_1h": 0,
            "txn_count_24h": 0,
            "sum_amount_24h": 0.0,
            "last_txn_time": time.time() - 3600,
            "last_amount": 25.0
        })

        # Calculate time delta
        time_since_last = max(1.0, time.time() - state["last_txn_time"])
        
        # Aggregate features
        txn_count_1h = state["txn_count_1h"] + 1
        txn_count_24h = state["txn_count_24h"] + 1
        sum_amount_24h = state["sum_amount_24h"] + current_amount
        avg_amount_24h = sum_amount_24h / txn_count_24h if txn_count_24h > 0 else current_amount

        device_risk = self._device_risk_scores.get(device_id, round(random.uniform(0.01, 0.20), 3))

        lookup_latency_ms = (time.perf_counter() - start_time) * 1000.0

        return {
            "txn_count_1h": float(txn_count_1h),
            "txn_count_24h": float(txn_count_24h),
            "sum_amount_24h": round(sum_amount_24h, 2),
            "avg_amount_24h": round(avg_amount_24h, 2),
            "time_since_last_txn_sec": round(time_since_last, 1),
            "distance_from_home_km": round(distance_km, 2),
            "device_risk_score": device_risk,
            "amount_to_avg_ratio": round(current_amount / (avg_amount_24h + 1.0), 2),
            "_feature_lookup_latency_ms": round(lookup_latency_ms, 3)
        }

    def update_online_features(self, user_id: str, device_id: str, amount: float):
        """Update online entity state after scoring or transaction settlement."""
        if user_id not in self._online_user_state:
            self._online_user_state[user_id] = {
                "txn_count_1h": 0,
                "txn_count_24h": 0,
                "sum_amount_24h": 0.0,
                "last_txn_time": time.time(),
                "last_amount": amount
            }
        
        st = self._online_user_state[user_id]
        st["txn_count_1h"] += 1
        st["txn_count_24h"] += 1
        st["sum_amount_24h"] += amount
        st["last_txn_time"] = time.time()
        st["last_amount"] = amount
