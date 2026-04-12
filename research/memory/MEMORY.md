# Memory Index

## Project Topic Files
- [Customer MDM](project_customer_mdm.md) — 5-phase matching pipeline, CRM+EBS dedup, all phases production complete (2026-03-18)
- [AI Use Case Builder](project_ai_use_case_builder.md) — v2.0, 21 skill files all A+ grade, comprehensive quality upgrade complete (2026-04-07)
- [Team AI Enablement](project_team_ai_enablement.md) — Claude Code for 27 users, 4 nodes (3 new node2 users 2026-04-07), Azure AI Foundry, LLM Gateway tracking
- [Skill Framework](project_skill_framework.md) — 17 active skills (9 standalone + 5 AI UCB companions + 1 KG + 1 doc-extract + 1 diagram), powerpoint-create enhanced (2026-04-10)
- [Daily Report](project_daily_report.md) — Weekly status for 8 projects, DOCX close-out + Excel carry-forward
- [UBI Gold Graph](project_ubi_gold_graph.md) — Neo4j knowledge graph from 431 Gold layer tables, Fabric Lakehouse
- [Presentation Beautification](project_pptx_beautify.md) — python-pptx skill with presets/palettes, mirrors docx_beautify; powerpoint-create.md enhanced with 3-stage QA (2026-04-10)
- [LLM Gateway Usage Tracking](project_llm_usage_tracking.md) — DuckDB on VM, HNS enabled, PBI v4 direct Delta, 12h cron
- [Paperclip Orchestration](project_paperclip.md) — Multi-agent orchestration skill, A+ grade, 5 modules, cherry-picked from paperclipai/paperclip
- [MSIS 579 Write-Up](project_579_writeup.md) — Two-pass case write-up workflow (v1→PhD review→v2), JTBD framework, seed for generic write-up skill
- [RAG Skills](project_rag_skills.md) — doc-intelligence (3-tier) + rag-multimodal (RAGAS eval + hybrid tuning), 3 repos reviewed, A+ grade (2026-04-07)
- [AI BI Tool](project_ai_bi_tool.md) — Multi-agent BI tool, 8 phases + MCP metadata integration, 190 tests, 4 DOCX + 3 PPTX, 15 diagrams (2026-04-11)
- [Alex B Fortive GL](project_alex_b_fortive_gl.md) — Fortive corporate GL (co 11/13) not in UBI pipeline; Gold view SQL prepared; DOCX report delivered (2026-04-06)
- [Graphify Skill](project_graphify.md) — Knowledge graph skill based on safishamsi/graphify repo, project dir: Claude code\graphify (2026-04-06)
- [Document Extraction Skill](project_doc_extract.md) — Unified doc-extract skill (ContextGem+RAG-Anything+agentic-doc), B+ 104/120 (2026-04-07)
- [PLM Drawing Extraction](project_plm_drawing_extraction.md) — Technical validation: 18/19 drawings, 94% title block accuracy, ContextGem vision routing learnings (2026-04-07)
- [Master Sync Repo](project_sync_repo.md) — GitHub sync repo, 3 scripts (hook+sync+push), 52 skills, MCPs, schannel SSL fix (2026-04-11)
- [Sandbox Logic Apps](project_sandbox_logic_apps.md) — 2 dynamic Logic Apps: sharepoint-copy (SP→ADLS) + api-to-adls (REST→ADLS), parameterized HTTP triggers, run_ID hierarchy (2026-04-08)
- [EM Leadership Forum](project_leadership_forum.md) — Bold Signal Light design, 3 PPTX + 3 HTML (animated), QA R2 complete, pending user review (2026-04-10)
- [Q1 Start Deck](project_q1_start_deck.md) — Q1 Summary + Q2-Q4 Upcoming (donut chart, 11 initiative cards, Fabric callout), 3-stage QA passed (2026-04-10)
- [PBI Semantic MCP](project_pbi_mcp.md) — FastMCP server for UBI PBI models, Phase 1 complete, metadata layer integrated into AI BI Tool (2026-04-11)
- [Obsidian SecondBrain](project_obsidian.md) — Obsidian vault, PARA method, OneDrive-synced, community plugins configured (2026-04-11)

## UBI Platform Key Facts
- **Repos**: AzureDataBricks (`C:\Users\tmanyang\AzureDataBricks`), ADF (`C:\Users\tmanyang\ADF`), Power BI UBI Curated Datasets
- **Deliverables folder**: `C:\Users\tmanyang\Claude\deliverebles\`
- **Backup folder**: `C:\Users\tmanyang\OneDrive - Fortive\Claude code\`
- **Skill file**: `C:\Users\adm-tmanyang\.claude\commands\ubi-dev.md`
- **STM format**: 45 columns, 7 stages (Source, Landing, Bronze, Silver, Gold DB, Gold ADLS, PBI)
- Landing = Bronze in UBI architecture (no separate raw zone)

## Feedback
- [PBI underlyingType encoding](feedback_pbi_underlyingtype.md) — 261=Double, 518=DateTime; chart axes use type for formatting
- [Auto-invoke skills](feedback_skill_invocation.md) — Always activate skills proactively, FYI user as you go; don't ask permission first
- [RBAC via REST API](feedback_rbac_rest_api.md) — az role assignment create fails on Fluke AI sub; always use REST API PUT
- [Arrow direction in docs](feedback_arrow_direction.md) — arrows point TOWARD the other section, not both same direction
- [Diagram quality gate](feedback_diagram_quality_gate.md) — validate every diagram for missing icons, overlap, distortion before embedding; fix+regenerate loop
- [PPTX layout discipline](feedback_pptx_layout.md) — mandatory 3-stage QA (content + programmatic layout + visual), safe zone, dynamic positioning for grids
- [Git push SSL fix](feedback_git_push_ssl.md) — use schannel SSL backend + bundle workflow for large pushes through corporate proxy

## Patterns Learned
- **Always use all-purpose clusters** for Databricks interactive/notebook work
- Oracle EBS columns use entity prefixes (OOHA=headers, OOLA=lines, MSIB=items, HCA/HCP/HCSUA=customers)
- All Oracle VARCHAR2 fields land as STRING in Bronze
- Silver layer does type casting, business logic, JOINs to ~25 dimension tables
- Gold layer creates views with business-friendly aliases (backtick-quoted in Spark SQL)
- ADLS publish is a direct mirror of Gold views in Delta format

## SO Backlog Stream Specifics
- 11 notebooks, 52 Gold views, bi-hourly refresh
- Primary source: `FLKUBI.ONT01_SALES_ORDERS_FV1` (~200+ columns)
- FactSOBacklog has ~275 columns in Silver, 184 mapped in comprehensive STM
- Key transforms: return sign logic, SalesCreditPct split, rtlRelativeAmountPct, currency conversion via cross-rate view
- Post-INSERT MERGE for HoldID assignment based on priority

## GL Investigation (INC1555542)
- Accounts 410120, 410150, 410700 incorrectly mapped as Expense instead of Revenue
- Root cause: Oracle source misconfiguration + no Silver-layer override
- Fix: CASE WHEN ACCOUNT LIKE '4%' THEN 'Revenue' in Refresh_DimGlAccount.sql
- Delivered: `C:\Users\tmanyang\OneDrive - Fortive\ADHOC\UBI\GL INC1555542\` (5 artifacts)
- GL/Revenue STM completed: 330 rows x 45 columns, 15 table groups

## Azure AI Foundry Configuration (Team — switched 2026-03-26)
- **Resource**: `flk-team-ai-enablement-ai` (East US 2)
- **Settings file**: `C:\Users\tmanyang\.claude\settings.json` (env section)
- **Models**: opus (750 TPM), sonnet (1,625 TPM), haiku (100 TPM)
- **Auth**: `ANTHROPIC_FOUNDRY_API_KEY` + `CLAUDE_CODE_USE_FOUNDRY=1`
- Billing: Fluke AI ML Technology subscription (Azure Marketplace)

## Claude Code Hooks (4 scripts)
- **Location**: `C:\Users\adm-tmanyang\.claude\hooks\`
- **secret-scanner.py**: PreToolUse on Bash, blocks git commits with secrets (30+ patterns)
- **dangerous-command-blocker.py**: PreToolUse on Bash, 3-level protection
- **change-logger.py**: PostToolUse on Edit/Write/MultiEdit/Bash, logs to `~/.claude/critical_log_changes.csv`
- **repo-sync.py**: PostToolUse on Edit/Write/MultiEdit, auto-copies skills/hooks/memory/MCPs/settings to sync repo (wired 2026-04-11). Redacts secrets in settings.json. Does NOT commit/push.
- **Python path**: `python` not `python3` (Windows, Python 3.12)

## Document Beautification Skill
- **Project dir**: `C:\Users\tmanyang\OneDrive - Fortive\Claude code\Document Beautification\`
- **Created**: 2026-03-20, **v6**: 2026-03-29
- **Files**: `docx-beautify.md` (skill), `docx_beautify.py` (module, ~2760 lines), `PROJECT_MEMORY.md`
- **Module**: 48+ functions, 4 presets, 4 palettes, diagram backends (Mermaid SVG, D2, matplotlib, cairosvg)
- **D2 CLI**: v0.7.1 at `C:\Users\tmanyang\tools\d2\d2-v0.7.1\bin\d2.exe`
- **Azure icons**: `Azure_Public_Service_Icons_V23` in project dir (V23, SVG)
- **D2 gotchas**: Forward-slash paths only, `$` triggers substitution, `|md|` blocks break on `<`
- **cairosvg**: Working (2026-04-06) — requires MSYS2 64-bit DLLs, see [cairosvg Windows Setup](reference_cairosvg_windows.md)
- **Promoted** to `~/.claude/commands/docx-beautify.md` on 2026-04-06

## SOX PCC20/PCC30 Audit Data
- **Location**: `C:\Users\tmanyang\OneDrive - Fortive\SOX\PCC20 and PCC30 Extract\`
- **File**: `latest-commits-linked-to-prs-20250715085713274` (.csv/.xlsx identical)
- 1,000 commits, Apr 4 - Jul 15 2025, 9 devs, only 9.1% linked to PRs
