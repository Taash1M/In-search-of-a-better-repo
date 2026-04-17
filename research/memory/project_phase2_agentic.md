---
name: Phase 2 Agentic Usage Tracking
description: Phase 2 plan for agentic AI layer on LLM usage tracking — 4 components, tool_use, deterministic QG, 87-finding eval resolved, plan v2 complete
type: project
originSessionId: f4d03941-dd0b-44f2-bb99-51b65b072972
---
Phase 2 adds an agentic AI analysis layer on top of the existing LLM Gateway Usage Tracking ETL (Phase 1).

**Why:** Enterprise requirement for automated pipeline monitoring, usage analytics, and future upgrade recommendations without manual analysis effort.

**How to apply:** Reference the Phase 2 folder at `C:\Users\tmanyang\OneDrive - Fortive\AI\Claude code deployment\Usage Tracking\Phase 2\` for plan, architecture, and deliverables. Primary plan is `Phase_2_Agentic_Usage_Tracking_Plan_v2.md`.

## Status (2026-04-14)
- **Plan v2.0 COMPLETE** — refined after 3-panel expert evaluation (87 findings, all CRITICAL+HIGH resolved)
- **Implementation NOT STARTED** — pending rollout Phases 2a-2d (5 weeks)
- **PBI Tab 5 GATED** on Phase 1 publish bug fix
- **Walkthrough PPTX COMPLETE** — 30 slides, 4 D2 diagrams + 1 Azure architecture diagram, all diagram stretching fixed (2026-04-14)

## Architecture (v2 Refined)
- **4 components** (not 5): Orchestrator+TaskManager (Python), 3 Claude Skills (tool_use), Quality Gate (Python)
- **3 LLM calls/run** via `tool_use` pattern (guaranteed JSON, temperature 0)
- **Deterministic Quality Gate** — full KPI verification against DuckDB, no LLM self-review
- **12 Level 1 self-healing fixes** + Azure Monitor alerts for Level 2+
- **Non-LLM fallback** when Claude API unreachable
- **Cost**: ~$11.14/month total ($5.87 incremental)

## Key Decisions from Evaluation
1. Merged Task Manager into Orchestrator (deterministic, saves tokens)
2. tool_use pattern eliminates JSON parsing failures
3. run_id merge key (not UUID) for idempotent upserts
4. No full_report_json column (typed columns only)
5. Safe Delta merge (no mode="overwrite" fallback)
6. Azure Key Vault for all secrets
7. Git-based deployment (runbook Step 3 = git pull)
8. 12-min watchdog + 15-min RunCommand timeout
9. PBI Tab 5 built natively in Desktop (not programmatic ZIP)
10. Prompt regression testing with golden inputs/outputs

## New Delta Tables (4)
- `delta/reports/engineering/` — pipeline metrics, lineage, quality score
- `delta/reports/analytics/` — usage trends, cost analysis, anomalies
- `delta/reports/recommendations/` — upgrade paths, Phase 3 readiness
- `delta/metadata/agent_runs/` — agent execution audit trail

## Deliverables (all in Phase 2 folder)
- `Phase_2_Agentic_Usage_Tracking_Plan_v2.md` — refined plan (primary)
- `Phase_2_Final_Plan.docx` — beautified plan
- `Phase_2_Architecture_and_Approach.docx` — architecture document
- `Phase_2_Walkthrough_Presentation.pptx` — 24-slide walkthrough
- `Phase_2_What_Was_Deployed.docx` — deployment record
- `Phase_2_How_to_Use.docx` — user guide

## Rollout Plan
- 2a (Week 1-2): Foundation — Key Vault, Monitor, git deploy, Orchestrator, QG, Data Eng
- 2b (Week 2-3): Full Skills — Analyst + Recs, golden tests, load tests
- 2c (Week 3-4): PBI — Fabric shortcuts, Tab 5, DAX (gated on publish bug)
- 2d (Week 4-5): Hardening — self-healing tests, edge cases, config tuning
