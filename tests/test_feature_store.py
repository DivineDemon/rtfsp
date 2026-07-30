import pytest
from rtfsp.feature_store.store import FeatureStore
from rtfsp.feature_store.registry import FeatureRegistry

def test_feature_store_online_lookup():
    fs = FeatureStore()
    feats = fs.get_online_features("usr_test1", "dev_test1", 120.50, 15.2)

    assert "txn_count_1h" in feats
    assert "txn_count_24h" in feats
    assert "avg_amount_24h" in feats
    assert feats["_feature_lookup_latency_ms"] < 10.0

def test_feature_store_state_update():
    fs = FeatureStore()
    fs.update_online_features("usr_test2", "dev_test2", 50.0)
    fs.update_online_features("usr_test2", "dev_test2", 150.0)

    feats = fs.get_online_features("usr_test2", "dev_test2", 100.0, 5.0)
    assert feats["txn_count_24h"] >= 2
    assert feats["sum_amount_24h"] >= 200.0

def test_feature_registry():
    registry = FeatureRegistry()
    features = registry.list_features()
    assert len(features) >= 5
    names = [f.name for f in features]
    assert "txn_count_1h" in names
    assert "device_risk_score" in names
