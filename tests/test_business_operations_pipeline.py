import pytest

from conftest import load_tool

ps = load_tool("business-operations-pipeline", "play_selector")


def test_select_by_play_name():
    r = ps.select(goal="fix-a-slow-process")
    assert r["play"] == "fix-a-slow-process"
    assert r["matched_by"] == "play-name"
    assert r["confidence"] == "high"
    assert r["sequence"][0] == "process-mapper"
    assert r["sequence"][-1] == "internal-comms"
    assert r["fork"] is True


def test_steps_have_carry_forward_contract():
    r = ps.select(goal="standardize-operations")
    steps = r["steps"]
    assert steps[0]["consumes"].startswith("engagement goal")
    assert "prior stage outputs" in steps[1]["consumes"]
    assert [s["order"] for s in steps] == [1, 2, 3]
    for s in steps:
        assert s["invoke"].startswith("run skill")


def test_select_by_keywords_high_confidence():
    r = ps.select(keywords=["bottleneck", "backlog"])
    assert r["play"] == "fix-a-slow-process"
    assert r["matched_by"] == "keywords"
    assert r["confidence"] == "high"


def test_select_by_free_text():
    r = ps.select(goal="we are drowning in tickets and understaffed")
    assert r["play"] == "scale-support"


def test_select_cut_spend():
    r = ps.select(goal="we have too many suppliers and want to save money")
    assert r["play"] == "cut-spend"


def test_custom_skills_ordered_by_value_chain():
    r = ps.select(skills=["internal-comms", "process-mapper", "knowledge-ops"])
    assert r["play"] == "custom"
    assert r["matched_by"] == "explicit-skills"
    # value-chain order: diagnose(1) -> document(4) -> communicate(5)
    assert r["sequence"] == ["process-mapper", "knowledge-ops",
                             "internal-comms"]


def test_custom_dedupes():
    r = ps.select(skills=["internal-comms", "internal-comms"])
    assert r["sequence"] == ["internal-comms"]


def test_custom_rejects_unknown_skill():
    with pytest.raises(ValueError):
        ps.select(skills=["not-a-skill"])


def test_custom_rejects_empty():
    with pytest.raises(ValueError):
        ps.select(skills=[])


def test_no_input_raises():
    with pytest.raises(ValueError):
        ps.select()


def test_no_keyword_match_falls_back_low_confidence():
    r = ps.select(goal="xyzzy nothing matches here")
    assert r["play"] == "full-ops-review"
    assert r["matched_by"] == "fallback"
    assert r["confidence"] == "low"
    assert "note" in r


def test_full_ops_review_is_complete_chain():
    r = ps.select(goal="full-ops-review")
    assert len(r["sequence"]) == 6
    assert r["sequence"][0] == "process-mapper"
    assert r["sequence"][-1] == "internal-comms"


def test_list_plays_shape():
    plays = ps.list_plays()
    assert set(plays) == {
        "fix-a-slow-process", "onboard-a-vendor", "cut-spend",
        "scale-support", "standardize-operations", "full-ops-review",
    }
    for info in plays.values():
        assert "sequence" in info and "summary" in info


def test_cli_list_runs():
    assert ps.main(["--list"]) == 0


def test_cli_goal_runs():
    assert ps.main(["--goal", "fix-a-slow-process", "--json"]) == 0
