#!/usr/bin/env python3
"""TD 2 (Pair C): routing rule derived from OUR TD 1 traces (DIA6-G5). Adapted from the teacher simulator.

Synthetic availability, no API call, no key. Eligibility levels come from our stored TD 1 results
(traces-TD1.csv / model-question-comparison-en.csv), not from model IQ or public index:
    level 1 = families without age condition (F1 period C01,C04-C07,C20 ; F3 product C03,C12-C14)
    level 2 = age-only questions (F2 C02,C08,C09,C11 ; F2b C10)
    level 3 = combined age + period/product (C15-C19): NO model was 100% in TD 1, so level 3 means
              "may propose, never alone": the checks column then always contains a quorum or a deterministic check.
Cost: fictional only for the paid OpenRouter route of the SAME model (0.15 / 0.60 USD per million tokens,
portfolio 2026-09-28): ~716 prompt + ~228 completion tokens per call in our traces -> ~0.00025 USD per request.
"""
import argparse
import json

TD1 = {
    "north": "TD1 north-mini: F1 6/6 (C01,C04-C07,C20), F3 4/4 (C03,C12-C14), F2 0/4 (C02,C08,C09,C11)",
    "dots": "TD1 dots: F1 6/6, F3 4/4, F2 0/4, F2b 1/1 (C10), combos 1/5",
    "20b": "TD1 gpt-oss-20b: F1 5/6 (C20 = Groq 429, not a wrong answer), F3 4/4, F2 2/4 (C09,C11 wrong), combos 4/5",
    "120b": "TD1 gpt-oss-120b: F1 6/6, F3 4/4, F2 4/4, F2b 1/1, combos 3/5 (C15,C16 wrong)",
}

RESOURCES = [
    {"id": "north-mini-free", "rank": 1, "level": 1, "access": "free", "available": True, "cash": 0.0,
     "allocation": 0.0, "reset_minutes": None, "td1": TD1["north"]},
    {"id": "dots-free", "rank": 2, "level": 1, "access": "free", "available": True, "cash": 0.0,
     "allocation": 0.0, "reset_minutes": None, "td1": TD1["dots"]},
    {"id": "gpt-oss-20b-groq-free", "rank": 3, "level": 1, "access": "free", "available": True, "cash": 0.0,
     "allocation": 0.0, "reset_minutes": None, "td1": TD1["20b"]},
    {"id": "gpt-oss-120b-groq-free", "rank": 4, "level": 3, "access": "free", "available": True, "cash": 0.0,
     "allocation": 0.0, "reset_minutes": None, "td1": TD1["120b"]},
    {"id": "gpt-oss-120b-openrouter-paid", "rank": 5, "level": 3, "access": "tokens", "available": True,
     "cash": 0.00025, "allocation": 0.00025, "reset_minutes": None, "td1": TD1["120b"] + " (same model, paid route)"},
]

FAMILY_LEVEL = {"F1": 1, "F3": 1, "F2": 2, "F2b": 2, "COMBO": 3}
# level 2 requests must go to a model that was 4/4 on F2: only 120b (qwen 3/4, 20b 2/4, north/dots 0/4).
LEVEL2_ONLY = {"gpt-oss-120b-groq-free", "gpt-oss-120b-openrouter-paid"}

# Checking level = f(family, cost of an error). Consistency constraint of the TD: a single free model, no check,
# only for an internal dashboard AND a family where that model scored 100% in TD 1.
CHECKS = {
    ("F1", "dashboard"): "single model + read-only execution and value check (F1 6/6 for north-mini, dots and 120b)",
    ("F1", "customer"): "2-of-3 quorum (120b, north-mini, qwen); abstain if no consensus",
    ("F1", "payout"): "deterministic reference SQL (human-written) + 2-of-3 quorum must agree",
    ("F3", "dashboard"): "single model + read-only execution and value check (all five models F3 4/4)",
    ("F3", "customer"): "2-of-3 quorum; abstain if no consensus",
    ("F3", "payout"): "deterministic reference SQL (human-written) + 2-of-3 quorum must agree",
    ("F2", "dashboard"): "120b alone + value check (only model 4/4 on F2); never north-mini/dots (0/4)",
    ("F2", "customer"): "2-of-3 quorum; on abstention (C08 case) fall back to deterministic SQL",
    ("F2", "payout"): "deterministic reference SQL (completed-age rule written by a human)",
    ("F2b", "dashboard"): "3-of-5 quorum (a single question C10 is too thin to trust one model alone)",
    ("F2b", "customer"): "3-of-5 quorum + deterministic SQL",
    ("F2b", "payout"): "deterministic reference SQL",
    ("COMBO", "dashboard"): "3-of-5 quorum, else deterministic SQL (no model 100% on C15-C19)",
    ("COMBO", "customer"): "deterministic reference SQL + human review",
    ("COMBO", "payout"): "deterministic reference SQL + human review (no free model answers alone)",
}


def choose(request, resources):
    """Same branch order as the teacher version (run included capacity, defer for a free refill,
    run a paid route within budget, abstain), plus: eligibility from TD 1 level, an explicit `rank`
    tie-break, the checking level from CHECKS and the TD 1 cells in the reason."""
    level = FAMILY_LEVEL.get(request["family"], 4)
    checks = CHECKS.get((request["family"], request["use"]), "unknown family: human review")
    eligible = [r for r in resources if r["level"] >= level
                and not (level == 2 and r["id"] not in LEVEL2_ONLY)]
    if level == 3:  # combos: the proposer is never trusted alone
        eligible = [r for r in eligible if r["id"] in LEVEL2_ONLY]
    why = lambda r, txt: f"{txt}; {r['td1']}"
    included = [r for r in eligible if r["available"] and r["cash"] == 0]
    if included:
        chosen = min(included, key=lambda r: (r["allocation"], r["level"], r["rank"], r["id"]))
        return {"action": "run", "resource": chosen["id"], "cash": 0, "checks": checks,
                "reason": why(chosen, "eligible included capacity")}
    waiting = [r for r in eligible if not r["available"] and r["cash"] == 0
               and r["reset_minutes"] is not None and 0 < r["reset_minutes"] <= request["deadline_minutes"]]
    if waiting and request["can_wait"]:
        chosen = min(waiting, key=lambda r: (r["reset_minutes"], r["rank"]))
        return {"action": "defer", "resource": chosen["id"], "cash": 0, "checks": checks,
                "reason": why(chosen, "free refill before deadline: recheck availability at wake-up (Groq 429 in TD1 cleared after retry for 20b C18/C19)"),
                "wake_in_minutes": chosen["reset_minutes"]}
    paid = [r for r in eligible if r["available"] and r["cash"] <= request["budget"]]
    if paid:
        chosen = min(paid, key=lambda r: (r["cash"], r["allocation"], r["rank"], r["id"]))
        return {"action": "run", "resource": chosen["id"], "cash": chosen["cash"], "checks": checks,
                "reason": why(chosen, "available route within the authorised budget")}
    return {"action": "abstain", "resource": None, "cash": 0, "checks": checks,
            "reason": "no eligible resource within deadline and budget: abstain rather than invent a figure"}


def scenarios():
    base = {"family": "F1", "use": "dashboard", "can_wait": True, "deadline_minutes": 120, "budget": 0.001}
    free_down = [dict(r, available=False, reset_minutes=1) if r["access"] == "free" else dict(r) for r in RESOURCES]
    return [
        ("F1 dashboard", base, RESOURCES),
        ("F1 customer figure", {**base, "use": "customer"}, RESOURCES),
        ("F3 dashboard", {**base, "family": "F3"}, RESOURCES),
        ("F2 dashboard", {**base, "family": "F2"}, RESOURCES),
        ("F2 customer, Groq 429 (can wait)", {**base, "family": "F2", "use": "customer"}, free_down),
        ("F2 customer, Groq 429, urgent", {**base, "family": "F2", "use": "customer", "can_wait": False, "deadline_minutes": 5}, free_down),
        ("F1 urgent, all free down", {**base, "can_wait": False, "deadline_minutes": 5}, free_down),
        ("COMBO payout", {**base, "family": "COMBO", "use": "payout"}, RESOURCES),
        ("COMBO payout, urgent, budget 0", {**base, "family": "COMBO", "use": "payout", "can_wait": False, "budget": 0}, free_down),
        ("unknown family", {**base, "family": "F9"}, RESOURCES),
    ]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scenario", help="show only the named scenario")
    args = parser.parse_args()
    found = False
    for name, request, resources in scenarios():
        if args.scenario and name != args.scenario:
            continue
        found = True
        print(json.dumps({"scenario": name, "nature": "simulation", "request": request,
                          "result": choose(request, resources)}, ensure_ascii=False))
    if not found:
        parser.error("unknown scenario")


if __name__ == "__main__":
    main()
