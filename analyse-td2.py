#!/usr/bin/env python3
"""TD 2, Pair A: 2-of-3 vs 3-of-5 on the stored TD 1 traces. No network, no model call.
    python3 analyse-td2.py            -> prints the markdown table and writes evidence/comparison-2of3-vs-3of5.csv
The vote never receives the reference; the comparison is done after the decision."""
import csv, importlib.util, sys
from collections import Counter
from pathlib import Path
from types import SimpleNamespace as NS
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("sk", HERE / "skeleton-multi-llm-en.py")
mod = importlib.util.module_from_spec(spec); sys.modules["sk"] = mod; spec.loader.exec_module(mod)
vote = lambda p, k: mod.Orchestrateur.vote_k_sur_n(None, p, k)
TRACES = next(p for p in (HERE / "traces-TD1.csv", HERE / "traces-td1.csv") if p.exists())  # repo uses the uppercase name
rows = list(csv.DictReader(open(TRACES, encoding="utf-8")))
ref = {r["case_id"]: int(r["reference"]) for r in rows}
last = {}
for r in rows:                      # chronological export: the last row is the last attempt
    last[(r["provider"], r["model_requested"], r["case_id"])] = r
ALL = [("groq","openai/gpt-oss-120b"),("groq","openai/gpt-oss-20b"),("openrouter","cohere/north-mini-code:free"),
       ("groq","qwen/qwen3.8-27b"),("openrouter","dots-studio/dots-3-note-preview:free")]
PANEL = [ALL[0], ALL[2], ALL[3]]
SHORT = {"openai/gpt-oss-120b":"120b","openai/gpt-oss-20b":"20b","cohere/north-mini-code:free":"north","qwen/qwen3.8-27b":"qwen","dots-studio/dots-3-note-preview:free":"dots"}
def props(c, ms):
    out = []
    for p, m in ms:
        r = last[(p, m, c)]
        ok = r["verdict"] in ("correct", "incorrect") and r["value"] != ""
        out.append(NS(provider=p, model_requested=m, value=int(r["value"]) if ok else None, verdict="executed" if ok else "error"))
    return out
def cell(c, pm):
    r = last[(pm[0], pm[1], c)]
    return r["value"] if r["value"] != "" else r["verdict"]
def show(d, rf):
    if not d["consensus"]: return f"abstain (top {d['votes']})"
    return f"{d['value']} ({d['votes']} votes) " + ("✔" if d["value"] == rf else "✘")
out, md = [], []
for c in sorted(ref):
    a, b = vote(props(c, PANEL), 2), vote(props(c, ALL), 3)
    wrong = {v: n for v, n in Counter(int(last[(p,m,c)]["value"]) for p, m in ALL
             if last[(p,m,c)]["verdict"] == "incorrect" and last[(p,m,c)]["value"] != "").items() if n >= 2}
    same = (a["consensus"], a["value"]) == (b["consensus"], b["value"])
    out.append(dict(case_id=c, reference=ref[c], **{f"v_{SHORT[m]}": cell(c, (p, m)) for p, m in ALL},
                    panel_2of3=show(a, ref[c]), quorum_3of5=show(b, ref[c]), decision_changes="no" if same else "yes",
                    shared_wrong_value=";".join(f"{v}x{n}" for v, n in wrong.items())))
(HERE / "evidence").mkdir(exist_ok=True)
w = csv.DictWriter(open(HERE / "evidence/comparison-2of3-vs-3of5.csv", "w", newline="", encoding="utf-8"), fieldnames=list(out[0]))
w.writeheader(); w.writerows(out)
print("| Case | Ref | 120b | 20b | north | qwen | dots | 2-of-3 (120b,north,qwen) | 3-of-5 (all) | Changes |")
print("|---|---|---|---|---|---|---|---|---|---|")
for o in out:
    print("| {case_id} | {reference} | {v_120b} | {v_20b} | {v_north} | {v_qwen} | {v_dots} | {panel_2of3} | {quorum_3of5} | {decision_changes} |".format(**o))
