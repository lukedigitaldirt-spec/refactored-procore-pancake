import pytest

from conftest import load_tool

cta = load_tool("process-mapper", "cycle_time_analyzer")
bd = load_tool("process-mapper", "bottleneck_detector")
bpmn = load_tool("process-mapper", "bpmn_validator")


# ---- cycle_time_analyzer -------------------------------------------------
def test_cycle_time_basic():
    steps = [
        {"name": "A", "process": 5, "wait": 15},
        {"name": "B", "process": 5, "wait": 75},
    ]
    r = cta.analyze(steps)
    assert r["process_time"] == 10
    assert r["wait_time"] == 90
    assert r["lead_time"] == 100
    assert r["process_cycle_efficiency"] == 0.1
    assert r["process_cycle_efficiency_pct"] == 10.0


def test_takt_time():
    steps = [{"name": "A", "process": 1, "wait": 0}]
    r = cta.analyze(steps, available_time=480, demand=60)
    assert r["takt_time"] == 8.0


def test_cycle_time_rejects_empty():
    with pytest.raises(ValueError):
        cta.analyze([])


def test_cycle_time_rejects_negative():
    with pytest.raises(ValueError):
        cta.analyze([{"name": "A", "process": -1, "wait": 0}])


def test_cycle_time_missing_field():
    with pytest.raises(ValueError):
        cta.analyze([{"name": "A", "process": 1}])


# ---- bottleneck_detector -------------------------------------------------
def test_bottleneck_identifies_min_capacity():
    steps = [
        {"name": "Intake", "capacity": 100},
        {"name": "Review", "capacity": 40},
        {"name": "Approve", "capacity": 80},
    ]
    r = bd.detect(steps)
    assert r["constraint"] == "Review"
    assert r["throughput"] == 40


def test_bottleneck_demand_shortfall():
    steps = [{"name": "A", "capacity": 30}, {"name": "B", "capacity": 50}]
    r = bd.detect(steps, demand=45)
    assert r["constraint"] == "A"
    assert r["meets_demand"] is False
    assert r["throughput_gap"] == 15


def test_bottleneck_meets_demand():
    steps = [{"name": "A", "capacity": 60}]
    r = bd.detect(steps, demand=50)
    assert r["meets_demand"] is True
    assert r["throughput_gap"] == 0


def test_bottleneck_rejects_zero_capacity():
    with pytest.raises(ValueError):
        bd.detect([{"name": "A", "capacity": 0}])


# ---- bpmn_validator ------------------------------------------------------
def _good_model():
    return {
        "nodes": [
            {"id": "s", "type": "startEvent"},
            {"id": "t", "type": "task"},
            {"id": "e", "type": "endEvent"},
        ],
        "flows": [{"from": "s", "to": "t"}, {"from": "t", "to": "e"}],
    }


def test_bpmn_valid_model():
    r = bpmn.validate(_good_model())
    assert r["valid"] is True
    assert r["errors"] == []


def test_bpmn_detects_two_starts():
    m = _good_model()
    m["nodes"].append({"id": "s2", "type": "startEvent"})
    m["flows"].append({"from": "s2", "to": "t"})
    r = bpmn.validate(m)
    assert r["valid"] is False
    assert any("start event" in e for e in r["errors"])


def test_bpmn_detects_orphan():
    m = _good_model()
    m["nodes"].append({"id": "orphan", "type": "task"})
    r = bpmn.validate(m)
    assert r["valid"] is False
    assert any("orphan" in e for e in r["errors"])


def test_bpmn_detects_dead_end():
    m = {
        "nodes": [
            {"id": "s", "type": "startEvent"},
            {"id": "t", "type": "task"},
            {"id": "d", "type": "task"},
            {"id": "e", "type": "endEvent"},
        ],
        "flows": [
            {"from": "s", "to": "t"},
            {"from": "t", "to": "e"},
            {"from": "t", "to": "d"},
        ],
    }
    r = bpmn.validate(m)
    assert r["valid"] is False
    assert any("dead end" in e for e in r["errors"])


def test_bpmn_flow_to_missing_node():
    m = _good_model()
    m["flows"].append({"from": "t", "to": "ghost"})
    r = bpmn.validate(m)
    assert r["valid"] is False
    assert any("ghost" in e for e in r["errors"])
