import math

import pytest

from conftest import load_tool

ec = load_tool("capacity-planner", "erlang_c")
sr = load_tool("capacity-planner", "staffing_requirements")
qm = load_tool("capacity-planner", "queue_metrics")


# ---- erlang_c ------------------------------------------------------------
def test_offered_load():
    # 100 calls / 30 min at 180s AHT -> 10 Erlangs.
    assert ec.offered_load(100, 1800, 180) == 10.0


def test_erlang_c_textbook_n24():
    # Classic A=20 example: N=24, AHT=180s, target 20s -> SL ~ 0.81.
    m = ec.service_metrics(20, 24, 180, 20)
    assert abs(m["probability_wait"] - 0.2981) < 0.001
    assert abs(m["service_level"] - 0.81) < 0.01


def test_erlang_c_textbook_n25():
    # One more agent lifts service level to ~0.88.
    m = ec.service_metrics(20, 25, 180, 20)
    assert abs(m["service_level"] - 0.88) < 0.01


def test_erlang_c_unstable_when_n_le_a():
    # N <= A: unstable queue, Pw = 1, SL = 0, no finite ASA.
    assert ec.erlang_c(20, 20) == 1.0
    m = ec.service_metrics(20, 20, 180, 20)
    assert m["service_level"] == 0.0
    assert m["asa_seconds"] is None
    assert m["stable"] is False


def test_erlang_c_occupancy():
    m = ec.service_metrics(10, 14, 180, 20)
    assert abs(m["occupancy"] - 10 / 14) < 1e-6


def test_plan_full_example():
    r = ec.plan({"calls_per_interval": 100, "interval_seconds": 1800,
                 "aht_seconds": 180, "agents": 14,
                 "target_answer_seconds": 20})
    assert r["offered_load"] == 10.0
    assert r["agents"] == 14
    assert 0.85 < r["service_level"] < 0.92


def test_min_agents_meets_target():
    n = ec.min_agents_for_target(10, 180, 20, 0.8)
    m = ec.service_metrics(10, n, 180, 20)
    assert m["service_level"] >= 0.8
    # One fewer agent must fail the target (minimality).
    below = ec.service_metrics(10, n - 1, 180, 20)
    assert below["service_level"] < 0.8


def test_min_agents_monotonic_in_target():
    # A stricter service level never needs fewer agents.
    easy = ec.min_agents_for_target(15, 240, 20, 0.70)
    hard = ec.min_agents_for_target(15, 240, 20, 0.90)
    assert hard >= easy


def test_plan_required_agents_mode():
    r = ec.plan({"calls_per_interval": 100, "interval_seconds": 1800,
                 "aht_seconds": 180, "target_answer_seconds": 20,
                 "target_service_level": 0.8})
    assert r["min_agents_for_target"] == 14


def test_erlang_c_rejects_missing_key():
    with pytest.raises(ValueError):
        ec.plan({"interval_seconds": 1800, "aht_seconds": 180})


# ---- staffing_requirements ----------------------------------------------
def test_staffing_basic():
    r = sr.compute({"contact_volume": 5000, "aht_seconds": 300,
                    "period_paid_hours_per_fte": 160,
                    "shrinkage_pct": 30, "occupancy_cap_pct": 85})
    # 5000 * 300 / 3600 = 416.667 productive hours.
    assert abs(r["productive_hours_needed"] - 416.6667) < 0.01
    base = 416.6667 / (160 * 0.85)
    assert abs(r["base_fte"] - base) < 0.01
    assert abs(r["required_fte"] - base / 0.70) < 0.01
    assert r["required_fte_rounded"] == math.ceil(r["required_fte"])


def test_staffing_shrinkage_grosses_up():
    # Higher shrinkage must require strictly more FTE for the same work.
    low = sr.compute({"contact_volume": 1000, "aht_seconds": 360,
                      "period_paid_hours_per_fte": 160,
                      "shrinkage_pct": 10, "occupancy_cap_pct": 100})
    high = sr.compute({"contact_volume": 1000, "aht_seconds": 360,
                       "period_paid_hours_per_fte": 160,
                       "shrinkage_pct": 40, "occupancy_cap_pct": 100})
    assert high["required_fte"] > low["required_fte"]


def test_staffing_rejects_bad_shrinkage():
    with pytest.raises(ValueError):
        sr.compute({"contact_volume": 100, "aht_seconds": 300,
                    "period_paid_hours_per_fte": 160, "shrinkage_pct": 100})


def test_staffing_rejects_bad_occupancy():
    with pytest.raises(ValueError):
        sr.compute({"contact_volume": 100, "aht_seconds": 300,
                    "period_paid_hours_per_fte": 160,
                    "occupancy_cap_pct": 0})


# ---- queue_metrics -------------------------------------------------------
def test_queue_metrics_stable():
    r = qm.metrics(0.5, 0.1, 6)
    assert r["stable"] is True
    assert abs(r["offered_load"] - 5.0) < 1e-6
    assert abs(r["utilization"] - 5.0 / 6) < 1e-6
    # Little's Law internal consistency: Wq = Lq / lambda.
    assert abs(r["Wq"] - r["Lq"] / 0.5) < 1e-4
    # L = Lq + A.
    assert abs(r["L"] - (r["Lq"] + 5.0)) < 1e-4


def test_queue_metrics_unstable():
    r = qm.metrics(1.0, 0.1, 6)
    assert r["stable"] is False
    assert r["prob_wait"] == 1.0
    assert r["Wq"] is None


def test_queue_metrics_rejects_missing_key():
    with pytest.raises(ValueError):
        qm.compute({"arrival_rate": 0.5, "service_rate": 0.1})
