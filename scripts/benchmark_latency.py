#!/usr/bin/env python3
"""
Latency & Throughput Benchmark Script for RTFSP.
Verifies p95 latency < 180ms SLA under simulated streaming transaction load.
"""
import time
import numpy as np
from rtfsp.generator.transaction_stream import TransactionGenerator
from rtfsp.pipeline.scoring_engine import FraudScoringEngine

def main():
    print("=" * 65)
    print("  RTFSP LATENCY & THROUGHPUT BENCHMARK (SLA: <180ms p95)")
    print("=" * 65)

    gen = TransactionGenerator()
    engine = FraudScoringEngine()

    sample_size = 500
    events = gen.generate_batch(sample_size)

    latencies = []
    start_total = time.perf_counter()

    for event in events:
        res = engine.score_transaction(event)
        latencies.append(res.total_latency_ms)

    total_time = time.perf_counter() - start_total
    qps = sample_size / total_time

    p50 = np.percentile(latencies, 50)
    p90 = np.percentile(latencies, 90)
    p95 = np.percentile(latencies, 95)
    p99 = np.percentile(latencies, 99)

    print(f"Total Transactions Scored : {sample_size}")
    print(f"Total Elapsed Time        : {total_time:.2f} seconds")
    print(f"Throughput (QPS)          : {qps:.1f} req/sec")
    print("-" * 65)
    print(f"p50 Latency               : {p50:.2f} ms")
    print(f"p90 Latency               : {p90:.2f} ms")
    print(f"p95 Latency               : {p95:.2f} ms  <-- TARGET SLA: <180ms")
    print(f"p99 Latency               : {p99:.2f} ms")
    print("-" * 65)

    if p95 < 180.0:
        print("✅ SUCCESS: p95 latency target (<180ms) strictly met!")
    else:
        print("❌ WARNING: p95 latency target exceeded.")

if __name__ == "__main__":
    main()
