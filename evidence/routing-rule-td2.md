# Routing rule worksheet (TD 2, DIA6-G5)

- **Use case and consequence of an error:** revenue figures of the shop. Internal dashboard (low), figure shown to a customer (medium), amount paid out (high).
- **Question family and supporting observations:** F1, F2, F2b, F3 and combinations, with the TD 1 rates of `reports/td2.md`, section 4 (cells C01 to C20).
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
