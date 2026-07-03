---
name: project_diag_cost_opus_july
description: July 2026 follow-up — correct diagnostic-only CLI Opus cost coefficient (Sonnet→Opus est)
metadata: 
  node_type: memory
  type: project
  originSessionId: a8fc746d-720a-4b46-b803-5585ff36821e
---

**Follow-up due: starting July 2026.** In the LLM usage-tracking ETL (`llm_usage_etl_v2.py`, per_user_usage SQL, ~lines 388-409), diagnostic-only CLI rows (`claude-code-nodeX`) were relabeled to `model_key='claude-opus-4-6'` for correct attribution in the claude-code→Opus relabel sprint (2026-06-27), BUT their **estimated cost + token coefficients were deliberately LEFT at the Sonnet values** (cost `$0.184361/req`, tokens `86549`) so the tracked headline est. cost number would not move mid-period.

**The July fix:** change the diagnostic cost/token CASE expressions so `claude-code` deployments estimate at the **Opus** coefficient (cost `$0.830668/req`, tokens `61905` — already in `EST_AVG_COST_PER_REQUEST['claude-opus-4-6']`). This raises the diagnostic-only estimate ~4.5× on those rows — that is the correct accounting, intentionally deferred to a clean period boundary.

**Why deferred:** mid-period cost-number stability for the dashboards. **How to apply:** the cost/token CASE blocks key on `model_deployment_name ILIKE '%opus%'` which does NOT match `claude-code-nodeX`; add a `'%claude-code%'` branch (or reuse the already-corrected model_key) routing to the Opus coefficient. Real-cost LiteLLM rows are unaffected (already Opus-priced). See [[project_llm_usage_tracking]].
