---
name: UBI Gold Graph Project
description: Neo4j knowledge graph project for UBI Gold layer — 431 tables from Fabric Lakehouse, project artifacts, connection details, skill development
type: project
---

**Project**: UBI Gold Graph — build enterprise knowledge graph in Neo4j from 431 Gold layer tables in Fabric Lakehouse.

**Why:** Enable GraphRAG, lineage analysis, impact analysis, and cross-domain discovery across the full UBI data model (CRM, Orders, Inventory, Procurement, AR, Service, VOC, Finance, etc.)

**How to apply:** All artifacts go in `<USER_HOME>/OneDrive - <ORG>\AI\Neo4j\UBI Gold Graph\`. Full project memory at `PROJECT_MEMORY.md` in that folder. Read-only access to prod. Skill (`ubi-neo4j.md`) lives in commands dir with backup in project folder.

**Key details:**
- Fabric Lakehouse: `FLK_UBI_LH_GOLDS`, ID `0a252e47-a44f-4002-8d96-4cbdb8dc1951`
- Workspace: `4037a9f7-9627-4b77-a7bb-ae42bbdaf1bc`
- SQL Endpoint: `ynfggd47woteda52r4ihq5wgsi-66utoqbhsz3uxj53vzblxwxrxq.datawarehouse.fabric.microsoft.com`
- Access: Fabric REST API via Azure AD token (az CLI) + ODBC Driver 18 (INSTALLED)
- Gold view source: `AzureDataBricks\FlukeCoreGrowth\Mart\Refresh\Refresh_*_Gold.{sql,py}`
- Status: Experiment 1 Dynamic Query — E2E validated (sample 19/19 PASS, real-data-mode 17/17 PASS), ready for VS Code real data run (2026-03-27)

**Architecture Decision (2026-03-27):** ONE graph with logical domain partitioning (not multiple small graphs like PBI semantic models). Shared hub nodes (Customer 2.3M, Product 100K) connect all domains. Splitting would waste 12M+ duplicated nodes.

**Experiment 1 — Orders & Shipments Graph + LLM:**
- Notebook: `experiments/Experiment1_Orders_Shipments_Graph_LLM.ipynb` (46 cells, 9 sections)
- Generator: `experiments/create_experiment1_notebook.py`
- Docs: `experiments/Experiment1_What_Was_Built.docx`, `experiments/Experiment1_How_To_Use.docx`
- Doc generator: `experiments/create_experiment_docs.py`
- Architecture rec: `UBI_Golden_Graph_Architecture_Recommendation.docx` (create_recommendation_docx.py)
- Approach doc: `UBI_Golden_Graph_Approach_Architecture.docx` (create_approach_docx.py)
- Dual data mode: `USE_REAL_DATA` toggle — Mode A (sample, works anywhere) vs Mode B (real Gold Lakehouse via spark.table or ODBC 18)
- LLM: GPT-5-mini on personal AI Foundry (`ai-taashimanyanga3461ai913834910233`), deployments: gpt-5-mini, gpt-5, gpt-5.4-pro, o4-mini, text-embedding-3-small
- Graph: 9 node types (Customer, Product, Order, Shipment, Country, Currency, SalesAgent, Organization, Calendar), 14+ relationship types (incl. CONTAINS_PRODUCT bookings, SHIPPED_PRODUCT actuals, ORDERED_ON, SHIPPED_ON, DELIVERED_ON role-playing date edges)
- Tech: NetworkX + pyvis + openai + pandas (+ pyodbc for ODBC mode)
- ODBC Driver 18: INSTALLED and working — `Authentication=ActiveDirectoryInteractive`

**GPT-5 API Compatibility (learned 2026-03-27):**
- `max_tokens` → `max_completion_tokens` (GPT-5 requires this)
- `temperature` must be `1` (GPT-5 does not support other values)
- These are the ONLY supported parameters for GPT-5 chat completions

**Gold Lakehouse Column Name Gotchas (validated 2026-03-27):**
- `vw_DimParty_OS`: `OrganizationName` is NULL for most records — use `PartyDisplayName` instead
- `vw_DimCurrency`: Column is `[Trx Currency Code]` (with space), not `CurrencyCode`
- `vw_DimCountry.CountryCode` is numeric (not ISO) — use `ISOCountryAlpha2Code` for 2-letter codes
- `vw_DimParty_OS.CountryCode` IS ISO 2-letter — joins to `DimCountry.ISOCountryAlpha2Code`
- `vw_DimCalendar_OS`: `CalendarYearNumber` (not `CalendarYear`), `DayOfWeek` (not `CalendarDayOfWeek`)
- `vw_FactOrderDetail_LR.LineFlowStatusCode` is mostly NULL
- pandas reads integer keys as float — use `norm_key()` to strip `.0` suffix before joining
- pyvis `save_graph()` uses Windows cp1252 — must use `open(path, "w", encoding="utf-8")` for international names

**Fact Table Switch (2026-03-27):**
- SWITCHED from `vw_FactOrderDetail_LR` / `vw_FactShipmentDetail_LR` (stale, max Feb 2025)
- TO `vw_FactOrdersLeadership` / `vw_FactShipmentsLeadership` (current, has 2026 data up to today)
- These are the SAME tables used by the PBI "Orders & Shipments" semantic model
- Leadership tables are separate Delta tables in the Lakehouse (not live views of _LR despite the SQL definition)
- `_LR` pipeline stalled Feb 2025; Leadership pipeline is healthy and current
- Leadership has 122/141 cols respectively; missing `BookDate` (derive from DimCalendarBookDateKey), `LineFlowStatusCode` → `ContractStatusCode` (mostly NULL)
- `ShippingMethodName` exists but mostly NULL; `PostedDate` available as datetime

**Validated Table/Column Mapping (2026-03-27):**
- Facts: `vw_FactOrdersLeadership` (122 cols, 441K rows 2026), `vw_FactShipmentsLeadership` (141 cols, 436K rows 2026)
- Dims: `vw_DimParty_OS` (70 cols), `vw_DimProduct_OS` (67 cols), `vw_DimCountry` (26 cols), `vw_DimCurrency` (16 cols), `vw_DimCalendar_OS` (115 cols)
- Join keys: `DimPartyShippingCustomerKey` → `DimPartyKey`, `DimProductKey` → `DimProductKey`, `DimCalendarBookDateKey` format `yyyyMMdd`
- 3-step load strategy: facts filtered to year → extract referenced keys → load only matching dims via IN clause
- CONTAINS_PRODUCT edges (bookings): `line_total`, `quantity`, `unit_price`, `order_date`, `order_month`
- SHIPPED_PRODUCT edges (actuals): `shipped_amount`, `shipped_qty`, `ship_date`, `ship_month`
- Shipment nodes carry `total_shipped_amount` (accumulated from all lines)

**Bookings vs Actuals (added 2026-03-27):**
- BOOKINGS = ordered amounts from FactOrdersLeadership, by book date (DimCalendarBookDateKey). Leading signal.
- ACTUALS = shipped revenue from FactShipmentsLeadership, by ship date (DimCalendarShipDateKey). Realized revenue.
- Shipments table `NetUSDExtdAmt` = USD-normalized shipped revenue (same column name as orders)
- LLM prompt: "revenue"/"sales" → SHIPPED_PRODUCT; "bookings"/"orders" → CONTAINS_PRODUCT
- E2E validated: Feb-2026 bookings $691K vs actuals $675K across 18+ countries and 43 product families
- Key finding: USA/Canada shipped MORE than booked (clearing backlog); India/Korea booked 6-14x more than shipped

**E2E Validation (2026-03-27):** 25/25 checks PASS
- Bookings: 1,296 orders, 1,109 lines, $12.5M / $2.9M
- Actuals: 1,804 shipments, 1,070 lines, $5.9M / $1.2M
- 472 customers (100% real names), 500 products, 43 families, 268 countries
- Cross-dimensional: Customer × Country × Product × Date all working for both bookings and actuals

**Experiment 1 — Dynamic Query Capable Version (2026-03-27):**
- Standalone generator: `experiments/create_experiment1_dynamic_notebook.py` (all code inline, no exec imports)
- Notebook: `experiments/Experiment1_Dynamic_Query_Capable.ipynb` (55 cells)
- Sections 1-6 from v1 (data loading, mapping, graph building, queries, visualization)
- Sections 7-9: Dynamic query engine — GPT-5 function calling writes Python code executed against live NetworkX graph (Text2Code pattern, maps to Text2Cypher in production Neo4j)
- 11 dynamic questions including cross-dimensional bookings vs actuals
- Intermediate v2 generator: `experiments/create_experiment1v2_notebook.py` (used exec() from v1, replaced by standalone)
- E2E tests: `experiments/test_full_pipeline.py` (25/25 PASS), `experiments/test_dynamic_query.py` (15/15 PASS)

**Critical bugs fixed in generators (2026-03-27):**
- `norm_key()` NameError: function defined in customer mapping but called earlier in product mapping — moved before products section. Fixed in BOTH `create_experiment1_notebook.py` and `create_experiment1_dynamic_notebook.py`.
- `calendar_dates` NameError: only generated in sample path, not real data path — added calendar generation to real data mapper cell (derives date range from actual order/shipment dates).
- `country_currency` NameError: only defined in sample path — added derivation from order data in real data mapper (most common currency per customer country).
- **Root cause of all 3 bugs**: Sample data cells (Section 3) had NO guards — when user ran "Run All" with `USE_REAL_DATA = True`, sample cells either (a) overwrote real data or (b) were skipped but variables they defined were never created in the real data path. FIX: wrapped all 5 sample data code cells with `if USE_REAL_DATA: print("skipping") else:` guards so "Run All" is safe in both modes.
- Lesson: ANY notebook with dual data modes MUST guard EVERY sample cell, not just add a markdown warning to skip.

**Next experiments planned:**
- Exp 2: Cross-domain bridges (add CRM, VOC, Warranty)
- Exp 3: Duplication cost analysis (one vs many graphs)
- Exp 4: Real data in Neo4j (Cypher queries)
- Exp 5: Graph algorithms (PageRank, community detection)
