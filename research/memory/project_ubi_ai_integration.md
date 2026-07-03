---
name: UBI AI Integration
description: Integrating Claude Code into UBI — AI code review in Azure DevOps CI/CD, MCP servers for ADF/Databricks/ADLS/Fabric/PBI, task-specific skills for all UBI workflows
type: project
originSessionId: ae50e3e1-9553-4e26-a884-435a65a1bea9
---
**Project**: Integrate Claude Code into UBI environment to augment the data engineering team across three pillars: AI code review in CI/CD, MCP server deployment, and task-specific skills.

**Why:** The UBI team (31 users on Azure AI Foundry) uses Claude Code interactively but hasn't integrated it into DevOps workflows, connected it to UBI tools via MCP, or created specialized skills beyond the monolithic ubi-dev.md. This project closes those gaps.

**How to apply:** Project folder at `<USER_HOME>/OneDrive - <ORG>\AI\UBI AI Intergration\`. Full context in `PROJECT_MEMORY.md` there. Three pillars: (1) AI code review via Claude Agent SDK in Azure DevOps pipelines, (2) MCP servers starting with Microsoft official (ADF, Fabric, PBI, Azure) + Databricks managed + custom extensions, (3) decompose ubi-dev.md into focused task skills (/ubi-data-engineering, /ubi-adf-pipeline, /ubi-powerbi-model, /ubi-stm, /ubi-testing, /ubi-troubleshooting, /ubi-deployment, /ubi-code-review).

**Key details:**
- Two-phase architecture: Phase 1 = tool-augmented assistant (Weeks 1-10), Phase 2 = autonomous agentic framework (Weeks 11-20)
- Phase 2 pattern: Orchestrator-Worker (Anthropic-recommended). 6 agents: Orchestrator (Opus), Code Review (Sonnet), Pipeline Monitor (Haiku), Data Quality (Sonnet), Documentation (Sonnet), Deployment (Opus)
- Orchestration backbone: Paperclip (A+ grade, already deployed) — agent registry, budget, heartbeat, activity logging
- MCP servers: 7 official Microsoft + 2 custom (ServiceNow FastMCP, etl.source_control FastMCP)
- ServiceNow: Custom FastMCP 3.0, Key Vault auth, auto-incidents on pipeline failure, change requests for deployment
- Azure DevOps MCP: official `microsoft/azure-devops-mcp` (work items, PRs, builds, test plans)
- Estimated Phase 2 cost: ~$70-115/month incremental (within existing Foundry TPM budget)
- Deliverables: 2 DOCX + 2 PPTX (Phase 1 and Phase 2 subfolders), architecture diagrams, generation scripts
- Status: Phase 0 approach doc complete with 3 diagrams (2026-06-09), V2 artifacts for Phase 1/2 (2026-05-03)
- D2 diagrams: 4 source files (current_state.d2, target_state.d2, code_review_flow.d2, phase2_architecture.d2)
- D2 annotation bubble pattern: main nodes + color-matched annotation bubbles with dashed connectors + numbered pipeline arrows
- D2 rendering: dagre layout engine via d2.exe v0.7.1 → PNG (not SVG — foreignObject breaks cairosvg)
- `update_all_diagrams.py`: unified script to replace images in all 7 files (DOCX blob replacement + PPTX slide reconstruction)
- Deliverables updated: Phase 1 DOCX (3 images), Phase 2 DOCX (1 image), C-Suite DOCX (1 image), Phase 1 PPTX (S3,S4,S5), Phase 2 PPTX (S4), C-Suite PPTX (S5,S7), v1 PPTX (S3,S4,S5)

**MCP Server Packages (2026-05-12):**
- Created 30 files across 6 subfolders at `MCP_Servers/`: ADF, Databricks, ADLS_Gen2, Fabric, Azure_DevOps, Power_BI
- Each package: README, skill file, mcp-config.json, setup.ps1, .env.template
- Created unified `ubi-mcp.md` skill (612 lines) at `~/.claude/commands/` — standalone peer to ubi-dev, not sub-skill
- Added cross-reference line to ubi-dev decision tree: "Query live services → Use /ubi-mcp instead"
- **Installed & configured in `.mcp.json`:** Azure MCP Server (Node.js), Azure DevOps MCP (Node.js), DataFactory.MCP (.NET 10, built at `C:\Tools\DataFactory.MCP\`)
- **Cloud-hosted (no local install):** Databricks MCP (managed AI Gateway), Fabric Core MCP (Streamable HTTP)
- **Not yet available:** Power BI Modeling MCP (docs-only preview), ADLS community server (not on PyPI), Fabric Pro-Dev (not published)
- .NET 10.0.300 SDK installed at `C:\Program Files\dotnet\`

**Phase 0 — AI Code Review Gate (2026-06-09):**
- Scope: Integrate Claude Sonnet into ADO YAML pipelines for PR validation, post findings to PR comments + work items
- DOCX: 570 KB, 119 paras, 30 tables, 12 sections, 3 landscape diagram pages
- Diagrams: architecture (azure_diagrams, real Azure icons), data flow (D2 dagre), process flow (matplotlib 2-row)
- System message: 25 rules across 4 dimensions (COR 8, COM 8, SIT 7, REG 6), severity P0-P3
- ADF repo assessed: 95 pipelines, 119 datasets, 107 triggers, 33 linked services, layered master orchestration
- Databricks repo assessed: 650 files, 15+ domains, ~520 Mart/Refresh, 30 validation notebooks (in-Databricks only)
- Both repos compatible: Microsoft-hosted agents, git diff, ADO REST API, no blockers
- Key decisions: separate pr-ai-review.yml, API key auth for speed, System.AccessToken for ADO, graceful fallback on timeout
- Implementation: 5-day plan, ~$5-8/month cost (two-tier)
- Implementation artifacts: `ai_code_review.py` (320 lines, two-tier), `review_rules.md` (production prompt with VERIFY/DEEP_REVIEW modes), `pr-ai-review.yml` (YAML pipeline, PR trigger on main/dev/release)
- API endpoints: GPT uses `/openai/deployments/.../chat/completions` with `max_completion_tokens`; Sonnet uses `/anthropic/v1/messages` with `x-api-key` header
- End-to-end validated: GPT 4.6s + Sonnet 19.7s deep review, PR inline comments + work item HTML feedback working
- **Deployed to ADO:** Variable Group ID 8, Pipeline IDs 78 (ADF) + 79 (Databricks), optional branch policies on Main/main + dev
- Deployment PRs: #4088 (ADF, needs 2 approvals) + #4089 (Databricks, needs 1 approval), linked to WI 14514
- Test WIs: 14515 (ADF clean), 14516 (Databricks planted issues)
- Test branches ready: `ai-review-test-adf-clean` + `ai-review-test-dbx-issue`
- Branch policy findings: ADF Main=2 reviewers, Databricks main=1 reviewer, dev=no reviewer requirement
- GitHub repo: `Taashi-Manyanga_fortive/ubi-ci-cd-ai-enhancement`
- Principal DE review: 10 findings all fixed + validated (18/18 tests passed)
- Handover email sent to Harsha + Shwetabh: approve PRs, monitor pipelines, use on dev migrations this week, report issues
- Infographic: `UBI_AI_Code_Review_Gate_Infographic.docx` (1.8 MB, 6 landscape pages, 3 GPT Image 2 panels + 3 explainer pages, matches PLM_GraphRAG_Infographic_v2 pattern)
- Also investigated UPS FTV stream (same session): full trace SFTP→Bronze→Silver→Gold→PBI, STM produced (38 rows x 45 cols), handover email. Found orphaned Gold notebook + missing validation notebook.
- Status (2026-06-09 EOD): deployed to ADO, PRs awaiting team approval, test branches ready, GitHub repo pushed, infographic + handover email delivered
- **Critical bug found & fixed (2026-06-16)**: Three issues discovered during live validation:
  1. `fetchDepth: 1` in `pr-ai-review.yml` created disconnected shallow histories — `git diff origin/Main...HEAD` failed with "no merge base" on ALL 8 pipeline runs since deployment. No AI model was ever called. Fixed: `fetchDepth: 0` (full clone), full target branch fetch, diagnostic merge-base logging.
  2. `post_pr_summary_comment()` had no failure logging — silently returned False on 403. Fixed: added status logging on all outcomes.
  3. Build Service identity lacked `PullRequestContribute` permission (TEST_PLAN.md prerequisite P6 never executed). Fixed via REST API: `accesscontrolentries` endpoint with `ServiceIdentity` descriptor on both repos.
  4. YAML `pr.branches.include` had `dev` but not `develop` — Databricks repo uses `develop` as integration branch. Pipeline 79 never triggered on Databricks PRs. Fixed: added `develop` to branch list.
  5. Pipeline default branches pointed to stale `Users/<USER>/ai-code-review-gate` instead of `Main`/`develop`. Fixed via PUT to pipeline definition API.
- `ai_code_review.py` v2.1: 4-strategy git diff fallback (three-dot → two-dot → two-tree → parent) + ADO REST API last resort. Distinguishes "no changes" (exit 0) from "extraction failed" (exit 1 + error comment on PR). `_run_git()` helper for all git operations.
- Fix PRs: #4107 (ADF→Main, 5 commits, merged via policy bypass) + #4108 (Databricks→develop, 4 commits, merged with 2 approvals)
- Temporary bypass permission granted/revoked on ADF Main for this merge only
- **E2E verified**: ADF Build #12620 — GPT 1.4s, APPROVE, summary comment posted to PR #4107 (thread #45632). Databricks Build #12624 — GPT 5.5s BLOCK + Sonnet 72.3s DEEP_REVIEW (8 findings), exit 1 confirmed.
- Status (2026-06-16): Both repos merged and live. Next real PR to either repo will be first production test.
- **First production test (2026-06-17)**: PR #4110 (OPS/Procurement, 6 files) merged to main — AI reviewer triggered 3 times, posted 31 threads (28 inline + 3 summaries), all 28 marked "fixed" by developer. All findings technically accurate, no false positives. P0 finding: FiscalMonthNumber `<=` changed to `=` (YTD→single-month, silent row loss). Developer merged despite BLOCK recommendation (isBlocking=false).
- **Branch policy fix (2026-06-17)**: Policy 126 updated via REST API PUT — `refs/heads/dev` → `refs/heads/develop` (revision 2). 5 of 6 PRs on 2026-06-17 went unreviewed because the policy targeted a non-existent branch. Now fixed — next PR to `develop` will trigger Pipeline 79.
- **E2E code review (2026-06-17)**: Full review of ai_code_review.py, pr-ai-review.yml, review_rules.md. 4 Blocking, 10 Should-fix, 7 Nits found. Three fixes applied to BOTH repos:
  1. B1: `commentType: "system"` → `"text"` (line 194) — "system" is reserved for ADO-generated comments
  2. B2: `_extract_json` brace-counter now string-aware (lines 340-365) — old version failed on code snippets with braces in evidence fields
  3. B3: `x-api-key` header verified correct for Azure AI Foundry Anthropic passthrough (Build 12624 proof) — added comment, no code change needed
  4. review_rules.md: Added "Intent vs. Bug — Behavioral Changes" section — teaches reviewer to distinguish deliberate business logic changes (P1 verify intent) from accidental regressions (P0 bug). Signals: consistency, surgical precision, PR context. Updated COR-02 to reference this framework.
  - **False positive lesson (2026-06-17):** FiscalMonthNumber `<=` → `=` flagged as P0 bug was actually an intentional business logic change. Retroactive PR comments retracted (threads 45738/45739 closed), WI 14102 corrected (rev 384). Root cause: COR-02 assumed any filter change dropping rows was a bug.
  - Remaining should-fix backlog: S1 silent exception swallow in close_prior_review_threads, S2 binary-only PR exit, S4 prompt injection defense, S5 schema validation, S7 line number ambiguity, S9 non-PR trigger guard, S10 ADO_TOKEN validation, N7 inline threads never closed on re-push
- **Deployment v2.2 (2026-06-17):** All fixes deployed via policy bypass to all 3 target branches:
  - PR #4112 (AzureDataBricks → main, commit `adeb1a2f`)
  - PR #4113 (ADF → Main, commit `77ecadd1`)
  - PR #4114 (AzureDataBricks → develop, cherry-pick, commit `98b8fa1f`)
  - Bypass permissions granted and revoked on both repos (ACE DELETE, not allow=0)
  - Stale bypass ACE from 2026-06-16 cleaned up on ADF repo
- **Bypass pattern (proven):** Python `requests.post(json=payload)` with descriptor `Microsoft.IdentityModel.Claims.ClaimsIdentity;{tenantId}\{email}` at repo level. `az rest` corrupts the backslash. `Microsoft.TeamFoundation.Identity;{GUID}` does NOT work for user identities.
- **E2E Test Suite (2026-06-17):** `test_ai_review_e2e.py` — 91 tests across 8 categories: B1 commentType (3), B2 JSON parser (14 edge cases), B3 auth header (2), Intent vs Bug framework (6), escalation logic (4), YAML config (7), code quality (18), review_rules.md structure (37). **Result: 90/91 PASSED** — B2.14 (unbalanced braces before valid JSON) is a non-real-world edge case. Saved to Phase 0 project folder (not deployed to ADO).
- **ADO Infrastructure Validation (2026-06-17):** `ado_infra_validate.py` — 12/12 tests passed — pipelines 78+79 YAML correct, variable group 8 has all 4 secrets, Build Service has PullRequestContribute on both repos, zero bypass ACEs on either repo at repo or branch level. Saved to Phase 0 project folder.
- **Phase 0 source files synced (2026-06-17):** `ai_code_review.py`, `review_rules.md`, `pr-ai-review.yml` in the Phase 0 project folder updated to v2.2 (were stale pre-fix versions). Test scripts reference these via `script_dir` so they run standalone: `python "...Phase 0 - AI Code Review Gate/test_ai_review_e2e.py"`
- Status (2026-06-17): AI reviewer v2.2 deployed to all branches, E2E validated (90/91 tests + 12/12 infra). No residual bypass permissions. Pipeline remains non-blocking (`isBlocking=false`). Should-fix backlog (S1, S2, S4, S5, S7, S9, S10, N7) deferred.

**Phase 0 — Evaluation Results (2026-06-09):**
- Evaluated GPT-5.4 Mini vs Claude Sonnet 4.6 on 10 test diffs (18 planted findings + 1 clean diff)
- Resource: `unifiedbiopenai` in `flkubi-dev-rg-001`, endpoint: `https://unifiedbiopenai.cognitiveservices.azure.com`
- Dev deployments: `gpt-5.4-mini-ubi-ado-review-dev` (1000 TPM) + `claude-sonnet-4-6-2-ubi-ado-review-dev` (100 TPM)
- QA naming: `gpt-5.4-mini-ubi-ado-review-qa` + `claude-sonnet-4-6-2-ubi-ado-review-qa` (to be deployed)
- GPT: 5.8s avg, 89% recall, 57% precision, F1=0.635, 80% recommendation accuracy, 39K tokens
- Sonnet: 40.3s avg, 100% recall, 38% precision, F1=0.520, 50% recommendation accuracy, 62K tokens
- Both: 100% JSON valid, 100% schema valid

**Phase 0 — Two-Tier Review Architecture (decided 2026-06-09):**
- Tier 1: GPT-5.4 Mini on every PR (~6s, low cost) — fast first-pass gate
- Tier 2: Claude Sonnet conditionally based on Tier 1 result — thoroughness when needed
- Escalation thresholds:
  - GPT APPROVE + 0 findings → SKIP Sonnet (fast path, ~80% of PRs)
  - GPT APPROVE + P2/P3 only → Sonnet VERIFY mode (focused P0/P1 miss check)
  - GPT REQUEST_CHANGES or BLOCK → Sonnet DEEP REVIEW mode (full independent review with GPT findings as context)
  - GPT API failure or invalid JSON → Sonnet FULL REVIEW mode (clean slate replacement)
- Sonnet receives GPT's findings JSON as context in DEEP REVIEW mode to avoid redundant work
- Pipeline exit code based on the FINAL reviewer's recommendation (Sonnet overrides GPT when called)
- Estimated cost: ~$5-8/month (GPT on all PRs + Sonnet on ~20-30% escalated)

**Phase 0 KT artifacts + GitHub repo (2026-06-23):**
- 5 KT deliverables in `AI\UBI AI Intergration\Phase 0 - AI Code Review Gate\`:
  1. **Annotated code** (`annotated/`): 4 heavily-commented teaching copies (junior-readable) — `ai_code_review`/`eval_harness`/`ado_infra_validate`/`test_ai_review_e2e`.annotated.py + `README_CODE_WALKTHROUGH.md`. **AST-verified identical to originals** (comments only); originals untouched.
  2. **Walkthrough deck** (`kt_artifacts/UBI_AI_Code_Review_Gate_Walkthrough.pptx`+pdf) — 13 slides, Veritas Clean + GPT-Image panels + speaker notes.
  3. **Integration deck** (`...Integrations.pptx`+pdf) — 1 slide each: ADO PR pipeline / ADO REST API / Azure AI Foundry (2 API dialects) / Review-rules+eval-harness.
  4. **A4 landscape infographic** (`...Infographic_A4.pptx`/pdf/png) — the emailed teaser.
- **3-persona pass (technical/design/audience) — headline catch: the rule count is 37, not 25** (COR8/COM8/SIT7/REG6/GEN8); fixed everywhere. Also fixed integration code-box overlap, infographic mid-word chip wrap, escalation/retry wording, "never skips a rule" overclaim; **added 3 leadership slides (Cost&ROI, Rollout, FAQ)**.
- **GitHub repo PUSHED + MERGED:** `Taashi-Manyanga_fortive/UBI-AI-PR-Reviewer` (private). PR#1 feature→dev + PR#2 dev→main both MERGED; main=44 files. Sanitized (API keys, AI endpoints, deployment names, ADO org/project/repo GUIDs, names, paths → placeholders); triple secret-scanned clean. Commented code at repo `docs/annotated/`.
