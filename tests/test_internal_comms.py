import pytest

from conftest import load_tool

adkar = load_tool("internal-comms", "adkar_assessment")
kotter = load_tool("internal-comms", "kotter_tracker")
matrix = load_tool("internal-comms", "stakeholder_matrix")


def _scores(**over):
    base = {"awareness": 4, "desire": 4, "knowledge": 4,
            "ability": 4, "reinforcement": 4}
    base.update(over)
    return base


# ---- adkar_assessment ----------------------------------------------------
def test_adkar_barrier_is_first_failing_in_order():
    # knowledge and reinforcement both fail; barrier is the earlier one.
    r = adkar.assess("CRM", _scores(knowledge=2, reinforcement=1))
    assert r["barrier_point"] == "knowledge"
    assert "training" in r["recommended_action"].lower()


def test_adkar_respects_adkar_sequence_not_lowest_score():
    # desire (2) fails before reinforcement (1): order wins over magnitude.
    r = adkar.assess("Change", _scores(desire=2, reinforcement=1))
    assert r["barrier_point"] == "desire"


def test_adkar_no_barrier_when_all_pass():
    r = adkar.assess("Change", _scores())
    assert r["barrier_point"] is None
    assert r["recommended_action"] is None
    assert r["overall"] == 4.0


def test_adkar_threshold_applied():
    r = adkar.assess("Change", _scores(awareness=3), threshold=4)
    assert r["barrier_point"] == "awareness"


def test_adkar_rejects_missing_dimension():
    with pytest.raises(ValueError):
        adkar.assess("Change", {"awareness": 4, "desire": 3})


def test_adkar_rejects_out_of_range():
    with pytest.raises(ValueError):
        adkar.assess("Change", _scores(ability=6))


def test_adkar_rejects_unknown_dimension():
    bad = _scores()
    bad["momentum"] = 3
    with pytest.raises(ValueError):
        adkar.assess("Change", bad)


# ---- kotter_tracker ------------------------------------------------------
def test_kotter_percent_and_current_step():
    r = kotter.track([
        {"step": 1, "status": "complete"},
        {"step": 2, "status": "in_progress"},
    ])
    # 1.0 + 0.5 over 8 steps = 18.75%
    assert r["percent_complete"] == 18.75
    assert r["current_step"] == 2
    assert r["next_action"] == "Build a guiding coalition"


def test_kotter_all_complete():
    r = kotter.track([{"step": n, "status": "complete"} for n in range(1, 9)])
    assert r["percent_complete"] == 100.0
    assert r["current_step"] is None
    assert r["next_action"] is None


def test_kotter_out_of_sequence_warning():
    r = kotter.track([
        {"step": 1, "status": "not_started"},
        {"step": 6, "status": "complete"},
    ])
    assert r["warnings"]
    assert any("out of sequence" in w for w in r["warnings"])


def test_kotter_missing_steps_default_not_started():
    r = kotter.track([{"step": 1, "status": "complete"}])
    assert len(r["steps"]) == 8
    assert r["steps"][7]["status"] == "not_started"


def test_kotter_rejects_bad_status():
    with pytest.raises(ValueError):
        kotter.track([{"step": 1, "status": "done"}])


def test_kotter_rejects_out_of_range_step():
    with pytest.raises(ValueError):
        kotter.track([{"step": 9, "status": "complete"}])


def test_kotter_rejects_duplicate_step():
    with pytest.raises(ValueError):
        kotter.track([
            {"step": 1, "status": "complete"},
            {"step": 1, "status": "in_progress"},
        ])


# ---- stakeholder_matrix --------------------------------------------------
def test_matrix_quadrants():
    r = matrix.classify([
        {"name": "CFO", "power": 5, "interest": 2},
        {"name": "Support lead", "power": 2, "interest": 5},
        {"name": "Sponsor", "power": 5, "interest": 5},
        {"name": "Contractor", "power": 1, "interest": 1},
    ])
    by_name = {s["name"]: s["quadrant"] for s in r["stakeholders"]}
    assert by_name["CFO"] == "Keep Satisfied"
    assert by_name["Support lead"] == "Keep Informed"
    assert by_name["Sponsor"] == "Manage Closely"
    assert by_name["Contractor"] == "Monitor"
    assert r["counts"]["Manage Closely"] == 1


def test_matrix_recommendation_present():
    r = matrix.classify([{"name": "Sponsor", "power": 5, "interest": 5}])
    assert "1:1" in r["stakeholders"][0]["recommendation"]


def test_matrix_rejects_empty():
    with pytest.raises(ValueError):
        matrix.classify([])


def test_matrix_rejects_out_of_range():
    with pytest.raises(ValueError):
        matrix.classify([{"name": "X", "power": 0, "interest": 3}])
