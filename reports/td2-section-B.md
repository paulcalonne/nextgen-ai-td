# TD 2 — Step 2 (Pair B: Paul, Nathanael): the wrong consensus

*Section of `reports/td2.md` written by Pair B. It is merged into the shared report at the assembly (16:45–17:15).*

Files of this step: `analyse-consensus-td2.py`, `evidence/wrong-consensus-td2.txt` (its output), `evidence/delta-c18.sql`.

```bash
python3 analyse-consensus-td2.py   # no network, no model call; exits 1 if a check fails
```

The script re-executes, read-only through `sandbox_sqlite.execute_query` on `data/boutique.sqlite`, the faulty SQL stored in `traces-TD1.csv`, the reference SQL of `reference-td1.csv` and the delta queries, then passes the stored values to our `vote_k_sur_n`. Every stored value was reproduced (0 failed checks).

**Nature of the cases:** real batch (TD 1 traces, `nature = real`, one run per cell, temperature 0). These are not replayed or synthetic examples. We did not need the supplied DEMO-VOTE case, because our batch contains wrong consensus cases.

## Main case: C18

| Field | Value |
|---|---|
| Identifier | C18, cells `openrouter:cohere/north-mini-code:free:C18` and `openrouter:dots-studio/dots-3-note-preview:free:C18` |
| Question | revenue excluding VAT (cents) of the orders of May 2026 placed by customers exactly 25 at the time of the order |
| Agreeing models | north-mini-code and dots-3-note-preview (two different providers' families) |
| Shared wrong value | 39580 |
| Reference | 62480 (reference SQL re-executed on the database, not a model answer) |
| Gap | 22900 |

**Cause in the SQL.** Both queries require `order_year − birth_year = 25` **and** the birthday already reached in the order year. A customer whose year gap is 26 but whose birthday has not yet come in the order year has a completed age of 25, so both queries drop them. The reference computes the completed age as `year gap − (strftime('%m-%d', order) < strftime('%m-%d', birth))` and compares it with 25. The two models wrote the query differently (north-mini with `SUBSTR`, dots with `strftime`), but they make the same mistake.

**Proof by the delta query** (`evidence/delta-c18.sql`): customers with a year gap of 26 whose birthday has not been reached at the order date.

| customer_id | birth_date | revenue (cents) |
|---|---|---|
| C004 | 2000-09-25 | 11940 |
| C022 | 2000-08-14 | 10960 |

Total 22900 = 62480 − 39580, exact to the cent.

**Declared quorums and what they return**

| Panel | k of n | Decision on C18 |
|---|---|---|
| Fixed course panel: 120b, north-mini, qwen | 2 of 3 | abstain (top 1: 120b 62480, north-mini 39580, qwen 0) |
| The five TD 1 models | 3 of 5 | abstain (top 2: 62480 by 120b + 20b, 39580 by north-mini + dots, qwen 0) |
| Other panel: 120b, north-mini, dots | 2 of 3 | **39580, 2 votes: wrong consensus** |

The two-model agreement does not by itself say what the fixed 2-of-3 panel returns: dots is not a member of that panel, so the fixed panel abstains. But a 2-of-3 panel that happens to contain north-mini and dots returns the wrong value with a valid strict majority. The quorum protected us here because of which models were in the panel, not because voting detects shared errors.

## Same mechanism: C16

| Agreeing models | Shared wrong value | Reference | Gap | Fixed 2-of-3 | 3-of-5 | 2-of-3 (120b, dots, north-mini) |
|---|---|---|---|---|---|---|
| gpt-oss-120b + dots | 211260 | 376740 | 165480 | abstain | abstain | **211260 wrong** |

Age on the date 2026-09-25, products a, b, c. The faulty queries force a year gap of exactly 25. The delta (second query of `evidence/delta-c18.sql`) gives C005 (born 2000-09-26, 92210) + C007 (born 2000-11-30, 73270) = 165480. Even the strongest model of TD 1 (120b) is in the wrong pair.

## A third case with a different cause: C08

north-mini and dots both return 18440 (reference 605580), and a 2-of-3 panel with 120b, north-mini and dots would return 18440. The cause is not the same as in C18. The question asks for "all their orders", but both queries add an order period that the question does not mention (`2026-03-01` to `2026-06-01`), and they keep only the customers born exactly on 2001-09-24 (25th birthday on the reference date) instead of the whole age band. So two models can also agree because they read the question in the same wrong way, not only because they use the same date formula.

## Consequence for the panel and the checking

1. **A strict majority does not detect a shared error.** It filters random disagreement. When two members make the same mistake (C18, C16) or read the question the same wrong way (C08), the majority certifies the wrong value.
2. **Panel choice:** do not put north-mini and dots together in a 2-of-3 panel for age questions (F2, F2b, combinations). They agree on the wrong value on C08 and C18. A different panel is a candidate check, not a guarantee: C16 shows that 120b can also be part of a wrong pair.
3. **Independent check that detects the error:** a reference query written by a human for age questions, using the completed-age formula, plus a delta query against the model value. If the delta is not empty, the model value is rejected and the gap is explained row by row. A sanity check by count also works cheaply: the number of distinct customers counted by the model query against the reference query (2 customers missing on C18, 2 on C16).
4. **For the routing rule (Pair C):** age families and combinations need the reference SQL for figures shown to customers and for payouts; a quorum alone is not enough there.

## Limits

- One run per cell; we do not know if the shared errors would repeat on another run.
- We did not test whether a change of prompt wording (for example, defining "exactly 25" as completed age) removes the error.
- The "other panel" lines are a what-if on the stored values, not a new experiment.
