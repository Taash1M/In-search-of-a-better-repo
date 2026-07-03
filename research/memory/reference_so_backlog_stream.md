---
name: so-backlog-stream-specifics
description: "SO Backlog stream internals — 11 notebooks, 52 Gold views, bi-hourly; ONT01 source; FactSOBacklog ~275 cols/184 mapped; key transforms; HoldID MERGE; Refresh_SOBacklogViews.py 2,679 lines"
metadata: 
  node_type: memory
  type: reference
  originSessionId: 26203117-c07b-47a6-b7d2-fc239094e124
---

# SO Backlog Stream — Specifics

- 11 notebooks, 52 Gold views, bi-hourly refresh
- Primary source: `FLKUBI.ONT01_SALES_ORDERS_FV1` (~200+ columns)
- FactSOBacklog has ~275 columns in Silver, 184 mapped in comprehensive STM
- Key transforms: return sign logic, SalesCreditPct split, rtlRelativeAmountPct, currency conversion via cross-rate view
- Post-INSERT MERGE for HoldID assignment based on priority

## Real file locations (verified 2026-06-29)

- `Refresh_SOBacklogViews.py` — `FlukeCoreGrowth\Mart\Refresh\Refresh_SOBacklogViews.py` — **2,679 lines**
- `Refresh_FactSOBacklog.sql` — `FlukeCoreGrowth\Mart\Refresh\Refresh_FactSOBacklog.sql` — TRUNCATE+INSERT at ~L1043, MERGE (HoldID) at ~L1452
- `Publish_Data_ADLS_Delta.py` — `FlukeCoreGrowth\Publish\Publish_Data_ADLS_Delta.py` — iterates Gold views via `etl.source_control`, writes to `/mnt/cgphase2/Reporting/`
- `Refresh_Mart_Stream.sql` — calls `Execute_Parallel_Notebooks(...)` pointing at `RefreshSOBacklogMart.json` on ADLS

## 9 inline DISTINCT CTEs replaced by SOB_DistinctKeys (post perf-retrofit)

All 9 CTE semi-joins now read from `flukebi_work.SOB_DistinctKeys` (688,492 rows, 11 key columns) instead of doing independent full scans of FactSOBacklogHistory (9.76M rows).

**11 key columns in SOB_DistinctKeys:**
`DimInvItemKey`, `OopaPricingAttribute`, `SoldToOrgId`, `Hca2CustAccountId`, `Hcsua2SiteUseId`, `Hcsua1SiteUseId`, `Hca1CustAccountId`, `Hcp1CustAccountProfileId`, `Hcp2CustAccountProfileId`, `DeliverToSiteUseID`, `TransactionalCurrCode`

**Nullable columns (by design — do NOT assert zero nulls):**
- `OopaPricingAttribute`: ~97% null (most orders have no pricing attribute)
- `DeliverToSiteUseID`: ~99% null (most orders have no separate deliver-to site)
- `Hcp2CustAccountProfileId`: ~36% null (many orders lack bill-to credit profile)
- `Hcp1CustAccountProfileId`: ~12% null (some customers lack credit profile)
- `DimInvItemKey`, `Hcsua2SiteUseId`, `Hcsua1SiteUseId`: sparse nulls (rare order types)

**Required non-null (assert these in tests):**
`SoldToOrgId`, `Hca2CustAccountId`, `Hca1CustAccountId`, `TransactionalCurrCode`

## Key ROW_NUMBER locations (determinism fixes applied in perf-retrofit)

| Line | View | Fix type |
|------|------|----------|
| 516 | vw_DimProduct_SOB | Fix 2a — ORDER BY Item ASC, OrganizationID ASC, ModelAlias ASC |
| 634 | vw_DimCustomerSiteBillTo_SOB | Fix 2b — DimCustomerKey tiebreaker |
| 686 | vw_DimCustomerSoldTo_SOB | Fix 2b |
| 716 | vw_DimCustomerBillTo_SOB | Fix 2b |
| 767 | vw_DimCustomerShipTo_SOB | Fix 2b |
| 799 | vw_DimCustomerSiteShipTo_SOB | Fix 2b |
| 1143 | vw_DimTeamsClassification_SOB | Fix 2b-extra — DimEmployeeKey ASC tiebreaker |
| 1186 | vw_DimTeamsClassification_SOB | Fix 2c — LIKE-join fan-out on DimFNDUser |
| 1941 | vw_DimCustomerDeliverTo_SOB | Fix 2b |

## DimFNDUser DDL (relevant for Fix 2c)

Columns: `FND_USER_ID`, `FND_USER_NAME`, `EMPLOYEE_ID`, `PERSON_PARTY_ID`, `FULL_NAME`, `SUPERVISOR_FULL_NAME`, `ORGANIZATION_NAME`, `CDC_LAST_UPDATE_TIMESTAMP`. **No first_nm or last_nm columns.**

## DimEmployee DDL (relevant for Fix 2b-extra)

Key columns: `DimEmployeeKey` (surrogate PK — use as tiebreaker), `EmployeeNumber`, `FullName`, `FirstName`, `LastName`, `CdcLastUpdateTimeStamp`, `ActiveInd`, `EffectiveStartDate`, `EffectiveEndDate`. **No FND_USER_ID column** — that only exists in DimFNDUser.

## FactSOBacklogHistory sizing (measured 2026-06-25 on prod)

- 1,011 files / 1.67 GB / 357 partitions (119 BacklogDate × 3 SnapshotTypes)
- OPTIMIZE never run (1,462 versions, 0 OPTIMIZE in history)
- 9.76M rows (prod) / 7,741,538 rows (DEV, 2 days of data)

## Prod row counts (measured 2026-07-02, read-only via prod cluster)

| Table/View | Prod count |
|---|---|
| flukebi_silver.FactSOBacklog | 91,418 |
| flukebi_silver.FactSOBacklogHistory | 10,598,850 |
| flukebi_gold.vw_DimProduct_SOB | 89,186 |
| flukebi_gold.vw_DimCustomerSoldTo_SOB | 25,321 |
| flukebi_gold.vw_DimCustomerBillTo_SOB | 28,513 |
| flukebi_gold.vw_DimCustomerShipTo_SOB | 35,028 |
| flukebi_gold.vw_DimPricingAttributes_SOB | 1,423 |
| flukebi_gold.vw_FactSOBacklogHistory_SOB | 10,586,636 |

## ADLS prod structure (discovered 2026-07-02)

- `Silver/Common/` — shared dims: DimCustomer, DimCustomerSites, DimEmployee, DimFNDUser, DimSalesAgent, etc.
- `Silver/SOBacklog/` — stream-specific Silver tables: FactSOBacklog, FactPriceAdjustments, FactSOHolds
- `Raw/SOBacklog/ONT01_SALES_ORDERS_FV1/YYYY/MM/DD/HH/` — raw landing (1 file per hour)
- `Reporting/SOBacklog/` — published Gold Delta tables
- Silver dimension tables are **Unity Catalog managed** — not in cgphase2 blob container; access only via Databricks

## E2E timing (n=83 measured, plus DEV simulation 2026-07-02)

| Stage | Prod median | DEV (2026-07-02) | NEW projected |
|---|---|---|---|
| Source DataPull | 9.9 min | N/A | ~6–7 min (ADF parallel) |
| Build_SOB_DistinctKeys | — | 32s | ~0.5 min |
| Refresh SOBacklog views | ~2–3 min | 32s | ~2–3 min |
| Publish_Data_ADLS_Delta | 35.1 min (59%) | N/A | ~14–18 min (est.) |
| E2E total | ~60+ min | — | ~35–42 min |
| **E2E improvement** | — | — | **~35–40%** |

## RefreshSOBacklogMart.json

Lives on ADLS at `/dbfs/mnt/cgphase2/Staging/Static/RefreshSOBacklogMart.json`. Must be updated to wire `Build_SOB_DistinctKeys` between `Refresh_FactSOBacklog` and `Refresh_SOBacklogViews`. Instructions in `FlukeCoreGrowth/Static/RefreshSOBacklogMart_retrofit_diff.md`.

Related: [[ubi-platform-key-facts]] · [[ubi-medallion-patterns]] · [[project_so_backlog_optimization]]
