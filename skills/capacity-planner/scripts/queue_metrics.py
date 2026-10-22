#!/usr/bin/env python3
"""M/M/c queue metrics (stdlib-only, self-contained).

Computes the steady-state performance of an M/M/c queue -- Poisson arrivals at
rate ``lambda``, exponential service at rate ``mu`` per server, and ``c``
identical parallel servers. This is the queueing-theory view behind Erlang-C
staffing: it reports how long work waits and how much work-in-progress piles up
for a given arrival rate and service rate.

Definitions:
    A    = lambda / mu                 offered load (Erlangs)
    rho  = lambda / (c * mu) = A / c   server utilization (must be < 1)
    Pw   = Erlang-C probability of wait
    Lq   = Pw * rho / (1 - rho)        mean number waiting in queue
    Wq   = Lq / lambda                 mean wait in queue (Little's Law)
    L    = Lq + A                      mean number in system
    W    = Wq + 1 / mu                 mean time in system

The Erlang-C term is derived from a self-contained, numerically stable Erlang-B
recursion; this script does NOT import erlang_c.py so it stands alone.

Input JSON schema (object):
    {
      "arrival_rate": 0.5,
      "service_rate": 0.1,
      "servers": 6
    }
Rates must share a time unit (e.g. per minute). ``service_rate`` is per server.
"""
from __future__ import annotations

import argparse
import json
import sys


def _erlang_b(a: float, n: int) -> float:
    """Stable Erlang-B recursion b_0 = 1, b_k = (a*b)/(k + a*b)."""
    b = 1.0
    for k in range(1, n + 1):
        b = (a * b) / (k + a * b)
    return b


def _erlang_c(a: float, n: int) -> float:
    """Erlang-C probability of wait for load ``a`` and ``n`` servers."""
    if n <= a:
        return 1.0
    b = _erlang_b(a, n)
    return (n * b) / (n - a * (1 - b))


def metrics(arrival_rate: float, service_rate: float, servers: int) -> dict:
    """Return M/M/c steady-state metrics for the given parameters."""
    if arrival_rate <= 0:
        raise ValueError("arrival_rate must be > 0")
    if service_rate <= 0:
        raise ValueError("service_rate must be > 0")
    if servers <= 0:
        raise ValueError("servers must be > 0")

    a = arrival_rate / service_rate
    rho = a / servers

    if rho >= 1:
        return {
            "offered_load": round(a, 6),
            "utilization": round(rho, 6),
            "stable": False,
            "prob_wait": 1.0,
            "Lq": None,
            "Wq": None,
            "L": None,
            "W": None,
        }

    pw = _erlang_c(a, servers)
    lq = pw * rho / (1 - rho)
    wq = lq / arrival_rate
    length = lq + a
    w = wq + 1 / service_rate

    return {
        "offered_load": round(a, 6),
        "utilization": round(rho, 6),
        "stable": True,
        "prob_wait": round(pw, 6),
        "Lq": round(lq, 6),
        "Wq": round(wq, 6),
        "L": round(length, 6),
        "W": round(w, 6),
    }


def compute(data: dict) -> dict:
    """Return M/M/c metrics for an input dict."""
    for key in ("arrival_rate", "service_rate", "servers"):
        if key not in data:
            raise ValueError(f"input missing required key '{key}'")
    return metrics(float(data["arrival_rate"]), float(data["service_rate"]),
                   int(data["servers"]))


def _load(path: str):
    if path == "-":
        return json.load(sys.stdin)
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _format_human(result: dict) -> str:
    lines = [
        "M/M/c Queue Metrics",
        "===================",
        f"Offered load (Erlangs):    {result['offered_load']}",
        f"Utilization (rho):         {round(result['utilization'] * 100, 1)}%",
    ]
    if not result["stable"]:
        lines.append("")
        lines.append("WARNING: utilization >= 1 - the queue is unstable and "
                     "grows without bound. Add servers or cut arrival rate.")
        return "\n".join(lines)
    lines.extend([
        f"Probability of wait:       {round(result['prob_wait'] * 100, 1)}%",
        f"Lq (waiting in queue):     {result['Lq']}",
        f"Wq (time waiting):         {result['Wq']}",
        f"L  (in system):            {result['L']}",
        f"W  (time in system):       {result['W']}",
    ])
    return "\n".join(lines)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("input", help="path to input JSON file, or '-' for "
                        "stdin")
    parser.add_argument("--json", action="store_true",
                        help="emit machine-readable JSON")
    args = parser.parse_args(argv)

    try:
        data = _load(args.input)
        result = compute(data)
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
