import time
import random
import uuid
from typing import Dict, Any, List
from pydantic import BaseModel, Field

class TransactionEvent(BaseModel):
    transaction_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    card_id: str
    amount: float
    merchant_category_code: int
    merchant_id: str
    timestamp: float = Field(default_factory=time.time)
    device_id: str
    ip_address: str
    location_lat: float
    location_lon: float
    distance_from_home_km: float
    is_international: bool = False
    is_fraud_ground_truth: bool = False

class TransactionGenerator:
    """Generates realistic payment streams with controlled fraud injection and feature drift."""

    def __init__(self, fraud_rate: float = 0.025, drift_factor: float = 0.0):
        self.fraud_rate = fraud_rate
        self.drift_factor = drift_factor
        self.merchant_categories = [5411, 5812, 5999, 4814, 5732, 5912, 7011, 4121]
        self.users = [f"usr_{i:05d}" for i in range(1, 1000)]
        self.devices = [f"dev_{i:05d}" for i in range(1, 1200)]

    def set_drift_factor(self, factor: float):
        """Set feature drift factor (0.0 = baseline, 1.0 = heavy drift in transaction amounts/locations)."""
        self.drift_factor = factor

    def generate_single(self) -> TransactionEvent:
        user_id = random.choice(self.users)
        card_id = f"card_{user_id.split('_')[1]}"
        device_id = random.choice(self.devices)
        
        is_fraud = random.random() < self.fraud_rate
        
        # Base amount with potential drift injection
        base_amount = random.expovariate(1.0 / 45.0) + 5.0
        if self.drift_factor > 0:
            # Shift distribution upwards to simulate inflation or fraud tactic shift
            base_amount += random.gauss(mu=80.0 * self.drift_factor, sigma=30.0)

        if is_fraud:
            # Fraudulent transactions tend to have higher amounts, strange MCCs, large distance
            amount = base_amount * random.uniform(3.0, 10.0)
            distance = random.uniform(150.0, 3000.0)
            is_int = random.random() < 0.65
            mcc = random.choice([5732, 7011, 5999])
        else:
            amount = max(1.0, base_amount)
            distance = random.expovariate(1.0 / 12.0)
            is_int = random.random() < 0.05
            mcc = random.choice(self.merchant_categories)

        return TransactionEvent(
            user_id=user_id,
            card_id=card_id,
            amount=round(amount, 2),
            merchant_category_code=mcc,
            merchant_id=f"merch_{random.randint(100, 999)}",
            device_id=device_id,
            ip_address=f"192.168.{random.randint(1, 254)}.{random.randint(1, 254)}",
            location_lat=round(37.7749 + random.uniform(-0.5, 0.5), 4),
            location_lon=round(-122.4194 + random.uniform(-0.5, 0.5), 4),
            distance_from_home_km=round(distance, 2),
            is_international=is_int,
            is_fraud_ground_truth=is_fraud
        )

    def generate_batch(self, count: int = 100) -> List[TransactionEvent]:
        return [self.generate_single() for _ in range(count)]
