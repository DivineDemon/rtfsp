import pytest
from rtfsp.generator.transaction_stream import TransactionGenerator
from rtfsp.pipeline.scoring_engine import FraudScoringEngine
from rtfsp.pipeline.batch_scheduler import DynamicBatchScheduler
from rtfsp.models.adjudication import AdjudicationBenchmark

def test_scoring_engine_single():
    gen = TransactionGenerator()
    engine = FraudScoringEngine()
    event = gen.generate_single()

    res = engine.score_transaction(event)
    assert res.transaction_id == event.transaction_id
    assert 0.0 <= res.fraud_probability <= 1.0
    assert res.decision in ["APPROVE", "CHALLENGE", "DECLINE"]
    assert res.total_latency_ms < 180.0  # SLA target

def test_dynamic_batch_scheduler():
    gen = TransactionGenerator()
    scheduler = DynamicBatchScheduler()
    batch = gen.generate_batch(20)

    results = scheduler.score_batch_sync(batch)
    assert len(results) == 20
    telemetry = scheduler.get_queue_telemetry()
    assert telemetry["total_processed_transactions"] == 20

def test_adjudication_benchmark():
    bench = AdjudicationBenchmark(sample_size=1000)
    metrics = bench.evaluate()

    assert "primary_classifier" in metrics
    assert "layered_ensemble" in metrics
    p_fpr = metrics["primary_classifier"]["false_positive_rate_pct"]
    l_fpr = metrics["layered_ensemble"]["false_positive_rate_pct"]
    # Layered ensemble must lower false positive rate
    assert l_fpr < p_fpr
