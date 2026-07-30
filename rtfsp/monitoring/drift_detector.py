import numpy as np
import pandas as pd
from typing import Dict, Any, List

class FeatureDriftDetector:
    """Calculates Population Stability Index (PSI) and distribution shifts for online streaming features."""

    def __init__(self, num_buckets: int = 10):
        self.num_buckets = num_buckets
        self.baseline_distributions: Dict[str, np.ndarray] = {}
        self._init_baseline_reference()

    def _init_baseline_reference(self):
        """Establish baseline distributions from reference training dataset."""
        np.random.seed(42)
        # Reference distributions matching typical non-drifted transactions
        self.baseline_distributions["amount"] = np.random.exponential(45.0, 5000) + 5.0
        self.baseline_distributions["distance_from_home_km"] = np.random.exponential(12.0, 5000)
        self.baseline_distributions["device_risk_score"] = np.random.uniform(0.01, 0.2, 5000)
        self.baseline_distributions["amount_to_avg_ratio"] = np.random.exponential(1.0, 5000)

    @staticmethod
    def calculate_psi(baseline: np.ndarray, target: np.ndarray, num_buckets: int = 10) -> float:
        """Calculate Population Stability Index (PSI) between baseline and target distributions."""
        if len(target) == 0 or len(baseline) == 0:
            return 0.0

        percentiles = np.linspace(0, 100, num_buckets + 1)
        buckets = np.percentile(baseline, percentiles)
        buckets[0] = -np.inf
        buckets[-1] = np.inf

        baseline_counts, _ = np.histogram(baseline, bins=buckets)
        target_counts, _ = np.histogram(target, bins=buckets)

        expected_pct = np.maximum(baseline_counts / len(baseline), 1e-4)
        actual_pct = np.maximum(target_counts / len(target), 1e-4)

        psi = np.sum((actual_pct - expected_pct) * np.log(actual_pct / expected_pct))
        return float(psi)

    def detect_drift_for_window(self, current_features: pd.DataFrame) -> Dict[str, Any]:
        """Compute PSI and drift status across all key features for a streaming window."""
        results = {}
        overall_max_psi = 0.0

        for col, baseline in self.baseline_distributions.items():
            if col in current_features.columns:
                target = current_features[col].dropna().values
                psi = self.calculate_psi(baseline, target, self.num_buckets)
                
                if psi >= 0.25:
                    status = "CRITICAL_DRIFT"
                elif psi >= 0.15:
                    status = "MODERATE_DRIFT"
                else:
                    status = "NO_DRIFT"

                overall_max_psi = max(overall_max_psi, psi)

                results[col] = {
                    "psi": round(psi, 4),
                    "status": status,
                    "mean_baseline": round(float(np.mean(baseline)), 2),
                    "mean_current": round(float(np.mean(target)), 2) if len(target) > 0 else 0.0
                }

        return {
            "overall_max_psi": round(overall_max_psi, 4),
            "feature_metrics": results,
            "requires_retraining": overall_max_psi >= 0.25
        }
