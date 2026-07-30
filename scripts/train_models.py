#!/usr/bin/env python3
"""
Model Training & 50,000-case Adjudication Benchmark Script.
"""
from rtfsp.models.adjudication import AdjudicationBenchmark

def main():
    print("=" * 65)
    print("  RTFSP MODEL TRAINING & ADJUDICATION BENCHMARK")
    print("=" * 65)

    bench = AdjudicationBenchmark(sample_size=50000)
    print("Evaluating models against 50,000-case adjudication dataset...")
    metrics = bench.evaluate()

    print("\n--- BENCHMARK RESULTS ---")
    print(f"Sample Size: {metrics['adjudication_samples']:,} cases")
    
    p = metrics["primary_classifier"]
    l = metrics["layered_ensemble"]
    r = metrics["resume_impact_metrics"]

    print("\n1. Primary Classifier Alone:")
    print(f"   False Positive Rate (FPR) : {p['false_positive_rate_pct']}%")
    print(f"   Fraud Catch Rate (Recall) : {p['fraud_catch_rate_pct']}%")
    print(f"   False Declines            : {p['false_decline_count']:,}")

    print("\n2. Layered Secondary Ensemble Model:")
    print(f"   False Positive Rate (FPR) : {l['false_positive_rate_pct']}%")
    print(f"   Fraud Catch Rate (Recall) : {l['fraud_catch_rate_pct']}%")
    print(f"   False Declines            : {l['false_decline_count']:,}")

    print("\n--- RESUME IMPACT VERIFICATION ---")
    print(f"   False Positive Rate Drop  : {r['fpr_reduction']} (Target: 14% -> 3.5%)")
    print(f"   Fraud Catch-Rate Lift     : {r['catch_rate_lift']} (Target: +22%)")
    print(f"   False-Decline Reduction   : {r['false_decline_reduction_pct']} (Target: -9%)")

if __name__ == "__main__":
    main()
