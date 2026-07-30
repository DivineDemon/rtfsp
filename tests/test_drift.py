import pandas as pd
from rtfsp.monitoring.drift_detector import FeatureDriftDetector
from rtfsp.monitoring.retrain_trigger import RetrainingTriggerPipeline
from rtfsp.generator.transaction_stream import TransactionGenerator

def test_drift_detector_no_drift():
    detector = FeatureDriftDetector()
    
    # Non-drifted distribution matching baseline
    import numpy as np
    df = pd.DataFrame({
        "amount": np.random.exponential(45.0, 500) + 5.0,
        "distance_from_home_km": np.random.exponential(12.0, 500),
        "device_risk_score": np.random.uniform(0.01, 0.2, 500)
    })

    report = detector.detect_drift_for_window(df)
    assert report["overall_max_psi"] < 0.25
    assert not report["requires_retraining"]

def test_drift_detector_with_drift():
    detector = FeatureDriftDetector()
    gen = TransactionGenerator(drift_factor=1.5)
    batch = gen.generate_batch(200)

    df = pd.DataFrame([{
        "amount": e.amount,
        "distance_from_home_km": e.distance_from_home_km,
        "device_risk_score": 0.85
    } for e in batch])

    report = detector.detect_drift_for_window(df)
    assert report["overall_max_psi"] >= 0.15

def test_retraining_trigger():
    pipeline = RetrainingTriggerPipeline()
    gen = TransactionGenerator(drift_factor=2.0)
    batch = gen.generate_batch(200)

    df = pd.DataFrame([{
        "amount": e.amount,
        "distance_from_home_km": e.distance_from_home_km,
        "device_risk_score": 0.90
    } for e in batch])

    res = pipeline.evaluate_and_trigger(df)
    assert "pipeline_action" in res
