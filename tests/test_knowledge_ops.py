import pathlib

import pytest

from conftest import load_tool

w2h = load_tool("knowledge-ops", "fivew2h_validator")
sop = load_tool("knowledge-ops", "sop_linter")
rb = load_tool("knowledge-ops", "runbook_validator")

ASSETS = (pathlib.Path(__file__).resolve().parent.parent
          / "skills" / "knowledge-ops" / "assets")


def _read_asset(name):
    return (ASSETS / name).read_text(encoding="utf-8")


# ---- fivew2h_validator ---------------------------------------------------
def _full_5w2h():
    return {
        "who": "AP clerk",
        "what": "process the vendor invoice",
        "when": "on receipt of a matched invoice",
        "where": "NetSuite AP module",
        "why": "pay vendors on terms and avoid late fees",
        "how": "three-way match, then post, then route for approval",
        "how_much": "invoices under the $5k auto-approve threshold",
    }


def test_5w2h_complete_structured():
    r = w2h.validate(_full_5w2h())
    assert r["valid"] is True
    assert r["completeness_score"] == 1.0
    assert r["missing"] == []


def test_5w2h_missing_and_empty_elements():
    data = _full_5w2h()
    del data["how_much"]
    data["why"] = "   "
    r = w2h.validate(data)
    assert r["valid"] is False
    missing = {m["element"] for m in r["missing"]}
    assert missing == {"why", "how_much"}
    assert all(m["prompt"] for m in r["missing"])


def test_5w2h_rejects_non_dict():
    with pytest.raises(ValueError):
        w2h.validate("not a dict")


def test_5w2h_text_worksheet_full():
    r = w2h.validate_text(_read_asset("5w2h-worksheet.md"))
    assert r["valid"] is True
    assert r["elements"]["how"] is True
    assert r["elements"]["how_much"] is True


def test_5w2h_text_detects_gaps():
    text = "# Intake\n\n## Who owns it\nThe clerk.\n\n## What happens\nStuff.\n"
    r = w2h.validate_text(text)
    assert r["valid"] is False
    missing = {m["element"] for m in r["missing"]}
    assert "why" in missing and "how_much" in missing


def test_5w2h_text_rejects_empty():
    with pytest.raises(ValueError):
        w2h.validate_text("   ")


# ---- sop_linter ----------------------------------------------------------
def _full_sop():
    return {
        "title": "Process a vendor invoice",
        "purpose": "Pay invoices accurately and on terms.",
        "scope": "Non-PO invoices under $5k in NetSuite.",
        "roles": ["AP clerk"],
        "steps": ["Open the invoice in NetSuite.",
                  "Match it against the receiving record."],
        "revision_history": [{"version": "1.0", "date": "2026-01-01"}],
    }


def test_sop_valid():
    r = sop.lint(_full_sop())
    assert r["valid"] is True
    assert r["errors"] == []
    assert r["stats"]["step_count"] == 2


def test_sop_missing_required_sections():
    r = sop.lint({"title": "x", "steps": []})
    assert r["valid"] is False
    joined = " ".join(r["errors"])
    assert "purpose" in joined and "scope" in joined and "steps" in joined


def test_sop_non_imperative_step_warns():
    data = _full_sop()
    data["steps"] = ["The invoice is opened by the clerk."]
    r = sop.lint(data)
    assert any("imperative" in w for w in r["warnings"])


def test_sop_long_step_warns():
    data = _full_sop()
    data["steps"] = ["Open " + "and record ".join(["x"] * 32)]
    r = sop.lint(data)
    assert any(">30" in w or "words" in w for w in r["warnings"])


def test_sop_no_revision_history_warns():
    data = _full_sop()
    data["revision_history"] = []
    r = sop.lint(data)
    assert any("revision" in w for w in r["warnings"])


def test_sop_rejects_non_dict():
    with pytest.raises(ValueError):
        sop.lint(["not", "a", "dict"])


def test_sop_text_template_valid():
    r = sop.validate_text(_read_asset("sop.template.md"))
    assert r["valid"] is True
    assert r["stats"]["section_count"] >= 4


def test_sop_text_detects_missing_section():
    text = "# Title only\n\n## Procedure\n1. Do a thing.\n2. Do another.\n"
    r = sop.validate_text(text)
    assert r["valid"] is False
    assert any("scope" in e for e in r["errors"])


# ---- runbook_validator ---------------------------------------------------
def _full_runbook():
    return {
        "title": "API latency incident response",
        "trigger": "p99 latency alarm fires for 5 minutes",
        "prerequisites": ["prod kubectl access"],
        "steps": ["Check the dashboard.", "Scale the deployment."],
        "verification": "p99 under 300ms for 10 minutes",
        "rollback": "Revert the scale change.",
        "escalation": ["platform on-call L2"],
    }


def test_runbook_valid():
    r = rb.validate(_full_runbook())
    assert r["valid"] is True
    assert r["completeness_score"] == 1.0
    assert r["errors"] == []


def test_runbook_missing_required_parts():
    data = _full_runbook()
    del data["verification"]
    del data["escalation"]
    r = rb.validate(data)
    assert r["valid"] is False
    joined = " ".join(r["errors"])
    assert "verification" in joined and "escalation" in joined


def test_runbook_warns_on_gaps():
    data = _full_runbook()
    data["prerequisites"] = []
    data["rollback"] = ""
    data["steps"] = ["Do the one thing."]
    r = rb.validate(data)
    joined = " ".join(r["warnings"])
    assert "prerequisites" in joined
    assert "rollback" in joined
    assert "step" in joined


def test_runbook_rejects_non_dict():
    with pytest.raises(ValueError):
        rb.validate(42)


def test_runbook_text_template_full():
    r = rb.validate_text(_read_asset("runbook.template.md"))
    assert r["completeness_score"] == 1.0
    assert r["valid"] is True
    assert r["stats"]["part_count"] == 7
