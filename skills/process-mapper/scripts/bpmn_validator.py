#!/usr/bin/env python3
"""Structural validator for a lightweight BPMN process graph (stdlib-only).

This does NOT parse BPMN XML. It validates a simplified JSON model that maps
cleanly onto BPMN 2.0 flow semantics, catching the structural mistakes that
make a process map wrong or un-runnable:

- exactly one start event
- at least one end event
- every node is reachable from a start event
- every node (except end events) can reach an end event
- every sequence flow references nodes that exist
- no dangling flows; no node with the wrong number of connections for its type

Input JSON schema:
    {
      "nodes": [
        {"id": "s1", "type": "startEvent", "name": "Start"},
        {"id": "t1", "type": "task", "name": "Do work"},
        {"id": "g1", "type": "exclusiveGateway", "name": "OK?"},
        {"id": "e1", "type": "endEvent", "name": "Done"}
      ],
      "flows": [
        {"from": "s1", "to": "t1"},
        {"from": "t1", "to": "g1"},
        {"from": "g1", "to": "e1"}
      ]
    }
"""
from __future__ import annotations

import argparse
import json
import sys

START = "startEvent"
END = "endEvent"
GATEWAYS = {"exclusiveGateway", "parallelGateway", "inclusiveGateway"}
TASKS = {"task", "userTask", "serviceTask", "subProcess"}
VALID_TYPES = {START, END} | GATEWAYS | TASKS


def _reachable(start_ids, adjacency):
    seen = set()
    stack = list(start_ids)
    while stack:
        node = stack.pop()
        if node in seen:
            continue
        seen.add(node)
        stack.extend(adjacency.get(node, []))
    return seen


def validate(model) -> dict:
    """Validate a BPMN-lite model; return {valid, errors, warnings, stats}."""
    errors = []
    warnings = []

    nodes = model.get("nodes")
    flows = model.get("flows")
    if not isinstance(nodes, list) or not nodes:
        raise ValueError("model needs a non-empty 'nodes' list")
    if not isinstance(flows, list):
        raise ValueError("model needs a 'flows' list")

    ids = [n.get("id") for n in nodes]
    id_set = set(ids)
    if len(id_set) != len(ids):
        errors.append("duplicate node ids present")

    for n in nodes:
        if n.get("type") not in VALID_TYPES:
            errors.append(f"node '{n.get('id')}' has unknown type "
                          f"'{n.get('type')}'")

    starts = [n["id"] for n in nodes if n.get("type") == START]
    ends = [n["id"] for n in nodes if n.get("type") == END]
    if len(starts) != 1:
        errors.append(f"expected exactly 1 start event, found {len(starts)}")
    if len(ends) < 1:
        errors.append("expected at least 1 end event, found 0")

    out_adj = {}
    in_deg = {i: 0 for i in id_set}
    out_deg = {i: 0 for i in id_set}
    for f in flows:
        src, dst = f.get("from"), f.get("to")
        if src not in id_set:
            errors.append(f"flow references missing source '{src}'")
            continue
        if dst not in id_set:
            errors.append(f"flow references missing target '{dst}'")
            continue
        out_adj.setdefault(src, []).append(dst)
        out_deg[src] += 1
        in_deg[dst] += 1

    # degree rules per BPMN element type
    for n in nodes:
        nid, ntype = n.get("id"), n.get("type")
        if ntype == START and in_deg.get(nid, 0) != 0:
            errors.append(f"start event '{nid}' must have no incoming flow")
        if ntype == START and out_deg.get(nid, 0) != 1:
            errors.append(f"start event '{nid}' must have exactly 1 outgoing "
                          "flow")
        if ntype == END and out_deg.get(nid, 0) != 0:
            errors.append(f"end event '{nid}' must have no outgoing flow")
        if ntype == END and in_deg.get(nid, 0) < 1:
            errors.append(f"end event '{nid}' must have >=1 incoming flow")
        if ntype in TASKS:
            if in_deg.get(nid, 0) < 1:
                errors.append(f"task '{nid}' has no incoming flow")
            if out_deg.get(nid, 0) < 1:
                errors.append(f"task '{nid}' has no outgoing flow")
        if ntype in GATEWAYS:
            deg = in_deg.get(nid, 0) + out_deg.get(nid, 0)
            if deg < 3:
                warnings.append(f"gateway '{nid}' has only {deg} connections; "
                                "a gateway should split or merge (>=3)")

    # reachability
    if starts:
        fwd = _reachable(starts, out_adj)
        for nid in id_set:
            if nid not in fwd:
                errors.append(f"node '{nid}' is not reachable from start")
        rev_adj = {}
        for src, dsts in out_adj.items():
            for d in dsts:
                rev_adj.setdefault(d, []).append(src)
        back = _reachable(ends, rev_adj)
        for n in nodes:
            nid = n.get("id")
            if n.get("type") != END and nid not in back:
                errors.append(f"node '{nid}' cannot reach an end event "
                              "(dead end)")

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "stats": {
            "nodes": len(nodes),
            "flows": len(flows),
            "starts": len(starts),
            "ends": len(ends),
            "tasks": sum(1 for n in nodes if n.get("type") in TASKS),
            "gateways": sum(1 for n in nodes if n.get("type") in GATEWAYS),
        },
    }


def _load(path: str):
    if path == "-":
        return json.load(sys.stdin)
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _format_human(result: dict) -> str:
    st = result["stats"]
    lines = [
        "BPMN Structural Validation",
        "==========================",
        f"Nodes: {st['nodes']}  Flows: {st['flows']}  "
        f"Tasks: {st['tasks']}  Gateways: {st['gateways']}",
        f"Result: {'VALID' if result['valid'] else 'INVALID'}",
    ]
    if result["errors"]:
        lines.append("")
        lines.append("Errors:")
        lines.extend(f"  - {e}" for e in result["errors"])
    if result["warnings"]:
        lines.append("")
        lines.append("Warnings:")
        lines.extend(f"  - {w}" for w in result["warnings"])
    return "\n".join(lines)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("model", help="path to BPMN-lite JSON, or '-'")
    parser.add_argument("--json", action="store_true",
                        help="emit machine-readable JSON")
    parser.add_argument("--strict", action="store_true",
                        help="treat warnings as failures (exit 1)")
    args = parser.parse_args(argv)

    try:
        model = _load(args.model)
        result = validate(model)
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(_format_human(result))

    if not result["valid"]:
        return 1
    if args.strict and result["warnings"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
