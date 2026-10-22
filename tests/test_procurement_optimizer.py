import pytest

from conftest import load_tool

cat = load_tool("procurement-optimizer", "spend_categorizer")
sa = load_tool("procurement-optimizer", "spend_analyzer")
ca = load_tool("procurement-optimizer", "consolidation_advisor")


# ---- spend_categorizer ---------------------------------------------------
def test_categorize_with_explicit_map():
    items = [
        {"description": "Dell laptops", "supplier": "Dell", "amount": 45000},
        {"description": "Printer paper", "supplier": "Staples", "amount": 500},
    ]
    cmap = {
        "IT Hardware": ["laptop", "server", "monitor"],
        "Office Supplies": ["paper", "pen", "toner"],
    }
    r = cat.categorize(items, cmap)
    assert r["spend_by_category"]["IT Hardware"]["total"] == 45000
    assert r["spend_by_category"]["IT Hardware"]["count"] == 1
    assert r["spend_by_category"]["Office Supplies"]["total"] == 500
    assert r["uncategorized_total"] == 0
    assert r["categorized_pct"] == 100.0


def test_categorize_uses_default_map_when_omitted():
    items = [{"description": "Annual SaaS subscription", "amount": 12000}]
    r = cat.categorize(items)
    assert r["spend_by_category"]["Software"]["total"] == 12000


def test_categorize_first_match_wins():
    items = [{"description": "laptop paper bundle", "amount": 100}]
    cmap = {
        "IT Hardware": ["laptop"],
        "Office Supplies": ["paper"],
    }
    r = cat.categorize(items, cmap)
    assert r["spend_by_category"]["IT Hardware"]["total"] == 100
    assert "Office Supplies" not in r["spend_by_category"]


def test_categorize_uncategorized_flagged():
    items = [
        {"description": "Mystery widget", "amount": 300},
        {"description": "laptop", "amount": 700},
    ]
    cmap = {"IT Hardware": ["laptop"]}
    r = cat.categorize(items, cmap)
    assert r["uncategorized_total"] == 300
    assert r["uncategorized_pct"] == 30.0
    assert r["categorized_pct"] == 70.0
    assert "Mystery widget" in r["uncategorized_descriptions"]


def test_categorize_case_insensitive():
    items = [{"description": "LAPTOP refresh", "amount": 100}]
    r = cat.categorize(items, {"IT Hardware": ["laptop"]})
    assert r["spend_by_category"]["IT Hardware"]["total"] == 100


def test_categorize_rejects_empty():
    with pytest.raises(ValueError):
        cat.categorize([])


def test_categorize_rejects_negative_amount():
    with pytest.raises(ValueError):
        cat.categorize([{"description": "x", "amount": -1}])


def test_categorize_missing_amount():
    with pytest.raises(ValueError):
        cat.categorize([{"description": "x"}])


# ---- spend_analyzer ------------------------------------------------------
def test_spend_analyzer_ranks_and_classifies():
    spend = [
        {"name": "A", "amount": 800},
        {"name": "B", "amount": 150},
        {"name": "C", "amount": 50},
    ]
    r = sa.analyze(spend)
    ranked = r["ranked"]
    assert ranked[0]["name"] == "A"
    assert ranked[0]["abc_class"] == "A"
    assert ranked[0]["cumulative_pct"] == 80.0
    assert ranked[-1]["abc_class"] == "C"
    assert r["summary"]["total"] == 1000


def test_spend_analyzer_first_entry_always_a():
    spend = [{"name": "Big", "amount": 950}, {"name": "Small", "amount": 50}]
    r = sa.analyze(spend)
    assert r["ranked"][0]["abc_class"] == "A"
    assert r["summary"]["a_count"] == 1


def test_spend_analyzer_tail_stats():
    spend = [
        {"name": "A", "amount": 800},
        {"name": "B", "amount": 150},
        {"name": "C", "amount": 50},
    ]
    r = sa.analyze(spend)
    s = r["summary"]
    assert s["tail_count"] == 1
    assert s["tail_spend"] == 50
    assert s["tail_pct"] == 5.0


def test_spend_analyzer_pareto_stat():
    spend = [
        {"name": "A", "amount": 800},
        {"name": "B", "amount": 150},
        {"name": "C", "amount": 50},
    ]
    r = sa.analyze(spend)
    # Only the first of three entries reaches 80% cumulative.
    assert r["summary"]["pareto_suppliers_pct_for_80"] == pytest.approx(33.33)


def test_spend_analyzer_rejects_empty():
    with pytest.raises(ValueError):
        sa.analyze([])


def test_spend_analyzer_rejects_negative():
    with pytest.raises(ValueError):
        sa.analyze([{"name": "A", "amount": -5}])


# ---- consolidation_advisor -----------------------------------------------
def test_consolidation_flags_fragmented_category():
    records = [
        {"supplier": "A", "category": "IT Hardware", "amount": 50000},
        {"supplier": "B", "category": "IT Hardware", "amount": 30000},
        {"supplier": "C", "category": "Software", "amount": 20000},
    ]
    r = ca.advise(records, savings_rate_pct=10, min_suppliers_to_flag=2)
    it = r["categories"]["IT Hardware"]
    assert it["supplier_count"] == 2
    assert it["flagged"] is True
    assert it["estimated_savings"] == 8000
    assert r["categories"]["Software"]["flagged"] is False
    assert r["categories"]["Software"]["estimated_savings"] == 0


def test_consolidation_ranks_by_savings():
    records = [
        {"supplier": "A", "category": "Small", "amount": 10000},
        {"supplier": "B", "category": "Small", "amount": 10000},
        {"supplier": "C", "category": "Big", "amount": 100000},
        {"supplier": "D", "category": "Big", "amount": 100000},
    ]
    r = ca.advise(records, savings_rate_pct=5)
    assert r["opportunities"][0]["category"] == "Big"
    assert r["total_estimated_savings"] == 11000


def test_consolidation_threshold_excludes_single_supplier():
    records = [
        {"supplier": "A", "category": "Solo", "amount": 5000},
        {"supplier": "A", "category": "Solo", "amount": 5000},
    ]
    r = ca.advise(records, min_suppliers_to_flag=2)
    assert r["categories"]["Solo"]["supplier_count"] == 1
    assert r["categories"]["Solo"]["flagged"] is False
    assert r["opportunities"] == []


def test_consolidation_rejects_bad_savings_rate():
    with pytest.raises(ValueError):
        ca.advise([{"supplier": "A", "category": "X", "amount": 1}],
                  savings_rate_pct=150)


def test_consolidation_rejects_empty():
    with pytest.raises(ValueError):
        ca.advise([])


def test_consolidation_missing_category():
    with pytest.raises(ValueError):
        ca.advise([{"supplier": "A", "amount": 10}])
