#!/usr/bin/env python3
"""Play selector for the business-operations pipeline (stdlib-only).

The pipeline runner chains several business-operations sub-skills as a named
"play" - a predefined, ordered sequence for a common operational goal. This
tool turns a goal (a play name, free-text keywords, or an explicit list of
skills) into a deterministic ordered sequence of sub-skills to run, each tagged
with its value-chain stage and a carry-forward contract.

Value chain (sequencing backbone):
    diagnose (1) -> decide: size/source (2) -> govern (3)
    -> document (4) -> communicate (5)

Input JSON schema (any one of the keys, all optional):
    {"goal": "fix-a-slow-process" | "free text describing the goal",
     "keywords": ["bottleneck", "backlog"],
     "skills": ["process-mapper", "internal-comms"]}

- goal that matches a play name  -> that play (confidence high)
- skills list                    -> a custom play, ordered by value chain
- goal text and/or keywords      -> best-matching play by keyword overlap
"""
from __future__ import annotations

import argparse
import json
import sys
from typing import Optional

# skill -> (stage, value-chain rank, what the step produces)
SKILL_STAGE = {
    "process-mapper": ("diagnose", 1,
                       "Process map, PCE/lead time, the constraint"),
    "capacity-planner": ("size", 2,
                         "Staffing/FTE, service level, occupancy verdict"),
    "procurement-optimizer": ("source", 2,
                              "Spend categorization, ABC, consolidation ops"),
    "vendor-management": ("govern", 3,
                          "SLA/error-budget, Kraljic risk, scorecard"),
    "knowledge-ops": ("document", 4, "SOP/runbook, 5W2H-validated"),
    "internal-comms": ("communicate", 5,
                       "ADKAR/Kotter/stakeholder comms plan"),
}

PLAYS = {
    "fix-a-slow-process": ["process-mapper", "capacity-planner",
                           "knowledge-ops", "internal-comms"],
    "onboard-a-vendor": ["vendor-management", "process-mapper",
                         "knowledge-ops", "internal-comms"],
    "cut-spend": ["procurement-optimizer", "vendor-management",
                  "internal-comms"],
    "scale-support": ["capacity-planner", "process-mapper",
                      "knowledge-ops", "internal-comms"],
    "standardize-operations": ["process-mapper", "knowledge-ops",
                               "internal-comms"],
    "full-ops-review": ["process-mapper", "capacity-planner",
                        "procurement-optimizer", "vendor-management",
                        "knowledge-ops", "internal-comms"],
}

PLAY_KEYWORDS = {
    "fix-a-slow-process": ["slow", "bottleneck", "delay", "backlog",
                           "cycle time", "lead time", "turnaround",
                           "takes too long", "stuck"],
    "onboard-a-vendor": ["onboard", "new vendor", "new supplier",
                         "vendor onboarding", "integrate supplier",
                         "set up vendor", "bring on a vendor"],
    "cut-spend": ["cut spend", "reduce cost", "save money", "consolidate",
                  "too many suppliers", "tail spend", "sourcing", "maverick"],
    "scale-support": ["drowning in tickets", "scale support", "understaffed",
                      "headcount", "hire", "volume spike", "staffing",
                      "can't keep up", "cannot keep up"],
    "standardize-operations": ["standardize", "document", "inconsistent",
                               "no sop", "tribal knowledge", "onboarding docs",
                               "runbook", "write it down"],
    "full-ops-review": ["full review", "end to end", "end-to-end", "overhaul",
                        "audit operations", "everything", "complete review",
                        "transform operations", "soup to nuts"],
}

PLAY_SUMMARY = {
    "fix-a-slow-process": "Diagnose the flow and constraint, decide if it is a "
                          "staffing problem, document the fix, announce it.",
    "onboard-a-vendor": "Risk-assess and scorecard the vendor, map onboarding, "
                        "write the runbook, communicate go-live.",
    "cut-spend": "Categorize and consolidate spend, govern the survivors, "
                 "communicate the sourcing change.",
    "scale-support": "Size staffing for demand, streamline the flow, document "
                     "SOPs, communicate the change.",
    "standardize-operations": "Map the as-is, author SOP/runbook, roll out via "
                              "change comms.",
    "full-ops-review": "The full value chain: diagnose, size, source, govern, "
                       "document, communicate.",
}

FALLBACK_PLAY = "full-ops-review"


def _ordered_custom(skills):
    unknown = [s for s in skills if s not in SKILL_STAGE]
    if unknown:
        raise ValueError(f"unknown skill(s): {', '.join(unknown)}")
    if not skills:
        raise ValueError("skills list is empty")
    # stable sort by value-chain rank; ties keep the caller's order
    return sorted(dict.fromkeys(skills), key=lambda s: SKILL_STAGE[s][1])


def _score_keywords(text):
    blob = text.lower()
    best, best_score = None, 0
    for play, kws in PLAY_KEYWORDS.items():
        score = sum(1 for kw in kws if kw in blob)
        if score > best_score:
            best, best_score = play, score
    return best, best_score


def _build_steps(sequence):
    steps = []
    for i, skill in enumerate(sequence):
        stage, rank, produces = SKILL_STAGE[skill]
        consumes = ("engagement goal + raw inputs" if i == 0
                    else "engagement packet (goal + prior stage outputs)")
        steps.append({
            "order": i + 1,
            "skill": skill,
            "stage": stage,
            "rank": rank,
            "consumes": consumes,
            "produces": produces,
            "invoke": f"run skill '{skill}' via context: fork",
        })
    return steps


def select(goal: Optional[str] = None, keywords=None, skills=None) -> dict:
    """Resolve a goal/keywords/skills into an ordered play. See module docs."""
    keywords = keywords or []
    if not goal and not keywords and not skills:
        raise ValueError("provide one of: goal, keywords, or skills")

    if skills:
        sequence = _ordered_custom(list(skills))
        return _result("custom", "explicit-skills", "high", sequence)

    if goal and goal in PLAYS:
        return _result(goal, "play-name", "high", PLAYS[goal])

    text = " ".join([goal or ""] + list(keywords)).strip()
    play, score = _score_keywords(text)
    if play is None:
        return _result(FALLBACK_PLAY, "fallback", "low", PLAYS[FALLBACK_PLAY],
                       note="No play matched; defaulting to a full review - "
                            "grill the user before running it.")
    confidence = "high" if score >= 2 else "medium"
    return _result(play, "keywords", confidence, PLAYS[play],
                   note=f"matched {score} keyword(s)")


def _result(play, matched_by, confidence, sequence, note=None) -> dict:
    out = {
        "play": play,
        "matched_by": matched_by,
        "confidence": confidence,
        "summary": PLAY_SUMMARY.get(play, "Custom value-chain sequence."),
        "sequence": sequence,
        "steps": _build_steps(sequence),
        "fork": True,
    }
    if note:
        out["note"] = note
    return out


def list_plays() -> dict:
    return {name: {"sequence": seq, "summary": PLAY_SUMMARY[name]}
            for name, seq in PLAYS.items()}


def _load(path: str):
    if path == "-":
        return json.load(sys.stdin)
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _format_human(result: dict) -> str:
    lines = [
        "Business-Operations Pipeline — Play",
        "===================================",
        f"Play:        {result['play']}",
        f"Matched by:  {result['matched_by']} (confidence: "
        f"{result['confidence']})",
        f"Summary:     {result['summary']}",
    ]
    if "note" in result:
        lines.append(f"Note:        {result['note']}")
    lines.append("")
    lines.append("Sequence (each step runs via context: fork):")
    for s in result["steps"]:
        lines.append(f"  {s['order']}. {s['skill']:<22} [{s['stage']}] -> "
                     f"{s['produces']}")
    return "\n".join(lines)


def _format_catalog() -> str:
    lines = ["Available plays", "==============="]
    for name, info in list_plays().items():
        lines.append(f"- {name}: {' -> '.join(info['sequence'])}")
        lines.append(f"    {info['summary']}")
    return "\n".join(lines)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("input", nargs="?", default=None,
                        help="path to a goal JSON file, or '-' for stdin")
    parser.add_argument("--goal", default=None,
                        help="a play name or free-text goal")
    parser.add_argument("--keyword", action="append", default=[],
                        help="a keyword (repeatable)")
    parser.add_argument("--skill", action="append", default=[],
                        help="an explicit sub-skill to include (repeatable)")
    parser.add_argument("--list", action="store_true",
                        help="list the named plays and exit")
    parser.add_argument("--json", action="store_true",
                        help="emit machine-readable JSON")
    args = parser.parse_args(argv)

    if args.list:
        if args.json:
            print(json.dumps(list_plays(), indent=2))
        else:
            print(_format_catalog())
        return 0

    try:
        if args.input:
            payload = _load(args.input)
            result = select(payload.get("goal"), payload.get("keywords"),
                            payload.get("skills"))
        else:
            result = select(args.goal or None, args.keyword or None,
                            args.skill or None)
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(_format_human(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
