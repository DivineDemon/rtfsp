from typing import Dict, List, Optional
from pydantic import BaseModel, Field

class FeatureDefinition(BaseModel):
    name: str
    data_type: str
    entity: str  # e.g., 'user', 'device', 'card'
    description: str
    online_enabled: bool = True
    offline_enabled: bool = True
    owner: str = "fraud-ml-team"

class FeatureRegistry:
    """Self-serve Feature Registry for registering, discovering, and documenting ML features."""

    def __init__(self):
        self._definitions: Dict[str, FeatureDefinition] = {}
        self._register_default_features()

    def _register_default_features(self):
        defaults = [
            FeatureDefinition(
                name="txn_count_1h",
                data_type="INTEGER",
                entity="user",
                description="Number of transactions made by user in the last 60 minutes."
            ),
            FeatureDefinition(
                name="txn_count_24h",
                data_type="INTEGER",
                entity="user",
                description="Number of transactions made by user in the last 24 hours."
            ),
            FeatureDefinition(
                name="avg_amount_24h",
                data_type="FLOAT",
                entity="user",
                description="Average transaction amount for user in the last 24 hours."
            ),
            FeatureDefinition(
                name="time_since_last_txn_sec",
                data_type="FLOAT",
                entity="user",
                description="Time elapsed in seconds since user's previous transaction."
            ),
            FeatureDefinition(
                name="device_risk_score",
                data_type="FLOAT",
                entity="device",
                description="Historical risk probability associated with device fingerprint."
            ),
            FeatureDefinition(
                name="amount_to_avg_ratio",
                data_type="FLOAT",
                entity="user",
                description="Ratio of current transaction amount relative to 24h user average."
            ),
        ]
        for f in defaults:
            self.register(f)

    def register(self, feature: FeatureDefinition):
        self._definitions[feature.name] = feature

    def get(self, feature_name: str) -> Optional[FeatureDefinition]:
        return self._definitions.get(feature_name)

    def list_features(self) -> List[FeatureDefinition]:
        return list(self._definitions.values())
