# TD 1 report — Comparing models

**Sub-group:** DIA6-5 · **Module:** Trustworthy Generative AI (ESILV, A4) · **Session:** 21 October 2026
· **Members:** Alexandre, Tom, Nathanael, Loïs, Clement, Paul (see the contributions section)

Files to provide:
[`reference-td1.csv`](../reference-td1.csv) · [`traces-TD1.csv`](../traces-TD1.csv) · [`model-question-comparison-en.csv`](../model-question-comparison-en.csv) · [`five-model-summary-en.csv`](../five-model-summary-en.csv)

---

## 1. What was attempted and completed

| Step | Planned | Status | Evidence |
|---|---|---|---|
| 1. Reference | 20 SQL queries on `boutique.sqlite`, values checked | Done | `reference-td1.csv`: all 20 values equal the published answer key |
| 2. Five models | 100 first-attempt cells (5 models × 20 questions) | Done | `traces-TD1.csv`: 107 lines (100 first attempts + 7 retries), all `nature = real` |
| 3. Read traces | Final verdict and cause per cell | Done | `model-question-comparison-en.csv`: 100 rows |
| 3. Summaries | Five-model portfolio summary | Done | `five-model-summary-en.csv`: 5 rows |
| 4. Plenary | Comparison with other sub-groups | Not documented here | – |

**Models evaluated** (identical prompt for all, temperature 0, one request at a time):

| Role | Model | Route |
|---|---|---|
| A | `openai/gpt-oss-120b` | Groq Free |
| B | `openai/gpt-oss-20b` | Groq Free |
| C | `cohere/north-mini-code:free` | OpenRouter Free |
| D | `qwen/qwen3.8-27b` | Groq Free |
| E | `dots-studio/dots-3-note-preview:free` | OpenRouter Free |

No proposed model had to be replaced. Calls ran on 2026-10-21 between 12:42 and 13:13 UTC (67 Groq lines, 40 OpenRouter lines).

## 2. Reference

The twenty queries share one pattern: `SUM(quantity_product * price)` over `orders JOIN product`, wrapped in `COALESCE(..., 0)`, with `JOIN customers` when an age is involved. Conventions applied:

- period closed on the left, open on the right (`date >= start AND date < end`);
- age is the completed age on the given date (year difference minus one if the birthday has not yet occurred), written as a birth-date range for the "reference date" questions and as an age computed at the order date for C10 and C18;
- revenue in cents excluding VAT, `0` when nothing matches (C06, C14).

All twenty values match the published reference values, so no discrepancy needed to be traced to a query error.

## 3. Results

### 3.1 Overall

| Model | Correct | Wrong value | Invalid / rejected SQL | Not executed | Calls (incl. retries) |
|---|---|---|---|---|---|
| gpt-oss-120b | **18/20** | 2 | 0 | 0 | 20 |
| gpt-oss-20b | 16/20 | 3 | 0 | 1 | 23 |
| dots-3-note-preview:free | 12/20 | 8 | 0 | 0 | 20 |
| qwen3.8-27b | 11/20 | 6 | 3 | 0 | 24 |
| north-mini-code:free | 10/20 | 10 | 0 | 0 | 20 |

Overall: 67 correct out of 100 final cells.

### 3.2 By family

| Family | Questions | 120b | 20b | dots | qwen | north-mini |
|---|---|---|---|---|---|---|
| Period only | C01, C04–C07, C20 (6) | 6 | 5* | 6 | 4 | 6 |
| Age only | C02, C08–C11 (5) | 5 | 3 | 1 | 3 | 0 |
| Product only | C12 (1) | 1 | 1 | 1 | 1 | 1 |
| Combined | C03, C13–C19 (8) | 6 | 7 | 4 | 3 | 3 |
| **Any age condition** | C02, C08–C11, C15–C19 (10) | 8 | 7 | 2 | 3 | 0 |
| **No age condition** | the other 10 | 10 | 9* | 10 | 8 | 10 |

\* gpt-oss-20b: C20 is `not_executed` (access failure), not a wrong answer.

Questions missed by most models: C15, C16 and C17 (1 model correct out of 5), then C08, C09, C11 and C18 (2 out of 5).

### 3.3 Observed causes of failure

- **Broken age convention** (the dominant cause across the 33 non-correct cells). Typical forms: matching a single birthday instead of the range `birth_date > date − 26 years AND <= date − 25 years`; fixing `birth_year = 2001` and so dropping late-2000 births (dots on C09, C11, C16, C17; 120b on C16); contradictory month-day conditions that return 0 (qwen on C08, C10, C17, C18); wrong sub-range (20b on C09, C17).
- **Added period filter** that the question does not contain: north-mini and dots both appended `2026-03-01 .. 2026-06-01` to age-only questions (north-mini on C02, C08–C11, C16; dots on C02, C08, C09, C11).

### 3.4 Access failures and retries

Observed in the trace:

| Cell(s) | Limit hit (Groq) | Outcome |
|---|---|---|
| 20b, C18, C19 | TPM limit 8000 (tokens per minute) | retry succeeded, both correct |
| 20b, C20 | TPM limit 8000 | retry also 429 → `not_executed` |
| qwen, C17–C20 | OTPM limit 1000 (output tokens per minute) | retries returned answers: C20 correct, C17 and C18 incorrect, C19 `sql_rejected` |

gpt-oss-120b, north-mini and dots recorded no 429. A `not_executed` cell is an access failure, so it is not counted as a wrong answer. C20 for 20b remains without a measurement.

### 3.5 Prompt control

Each question has a single prompt fingerprint across all five models: 20 distinct fingerprints for 20 questions, so gaps between models are not attributable to different wording.

## 4. Portfolio reading (Step 3, summary CSV)

- Only gpt-oss-120b has a documented paid route for the exact model (input 0.15 / output 0.60 USD per million tokens on the aggregator, read 2026-09-29). All five were used on free routes at $0 (`cost_native` is 0 on every line).
- Public index (portfolio of 2026-09-28): qwen3.8-27b 33.7, gpt-oss-120b 11.6, gpt-oss-20b 9.0. north-mini and dots are absent from that snapshot, so their price and index fields are `N/A`.
- **The public index does not predict the result of this batch:** qwen has the highest index (33.7) and finished at 11/20, while gpt-oss-120b (11.6) finished first.

## 5. Interpretation

**Facts:** the 120b model is the only one correct on all five age-only questions; four of the five models get 10/10 on questions without an age condition when they are reachable (qwen is the exception at 8/10 because of syntax slips); the two OpenRouter free models score 0/10 and 2/10 on questions with an age condition.

**Hypotheses:**
1. The completed-age rule is hard to produce in one shot because it requires reasoning about a date range or a month-day comparison; the failures cluster there across all families.
2. The added `2026-03-01 .. 2026-06-01` filter in north-mini and dots may come from an example date in the prompt being copied. We have not compared this with the prompt text, so it is only a lead.
3. A routing rule "cheap model for period/product questions, stronger model for age questions" looks plausible from this batch. It rests on one run at temperature 0, one question set and a single sample per cell, so it is a routing hypothesis and not a model ranking.

## 6. Limits

- One run per cell: no measure of variability between runs.
- 20 questions, 6 of which are period-only and 1 product-only: the family percentages rest on very small counts (the product family has a single question).
- The rate limits (Groq TPM and OTPM) affected only the 20b and qwen models; their results include retry effects, and the C20 value for 20b is missing.
- Prices and public indices come from the portfolio snapshot of 2026-09-28/29 and not from a live read on the day of the session.
- Files named in the hand-in page that are **not yet in the repository** at the time of writing: `traces-td1.jsonl`, `prompts-en.md` (system message and user template as used), a configuration file read by the code, and the orchestrator code itself. The README also names the traces file in lowercase (`traces-td1.csv`) while the file is `traces-TD1.csv`. These must be added or corrected before the hand-in.
- The `reference-td1.csv` file contains the query and value of each case but not which member wrote or cross-checked which query.

## 7. Contributions

Roles as recorded in the README (each member also took part in the reference queries):

| Member | Role |
|---|---|
| Alexandre | A — gpt-oss-120b (Groq) |
| Tom | B — gpt-oss-20b (Groq) |
| Nathanael | C — north-mini-code (OpenRouter) |
| Loïs | D — qwen3.8-27b (Groq) |
| Clement | E — dots-3-note-preview (OpenRouter) |
| Paul | F — cross-checking references, trace consolidation, summaries |


## 8. Next steps for TD 2

1. Add the missing files listed in section 6 and fix the file-name case in the README.
2. Prepare `atelier-vote.py` and the routing rule for the k-of-n vote.
3. Test the routing hypothesis on the age questions, using more precise tests than this single run.
4. Investigate the copied-date lead (hypothesis 2) by diffing the prompt against the north-mini and dots SQL.
5. Plan the TD 2 allowance in advance: the 20b and qwen models hit Groq's per-minute limits in TD 1, which the vote (several calls per question) will aggravate.
