---
name: AI Usage Analytics UBI Stream
description: UBI stream migrating LLM Gateway ETL to Databricks/ADF — v3.1 complete, E2E verified (26 DB objects, 0 WARNs), 3 WARN fixes applied (freshness gate, skew checks, critical scope), Phase 5 Fabric next
type: project
originSessionId: 61ad1a6b-ccfa-4ad3-989e-c0cf44ad9779
---
New UBI stream `AI_Usage_Analytics` that brings the existing LLM Gateway Usage Tracking ETL into the UBI platform standard flow.

**Why:** The current ETL runs as a standalone DuckDB script on a VM outside UBI governance. Migrating to UBI standardizes orchestration (ADF), compute (Databricks), storage (ADLS `flkubiadlsdev`), and reporting (Fabric Lakehouse + PBI) — making AI usage data a first-class enterprise data stream alongside SO Backlog, Revenue, Inventory, etc.

**How to apply:** Use the UBI dev skill (`/ubi-dev`) for all implementation work. Follow the plan at `<ADMIN_HOME>/.claude\plans\breezy-wandering-sparkle.md`.

## Key Decisions
- **ADF Copy Activity for cross-sub data movement** (v3) — ADF `flkaienablement_adls` linked service copies Delta→Parquet to landing zone `/mnt/cgphase2/Raw/AI_Usage_Analytics/{table}/{YYYY}/{MM}/{DD}/`, no SHIR needed (AutoResolveIR), Databricks reads locally
- **Read existing Delta tables as Bronze source** (not raw JSON blobs) — avoids duplicating blob parsing and Sonnet API integration
- **Content safety analysis stays on VM** — rate-limited Sonnet API calls don't fit Spark's parallel execution model
- **Data classification** — two Fabric Lakehouses (`ubi_ai_usage` general, `ubi_ai_content_safety` restricted) + two PBI semantic models
- **Daily schedule** (07:00 UTC) — buffer for VM's 00:00 UTC run; two-stage freshness gate (ADF + extraction notebook 18h threshold)
- **Reuse platform DimCalendar** — map date_key (YYYYMMDD int) to existing `flukebi_Bronze.DimCalendar`
- **Cross-sub auth via Key Vault** — `flkaienablement-storage-key` in `FlukeDevKeyVault`

## Plan Review
- **3 review rounds**: Enterprise Architect (26 findings), Principal Data Engineer (30 findings), Solutions Architect (23 findings)
- **79 total findings**: 5 CRITICAL, 29 HIGH, 32 MEDIUM, 13 LOW — all addressed in v2→v3
- **v3 correction**: ADF Copy Activity handles cross-sub data movement (not Databricks MSI/SAS)

## Artifacts
- **Project folder**: `<USER_HOME>/OneDrive - <ORG>\Projects\UBI\AI Usage Analytics\`
- **Plan file**: `<ADMIN_HOME>/.claude\plans\breezy-wandering-sparkle.md` (v3)
- **Plan .md copy**: `AI_Usage_Analytics_Implementation_Plan_v3.md` (in project folder)
- **Plan DOCX**: `AI_Usage_Analytics_Implementation_Plan_v3.docx` (beautified, in project folder)
- **Dev resource group**: `flkubi-dev-rg-001` (Fluke Unified BI subscription `52a1d076-...`)
- **Dev Databricks**: `adb-1943773873358740.0.azuredatabricks.net`
- **Dev ADLS**: `flkubiadlsdev`
- **Source**: `flkaienablement` storage (AI/ML subscription `77a0108c-...`)

## Notebooks (5 new)
1. `FlukeCoreGrowth/Tools/Tools_AI_Usage_Utils.py` — shared utilities (quality, schema, skew, freshness)
2. `FlukeCoreGrowth/Staging/Extraction/Extract_AI_Usage_Analytics.py` — Bronze extraction from local landing zone
3. `FlukeCoreGrowth/Mart/Refresh/Refresh_AI_Usage_Analytics.py` — Silver transformation + dims
4. `FlukeCoreGrowth/Mart/Refresh/Refresh_AI_Usage_Analytics_Views.py` — Gold views + 4 aggregation tables
5. `FlukeCoreGrowth/Mart/Validation/Test_Insert_Mart_AI_Usage_Analytics.py` — 20 BVT tests (9 mandatory categories)

## ADF Files (5 deployed + 1 pending)
- `ADF/linkedService/flkaienablement_adls.json` — cross-sub ADLS (AutoResolveIR, Key Vault)
- `ADF/dataset/DS_flkaienablement_Binary.json` — Binary source dataset (preserves _delta_log)
- `ADF/dataset/DS_AI_Usage_Landing_Binary.json` — Binary sink dataset (cgphase2 landing zone)
- `ADF/dataset/DS_flkaienablement_Parquet.json` + `DS_AI_Usage_Landing_Parquet.json` — legacy Parquet datasets (Phase 0 smoke test)
- `PL_AI_Usage_Analytics_DataPull` — 6-table ForEach Binary copy pipeline (deployed via REST API)
- `ADF/trigger/Trigger_AI_Usage_Analytics.json` — daily 07:00 UTC (Phase 4)

## Tables
- **Bronze**: 6 tables (LLMUsage, ContentLogs, DiagnosticActivity, DimNodes, DimModels, DimAADUsers)
- **Silver**: 6 tables (FactAIUsage, FactAIContentLog, DimAINode_AUA, DimAIModel_AUA, DimAIUser_AUA, DimAADUser_AUA)
- **Gold**: 7 views + 4 aggregation tables (FactAIUsageDaily, FactAISafetyDaily, FactAIUserActivity, FactAIContentAlerts)

## Documentation Deliverables
- STM Excel (45 columns, 7 stages, ~150-200 rows)
- Approach & Architecture DOCX (D2 diagrams, lineage bridge, runbook)
- Test Results MD (20 BVTs)
- Build Walkthrough PPTX

## Status
- **Plan**: v3 Complete (2026-05-10)
- **Phase 0**: COMPLETE & signed off (2026-05-10) — all 6 gates passed
  - PIA signed, DimCalendar INT YYYYMMDD confirmed, no firewall on flkaienablement
  - Linked service `flkaienablement_adls` deployed, smoke test pipeline succeeded (35s, 14 files, AutoResolveIR)
  - 93 columns pinned across 6 tables, 4 schema findings addressed in plan
  - Finding: Delta Parquet copy includes all version files — Phase 1 needs Binary copy or dedup
  - Report: `Phase0_Report_AI_Usage_Analytics.docx` (2.2 MB, with D2 diagrams)
- **Phase 1**: COMPLETE & signed off (2026-05-11) — Infrastructure + Bronze
  - ADF Binary Copy pipeline deployed: `PL_AI_Usage_Analytics_DataPull` (6 tables, 38s parallel)
  - **Delta dedup fix**: Binary copy preserves `_delta_log/` — Databricks reads Delta format (zero duplicates)
  - Datasets: `DS_flkaienablement_Binary` (source), `DS_AI_Usage_Landing_Binary` (sink) — replaces old Parquet datasets
  - Landing zone: `/mnt/cgphase2/Raw/AI_Usage_Analytics/{table}/2026/05/11/` (all 6 tables)
  - Notebooks deployed: `Tools_AI_Usage_Utils`, `Extract_AI_Usage_Analytics`
  - 6 Bronze Hive tables populated: LLMUsage (13,085), ContentLogs (3,415), DiagnosticActivity (16,592), DimNodes (7), DimModels (5), DimAADUsers (53)
  - etl.source_control: 6 rows inserted; status_control: auto-created by framework
  - TDD: 8/8 passed (row count, PK uniqueness, date_key format, schema validation, completeness, metadata)
  - Report: `Phase1_Report_AI_Usage_Analytics.docx` (4.7 MB, with D2 diagram)
- **Phase 2**: COMPLETE & signed off (2026-05-11) — Silver layer
  - Notebook deployed: `Refresh_AI_Usage_Analytics` 
  - 6 Silver tables: FactAIUsage (13,085/39cols), FactAIContentLog (3,415/43cols), DimAINode_AUA (7), DimAIModel_AUA (5), DimAIUser_AUA (20 derived from 16,592 diag records), DimAADUser_AUA (53)
  - Key transforms: type casting, DimCalendarKey, cost recalculation (broadcast DimModels), alert_severity derivation, node_key validation, is_cached, hour_of_day
  - Cost variance: all within $0.01 tolerance
  - Delta maintenance: OPTIMIZE + VACUUM RETAIN 336h on fact tables
  - TDD: 12/12 passed (PK, RI, value range, reconciliation, schema)
  - Report: `Phase2_Report_AI_Usage_Analytics.docx` (2.7 MB, with D2 diagram)
- **Phase 3**: COMPLETE & signed off (2026-05-11) — Gold layer
  - Notebook deployed: `Refresh_AI_Usage_Analytics_Views`
  - 7 Gold views: vw_FactAIUsage_AUA (13,085), vw_FactAIContentLog_AUA (3,415), vw_DimAINode_AUA (7), vw_DimAIModel_AUA (5), vw_DimAIUser_AUA (20), vw_DimAADUser_AUA (53), vw_DimCalendarUsage_AUA (39)
  - 4 Aggregation tables: FactAIUsageDaily (90), FactAISafetyDaily (10), FactAIUserActivity (4), FactAIContentAlerts (55/MERGE)
  - Gold-Silver reconciliation: 0.0000% difference (13,085 == 13,085)
  - Quality: 11/11 passed, OPTIMIZE on all 4 agg tables
  - Fix: DimCalendar column names corrected (FiscalQuarter, CalendarMonthName, CalendarDayName, WeekOfYearNumber, WeekDayFlag)
  - Report: `Phase3_Report_AI_Usage_Analytics.docx` (3.2 MB, with D2 diagram)
- **Phase 4**: COMPLETE & signed off (2026-05-11) — ADF Pipeline + BVT Framework
  - BVT notebook deployed: `Test_Insert_Mart_AI_Usage_Analytics` (20 tests, 9 categories)
  - BVT results: 19/19 PASS, 4 KPI baselines (FactAIUsage 9,176 | FactAIContentLog 3,415 | FactAIUsageDaily 90 | FactAIContentAlerts 55)
  - Mart refresh JSON: `/mnt/cgphase2/Staging/Static/RefreshAI_Usage_AnalyticsMart.json` (3-notebook chain)
  - ADF trigger deployed: `Trigger_AI_Usage_Analytics` (daily 07:00 UTC, Stopped)
  - Data quality remediation: 3,909 Bronze duplicates removed (13,085→9,176), "unassigned" node added, null date_key defaulted
  - Gold FactAIUsageDaily rebuilt: 9,176 == 9,176 reconciliation
  - Report: `Phase4_Report_AI_Usage_Analytics.docx` (1.8 MB, with D2 diagram)
- **v3.1 Retrofit**: COMPLETE (2026-05-19) — per_user_usage added end-to-end
  - All 5 notebooks updated: Utils (25-col llm_usage + per_user_usage schema), Extract (7 Bronze tables, 10 TDD), Refresh (7 Silver tables, 15 TDD), Views (8 Gold views), BVT (24 tests)
  - `azure_correlation_id` added to FactAIUsage Silver + Gold view
  - `vw_FactAIPerUserUsage_AUA` Gold view (star schema join to DimNode, DimModel, DimCalendar)
  - ADF pipeline needs per_user_usage added to ForEach items (REST API deploy)
  - Plan updated to v3.1
- **E2E Verification**: COMPLETE (2026-05-19) — clean bill of health
  - **Code-level**: Schema alignment 6/7 exact + 1 benign extra, cross-notebook consistency 15/15 PASS, SQL correctness 19 PASS + 3 WARN
  - **Artifact inventory**: 26 DB objects verified (7 Bronze + 7 Silver + 8 Gold views + 4 Gold agg tables), 28 DataFrames, 11 functions, 5 temp views, 5 config dicts
  - **12/12 cross-artifact checks** passed (schema keys, sink names, load types, join patterns, SetTableStatus, BVT coverage, node_key remap, NULL defaults)
  - **3 WARNs resolved** (2026-05-19):
    1. Freshness gate wired up in Extract preflight (`landing_zone_freshness_gate(spark, llm_usage_path, 18h)`)
    2. `check_skew` added for FactAIContentLog.node_key and FactAIPerUserUsage.node_key in Refresh
    3. Critical failure scope narrowed from `f.startswith("Fact")` to explicit `f in ("FactAIUsage", "FactAIContentLog")` — PerUserUsage failure no longer halts pipeline
  - **2 INFOs accepted by design**: `etl_run_id` extra in llm_usage (VM internal, dropped at Silver); null hour_of_day/day_of_week from null start_time (correct behavior)
- **Phase 5**: PENDING — Fabric Lakehouse + PBI
