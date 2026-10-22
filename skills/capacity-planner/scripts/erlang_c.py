#!/usr/bin/env python3
"""Erlang-C staffing calculator for queues with waiting (stdlib-only).

Given an offered call/contact load and a team size, this computes the core
Erlang-C service metrics used to size inbound queues (contact centers, help
desks, dispatch, triage):

- Offered load A (Erlangs): (calls_per_interval * aht_seconds) / interval_seconds.
- Probability of wait (Erlang-C): the chance an arriving contact is queued.
- Service level: fraction answered within the target answer time.
- Average speed of answer (ASA): mean wait across all contacts.
- Occupancy: the share of agent time spent handling contacts = A / N.

Erlang-C assumes Poisson arrivals, exponential handle times, N parallel agents,
infinite patience (no abandonment), and queued-not-blocked contacts. It is the
industry-standard first-cut staffing model; it tends to over-staff slightly
because real callers abandon (see references/erlang-c-queueing.md).

The probability of wait is derived from a numerically stable Erlang-B recursion
and then converted to Erlang-C, which avoids the factorial overflow that the
textbook closed form hits for large N.

Input JSON schema (object):
    {
      "calls_per_interval": 100,
      "interval_seconds": 1800,
      "aht_seconds": 180,
      "agents": 14,
      "target_answer_seconds": 20
    }
Optional "target_service_level" (e.g. 0.8) with "target_answer_seconds" adds
"min_agents_for_target": the smallest agent count meeting that service level.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from typing import Optional


def erlang_b(a: float, n: int) -> float:
    """Return Erlang-B blocking probability for load ``a`` and ``n`` servers.

    Uses the stable iterative recursion b_0 = 1, b_k = (a*b)/(k + a*b).
    """
    if a < 0:
        raise ValueError("offered load must be >= 0")
    if n < 0:
        raise ValueError("servers must be >= 0")
    b = 1.0
    for k in range(1, n + 1):
        b = (a * b) / (k + a * b)
    return b


def erlang_c(a: float, n: int) -> float:
    """Return the Erlang-C probability that an arriving contact must wait.

    ``a`` is the offered load in Erlangs; ``n`` is the number of agents. If
    ``n <= a`` the queue is unstable and the probability of wait is 1.0.
    """
    if a < 0:
        raise ValueError("offered load must be >= 0")
    if n <= 0:
        raise ValueError("agents must be > 0")
    if n <= a:
        return 1.0
    b = erlang_b(a, n)
    return (n * b) / (n - a * (1 - b))


def service_metrics(a: float, n: int, aht_seconds: float,
                    target_answer_seconds: float) -> dict:
    """Return probability of wait, service level, ASA, and occupancy."""
    if aht_seconds <= 0:
        raise ValueError("aht_seconds must be > 0")
    if target_answer_seconds < 0:
        raise ValueError("target_answer_seconds must be >= 0")
    pw = erlang_c(a, n)
    if n <= a:
        return {
            "probability_wait": 1.0,
            "service_level": 0.0,
            "asa_seconds": None,
            "occupancy": round(a / n, 6) if n else None,
            "stable": False,
        }
    exponent = -(n - a) * target_answer_seconds / aht_seconds
    service_level = 1 - pw * math.exp(exponent)
    asa = pw * aht_seconds / (n - a)
    return {
        "probability_wait": round(pw, 6),
        "service_level": round(service_level, 6),
        "asa_seconds": round(asa, 4),
        "occupancy": round(a / n, 6),
        "stable": True,
    }


def offered_load(calls_per_interval: float, interval_seconds: float,
                 aht_seconds: float) -> float:
    """Return offered load A in Erlangs."""
    if calls_per_interval < 0:
        raise ValueError("calls_per_interval must be >= 0")
    if interval_seconds <= 0:
        raise ValueError("interval_seconds must be > 0")
    if aht_seconds <= 0:
        raise ValueError("aht_seconds must be > 0")
    return (calls_per_interval * aht_seconds) / interval_seconds


def min_agents_for_target(a: float, aht_seconds: float,
                          target_answer_seconds: float,
                          target_service_level: float) -> int:
    """Return the smallest agent count meeting the target service level.

    Iterates N up from floor(A) + 1 (the first potentially stable count).
    """
    if not 0 < target_service_level < 1:
        raise ValueError("target_service_level must be in (0, 1)")
    n = int(math.floor(a)) + 1
    # Hard ceiling guards against a target that can never be met numerically.
    ceiling = n + 10000
    while n < ceiling:
        sl = service_metrics(a, n, aht_seconds, target_answer_seconds)
        if sl["service_level"] >= target_service_level:
            return n
        n += 1
    raise ValueError("could not meet target service level below agent ceiling")


def plan(data: dict) -> dict:
    """Return the full Erlang-C staffing result for an input dict."""
    required = ("calls_per_interval", "interval_seconds", "aht_seconds")
    for key in required:
        if key not in data:
            raise ValueError(f"input missing required key '{key}'")
    a = offered_load(float(data["calls_per_interval"]),
                     float(data["interval_seconds"]),
                     float(data["aht_seconds"]))
    aht = float(data["aht_seconds"])
    target_t = float(data.get("target_answer_seconds", 20))

    result = {
        "offered_load": round(a, 6),
        "target_answer_seconds": target_t,
    }

    if "agents" in data:
        n = int(data["agents"])
        if n <= 0:
            raise ValueError("agents must be > 0")
        metrics = service_metrics(a, n, aht, target_t)
        result["agents"] = n
        result.update(metrics)

    tsl = data.get("target_service_level")
    if tsl is not None:
        tsl = float(tsl)
        result["target_service_level"] = tsl
        result["min_agents_for_target"] = min_agents_for_target(
            a, aht, target_t, tsl)

    return result


def _load(path: str):
    if path == "-":
        return json.load(sys.stdin)
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _format_human(result: dict) -> str:
    lines = [
        "Erlang-C Staffing Analysis",
        "==========================",
        f"Offered load (Erlangs):    {result['offered_load']}",
    ]
    if "agents" in result:
        lines.append(f"Agents:                    {result['agents']}")
        lines.append(f"Occupancy:                 "
                     f"{round(result['occupancy'] * 100, 1)}%")
        lines.append(f"Probability of wait:       "
                     f"{round(result['probability_wait'] * 100, 1)}%")
        lines.append(f"Service level (<= {int(result['target_answer_seconds'])}s): "
                     f"{round(result['service_level'] * 100, 1)}%")
        asa = result["asa_seconds"]
        lines.append(f"Avg speed of answer (s):   "
                     f"{asa if asa is not None else 'n/a (unstable)'}")
        if not result.get("stable", True):
            lines.append("")
            lines.append("WARNING: agents <= offered load - the queue is "
                         "unstable and wait grows without bound. Add agents.")
    if "min_agents_for_target" in result:
        lines.append("")
        lines.append(f"Min agents for {round(result['target_service_level'] * 100)}% "
                     f"in {int(result['target_answer_seconds'])}s: "
                     f"{result['min_agents_for_target']}")
    return "\n".join(lines)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("input", help="path to input JSON file, or '-' for "
                        "stdin")
    parser.add_argument("--required-agents", action="store_true",
                        help="report only the min agents meeting the target "
                        "service level (needs target_service_level in input)")
    parser.add_argument("--json", action="store_true",
                        help="emit machine-readable JSON")
    args = parser.parse_args(argv)

    try:
        data = _load(args.input)
        if args.required_agents and "target_service_level" not in data:
            raise ValueError(
                "--required-agents needs 'target_service_level' in input")
        result = plan(data)
        if args.required_agents:
            result = {
                "offered_load": result["offered_load"],
                "target_answer_seconds": result["target_answer_seconds"],
                "target_service_level": result["target_service_level"],
                "min_agents_for_target": result["min_agents_for_target"],
            }
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
