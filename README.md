# DIA6 - DIA6-G5

**Module:** Trustworthy Generative AI · TD 1  

## Sub-group Members & Role Assignment

Tasks were shared equitably among all six members across every stage of the lab session:
* **Alexandre** : Role A — Model Evaluation (`groq:openai/gpt-oss-120b`) & Reference Queries
* **Tom** : Role B — Model Evaluation (`groq:openai/gpt-oss-20b`) & Reference Queries
* **Nathanael** : Role C — Model Evaluation (`openrouter:cohere/north-mini-code:free`) & Reference Queries
* **Loïs** : Role D — Model Evaluation (`groq:qwen/qwen3.8-27b`) & Reference Queries
* **Clement** : Role E — Model Evaluation (`openrouter:dots-studio/dots-3-note-preview:free`) & Reference Queries
* **Paul** : Role F — Cross-checking references, trace consolidation, and summary preparation

*Workflow strategy*: The 20 reference queries were split equally among members, independently checked, and cross-validated into `reference-td1.csv`. For model evaluations, each member took charge of one specific model batch, and results were pooled together into `traces-td1.csv`.

---

## Repository Structure
* `reference-td1.csv` : The 20 independently checked reference queries and their values.
* `traces-td1.csv` : Raw combined traces of all model calls (including retries and attempts).
* `model-question-comparison-en.csv` : Final comparison matrix (100 rows, final verdicts, and causal explanations).
* `five-model-summary-en.csv` : Portfolio summary for the 5 evaluated models (public indices, prices, and family breakdowns).
* `reports/td1.md` : Detailed lab session report, pivot analysis, and routing hypotheses.
