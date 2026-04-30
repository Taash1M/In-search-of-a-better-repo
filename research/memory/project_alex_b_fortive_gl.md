---
name: Alex B Fortive GL Investigation
description: Fortive corporate GL (15 entities) — full pipeline research, 2 proposed options (UNION ALL vs separate ADF), handover DOCX with 4 diagrams + 32-account mapping + entity 8650 context (2026-04-22)
type: project
originSessionId: 16123451-50c1-4bd1-bf89-c33d5f382919
---
## Investigation (2026-04-06)

Alex B needs visibility into Fortive corporate accounts — intercompany/treasury journal entries like TGA Finance (Cayman Islands) liquidation and monthly interest accruals.

### Finding
Fortive corporate GL data is **NOT** in the UBI pipeline. The Fortive Global Ledger Set is a separate Oracle ledger from Fluke ledger sets. Three Gold-layer filters also exclude: company whitelist (51 Fluke opcos), account range (LIKE '6%'), cost center (<> '0000').

**Why:** UBI extraction (Extract_Revenue_OTL.sql) only queries Fluke ledger sets. Fortive entities never enter Bronze.

**How to apply:** Any future requests for Fortive corporate data require Oracle extraction expansion first. The Gold view (`vw_FactGLDetails_Flat_FTV.sql`) is prepared but blocked on Bronze data.

## Scope Expansion (2026-04-22)

Expanded from 2 entities (11, 13) to **all 15 Fortive entities** found in Tom Kepler's GL Query Tool export:
- **Numeric**: 10 (2,004 rows), 11 (6,467 rows), 12 (126 rows), 13 (1,034 rows)
- **Alpha**: F2, F3, F4, F6, UG, VI, VJ, VM, VN, VP, VR (44 rows combined)
- **Onestream entity 8650** (from YTD G&A Detail) maps to Oracle cost center 8650, present under entities 10 and 11

**Why:** The `Copy of YTD_GA_Detail.xlsx` (Alex B's reference report) uses Onestream entity 8650 which requires Oracle entities 10 and 11 (CC 8650). Original scope of just 11/13 would miss entity 10 entirely.

**How to apply:** SQL view and handover doc now reference all 15 entities. Account Mapping expanded from 31→32 rows (full `Account Mapping.xlsx`). Note: 56 of 86 GL Query Tool accounts still unmapped — flag to Tom Kepler.

## Handover Document (2026-04-19, updated 2026-04-22)

### Context
Tom Kepler email (2026-04-07) to Alex Becker, Taashi Manyanga, Baker Funkhouser — provided Account Mapping (32 Oracle accounts → Onestream AccBucket codes) and GL report sample (9,675 rows, 15 entities). Specified Supplier Name logic: if Source='Payables' → use Supplier/Customer Name, else → JE Line Description.

### Pipeline Research
- **Oracle Linked Service**: `flkubi_oci_oracle.json` — server flkonv-odb01-p.oci.fluke.com:1591/flkp, user flkubi, IR: integrationRuntime-OCIADF
- **Extraction**: `Extract_Revenue_OTL.sql` — 6 OTL views (IsOTL=1) + 6 standard views (IsOTL=0)
- **Gold filter**: `Refresh_Revenue_Gold.sql` lines 776-880 — `vw_FactGLDetils_Flat` has 51-company Fluke whitelist, `Acct LIKE '6%'`, `CC <> '0000'`
- **Three blockers**: (1) company whitelist excludes all 15 Fortive entities, (2) account range filter, (3) cost center filter

### Two Proposed Options
- **Option A — UNION ALL in existing pipeline**: Modify extraction SQL to include Fortive ledger set views, add all 15 entities to Gold whitelist, relax account/CC filters for Fortive rows. Lower effort but tightly couples Fortive data to Fluke pipeline.
- **Option B — Separate ADF source query** (recommended): New ADF pipeline with dedicated Oracle extraction for all 15 Fortive entities, apply Account Mapping at Silver layer, integrate into existing Revenue Gold views. Clean separation, independent scheduling, no risk to existing Fluke data.

### Sample Data Validation
- Tom Kepler's GL export: 9,675 rows, 18 columns, 15 entities
- Entity 11: 6,467 rows; Entity 10: 2,004 rows; Entity 13: 1,034 rows; Entity 12: 126 rows; 11 alpha entities: 44 rows
- Periods: JAN-26, FEB-26, MAR-26
- 10+ transaction categories (Allocation, MassAllocation, Payroll, Purchase Invoices, etc.), multi-currency (USD, AUD, CNY)
- 100+ distinct cost centers, 86 unique accounts (32 mapped, 56 unmapped)

### Artifacts
- `<USER_HOME>/OneDrive - <ORG>\ADHOC\UBI\Alex B - Fortive\`
- `vw_FactGLDetails_Flat_FTV.sql` — Gold view for all 15 Fortive entities (updated 2026-04-22)
- `Fortive_GL_Data_Investigation_Report.docx` — 2-page investigation report (2026-04-06)
- `Fortive_GL_Handover_Document.docx` — 7-section handover with 4 diagrams, 32-account mapping, 15-entity scope (updated 2026-04-22)
- `Fortive_GL_Handover_Document_BACKUP.docx` — Pre-expansion backup (2026-04-19 version)
- `Account Mapping.xlsx` — 32 rows Oracle → Onestream AccBucket
- `Fortive_GL_Query_Tool___G_A_De_070426_` — Tom Kepler's GL data (TSV, 9,675 rows, 15 entities)
- `Copy of YTD_GA_Detail.xlsx` — Alex B's Onestream YTD G&A Detail (entity 8650, 96 rows)
- `RE Fortive Access to BI.htm` — Tom Kepler's original email
- `PROJECT_MEMORY.md` — Full project context
