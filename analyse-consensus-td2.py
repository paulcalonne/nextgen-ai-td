#!/usr/bin/env python3
"""TD 2, Pair B (Paul, Nathanael): wrong consensus C18, C16, C08 on the stored TD 1 traces.

No network, no model call. Every query (faulty model SQL from the traces, reference SQL,
delta query) runs read-only through sandbox_sqlite.execute_query on data/boutique.sqlite.

    python3 analyse-consensus-td2.py      -> prints the checks, writes evidence/wrong-consensus-td2.txt

Nature of the cases: real batch (TD 1 traces, nature = real). The vote never receives the reference;
the comparison is done after the decision.
"""
import csv
import importlib.util
import sys
from pathlib import Path
from types import SimpleNamespace as NS

HERE = Path(__file__).resolve().parent


def load(name, filename):
    spec = importlib.util.spec_from_file_location(name, HERE / filename)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


sk = load("sk", "skeleton-multi-llm-en.py")
sandbox = load("sandbox", "sandbox_sqlite.py")
vote = lambda proposals, k: sk.Orchestrateur.vote_k_sur_n(None, proposals, k)
DB = HERE / "data" / "boutique.sqlite"
TRACES = next(p for p in (HERE / "traces-TD1.csv", HERE / "traces-td1.csv") if p.exists())

M = {
    "120b": ("groq", "openai/gpt-oss-120b"),
    "20b": ("groq", "openai/gpt-oss-20b"),
    "north-mini": ("openrouter", "cohere/north-mini-code:free"),
    "qwen": ("groq", "qwen/qwen3.8-27b"),
    "dots": ("openrouter", "dots-studio/dots-3-note-preview:free"),
}
PANELS = {
    "2-of-3 fixed (120b, north-mini, qwen)": (["120b", "north-mini", "qwen"], 2),
    "3-of-5 (all five)": (list(M), 3),
}
# For each case: the agreeing pair and a valid 2-of-3 panel that contains it (what a panel
# choice would have returned), plus the delta query (rows the reference counts, the faulty SQL drops).
CASES = {
    "C18": {
        "pair": ["north-mini", "dots"],
        "counter_panel": ["120b", "north-mini", "dots"],
        "delta": """SELECT c.customer_id, c.birth_date, SUM(o.quantity_product * p.price)
FROM orders o JOIN product p ON p.product_id = o.product_id JOIN customers c ON c.customer_id = o.customer_id
WHERE o.date >= '2026-05-01 00:00:00' AND o.date < '2026-06-01 00:00:00'
  AND CAST(strftime('%Y', o.date) AS INTEGER) - CAST(strftime('%Y', c.birth_date) AS INTEGER) = 26
  AND strftime('%m-%d', o.date) < strftime('%m-%d', c.birth_date)
GROUP BY c.customer_id ORDER BY c.customer_id""",
    },
    "C16": {
        "pair": ["120b", "dots"],
        "counter_panel": ["120b", "dots", "north-mini"],
        "delta": """SELECT c.customer_id, c.birth_date, SUM(o.quantity_product * p.price)
FROM orders o JOIN product p ON p.product_id = o.product_id JOIN customers c ON c.customer_id = o.customer_id
WHERE o.product_id IN ('a','b','c')
  AND 2026 - CAST(strftime('%Y', c.birth_date) AS INTEGER) = 26
  AND strftime('%m-%d', '2026-09-25') < strftime('%m-%d', c.birth_date)
GROUP BY c.customer_id ORDER BY c.customer_id""",
    },
    "C08": {
        "pair": ["north-mini", "dots"],
        "counter_panel": ["120b", "north-mini", "dots"],
        "delta": None,
    },
}

rows = [r for r in csv.DictReader(open(TRACES, encoding="utf-8")) if r["nature"] == "real"]
last = {}
for r in rows:  # chronological export: the last row is the last attempt
    last[(r["provider"], r["model_requested"], r["case_id"])] = r
references = {}
for r in csv.DictReader(open(HERE / "reference-td1.csv", encoding="utf-8")):
    references[r[next(iter(r))]] = r


def run(sql):
    result = sandbox.execute_query(DB, sql)
    if not result["ok"]:
        raise RuntimeError(f"{result['reason']}: {result['detail']}")
    return result


def proposals(case, names):
    out = []
    for name in names:
        provider, model = M[name]
        row = last.get((provider, model, case), {})
        value = row.get("value", "")
        ok = row.get("verdict") in {"correct", "incorrect"} and value != ""
        out.append(NS(provider=provider, model_requested=model,
                      value=int(value) if ok else None, verdict="executed" if ok else "error"))
    return out


def show(decision, reference):
    if not decision["consensus"]:
        return f"abstain (top {decision['votes']})"
    mark = "matches reference" if decision["value"] == reference else "WRONG CONSENSUS"
    return f"{decision['value']} ({decision['votes']} votes) -> {mark}"


lines = []
say = lines.append
say(f"TD 2 Step 2, wrong consensus. Traces: {TRACES.name} (nature = real). DB: {DB.relative_to(HERE)} "
    f"sha256 {sandbox.sha256_file(DB)[:16]}...")
failures = 0
for case, spec in CASES.items():
    ref_row = references[case]
    ref_sql = next(v for k, v in ref_row.items() if "sql" in k.lower() or "query" in k.lower())
    reference = int(run(ref_sql)["value"])
    stored_ref = int(last[(*M["120b"], case)]["reference"])
    say(f"\n== {case} == reference (re-executed) {reference}, reference in traces {stored_ref}")
    failures += reference != stored_ref
    for name in M:
        row = last[(*M[name], case)]
        executed = run(row["sql"])["value"] if row["sql"] and row["verdict"] in {"correct", "incorrect"} else None
        same = "" if executed is None or str(executed) == row["value"] else "  << differs from stored value"
        failures += bool(same)
        say(f"  {name:10s} stored {row['value'] or '-':>8s} verdict {row['verdict']:12s} re-executed {executed}{same}")
    shared = {int(last[(*M[n], case)]["value"]) for n in spec["pair"]}
    wrong = shared.pop()
    say(f"  agreeing pair {' + '.join(spec['pair'])}: shared wrong value {wrong}, gap {reference - wrong}")
    for label, (names, k) in PANELS.items():
        say(f"  {label:40s} k={k}/n={len(names)}: {show(vote(proposals(case, names), k), reference)}")
    names = spec["counter_panel"]
    say(f"  2-of-3 ({', '.join(names)}){'':6s} k=2/n=3: {show(vote(proposals(case, names), 2), reference)}"
        "   <- panel containing the pair")
    if spec["delta"]:
        delta_rows = run(spec["delta"])["rows"]
        total = sum(r[2] for r in delta_rows)
        for r in delta_rows:
            say(f"  delta row {r[0]} born {r[1]}: {r[2]}")
        ok = total == reference - wrong
        failures += not ok
        say(f"  delta total {total} == reference - wrong value ({reference - wrong}): {ok}")

say(f"\nChecks failed: {failures}")
text = "\n".join(lines)
print(text)
(HERE / "evidence" / "wrong-consensus-td2.txt").write_text(text + "\n", encoding="utf-8")
sys.exit(1 if failures else 0)
