---
name: Customer MDM Project
description: Customer Master Data Management — 5-phase Splink/Custom matching pipeline, CRM+EBS dedup, cross-match, golden records, Gold views. All phases production complete.
type: project
---

## Project Directory
`C:\Users\tmanyang\OneDrive - Fortive\Projects\MDM\Customer Data\Customer Data Matching and Linking\`

## Key Files
- **Memory file**: `PROJECT_MEMORY.md` in project dir (full session log, table catalog, bridge keys, design decisions)
- **E2E Report**: `CustomerMDM_E2E_Run_Report_20260318.docx` in project dir
- **Validation scripts**: `validate_phase2.py` through `validate_phase5.py` (reusable, run on Databricks)
- **Splink memory**: `splink/SPLINK_MEMORY.md` in project dir

## ADLS Storage
- Container: `cgphase2` on `flkubiadlsdev` (`52a1d076-bbbf-422a-9bf7-95d61247be4b` / `flkubi-dev-rg-001`)
- Databricks mount: `dbfs:/mnt/cgphase2/`
- Splink path: `cgphase2/MDMPilotData/Matching and Linking/Splink/`

## Source Tables
- CRM: `flukebi_Silver.dimcrmaccount` (2.27M, 382 cols)
- EBS: `flukebi_Silver.dimcustomersites` (4.35M, 50 cols)
- Bridge: `flukebi_Silver.dimcrmoraclecustomer` (420K, 129 cols)
- Bridge linkage: CRM.flk_oracleaccountid -> bridge.Id -> bridge.flk_partynumber -> EBS.PartyNumber

## Status (2026-03-18)
ALL 5 PHASES PRODUCTION COMPLETE + VALIDATED. E2E artifact review COMPLETED. Documentation review COMPLETED — 9 discrepancies fixed in Approach v2->v2.2. Feature branches `Users/tmanyang/CustomerMDM` in both repos — committed but NOT pushed.

## Production Results
- **Phase 2 (Dedup)**: CRM 2.27M->1.58M survivors (30.2% dup). EBS 4.35M->1.22M survivors (71.9% dup). CRM scored 5.6M pairs, EBS scored 3.3M pairs.
- **Phase 3 (Cross-Match)**: 2,930 pairs (all TIER1_KEY). Tier 2 fuzzy produced 0 additional matches.
- **Phase 4 (Golden Records)**: 2,806,713 golden records (328 Matched, 1,582,693 CRM Only, 1,223,692 EBS Only).
- **Phase 5 (Gold Views)**: DimCustomerMaster (2,806,713), BridgeCustomerSource (6,621,455), BridgeCustomerXref (8,914,941).

## Production Tables
MDM_CRM_Cleaned (2.27M), MDM_EBS_Cleaned (4.35M), MDM_CRM_ScoredPairs (5.6M), MDM_EBS_ScoredPairs (3.3M), MDM_CRM_Dedup (2.27M), MDM_EBS_Dedup (4.35M), MDM_CrossMatch_Pairs (2,930), DimCustomerMaster (2,806,713), BridgeCustomerSource (6,621,455), BridgeCustomerXref (8,914,941), MDM_Run_Metadata (37 cols).

## Key Technical Decisions
- **OOM fix v3**: Delta materialization (`_delta_materialize()`) — all `.checkpoint()/.cache()` replaced. Delta writes to ADLS = 100% durable. Prior fixes (.checkpoint, .localCheckpoint) failed under memory pressure.
- **Phase 2 split**: 4 notebooks (2.1 CRM Scoring, 2.2 CRM Dedup, 2.3 EBS Scoring, 2.4 EBS Dedup). Job 753541170472760.
- **CC label dedup**: Country-batched CC can produce duplicate node labels. Always `groupBy("source_id").agg(F.min("cluster_id"))` before joining.
- **Cell boundary fix**: `# COMMAND ----------` markers inside try-except blocks break Databricks compilation. Use inline `# --- Step N ---` comments instead.
- **US data dominance**: 58-66% of data — salted repartition needed for executor skew.
- **`%pip install`**: Does NOT persist via Command Execution API — use cluster library config.
- **EBS CountryCode**: Already has ISO 2-letter codes (not just full names).
- **Build cadence**: Build each phase, pause for review.

## Key Constants
BLOCK_SIZE_CAP=500, PAIR_COUNT_LIMIT=50M, COUNTRY_BATCH_THRESHOLD=50K, CC_BATCH_THRESHOLD=100K, RESUME_THRESHOLD=10K, NOTEBOOK_TIMEOUT_SECONDS=21600 (6h).

## Cluster
`flkubi_adb_dev` (0217-060922-xqqlev35), Standard_D3_v2 driver (14GB), 4x Standard_D4s_v3 workers, DBR 14.3.

## Incremental Processing
Plan documented in `Plan_Incremental_Processing_Phase6Plus.md` (READY status). LoadType widget, MDM_Watermark table, and MERGE upsert NOT in production notebooks — all runs are full-load. Incremental logic is Phase 6 work.

## Splink POC
DuckDB full-scale PROVEN. Spark INFEASIBLE (18 failures). Threshold experiments: T=-2/+2/+4. Splink over-merges ~2x vs Custom. Recommendation: Hybrid (Custom backbone + Splink supplementary). VM: `splink-ebs-1tb` (Standard_E96ds_v5, 96 vCPU, 768GB RAM), deallocated between runs (~$7.25/hr).

## TDD
Phase 1 (3 suites/29 tests), Phase 2 (5 suites/34 tests), Phase 3 (3 suites/19 tests).
