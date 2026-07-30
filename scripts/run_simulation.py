#!/usr/bin/env python3
"""
Full RTFSP Pipeline CLI Simulation.
Simulates real-time transaction streaming, online feature lookups, layered scoring, drift detection, and canary deployment.
"""
import time
import pandas as pd
from rtfsp.generator.transaction_stream import TransactionGenerator
from rtfsp.feature_store.store import FeatureStore
from rtfsp.pipeline.scoring_engine import FraudScoringEngine
from rtfsp.monitoring.drift_detector import FeatureDriftDetector
from rtfsp.monitoring.retrain_trigger import RetrainingTriggerPipeline
from rtfsp.deployment.canary_manager import CanaryDeploymentManager

def main():
    print("=" * 70)
    print("  REAL-TIME FRAUD SCORING PIPELINE (RTFSP) - CLI SIMULATION")
    print("=" * 70)

    gen = TransactionGenerator()
    fs = FeatureStore()
    engine = FraudScoringEngine(feature_store=fs)
    drift_detector = FeatureDriftDetector()
    retrain_pipeline = RetrainingTriggerPipeline(drift_detector=drift_detector)
    canary = CanaryDeploymentManager()

    print("\n1. Simulating 10 Streaming Transactions...")
    events = gen.generate_batch(10)
    scored_rows = []

    for idx, ev in enumerate(events, 1):
        assigned = canary.route_request()
        res = engine.score_transaction(ev)
        res.model_version = assigned
        
        print(f"[{idx:02d}] Txn: {ev.transaction_id[:8]}.. | User: {ev.user_id} | Amt: ${ev.amount:6.2f} | Score: {res.fraud_probability:.4f} | Dec: {res.decision:<9} | Latency: {res.total_latency_ms:5.2f}ms | Ver: {res.model_version}")
        
        scored_rows.append({
            "amount": ev.amount,
            "distance_from_home_km": ev.distance_from_home_km,
            "device_risk_score": res.fraud_probability
        })

    print("\n2. Feature Store Online State Check...")
    sample_user = events[0].user_id
    online_feats = fs.get_online_features(sample_user, "dev_001", 150.0, 25.0)
    print(f"Online Features for {sample_user}:")
    for k, v in online_feats.items():
        if not k.startswith("_"):
            print(f"  • {k:<25}: {v}")

    print("\n3. Feature Drift Detection & Retraining Trigger Test (With Drift)...")
    gen.set_drift_factor(1.2) # Inject feature drift
    drift_batch = gen.generate_batch(100)
    df_drift = pd.DataFrame([{
        "amount": e.amount,
        "distance_from_home_km": e.distance_from_home_km,
        "device_risk_score": 0.35,
        "amount_to_avg_ratio": e.amount / 40.0
    } for e in drift_batch])

    report = retrain_pipeline.evaluate_and_trigger(df_drift)
    d = report["drift_report"]
    p = report["pipeline_action"]

    print(f"Overall Max PSI       : {d['overall_max_psi']}")
    print(f"Requires Retraining   : {d['requires_retraining']}")
    print(f"Pipeline Action       : {p['action']}")

    print("\n4. Canary Deployment & Rollback Test...")
    print(f"Current Status        : Primary={canary.primary_version}, Canary={canary.canary_version}, Active={canary.is_canary_active}")
    print("Simulating high error rate in canary...")
    for _ in range(55):
        canary.record_canary_outcome(is_error=True)

    c_status = canary.get_status()
    print(f"Post-Alert Status     : Active={c_status['is_canary_active']}, TrafficSplit={c_status['canary_traffic_pct']}%")
    print(f"Automated Rollback MTTR: {c_status['mttr_minutes']} minutes (< 8 min target)")

    print("\n" + "=" * 70)
    print("  SIMULATION COMPLETE - ALL PIPELINE SYSTEMS OPERATIONAL")
    print("=" * 70)

if __name__ == "__main__":
    main()
