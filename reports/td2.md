# TD 2 report — The quorum, then the routing rule

**Sub-group:** DIA6-G5 · **Module:** Trustworthy Generative AI (ESILV, A4) · **Session:** 18 November 2026
· **Members:** Alexandre, Tom, Nathanael, Loïs, Clement, Paul ·
Files: [`skeleton-multi-llm-en.py`](../skeleton-multi-llm-en.py) · [`test-vote.py`](../test-vote.py) · [`analyse-td2.py`](../analyse-td2.py) · [`analyse-consensus-td2.py`](../analyse-consensus-td2.py) · [`atelier-routage.py`](../atelier-routage.py) · [`evidence/`](../evidence)

---

## 1. What was attempted and completed

| Step | Planned | Status | Evidence |
|---|---|---|---|
| 1. k-of-n vote (Pair A) | `vote_k_sur_n` and the 20-question table, 2-of-3 vs 3-of-5 | Done | `test-vote.py` (14 tests), `evidence/comparison-2of3-vs-3of5.csv` |
| 2. Wrong consensus (Pair B) | One wrong shared value, SQL cause, delta query | Done (C18, C16 proven, C08 explained) | `analyse-consensus-td2.py`, `evidence/wrong-consensus-td2.txt`, `evidence/delta-c18.sql`, `reports/td2-section-B.md` |
| 3. Routing rule (Pair C) | One rule per family, simulator adapted | Done | `atelier-routage.py`, `evidence/simulateur-avant.jsonl`, `evidence/simulateur-apres.jsonl` |
| 4. Plenary | Compare with other sub-groups | To fill in after 17:15 | – |

Everything uses the stored TD 1 traces (`traces-TD1.csv`, 107 lines, real). No new model call was made and the prompts are unchanged. Simulator outputs are simulations.

## 2. Step 1 — The k-of-n vote

`vote_k_sur_n` follows the docstring: only executed proposals with a value vote; an error stays in n without a vote; k must satisfy `n // 2 < k <= n`; a duplicate `(provider, model)` raises `ValueError`; a value with at least k votes wins, otherwise the method abstains (`value: None`).
`python3 test-vote.py` passes 14 tests (invalid k, duplicate, abstention, error kept in n, value 0 counted as a vote, wrong consensus returned as is). The tests are also listed on the course form in `evidence/voting-tests.csv` (agreement, disagreement, unavailable members, duplicate route, invalid k, wrong consensus, and six real cases from the TD 1 traces).

Panels: 2-of-3 = gpt-oss-120b, north-mini-code, qwen3.8-27b (k = 2); 3-of-5 = the five TD 1 models (k = 3).

| Case | Reference | 2-of-3 (120b, north-mini, qwen) | 3-of-5 (all five) |
|---|---|---|---|
| C01 | 792800 | 792800 (2 votes) ✔ | 792800 (4 votes) ✔ |
| C02 | 590320 | 590320 (2 votes) ✔ | 590320 (3 votes) ✔ |
| C03 | 936350 | 936350 (3 votes) ✔ | 936350 (5 votes) ✔ |
| C04 | 2826250 | 2826250 (3 votes) ✔ | 2826250 (5 votes) ✔ |
| C05 | 38480 | 38480 (3 votes) ✔ | 38480 (5 votes) ✔ |
| C06 | 0 | 0 (2 votes) ✔ | 0 (4 votes) ✔ |
| C07 | 13970 | 13970 (3 votes) ✔ | 13970 (5 votes) ✔ |
| C08 | 605580 | abstain (top 1) | abstain (top 2) |
| C09 | 487980 | 487980 (2 votes) ✔ | abstain (top 2) |
| C10 | 558980 | abstain (top 1) | 558980 (3 votes) ✔ |
| C11 | 446690 | 446690 (2 votes) ✔ | abstain (top 2) |
| C12 | 1666490 | 1666490 (3 votes) ✔ | 1666490 (5 votes) ✔ |
| C13 | 107740 | 107740 (3 votes) ✔ | 107740 (5 votes) ✔ |
| C14 | 0 | 0 (3 votes) ✔ | 0 (5 votes) ✔ |
| C15 | 168680 | abstain (top 1) | abstain (top 1) |
| C16 | 376740 | abstain (top 1) | abstain (top 2) |
| C17 | 258180 | abstain (top 1) | abstain (top 1) |
| C18 | 62480 | abstain (top 1) | abstain (top 2) |
| C19 | 1990 | abstain (top 1) | 1990 (3 votes) ✔ |
| C20 | 1106090 | 1106090 (3 votes) ✔ | 1106090 (4 votes) ✔ |

(✔ = equals the reference, ✘ would be a wrong consensus. The per-model values are in `evidence/comparison-2of3-vs-3of5.csv`.)

**Totals:** both schemes give 13 correct consensus and 7 abstentions. **No quorum returned a wrong value.** 16 questions get the same decision in both; 4 change.

**The 4 questions that change**

- **C09 and C11:** 2-of-3 finds the right value (120b + qwen), 3-of-5 abstains. Only two models are right; the three others give three different wrong values, so a threshold of 3 cannot be reached.
- **C10:** 2-of-3 abstains (120b right, north-mini 39580, qwen 0), 3-of-5 finds 558980 with 120b + 20b + dots.
- **C19:** 2-of-3 abstains. qwen's SQL was rejected (`sql_rejected`), so it stays in n without voting, and north-mini gives 13930. 3-of-5 finds 1990 with 120b + 20b + dots.

**Questions that do not change:** C01, C06 (qwen `sql_rejected` / `sql_invalid`) and C20 (20b `not_executed`) keep their consensus because the other members still agree. C15 and C17 abstain in both: every model gives a different value. C08, C16 and C18 abstain in both because of a shared wrong value (next section).

## 3. Step 2 — The wrong consensus

| Question | Models that agree | Shared wrong value | Reference | 2-of-3 | 3-of-5 |
|---|---|---|---|---|---|
| C18 | north-mini + dots | 39580 | 62480 | abstain | abstain |
| C16 | 120b + dots | 211260 | 376740 | abstain | abstain |
| C08 | north-mini + dots | 18440 | 605580 | abstain | abstain |

Nature: real batch (TD 1 traces). The wrong value never wins with our two declared panels, but a valid 2-of-3 panel containing the agreeing pair (for example 120b, north-mini, dots) returns it in all three cases: 39580 on C18, 211260 on C16, 18440 on C08 (`python3 analyse-consensus-td2.py`, output in `evidence/wrong-consensus-td2.txt`). C08 has a different cause: both queries add an order period the question does not ask for and keep only customers born on 2001-09-24. Full commentary: `reports/td2-section-B.md`.

**Independent check:** a human-written reference query with the completed-age formula, plus a delta query against the model value; a non-empty delta rejects the value. Another panel is a candidate check, not a guarantee (120b is in the wrong pair on C16).

**C18** (orders of May 2026, customers exactly 25 at the time of the order). The faulty queries (north-mini and dots, both 39580) require `order_year − birth_year = 25` and the birthday already reached. A customer born in 2000 whose birthday has not yet occurred in the order year has a gap of 26 but a completed age of 25, so they are dropped. The reference subtracts 1 when `strftime('%m-%d', order) < strftime('%m-%d', birth)`.

Delta query (`evidence/delta-c18.sql`, run on `data/boutique.sqlite`): it lists the customers with a year gap of 26 and a birthday not yet reached.

| customer_id | birth_date | revenue (cents) |
|---|---|---|
| C004 | 2000-09-25 | 11940 |
| C022 | 2000-08-14 | 10960 |

Total 22900 = 62480 − 39580, exact to the cent. A separate Python check (completed age by tuple comparison) gives 62480.

**Complete queries of C18** (cells `openrouter:cohere/north-mini-code:free:C18` and `openrouter:dots-studio/dots-3-note-preview:free:C18` in `traces-TD1.csv`).

north-mini-code (39580):
```sql
SELECT COALESCE(SUM(o.quantity_product * p.price), 0) AS revenue_cents
FROM orders o
JOIN product p ON p.product_id = o.product_id
JOIN customers c ON c.customer_id = o.customer_id
WHERE o.date >= '2026-05-01 00:00:00'
  AND o.date <  '2026-06-01 00:00:00'
  AND (
    -- Compute age on order date: exactly 25 means the 25th birthday has occurred on or before the order date,
    -- and the 26th birthday is after the order date.
    -- Extract year, month, day from order date and birth date.
    -- Age = (order_year - birth_year) - ((order_month, order_day) < (birth_month, birth_day))
    -- Exactly 25: age = 25 AND (order_year - birth_year) = 25
    -- Equivalent condition: order_year - birth_year = 25 AND (order_month > birth_month OR (order_month = birth_month AND order_day >= birth_day))
    -- Also ensure the 26th birthday hasn't occurred: (order_month > birth_month OR (order_month = birth_month AND order_day >= birth_day)) is already covered.
    -- Actually we need: (order_year - birth_year) = 25 AND (order_month > birth_month OR (order_month = birth_month AND order_day >= birth_day))
    -- But we also need to ensure the 26th hasn't occurred: that is automatically satisfied if the above holds.
    -- So we compute:
    CAST(SUBSTR(o.date, 1, 4) AS INTEGER) - CAST(SUBSTR(c.birth_date, 1, 4) AS INTEGER) = 25
    AND (
        CAST(SUBSTR(o.date, 6, 2) AS INTEGER) > CAST(SUBSTR(c.birth_date, 6, 2) AS INTEGER)
        OR (
            CAST(SUBSTR(o.date, 6, 2) AS INTEGER) = CAST(SUBSTR(c.birth_date, 6, 2) AS INTEGER)
            AND CAST(SUBSTR(o.date, 9, 2) AS INTEGER) >= CAST(SUBSTR(c.birth_date, 9, 2) AS INTEGER)
        )
    )
  );
```

dots-3-note-preview (39580):
```sql
SELECT COALESCE(SUM(o.quantity_product * p.price), 0) AS revenue_cents
FROM orders o
JOIN product p ON p.product_id = o.product_id
JOIN customers c ON c.customer_id = o.customer_id
WHERE o.date >= '2026-05-01 00:00:00'
  AND o.date <  '2026-06-01 00:00:00'
  AND CAST(strftime('%Y', o.date) AS INTEGER) - CAST(strftime('%Y', c.birth_date) AS INTEGER) = 25
  AND (CAST(strftime('%m', o.date) AS INTEGER) > CAST(strftime('%m', c.birth_date) AS INTEGER)
       OR (CAST(strftime('%m', o.date) AS INTEGER) = CAST(strftime('%m', c.birth_date) AS INTEGER)
           AND CAST(strftime('%d', o.date) AS INTEGER) >= CAST(strftime('%d', c.birth_date) AS INTEGER)));
```

Reference query (62480):
```sql
SELECT COALESCE(SUM(o.quantity_product * p.price), 0) AS revenue_cents FROM orders o JOIN product p ON o.product_id = p.product_id JOIN customers c ON o.customer_id = c.customer_id WHERE o.date >= '2026-05-01 00:00:00' AND o.date < '2026-06-01 00:00:00' AND (CAST(strftime('%Y', o.date) AS INTEGER) - CAST(strftime('%Y', c.birth_date) AS INTEGER) - (strftime('%m-%d', o.date) < strftime('%m-%d', c.birth_date))) = 25
```

Delta query (`evidence/delta-c18.sql`):
```sql
SELECT c.customer_id, c.birth_date,
       SUM(o.quantity_product * p.price) AS delta_cents   -- revenue excluding VAT, in euro cents
FROM orders o
JOIN product p   ON p.product_id   = o.product_id
JOIN customers c ON c.customer_id = o.customer_id
WHERE o.date >= '2026-05-01 00:00:00' AND o.date < '2026-06-01 00:00:00'
  AND CAST(strftime('%Y', o.date) AS INTEGER) - CAST(strftime('%Y', c.birth_date) AS INTEGER) = 26
  AND strftime('%m-%d', o.date) < strftime('%m-%d', c.birth_date)   -- birthday not yet reached => completed age is 25
GROUP BY c.customer_id;
```

**C16** has the same cause (120b and dots force a year gap of 25). The delta is C005 (born 2000-09-26, 92210) + C007 (born 2000-11-30, 73270) = 165480 = 376740 − 211260.

## 4. Step 3 — The routing rule

**TD 1 rates by family** (final verdicts, cells C01 to C20):

| Family | Cells | 120b | 20b | north-mini | qwen | dots |
|---|---|---|---|---|---|---|
| F1 period | C01, C04–C07, C20 | 6/6 | 5/6 | 6/6 | 4/6 | 6/6 |
| F2 age on a date | C02, C08, C09, C11 | 4/4 | 2/4 | 0/4 | 3/4 | 0/4 |
| F2b age at the order | C10 | 1/1 | 1/1 | 0/1 | 0/1 | 1/1 |
| F3 product list | C03, C12–C14 | 4/4 | 4/4 | 4/4 | 4/4 | 4/4 |
| Combined | C15–C19 | 3/5 | 4/5 | 0/5 | 0/5 | 1/5 |

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
- **Combinations C15–C19.** 120b is 3/5 (C15 68670 and C16 211260 wrong), 20b 4/5 (C17 194000 wrong), dots 1/5, north-mini and qwen 0/5. The 3-of-5 quorum answers only C19 and the 2-of-3 panel none, so no free model nor quorum is enough: reference SQL and human review.

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
| Combined, payout, urgent, budget 0 | abstain | – |

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

### Routing rule on the course worksheet (`evidence/routing-rule-td2.md`)

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

## 5. Interpretation

**Facts:** no quorum returned a wrong value; the abstentions are all on age questions; the shared wrong values of C16 and C18 come from the same completed-age mistake in models from different families; on C08 the shared value comes from the same misreading of the question (an invented order period and a single birth date).

**Hypotheses:**
1. A strict majority protects against random errors but not against a shared convention error, so age questions need a reference query written by a human.
2. Using the strongest model is not enough: 120b is in the wrong pair on C16.
3. The rule is based on one run per cell and families of 1 to 6 questions: it is a routing hypothesis, not a ranking.

## 6. Limits

- One run per cell at temperature 0; 20 questions; F2b rests on a single question (C10).
- We did not test whether the prompt wording causes the shared age errors.
- The simulator uses fictional availability and a fictional cost for the paid route.
- Files of the TD 1 hand-in still missing from the repository: `traces-td1.jsonl`, `prompts-en.md`, a configuration file. The README says `traces-td1.csv` but the file is `traces-TD1.csv`.
- An AI assistant (Claude) helped prepare the analysis scripts, the delta queries and the tables of this report. The group re-ran them and checked the values against `reference-td1.csv` and the database; the references come from SQL, not from a model answer.

## 7. Contributions

| Member | Pair | Contribution |
|---|---|---|
| Alexandre | A | `vote_k_sur_n`, tests of the vote, 20-question table (2-of-3 vs 3-of-5) |
| Tom | A | `vote_k_sur_n`, tests of the vote, 20-question table (2-of-3 vs 3-of-5) |
| Paul | B | wrong consensus (C18, C16, C08): faulty queries, SQL cause, delta query, `analyse-consensus-td2.py`, section B |
| Nathanael | B | wrong consensus (C18, C16): faulty queries, SQL cause, delta query |
| Clement | C | routing rule per family, simulator adapted, priority analysis |
| Loïs | C | routing rule per family, simulator adapted, priority analysis |

Roles are those decided at the start of the session; all members read the three steps in the internal cross-review.

## 8. Next steps for TD 3

1. Put a cost on the checks (reference SQL and human review) for C08 and C15–C18.
2. Test the routing rule with more samples per family.
3. Compare our rule with the other sub-groups after the plenary.
