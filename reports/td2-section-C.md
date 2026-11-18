# TD 2, Step 3 (Pair C: Clement, Loïs): the routing rule

*Section of `reports/td2.md` written by Pair C. It is merged into the shared report at the assembly (16:45 to 17:15).*

Files of this step: `atelier-routage.py` (adapted `RESOURCES` and `choose`), `evidence/routing-rule-td2.md`, `evidence/simulateur-avant.jsonl`, `evidence/simulateur-apres.jsonl`.

**TD 1 rates by family** (final verdicts, cells C01 to C20):

| Family | Cells | 120b | 20b | north-mini | qwen | dots |
|---|---|---|---|---|---|---|
| F1 period | C01, C04-C07, C20 | 6/6 | 5/6 | 6/6 | 4/6 | 6/6 |
| F2 age on a date | C02, C08, C09, C11 | 4/4 | 2/4 | 0/4 | 3/4 | 0/4 |
| F2b age at the order | C10 | 1/1 | 1/1 | 0/1 | 0/1 | 1/1 |
| F3 product list | C03, C12-C14 | 4/4 | 4/4 | 4/4 | 4/4 | 4/4 |
| Combined | C15-C19 | 3/5 | 4/5 | 0/5 | 0/5 | 1/5 |

(20b F1: C20 is a Groq 429, not a wrong answer.) All models ran on free routes. Only gpt-oss-120b has a paid route for the same model (OpenRouter, 0.15 / 0.60 USD per million tokens, about 0.00025 USD per request).

**Rule**

| Family | First model | Internal dashboard | Customer figure | Payout | If first model unavailable |
|---|---|---|---|---|---|
| F1, F3 | north-mini (free) | one model + value check | 2-of-3 quorum | reference SQL + quorum | dots, then 20b, then wait, then 120b, then abstain |
| F2 | 120b | 120b alone + value check | 2-of-3, else reference SQL | reference SQL | wait for Groq refill, then 120b paid, then abstain |
| F2b | 120b | 3-of-5 quorum | 3-of-5 + reference SQL | reference SQL | same as F2 |
| Combined | 120b as proposer only | 3-of-5, else reference SQL | reference SQL + human review | reference SQL + human review | same as F2 |

A single free model without a check is used only for a dashboard and only where it scored 100% in TD 1. C15, C16 and C17 (one model right out of five) cannot be answered by any free model alone.

**Why each choice (TD 1 cells and cost of an error)**

- **F1, first model north-mini.** It is right on all six cells C01, C04, C05, C06, C07, C20 (6/6) and costs 0 USD; dots and 120b are also 6/6, 20b is 5/6 (C20 was a Groq 429), qwen 4/6 (C01 and C06 rejected). We keep the stronger models for harder families.
- **F3, first model north-mini.** All five models are 4/4 on C03, C12, C13, C14, so the cheapest free one is enough.
- **F2, first model 120b.** It is the only model right on C02, C08, C09 and C11 (4/4). qwen is 3/4 (C08 wrong, 0), 20b 2/4 (C09 208820, C11 0), north-mini and dots 0/4.
- **F2b (C10 only).** 120b, 20b and dots are right (558980), north-mini (39580) and qwen (0) are wrong. One question is too thin for one model alone, hence the 3-of-5 quorum (2-of-3 abstains on C10, 3-of-5 finds 558980).
- **Combinations C15-C19.** 120b is 3/5 (C15 68670 and C16 211260 wrong), 20b 4/5 (C17 194000 wrong), dots 1/5, north-mini and qwen 0/5. The 3-of-5 quorum answers only C19 and the 2-of-3 panel none, so no free model nor quorum is enough: reference SQL and human review.

| Use | Cost of a wrong figure | Check required |
|---|---|---|
| Internal dashboard | low: seen quickly by the team and corrected | one model with a value check, only where it was 100% in TD 1; otherwise a quorum |
| Figure shown to a customer | medium: wrong figure published outside the company | quorum (2-of-3 or 3-of-5), abstain if there is no consensus |
| Amount paid out | high: money paid, hard to reverse | reference SQL written by a human (the quorum can agree on a wrong value, see C16 and C18) |


**Simulator** (`python3 atelier-routage.py`). Before: teacher resources (small-free, senior-subscription, senior-api), 7 scenarios. After: north-mini, dots, 20b, 120b free, 120b paid, with a level taken from the TD 1 family rates and the TD 1 cells quoted in each `reason`. Examples of the new outputs:

| Scenario | Action | Resource |
|---|---|---|
| F1 dashboard | run | north-mini-free |
| F2 dashboard | run | gpt-oss-120b-groq-free |
| F2 customer figure, Groq 429, can wait | defer (1 min) | gpt-oss-120b-groq-free |
| F2 customer figure, Groq 429, urgent | run (0.00025 USD) | gpt-oss-120b-openrouter-paid |
| Combined, payout, urgent, budget 0 | abstain | none |

**The seven scenarios of the teacher simulator, before and after adaptation** (each original scenario is matched with its equivalent in our rule; full outputs in `evidence/simulateur-avant.jsonl` and `evidence/simulateur-apres.jsonl`):

| Original scenario | Before (teacher rule) | Adapted scenario | After (our rule) | Checks after |
|---|---|---|---|---|
| simple | run → small-free | F1 dashboard | run → north-mini-free | single model + read-only execution and value check (F1 6/6 for north-mini, dots and 120b) |
| complex | run → senior-subscription | F2 dashboard | run → gpt-oss-120b-groq-free | 120b alone + value check (only model 4/4 on F2); never north-mini/dots (0/4) |
| deferrable | defer → senior-subscription (60 min) | F2 customer, Groq 429 (can wait) | defer → gpt-oss-120b-groq-free (1 min) | 2-of-3 quorum; on abstention (C08 case) fall back to deterministic SQL |
| urgent | run → senior-api, 0.3 USD | F2 customer, Groq 429, urgent | run → gpt-oss-120b-openrouter-paid, 0.00025 USD | 2-of-3 quorum; on abstention (C08 case) fall back to deterministic SQL |
| budget exhausted | abstain | COMBO payout, urgent, budget 0 | abstain | deterministic reference SQL + human review (no free model answers alone) |
| high impact | run → senior-subscription | COMBO payout | run → gpt-oss-120b-groq-free | deterministic reference SQL + human review (no free model answers alone) |
| unknown capability | abstain | unknown family | abstain | unknown family: human review |

## Routing rule on the course worksheet (`evidence/routing-rule-td2.md`)

- **Use case and consequence of an error:** revenue figures of the shop. Internal dashboard (low), figure shown to a customer (medium), amount paid out (high).
- **Question family and supporting observations:** F1, F2, F2b, F3 and combinations, with the rates of the table above (cells C01 to C20).
- **Eligible models and access routes:** north-mini, dots and 20b for F1/F3 (free); gpt-oss-120b only for F2 and above (Groq free, or OpenRouter paid, about 0.00025 USD per request).
- **First route and reason:** north-mini for F1/F3 (6/6 and 4/4 in TD 1, free, no 429); gpt-oss-120b for F2 (4/4, the only model at 100%).
- **Additional check or escalation:** by use (see the rule table): value check, 2-of-3 or 3-of-5 quorum, reference SQL written by a human, human review.
- **Maximum acceptable delay and cost basis:** a free refill is awaited only if it comes back before the deadline; the paid route is used only within the budget of the request.
- **Stop, defer or human-review condition:** abstain when no eligible route fits the deadline and budget; defer when a free quota refills in time; human review for combined families and payouts.

| ID | Situation | Selected action | Reason tied to the rule | Evidence |
|---|---|---|---|---|
| R1 | Ordinary question, preferred route available | run north-mini-free (F1 dashboard) | F1 6/6 in TD 1, free | `simulateur-apres.jsonl`, F1 dashboard |
| R2 | Preferred provider unavailable | run 120b paid route, 0.00025 USD (F2 customer figure, Groq 429, urgent) | F2 only 120b is eligible; same model on another route | scenario "F2 customer, Groq 429, urgent" |
| R3 | Deferrable request, free quota exhausted | defer 1 min to 120b Groq (F2, can wait) | free refill before the deadline, availability re-checked at wake-up | scenario "F2 customer, Groq 429 (can wait)" |
| R4 | Urgent request, no adequate route within the budget | abstain (combined payout, budget 0) | nothing eligible is free and available; never invent a figure | scenario "COMBO payout, urgent, budget 0" |
| R5 | High consequence of error, model answers agree | run 120b as proposer, then reference SQL + human review | agreement is not proof: C16 and C18 show models agreeing on a wrong value | scenario "COMBO payout" and section 3 |

**Reading of the branches of `choose`** (same order as the teacher version; `request` carries the family, the use, `can_wait`, `deadline_minutes` and `budget`):

1. **Eligible resources:** level of the resource ≥ level of the family. For F2/F2b and combinations only 120b (Groq or paid route) is kept, because no other model was at 100% on age questions. An unknown family gets level 4, so nothing is eligible.
2. **`included`:** eligible, available and `cash == 0`. If there is one, the action is `run` on the one with the lowest `(allocation, level, rank)`. The reason is "eligible included capacity" followed by the TD 1 cells of that model.
3. **`waiting`:** only if `included` is empty. Eligible, not available, `cash == 0`, a reset time between 0 and `deadline_minutes`, and `can_wait` is true: the action is `defer` with `wake_in_minutes`. Availability must be measured again at wake-up.
4. **`paid`:** eligible, available and `cash <= budget`: `run` on the cheapest one.
5. **Otherwise** `abstain`, with the reason "no eligible resource within deadline and budget": no figure is invented.

Branch taken in our scenarios, with the reason string printed by the simulator:

| Scenario | Branch | Reason printed |
|---|---|---|
| F1 dashboard | 2 included | eligible included capacity; TD1 north-mini: F1 6/6 (C01,C04-C07,C20), F3 4/4 (C03,C12-C14), F2 0/4 (C02,C08,C09,C11) |
| F2 dashboard | 2 included | eligible included capacity; TD1 gpt-oss-120b: F1 6/6, F3 4/4, F2 4/4, F2b 1/1, combos 3/5 |
| F2 customer, Groq 429, can wait | 3 waiting | free refill before deadline: recheck availability at wake-up (Groq 429 in TD1 cleared after retry for 20b C18/C19); TD1 gpt-oss-120b: F1 6/6, F3 4/4, F2 4/4, F2b 1/1, combos 3/5 (C15,C16 wrong) |
| F2 customer, Groq 429, urgent | 4 paid (`can_wait` is false, so no deferral) | available route within the authorised budget; TD1 gpt-oss-120b (same model, paid route) |
| Combined, payout | 2 included | eligible included capacity; the check is reference SQL + human review |
| Combined, payout, urgent, budget 0 | 5 abstain | no eligible resource within deadline and budget |
| unknown family | 5 abstain | nothing eligible (level 4) |

**Priority in `choose`.** An available no-cash resource (`included`) is tested before waiting for an exhausted free one (`waiting`). It costs nothing, answers now, and the code warns that a reset time does not prove capacity is back (in TD 1, the 20b retries worked for C18 and C19 but C20 got a second 429). The priority should be reversed when the available resource has a scarce allocation that must be kept for harder or higher-stakes requests, the request is easy, it can wait, and the free refill is short compared with the deadline (Groq per-minute limits reset within about a minute).
