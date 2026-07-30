import numpy as np
from typing import Dict, Any, Tuple
from sklearn.ensemble import GradientBoostingClassifier

class PrimaryFraudClassifier:
    """Primary high-speed Gradient Boosted Tree model for real-time transaction scoring."""

    def __init__(self):
        self.feature_names = [
            "amount",
            "merchant_category_code",
            "distance_from_home_km",
            "is_international",
            "txn_count_1h",
            "txn_count_24h",
            "avg_amount_24h",
            "time_since_last_txn_sec",
            "device_risk_score",
            "amount_to_avg_ratio"
        ]
        self.model = GradientBoostingClassifier(n_estimators=50, max_depth=4, random_state=42)
        self.is_trained = False
        self._fit_mock_model()

    def _fit_mock_model(self):
        """Train a lightweight baseline model on synthetic features."""
        np.random.seed(42)
        X = np.random.rand(1000, len(self.feature_names))
        # Amount, distance, ratio drive fraud score
        y = ((X[:, 0] * 0.4 + X[:, 2] * 0.3 + X[:, 9] * 0.3) > 0.55).astype(int)
        self.model.fit(X, y)
        self.is_trained = True

    def predict_proba(self, feature_dict: Dict[str, Any]) -> float:
        """Predict fraud probability for a single transaction. Executed under 10ms."""
        vec = np.array([[
            float(feature_dict.get(name, 0.0)) for name in self.feature_names
        ]])
        score = self.model.predict_proba(vec)[0][1]
        
        # Add slight rule-based heuristic boosting for extreme transaction amounts/distances
        if feature_dict.get("amount", 0.0) > 1000.0 and feature_dict.get("distance_from_home_km", 0.0) > 500.0:
            score = max(score, 0.75)
            
        return float(score)
