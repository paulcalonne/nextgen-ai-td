#!/usr/bin/env python3
"""TD 2, Pair A: unit tests of Orchestrateur.vote_k_sur_n (no network, no key, no reference).
    python3 test-vote.py        -> prints one line per test and exits 1 on the first failure"""
import importlib.util
import sys
from pathlib import Path
from types import SimpleNamespace as P

spec = importlib.util.spec_from_file_location("sk", Path(__file__).with_name("skeleton-multi-llm-en.py"))
mod = importlib.util.module_from_spec(spec); sys.modules["sk"] = mod; spec.loader.exec_module(mod)
vote = lambda props, k: mod.Orchestrateur.vote_k_sur_n(None, props, k)


def prop(model, value, verdict="executed", provider="groq"):
    return P(provider=provider, model_requested=model, value=value, verdict=verdict)


def expect_error(name, props, k):
    try:
        vote(props, k)
    except ValueError as exc:
        print(f"OK   {name}: ValueError ({exc})")
        return
    print(f"FAIL {name}: no ValueError"); sys.exit(1)


def expect(name, props, k, **want):
    got = vote(props, k)
    bad = {key: (got[key], val) for key, val in want.items() if got[key] != val}
    if bad:
        print(f"FAIL {name}: {bad}"); sys.exit(1)
    print(f"OK   {name}: {got}")


a, b, c = prop("a", 100), prop("b", 100), prop("c", 120)
# 1. strict majority of k
expect_error("k=1 with n=3 (not a strict majority)", [a, b, c], 1)
expect_error("k=4 with n=3 (k > n)", [a, b, c], 4)
expect_error("k=2 with n=4 (n // 2 = 2, need k > 2)", [a, b, c, prop("d", 100)], 2)
expect_error("k=0", [a, b, c], 0)
# 2. a duplicate is not a second vote
expect_error("same (provider, model) twice", [a, prop("a", 100), c], 2)
# 3. consensus and abstention
expect("2-of-3 agreement", [a, b, c], 2, consensus=True, value=100, votes=2, models=["groq:a", "groq:b"])
expect("2-of-3 disagreement abstains", [a, prop("b", 110), c], 2, consensus=False, value=None, votes=1, models=[])
expect("3-of-5 with only 2 equal values abstains", [a, b, c, prop("d", 130), prop("e", 140)], 3, consensus=False, value=None, votes=2)
expect("3-of-5 with 3 equal values", [a, b, prop("c", 100), prop("d", 130), prop("e", 140)], 3, consensus=True, value=100, votes=3)
# 4. errors and unavailable members stay in n without a vote
err = prop("c", None, verdict="error")
expect("error stays in n: 2-of-3 still reachable", [a, b, err], 2, consensus=True, value=100, votes=2)
expect("error stays in n: k=3 is not reachable with 2 votes", [a, b, err], 3, consensus=False, votes=2)
expect("all members failed", [prop("a", None, "error"), prop("b", None, "error"), err], 2, consensus=False, value=None, votes=0)
# 5. a wrong consensus is still a consensus: the vote never sees the reference
expect("wrong consensus is returned (agreement is not a proof)", [prop("a", 0), prop("b", 0), prop("c", 100)], 2, consensus=True, value=0, votes=2)
# 6. value 0 is a valid vote (revenue 0, C06 and C14), not a missing value
expect("value 0 counts as a vote", [prop("a", 0), prop("b", 0), prop("c", 5)], 2, consensus=True, value=0, votes=2)
print("all tests passed")
