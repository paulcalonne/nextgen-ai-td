# TD 2 — Step 1 (Pair A: Alexandre, Tom): the k-of-n vote

*Section of `reports/td2.md` written by Pair A. It is merged into the shared report at the assembly (16:45–17:15).*

Files of this step: `skeleton-multi-llm-en.py` (`vote_k_sur_n`), `test-vote.py`, `atelier-vote.py`, `analyse-td2.py`, `evidence/comparison-2of3-vs-3of5.csv`, `evidence/voting-tests.csv`, `evidence/test-vote-output.txt`.

## The k-of-n vote

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
