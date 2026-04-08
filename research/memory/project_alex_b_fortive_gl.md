---
name: Alex B Fortive GL Investigation
description: Fortive corporate GL data (companies 11, 13) traced through UBI pipeline — not available; Gold view SQL and DOCX report delivered
type: project
---

## Investigation (2026-04-06)

Alex B needs visibility into Fortive corporate accounts (companies 11, 13) — intercompany/treasury journal entries like TGA Finance (Cayman Islands) liquidation and monthly interest accruals.

### Finding
Fortive corporate GL data is **NOT** in the UBI pipeline. The Fortive Global Ledger Set is a separate Oracle ledger from Fluke ledger sets. Three Gold-layer filters also exclude: company whitelist (51 Fluke opcos), account range (LIKE '6%'), cost center (<> '0000').

**Why:** UBI extraction (Extract_Revenue_OTL.sql) only queries Fluke ledger sets. Company 13 never enters Bronze.

**How to apply:** Any future requests for Fortive corporate data require Oracle extraction expansion first. The Gold view (`vw_FactGLDetails_Flat_FTV.sql`) is prepared but blocked on Bronze data.

### Artifacts
- `C:\Users\tmanyang\OneDrive - Fortive\ADHOC\UBI\Alex B - Fortive\`
- `vw_FactGLDetails_Flat_FTV.sql` — Gold view for companies 11, 13
- `Fortive_GL_Data_Investigation_Report.docx` — 2-page investigation report
- `PROJECT_MEMORY.md` — Full project context
