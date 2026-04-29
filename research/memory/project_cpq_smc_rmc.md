---
name: CPQ SMC RMC for UBI
description: Oracle CPQ/SMC/RMC subscription data integration into UBI — Miro board with 8 canvases (17 artifacts), hybrid architecture designed, 3 ER diagrams, Phase 0 ready to start (2026-04-29)
type: project
originSessionId: dcc84167-b07b-42e7-8e3d-d14ad0f99f66
---
Oracle CPQ (Configure Price Quote), SMC (Subscription Management Cloud), and RMC (Revenue Management Cloud) subscription data integration into UBI.

**Why:** With CPQ implementation, subscription orders now bypass legacy EBS Order Management and flow through SMC → AR, requiring a new UBI data pipeline.

**How to apply:** When working on this project, reference files at `C:\Users\tmanyang\OneDrive - Fortive\Projects\UBI\CPQ - SMC and RMC\`.

## Project Directory
`C:\Users\tmanyang\OneDrive - Fortive\Projects\UBI\CPQ - SMC and RMC\`

## Status (2026-04-29)
- **Phase:** Technical Design → Miro board walkthrough ready, pending stakeholder review
- 7 clarifying questions sent 2026-03-24, updated 2026-04-08, answers received by 2026-04-22
- Sample reports: RevRec (68 rows), Month-end QM (9,463 rows), SMC Backlog (2,225 rows, 44 cols), ARR PBI dashboard
- BRD has 26+ field mappings

## Miro Board (2026-04-29)
- **Board URL**: `https://miro.com/app/board/o9J_lAknUAk=/`
- **17 artifacts** across 8 logical canvases, laid out left-to-right for sequential walkthrough
- All items at y=-800, x ranges from 80000 to 128947
- **Pending cleanup**: Items need frames — related doc+table/diagram pairs are separated; user cleaned up old frames but new ones not yet created

### Canvas Layout
| # | Canvas | Artifacts |
|---|--------|-----------|
| 1 | What is CPQ/SMC/RMC | Doc (intro) + Flowchart (lifecycle) |
| 2 | Current State — Reporting Today | Doc (pain points) + Table (4 OTBI reports + limitations) |
| 3 | Problem Statement | Doc (gap analysis) + Table (5 requirement areas, color-coded UBI coverage) |
| 4 | Data Landscape — UBI Coverage Gaps | Flowchart (existing streams vs gaps) + Table (integration fit assessment) |
| 5 | Proposed Solution — Hybrid Architecture | Doc (design principles) + Flowchart (Oracle→OIC→Bronze→Silver→Gold→PBI) |
| 6 | Detailed Data Flow | Flowchart (5 paths: revenue, backlog, bookings, ARR, subscription dim) |
| 7 | Solution Detail — Data Models | Doc (schemas) + ER Diagram (proposed model, 7 tables) + ER Diagram (before/after changes) |
| 8 | Implementation Plan & Next Steps | Doc (phases/risks) + Table (4 phases) + Table (6 open items with owners) |

### Diagrams Created
- CPQ/SMC/RMC Lifecycle (flowchart, LR)
- Current UBI Streams — What Exists vs. Gaps (flowchart, TB)
- Hybrid Integration Architecture (flowchart, LR, 5 clusters)
- Detailed Data Flow — By Data Type (flowchart, LR, 5 paths)
- Proposed Data Model — New & Extended Tables (ER, 7 entities, 12 relationships)
- Data Model Changes — Before vs After (ER, 7 entities, 5 relationships)

## Architecture
- **Two GL paths:** SMC → OIC → Autoinvoice → AR → GL (invoices) | SMC → RMC → GL (revenue recognition)
- **Deferred revenue:** Contracts recognized over time via RMC (e.g., $12K → ~$850/month × 12)
- **Subscription lifecycle:** New → Update → Renewal → Upsell (future simplifies to 3 types)

## Source Tables (Oracle Fusion OSS)
- `OSS_SUBSCRIPTIONS` — headers with dates, customer, amounts
- `OSS_PRODUCTS` — product lines per subscription
- `OSS_BILL_LINES` — invoice/billing details, interface flags
- `OSS_CHARGES` — charge definitions (recurring vs. one-time)
- `OSS_SALES_CREDITS` — salesperson commission splits
- `HZ_PARTIES` / `HZ_CUST_ACCOUNTS` — customer master
- `XLE_ENTITY_PROFILES` — legal entity mapping
- `EGP_SYSTEM_ITEMS_B/TL` — product definitions (PLM)

## Corrections to Our Understanding
- Revenue recognition path is **SMC/AR → RMC → GL** (not SMC → RMC → GL directly)
- Currently **NO Field Service Orders** running through SMC

## Q&A Answers (April 8, 2026)

### Q1 — Source System Access (RED)
- Invoices land in AR, but **bookings and revenue recognition are NOT in AR**. GL journals visible in UBI for each accounting event (retro perspective).
- Only the invoice is in existing AR tables — not bookings/backlog/revenue data
- **Currently using Fusion OBI + PowerAutomate**. Future: general extraction from Fusion (**BICC?**)
- **Implication: NEW UBI stream needed** (can't extend existing AR stream)

### Q2 — Cutover Date (RED)
- **CPQ and SMC/RMC are LIVE** — already deployed, no future cutover to plan for
- **No double booking** — orders go through one route or the other
- **Historical data load requested** ("would be great")

### Q3 — ARR Definition (RED)
- ARR = **contracted annual amount** (not monthly × 12) — **needs Kerry/Darby confirmation**
- Active = subscription header/lines have status field + start/end dates needed
- **Month-end snapshots: YES** (agreed approach)
- Subscriptions booked in **local currency**, convert for reporting (same FX approach as UBI)

### Q4 — NDR & VLO (AMBER)
- NDR baseline = **snapshot** (as understood) — **needs Kerry/Darby confirmation**
- "New logo" = **new subscription during measurement period**
- VLO: **not currently required for Azima**; need Kerry for eMaint threshold
- Kerry provides NDR worked example for eMaint; Darby for Azima

### Q5 — Compensation (AMBER)
- **Booking date** drives compensation timing (understanding, not confirmed)
- Contract changes: **delta only** (not full new value)
- **Kristen needs to confirm**: credit split source and activation-date retroactivity

### Q6 — Field Mappings (AMBER)
- **Region**: Use standard EBS Salesperson relation (same as existing UBI — no new mapping)
- **FX rates**: From EBS, monthly, same as UBI
- **Pricing Attribute Item No**: Currently only in CPQ; perhaps map to custom SMC field for reporting
- **Item flow bug**: Needs re-verification

### Q7 — Refresh & Volumes (GREEN)
- Bookings: **daily**; ARR/NDR: **weekly**; Compensation: TBD
- **~250 active subscriptions**, growing slowly
- Timeline: **ASAP — system is in use**

## Open Items Needing Confirmation
| Item | Owner | Status |
|------|-------|--------|
| ARR = contracted annual amount? | Kerry / Darby | Pending |
| NDR snapshot methodology | Kerry / Darby | Pending |
| NDR worked example (eMaint) | Kerry | Pending |
| NDR worked example (Azima) | Darby | Pending |
| Compensation date rules, credit splits, retroactivity | Kristen | Pending |
| VLO threshold for eMaint | Kerry | Pending |
| Item flow bug (one-time services as subscriptions) | CPQ team | Pending |
| BICC as future extraction method | TBD | Pending |
| Pricing Attribute Item No → SMC custom field | CPQ/SMC team | Pending |

## Sample Reports
- `Reports/First Jan RevRec.csv` — 68 rows, monthly revenue recognition, GL account 21000
- `Reports/QM_ Draft month end all entities.csv` — 9,463 rows, satisfaction events, multi-currency
- `Reports/SMC Backlog.csv` — 2,225 rows, 44 columns, active subscriptions
- `Reports/ARR Azima & Service.pbix` — Power BI dashboard

## Approach Documents Delivered (2026-04-22)
- **Option A (Standalone)**: `CPQ_SMC_RMC_Approach_Architecture_20260422.docx` — New "Subscription" stream, 3 fact tables, DimSubscription, dedicated pipeline
- **Option B (Integrated)**: `CPQ_SMC_RMC_Approach_OptionB_Integrated_20260422.docx` — Integrate into existing Revenue/SOBacklog/Orders streams
- **Hybrid Recommended**: Revenue → integrate (already flowing via GL), Backlog/Bookings → companion tables, ARR/NDR → new tables

### Key Discovery (Corrected 2026-04-22 after DEV query)
- **`RMC_CONTRACT_NUMBER` column does NOT exist** in `flukebi_silver.FactRevenue` — earlier assumption was wrong
- FactRevenue has 193 columns, 233.7M rows total
- **Contract columns that DO exist**: `CONTRACT_START_DATE`, `CONTRACT_END_DATE`, `CONTRACT_DURATION`, `DEFERRED_PERCENT`, `SERVICED_PRODUCT_NUM`
- **Contract data population**: 6.8M rows have CONTRACT_START_DATE, 6.8M have CONTRACT_END_DATE, 6.8M have CONTRACT_DURATION, 23.1M have DEFERRED_PERCENT, 8.1M have SERVICED_PRODUCT_NUM
- **BUT** these contract rows come from `JE_SOURCE = 'Receivables'`, `JE_CATEGORY = 'Sales Invoices'` — i.e., AR invoice data, NOT RMC revenue recognition
- **`Revenue Management` JE_SOURCE**: Only 18 rows total (all from Fluke Poland/Europe, FEB-25 and MAY-24 periods), with JE_CATEGORY = `Revenue Contract`. These are the only true RMC-sourced rows, and they have NO contract detail columns populated (all NULL for CONTRACT_START_DATE, CONTRACT_END_DATE, CONTRACT_DURATION, DEFERRED_PERCENT, SERVICED_PRODUCT_NUM)
- **No RMC/SMC/subscription tables** exist in Silver or Bronze (searched `*rmc*`, `*subscri*`, `*smc*`)
- **No JE_SOURCE** with 'RMC', 'subscri', 'contract', or 'deferred' keywords (0 rows)
- **Conclusion**: RMC subscription revenue data is essentially NOT in UBI. The 18 "Revenue Management" rows are a tiny fraction with no detail. A new stream is definitively required.

## Validation Query Script
- `C:\Users\tmanyang\OneDrive - Fortive\Projects\UBI\CPQ - SMC and RMC\check_rmc_in_factrevenue.py`

## Next Steps
1. ~~Phase 0: Validate RMC data in FactRevenue~~ **DONE** — confirmed NOT present
2. ~~Miro board for stakeholder walkthrough~~ **DONE** — 8 canvases, 17 artifacts (2026-04-29)
3. **Create frames on Miro board** — group related items into 8 frames with consistent sizing
4. Walk stakeholders through Miro board — confirm hybrid approach
5. Confirm ARR definition with Kerry/Darby
6. Resolve blockers: OIC/API access (Kerry/IT), source table list (Kerry/Darby), product mapping (Kristen)
7. Produce STM (Source-to-Target Mapping)
8. Begin Phase 1: Bronze extraction
