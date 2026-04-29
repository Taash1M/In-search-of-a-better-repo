# Memory Index

## Project Topic Files
- [Customer MDM](project_customer_mdm.md) — 5-phase matching pipeline, CRM+EBS dedup, all phases production complete (2026-03-18)
- [AI Use Case Builder](project_ai_use_case_builder.md) — v2.0, 21 skill files all A+ grade, comprehensive quality upgrade complete (2026-04-07)
- [Team AI Enablement](project_team_ai_enablement.md) — 35+ users, 5 nodes, AAD auth live, ETL v3, Miro board with 15 diagrams + 5 Azure-icon PNGs + 5 D2 SVGs (2026-04-28)
- [Skill Framework](project_skill_framework.md) — 40 skills (was 37), +3 new (qa-session, github-triage, ubiquitous-language), 6 patterns extracted, 5 frontmatter fixes (2026-04-16)
- [Skill Evaluation](project_skill_evaluation.md) — mattpocock/skills + Cocoon-AI reviews, semantic colors, Skill Judge revised: azure-diagrams A+ (112), docx-beautify A+ (112), ubi-dev A (110), pptx A (106) — D5 re-scored per no-split policy (2026-04-17)
- [Daily Report](project_daily_report.md) — Weekly status for 8 projects, DOCX close-out + Excel carry-forward
- [UBI Gold Graph](project_ubi_gold_graph.md) — Neo4j knowledge graph from 431 Gold layer tables, Fabric Lakehouse
- [AI Next Steps Plan](project_ai_next_steps.md) — 6-slide C-Suite deck, 7 AI decisions + Steering Committee, 3 versions + C-Suite email DOCX (Apr 24), meeting cadences (2026-04-24)
- [Presentation Beautification](project_pptx_beautify.md) — python-pptx skill; 2 design systems: Bold Signal Light (dark/navy) + Veritas Clean (white/minimal), dashed borders, 3-stage QA (2026-04-21)
- [LLM Gateway Usage Tracking](project_llm_usage_tracking.md) — DuckDB on VM, 5 gateways, 13 Delta tables, .pbip report (6 pages), AAD user tracking live (diagnostic+dim_aad_users), 5 models incl. Claude Code, 14 relationships (2026-04-29)
- [Phase 2 Agentic Usage Tracking](project_phase2_agentic.md) — 4-component agentic AI layer, plan v2 complete, 30-slide PPTX delivered (2026-04-14)
- [Paperclip Orchestration](project_paperclip.md) — Multi-agent orchestration skill, A+ grade, 5 modules, cherry-picked from paperclipai/paperclip
- [MSIS 511 MOOC Presentation](project_mooc_presentation.md) — v3 FINAL: 16 slides (12 main + 4 appendix), 551 shapes, 8 charts, 3-stage QA passed (2026-04-21)
- [MSIS 579 Write-Up](project_579_writeup.md) — Two-pass case write-up workflow (v1→PhD review→v2), JTBD framework, seed for generic write-up skill
- [RAG Skills](project_rag_skills.md) — doc-intelligence (3-tier) + rag-multimodal (RAGAS eval + hybrid tuning), 3 repos reviewed, A+ grade (2026-04-07)
- [AI BI Tool](project_ai_bi_tool.md) — Multi-agent BI tool, 8 phases + 3-wave hardening (38 fixes), 386 tests/80% cov, 8 DOCX + 4 PPTX, GA-ready (2026-04-13)
- [Alex B Fortive GL](project_alex_b_fortive_gl.md) — Fortive GL (15 entities, was 2): full pipeline research, 2 options, handover DOCX + 32-account mapping + entity 8650 context (2026-04-22)
- [Graphify Skill](project_graphify.md) — Knowledge graph skill based on safishamsi/graphify repo, project dir: Claude code\graphify (2026-04-06)
- [Document Extraction Skill](project_doc_extract.md) — Unified doc-extract skill (ContextGem+RAG-Anything+agentic-doc), B+ 104/120 (2026-04-07)
- [PLM Drawing Extraction](project_plm_drawing_extraction.md) — Technical validation: 18/19 drawings, 94% title block accuracy, ContextGem vision routing learnings (2026-04-07)
- [Master Sync Repo](project_sync_repo.md) — GitHub sync repo, 3 scripts (hook+sync+push), 52 skills, MCPs, schannel SSL fix (2026-04-11)
- [Sandbox Logic Apps](project_sandbox_logic_apps.md) — 2 dynamic Logic Apps: sharepoint-copy (SP→ADLS) + api-to-adls (REST→ADLS), parameterized HTTP triggers, run_ID hierarchy (2026-04-08)
- [EM Leadership Forum](project_leadership_forum.md) — 29-slide deck, hybrid slide (scorecard+agents), 7-section stamps on 25 slides, Bold Signal Light design (2026-04-17)
- [Q1 Start Deck](project_q1_start_deck.md) — Q1 Summary + Q2-Q4 Upcoming (donut chart, 11 initiative cards, Fabric callout), 3-stage QA passed (2026-04-10)
- [PBI Semantic MCP](project_pbi_mcp.md) — FastMCP server for UBI PBI models, Phase 1 complete, metadata layer integrated into AI BI Tool (2026-04-11)
- [Obsidian SecondBrain](project_obsidian.md) — Obsidian vault as Claude's persistent second brain, auto-logging hook, CLAUDE.md read/write instructions, session logs, MCP npx.cmd fix (2026-04-17)
- [CPQ SMC RMC](project_cpq_smc_rmc.md) — Oracle CPQ/SMC/RMC into UBI, Miro board (8 canvases, 17 artifacts), hybrid arch designed, 3 ER diagrams, Phase 0 ready (2026-04-29)
- [Miro MCP](project_miro_mcp.md) — Official MCP (OAuth 2.1), 13 tools, 2 boards (Claude Code Deployment + CPQ SMC RMC), artifacts at AI\Miro\, no image upload (2026-04-29)

## UBI Platform Key Facts
- **Repos**: AzureDataBricks (`C:\Users\tmanyang\AzureDataBricks`), ADF (`C:\Users\tmanyang\ADF`), Power BI UBI Curated Datasets
- **Deliverables folder**: `C:\Users\tmanyang\Claude\deliverebles\`
- **Backup folder**: `C:\Users\tmanyang\OneDrive - Fortive\Claude code\`
- **Skill file**: `C:\Users\adm-tmanyang\.claude\commands\ubi-dev.md`
- **STM format**: 45 columns, 7 stages (Source, Landing, Bronze, Silver, Gold DB, Gold ADLS, PBI)
- Landing = Bronze in UBI architecture (no separate raw zone)
- **BigQuery GCP project**: `cobalt-cider-279717`, service account key in Key Vault `flkubi-kv-prd` (secret: `Google-Fluke-ServiceAccount-Json`)

## Feedback
- [PBI encoding & modelExtensions](feedback_pbi_underlyingtype.md) — underlyingType, modelExtensions inside config, Fabric DirectQuery M folding (no computed cols), Fabric shortcuts don't auto-sync Delta schema, ambiguous paths from bidirectional cross-filter, schema_mode="overwrite"
- [Auto-invoke skills](feedback_skill_invocation.md) — Always activate skills proactively, FYI user as you go; don't ask permission first
- [RBAC via REST API](feedback_rbac_rest_api.md) — az role assignment create fails on Fluke AI sub; always use REST API PUT
- [Arrow direction in docs](feedback_arrow_direction.md) — arrows point TOWARD the other section, not both same direction
- [Diagram quality gate](feedback_diagram_quality_gate.md) — validate every diagram for missing icons, overlap, distortion before embedding; fix+regenerate loop
- [PPTX layout discipline](feedback_pptx_layout.md) — 3-stage QA, safe zone, add_picture_fit(), D2 grid-rows, Veritas clean header/footer, dashed border XML technique
- [Diagram visual quality standard](feedback_diagram_visual_standard.md) — Veritas-derived: node shape variety, bracket connectors, numbered timelines, color restraint, 2 design systems (Bold Signal Light + Veritas Clean)
- [Git push SSL fix](feedback_git_push_ssl.md) — use schannel SSL backend + bundle workflow for large pushes through corporate proxy
- [O365 apps user context](feedback_o365_user.md) — open O365 apps as tmanyang, not adm-tmanyang
- [Keep skills intact](feedback_skill_no_split.md) — no progressive disclosure splits; decision trees at top instead; only split if context limits hit

## References
- [Outlook Automation Pattern](reference_outlook_automation.md) — COM cross-session trick (explorer.exe), DASL filters, Edge PDF, daily scan + full export
- [Daily Access Request Workflow](reference_access_request_workflow.md) — 3-step repeatable: scan inbox → identify new requests → update DOCX (16 requests, 19 pending seats as of Apr 24)
- [cairosvg Windows Setup](reference_cairosvg_windows.md) — MSYS2 64-bit DLLs for cairosvg on Windows
- [BigQuery / GCP Access](reference_bigquery_gcp.md) — cobalt-cider-279717, service account in flkubi-kv-prd, browser login via taashi.manyanga@gmail.com
- [Miro Artifacts Folder](reference_miro_artifacts.md) — `AI\Miro\` for board assets (PNGs/SVGs), drag-drop since MCP has no image upload

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
- **Auth (legacy)**: `ANTHROPIC_FOUNDRY_API_KEY` + `CLAUDE_CODE_USE_FOUNDRY=1`
- **Auth (live for 4+ users)**: AAD via `az login` (no API key) — populates objectId in diagnostic logs
- **Diagnostic logging**: `RequestResponse` category enabled on AI Services (2026-04-24), NDJSON → `flkaienablement` storage
- **ETL v3**: 939 lines, processes LiteLLM logs + diagnostic logs, `sync_aad_users.py` pre-seeds 35 users
- **VM scripts**: `/home/azureuser/{llm_usage_etl.py, sync_aad_users.py, infra_health_check.py}`
- **VM Azure CLI**: v2.85.0 installed (2026-04-27)
- Billing: Fluke AI ML Technology subscription (Azure Marketplace)

## Claude Code Hooks (5 scripts)
- **Location**: `C:\Users\adm-tmanyang\.claude\hooks\`
- **secret-scanner.py**: PreToolUse on Bash, blocks git commits with secrets (30+ patterns)
- **dangerous-command-blocker.py**: PreToolUse on Bash, 3-level protection
- **change-logger.py**: PostToolUse on Edit/Write/MultiEdit/Bash, logs to `~/.claude/critical_log_changes.csv`
- **repo-sync.py**: PostToolUse on Edit/Write/MultiEdit, auto-copies skills/hooks/memory/MCPs/settings to sync repo (wired 2026-04-11). Redacts secrets in settings.json. Does NOT commit/push.
- **obsidian-session-logger.py**: PostToolUse on Edit/Write/MultiEdit/Bash, appends tool activity to Obsidian vault `1-Projects/Claude Sessions/YYYY-MM-DD.md` (added 2026-04-17). Self-protecting (skips own session file). Read-only commands filtered.
- **CLAUDE.md**: `~/.claude/CLAUDE.md` — instructs Claude to read Obsidian session logs on start, write decisions/findings during sessions, summarize at end
- **Python path**: `python` not `python3` (Windows, Python 3.12)

## MCP Servers (2 active — `~/.claude/.mcp.json`)
- **context7**: `@upstash/context7-mcp@latest` — library/framework documentation lookup
- **obsidian**: `@bitbonsai/mcpvault@latest` v0.11.0 — direct file access to Obsidian vault at `C:\Users\tmanyang\OneDrive - Fortive\Claude code\Obsidian` (no Obsidian app needed)

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
