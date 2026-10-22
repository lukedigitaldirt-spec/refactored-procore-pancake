import pytest

from conftest import load_tool

sla = load_tool("vendor-management", "sla_calculator")
risk = load_tool("vendor-management", "vendor_risk_scorer")
sc = load_tool("vendor-management", "scorecard")


# ---- sla_calculator ------------------------------------------------------
def test_sla_breach_and_credit():
    spec = {
        "target_pct": 99.9,
        "period_hours": 720,
        "downtime_minutes": 130,
        "credit_tiers": [
            {"below_pct": 99.9, "credit_pct": 10},
            {"below_pct": 99.0, "credit_pct": 25},
        ],
    }
    r = sla.calculate(spec)
    assert r["period_minutes"] == 43200
    assert r["allowed_downtime_minutes"] == 43.2
    assert r["error_budget_minutes_remaining"] == -86.8
    assert r["breached"] is True
    assert r["service_credit_pct"] == 10
    assert round(r["actual_uptime_pct"], 4) == 99.6991


def test_sla_pass_no_credit():
    spec = {
        "target_pct": 99.0,
        "period_hours": 720,
        "downtime_minutes": 30,
        "credit_tiers": [{"below_pct": 99.0, "credit_pct": 10}],
    }
    r = sla.calculate(spec)
    assert r["breached"] is False
    assert r["service_credit_pct"] == 0
    assert r["error_budget_minutes_remaining"] > 0


def test_sla_worst_tier_wins():
    spec = {
        "target_pct": 99.9,
        "period_hours": 720,
        "downtime_minutes": 3000,
        "credit_tiers": [
            {"below_pct": 99.9, "credit_pct": 10},
            {"below_pct": 99.0, "credit_pct": 25},
            {"below_pct": 95.0, "credit_pct": 50},
        ],
    }
    r = sla.calculate(spec)
    # ~93.06% uptime -> falls below 95 -> 50% credit (largest applicable)
    assert r["service_credit_pct"] == 50


def test_sla_rejects_downtime_over_period():
    with pytest.raises(ValueError):
        sla.calculate({"target_pct": 99.9, "period_hours": 1,
                       "downtime_minutes": 120})


def test_sla_rejects_bad_target():
    with pytest.raises(ValueError):
        sla.calculate({"target_pct": 0, "period_hours": 720,
                       "downtime_minutes": 10})


# ---- vendor_risk_scorer --------------------------------------------------
def test_risk_bottleneck_quadrant_and_band():
    spec = {
        "name": "Acme",
        "supply_risk": 4,
        "profit_impact": 2,
        "dimensions": {"financial": 3, "operational": 4, "compliance": 2,
                       "concentration": 5, "geographic": 1},
        "weights": {"financial": 0.3, "operational": 0.25, "compliance": 0.2,
                    "concentration": 0.15, "geographic": 0.1},
    }
    r = risk.score(spec)
    assert r["quadrant"] == "Bottleneck"
    assert r["weighted_score"] == 3.15
    assert r["band"] == "Medium"
    assert r["weights_normalized"] is False


def test_risk_quadrant_mapping():
    assert risk.quadrant(5, 5) == "Strategic"
    assert risk.quadrant(1, 5) == "Leverage"
    assert risk.quadrant(5, 1) == "Bottleneck"
    assert risk.quadrant(1, 1) == "Non-critical"


def test_risk_normalizes_weights():
    spec = {
        "name": "V",
        "supply_risk": 3,
        "profit_impact": 3,
        "dimensions": {"a": 4, "b": 2},
        "weights": {"a": 2, "b": 2},
    }
    r = risk.score(spec)
    assert r["weights_normalized"] is True
    assert r["weighted_score"] == 3.0
    assert r["quadrant"] == "Strategic"


def test_risk_rejects_out_of_range_dimension():
    with pytest.raises(ValueError):
        risk.score({"name": "V", "supply_risk": 3, "profit_impact": 3,
                    "dimensions": {"a": 6}, "weights": {"a": 1}})


def test_risk_rejects_missing_weight():
    with pytest.raises(ValueError):
        risk.score({"name": "V", "supply_risk": 3, "profit_impact": 3,
                    "dimensions": {"a": 3, "b": 3}, "weights": {"a": 1}})


def test_risk_rejects_bad_axis():
    with pytest.raises(ValueError):
        risk.score({"name": "V", "supply_risk": 0, "profit_impact": 3,
                    "dimensions": {"a": 3}, "weights": {"a": 1}})


# ---- scorecard -----------------------------------------------------------
def test_scorecard_grade_and_at_risk():
    spec = {
        "vendor": "Acme",
        "criteria": [
            {"name": "Quality", "score": 4, "weight": 0.3},
            {"name": "Delivery", "score": 3, "weight": 0.25},
            {"name": "Cost", "score": 5, "weight": 0.2},
            {"name": "Service", "score": 4, "weight": 0.15},
            {"name": "Responsiveness", "score": 2, "weight": 0.1},
        ],
    }
    r = sc.evaluate(spec)
    assert r["weighted_total"] == 3.75
    assert r["grade"] == "B"
    assert r["pct"] == 75.0
    assert r["at_risk"] == ["Responsiveness"]
    assert r["weights_normalized"] is False


def test_scorecard_normalizes_weights():
    spec = {
        "vendor": "V",
        "criteria": [
            {"name": "A", "score": 5, "weight": 1},
            {"name": "B", "score": 5, "weight": 1},
        ],
    }
    r = sc.evaluate(spec)
    assert r["weights_normalized"] is True
    assert r["weighted_total"] == 5.0
    assert r["grade"] == "A"
    assert r["at_risk"] == []


def test_scorecard_rejects_empty_criteria():
    with pytest.raises(ValueError):
        sc.evaluate({"vendor": "V", "criteria": []})


def test_scorecard_rejects_out_of_range_score():
    with pytest.raises(ValueError):
        sc.evaluate({"vendor": "V",
                     "criteria": [{"name": "A", "score": 7, "weight": 1}]})


def test_scorecard_missing_weight():
    with pytest.raises(ValueError):
        sc.evaluate({"vendor": "V",
                     "criteria": [{"name": "A", "score": 3}]})
