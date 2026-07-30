from rtfsp.deployment.canary_manager import CanaryDeploymentManager

def test_canary_routing():
    manager = CanaryDeploymentManager()
    assert manager.is_canary_active
    versions = set(manager.route_request() for _ in range(100))
    assert manager.primary_version in versions

def test_automated_rollback():
    manager = CanaryDeploymentManager()
    manager.canary_traffic_pct = 100.0  # Force all requests to canary candidate
    # Route requests to canary and record errors to breach threshold
    for _ in range(60):
        manager.route_request()
        manager.record_canary_outcome(is_error=True)

    status = manager.get_status()
    assert not status["is_canary_active"]
    assert status["canary_traffic_pct"] == 0.0
    assert len(status["rollback_history"]) >= 1
