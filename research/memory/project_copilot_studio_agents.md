---
name: project-copilot-studio-agents
description: "Copilot Studio agent building capability — plugin, tooling, environment config for Growth Kaizen and future agents"
metadata: 
  node_type: memory
  type: project
  originSessionId: 91bd5ecc-c992-4ed7-8213-ef549bae0522
---

## Capability: Copilot Studio Agent Building via Claude Code

Established 2026-06-02 for Growth Kaizen key account scoring, reusable for any future Copilot Studio agent.

**Why:** Sue-Anne's Kaizen team needed a custom AI agent for key account classification. Built the toolchain so we can rapidly create/modify agents programmatically.

**How to apply:** When anyone asks for a Copilot Studio agent, this stack is ready — no setup needed.

### Installed Components
- **Plugin**: `copilot-studio@skills-for-copilot-studio` v1.0.11 (user scope, auto-updates via marketplace `microsoft/skills-for-copilot-studio`)
- **VS Code Extension**: `ms-copilotstudio.vscode-copilotstudio` v1.4.37 (on `<USER>` profile)
- **LSP binary**: `<USER_HOME>/.vscode/extensions/ms-copilotstudio.vscode-copilotstudio-1.4.37-win32-x64/lspOut/LanguageServerHost.exe` — persisted as `CPS_LSP_BINARY` env var in settings.json
- **Node.js**: v22.14.0

### 31 Available Skills
Author: `new-topic`, `edit-agent`, `edit-action`, `edit-triggers`, `add-knowledge`, `add-action`, `add-adaptive-card`, `add-generative-answers`, `add-global-variable`, `add-node`, `add-other-agents`
Manage: `clone-agent`, `manage-agent`, `list-topics`, `list-kinds`, `lookup-schema`, `validate`
Test: `chat-directline`, `chat-sdk`, `chat-with-agent`, `directline-chat`, `test-auth`, `create-eval`, `create-eval-set`, `run-eval`, `run-tests-kit`, `analyze-evals`
Advisor: `detect-mode`, `int-patterns`, `int-project-context`, `int-reference`

### Environment
- **Tenant**: `0f634ac3-b39f-41a6-83ba-8f107876c692` (Fortive)
- **Dataverse**: `org2c21e028.crm.dynamics.com`
- **Auth**: Browser-based AAD via `<USER>` — tokens cache after first sign-in per session

### First Agent: Key Account Scorer (Test)
- **Agent URL**: `https://copilotstudio.microsoft.com/environments/Default-0f634ac3-b39f-41a6-83ba-8f107876c692/bots/dd919fc2-a05e-f111-a826-000d3a18ca63/overview`
- **Schema**: `cr52a_KeyAccountScorerTest`
- **Local clone**: `<USER_HOME>/OneDrive - <ORG>/Claude code/copilot-studio-agents/key-account-scorer/Key Account Scorer %28Test%29/`
- **Local project memory**: `<USER_HOME>/OneDrive - <ORG>/ADHOC/Kaizen/Growth Kaizen/PROJECT_MEMORY.md`
- **Components**: Agent instructions (EMEA 7-criteria model, 4 tiers, hybrid auto-research+confirm), ScoreAccount topic (AI research → propose → confirm/adjust → calculate), BatchScoreAccounts topic (CSV upload, auto-score C1-C4, flag C5-C7), 13 system topics
- **Scoring model source**: `Requirements/Copy_Key_Account_Scoring_Model.xlsx`
- **Pending**: Top 5 corporate priority verticals (placeholder in C4), data source connection, channel deployment
- **3 Deliverables**: Process Infographic (3pg landscape, 12 panels), Architecture (10 sections, D2 diagram), Manual Guide (17 sections, 11 screenshots)

### E2E Validation (2026-06-02) — All Passed
1. **Clone** — agent cloned from cloud to local YAML files via LSP binary
2. **Author** — created ScoreAccount (10-step) and BatchScoreAccounts (6-step) topics with triggers, questions, AI scoring nodes
3. **Validate** — 17 files, 0 errors, 0 warnings (full LSP diagnostics)
4. **Push** — synced to Copilot Studio cloud (draft), HTTP 200
5. **List** — read all 15 topics (2 custom + 13 system) with metadata extraction
6. **Edit** — updated agent.mcs.yml instructions (scoring model, thresholds, output format)
7. **Env var** — `CPS_LSP_BINARY` persisted in settings.json, auto-detected by manage-agent

### Agent v2 Update (2026-06-03) — Validated, Pushed, Published
Updated from new 103KB scoring spreadsheet (6 tabs, ~125 real scored accounts).
1. **Tier thresholds**: T1 ≥ 8.0, T2 7.1–7.99, T3 6.5–7.09, T4 < 6.5
2. **Category labels**: Revenue Value (C1,C2), Future Potential (C3), Strategic Fit (C4,C7), Relationship Strength (C5), Engagement & Risk (C6)
3. **Research integrity guardrails**: source citation, confidence labeling (Verified/Estimated/Unverified), cross-check rule, no fabrication
4. **Human-in-the-loop**: clarification questions for unclear input, won't calculate with missing data, handles contradictions
5. **Output template**: matches Setup tab format (Category, Criterion, Score, Definition, Weight, Confidence, Notes)
6. **Calibration examples**: 6 real accounts from EMEA data (BAE Systems, ADVANTEST, Framatome, BAE Marine, British Airways, John Cockerill)
7. **Tier-specific actions**: T1=dedicated coverage, T2=targeted expansion, T3=efficient coverage, T4=reactive engagement
8. **Auth settings**: `authenticationMode: None`, `authenticationTrigger: AsNeeded`, `accessControlPolicy: Any` — required for Demo Website channel
9. **Handover email**: `kaizen_agent_testing_email.html` (HTML, Outlook paste-ready)

### Agent v3 Update (2026-06-04) — Validated, Pushed, Published, Tested
Enhanced C3 (Future Potential) scoring from team doc `Future Potential Scoring Prompt for Co-Pilot including 2 examples.docx`.
1. **C3 restructured**: 3 explicit sub-criteria (Company Size: sites+geographic scope, Portfolio Alignment: Fluke product family count, Investment Activity: capital/contracts/growth)
2. **Fluke product catalog in instructions**: Industrial (Power Quality, Renewable Energy, EV Charging, Reliability, Process Instruments, Thermal Imaging, Test Tools), Calibration (Electrical, Pressure, Temperature), Networks
3. **Scoring logic**: Best-fit judgement "ALL OR MOST", 10/5/1 only, no averaging
4. **Penetration logic removed**: Old C3 used Fluke penetration (low=high); new model is purely external company profile
5. **Commercial barrier flagging**: Score normally, flag barriers in output (user decides whether to adjust) — Thales example
6. **C3 output format**: Sub-criterion summaries + Commercial Barriers + Score + Rationale (2-4 sentences)
7. **2 C3 calibration examples**: Rolls-Royce (score 10), Thales (score 10 with barrier flag)
8. **10/5/1 scoring guardrail**: Reinforced in both system instructions AND topic prompts — Sonnet was using intermediate values (8, 9)
9. **GitHub repo**: `Taashi-Manyanga_fortive/custom-copilot-scoring-agent` (private, 2 commits)
10. **DirectLine test**: Rolls-Royce PASS — C3 sub-criteria correct, all scores 10/5/1, sources cited

### Proven Workflow for New Agents (Battle-Tested Formula)
This workflow has been validated E2E twice (Jun 2 initial build + Jun 3 v2 update). It works.

1. User creates blank agent in Copilot Studio browser UI
2. User pastes the agent URL
3. Claude clones via `copilot-studio:manage-agent` (clone)
4. Claude authors topics via `copilot-studio:new-topic`
5. Claude sets instructions via `copilot-studio:edit-agent`
6. Claude adds knowledge via `copilot-studio:add-knowledge`
7. Claude validates via `copilot-studio:validate` (0 errors required)
8. Claude pushes via `copilot-studio:manage-agent` (push)
9. Claude publishes via `copilot-studio:manage-agent` (push and publish)
10. Test via Demo Website channel (requires `authenticationMode: None`) or built-in test pane
11. For iterative updates: edit YAML locally → validate → push → publish (skip clone)

**Typical cycle time**: ~30 min for a new agent from blank to published. ~15 min for updates (edit → validate → push → publish).

### Known Gotchas (Comprehensive — Updated 2026-06-03)

**Power Fx / YAML**
- Power Fx `contains()` and `toLower()` are UNSUPPORTED in Copilot Studio conditions — use `||` with exact string equality (e.g., `=Topic.X = "A" || Topic.X = "a"`)
- Power Fx is case-sensitive for string comparisons — list both cases explicitly
- YAML duplicate keys cause push failures — always validate before pushing
- Long AI prompts in `userInput` fields must be a single line (use `& " " &` for concatenation, not YAML multiline)

**Authentication & Channels**
- Demo Website channel is BLOCKED when `authenticationMode: Integrated` — must set to `None` for the demo site to work
- `accessControlPolicy: AnyUser` is INVALID — valid values are `Any`, `ChatbotReaders`, `GroupMembership`, `AnyMultiTenant`
- With `authenticationMode: Integrated`, only Teams, M365, and SharePoint channels are available
- For testing: set `authenticationMode: None` + `accessControlPolicy: Any` + `authenticationTrigger: AsNeeded`
- For production with Teams: set `authenticationMode: Integrated` + `accessControlPolicy: GroupMembership`

**Push/Pull/Publish**
- Push creates a **draft** — must publish to make changes live
- `ConcurrencyVersionMismatch` error on push = pull first to get fresh row versions, then push again
- `CPS_LSP_BINARY` path includes extension version — if VS Code extension updates, path breaks (update env var)
- Auth tokens are session-scoped — first push/pull per session triggers browser sign-in
- Running as `<ADMIN_USER>` but VS Code extension is under `<USER>` profile
- The Copilot Studio UI may rename the agent (`displayName`) — pull after any UI change to stay in sync
- After pull, `settings.mcs.yml` may gain new fields (voice, speech, etc.) — these are harmless, don't remove them

**Agent Design**
- Criterion 3 (Future Potential) uses structured 3 sub-criteria approach (Company Size, Portfolio Alignment, Investment Activity) — all publicly researchable. Old penetration logic removed.
- Copilot Studio Sonnet model ignores "only 10/5/1" constraints unless reinforced in BOTH system instructions AND topic-level prompts — discovered during v3 testing (C2=8, C4=9 on first attempt)
- C5, C6, C7 always need user input — never let the AI guess these from public data
- C1 (Past Revenue) needs Fluke internal data — mark as "Unverified" unless user provides ranking
- AnswerQuestionWithAI nodes are the workhorse — use them for research, clarification, and calculation steps
- Question nodes with `StringPrebuiltEntity` capture free-text responses
- ConditionGroup with `elseActions` → `AnswerQuestionWithAI` is the pattern for handling ambiguous user responses

### Custom Wide Chat Canvas (2026-06-04)
Default Copilot Studio demo site chat widget (450x520px) is too narrow for the 7-column scoring table. Built custom HTML using Bot Framework Web Chat SDK.

**Solution**: `key-account-scorer-wide.html` in Growth Kaizen folder
- **Auth method**: Direct Line secret (from Settings > Security > Web channel security) — NOT the token endpoint URL
- **Token generation**: `POST https://directline.botframework.com/v3/directline/tokens/generate` with `Authorization: Bearer {secret}`
- **Key styleOptions**: `bubbleMessageMaxWidth: 1050`, `bubbleAttachmentMaxWidth: 1050`
- **Critical CSS fix**: Web Chat SDK ignores `bubbleMessageMaxWidth` for table content — must add `#webchat [class*="bubble"] { max-width: 100% !important; }` and similar overrides for all bubble/content/row/stackedLayout classes
- **Table CSS**: `th { white-space: nowrap }`, short columns (# / Score / Weight) get `nowrap + text-align: center`, markdown containers get `overflow-x: auto`
- **Size presets**: Extra Wide 1100x750 (default), Wide 900x700, Full Page, Default 450x520
- **Fluke branding**: Navy header (#003366), teal accents (#00838F), KAS avatar initials

**Hosting**: Azure Storage static website on `aisandbox02` (flk-taashi-ai-sandbox RG)
- **URL**: `https://aisandbox02.z13.web.core.windows.net/`
- **Deploy method**: Enable static website via Blob Service Properties API, upload to `$web` container via REST PUT
- **No backend needed**: HTML connects directly to Copilot Studio agent via Direct Line

**Gotcha — Token Endpoint vs Direct Line Secret**:
- The "Token Endpoint URL" is hard to find in Copilot Studio UI (Settings > Channels > Mobile app/Email)
- Easier path: use the Direct Line secret (Settings > Security > Web channel security > Secret 1)
- Secret works with `directline.botframework.com/v3/directline/tokens/generate` — confirmed working
- Token endpoint regional URL format (`default{guid}.{region}.environment.api.powerplatform.com`) — region codes are not guessable, probing failed

### Deliverables Summary (2026-06-04)
1. Process Infographic (3pg landscape, 12 GPT Image 2 panels) — built 2026-06-02
2. Architecture doc (10 sections, D2 diagram) — built 2026-06-02
3. Manual Guide (17 sections, 11 screenshots) — built 2026-06-02
4. **How It Works infographic** (2pg landscape, 8 images: 5 GPT Image 2 + 3 screenshots) — built 2026-06-04
5. **Custom wide chat canvas** (HTML, Bot Framework Web Chat SDK) — built 2026-06-04
6. **Chat widget research report** (`chat_widget_research.md`) — resize + DOCX export options — 2026-06-04
7. **Launch email** (`kaizen_agent_launch_email.html`) — short intro with live URL — 2026-06-04
8. **Azure Static Web App** — live at `https://aisandbox02.z13.web.core.windows.net/` — 2026-06-04

- [[project_growth_kaizen]] — project-specific context (hosting decision, response time, next steps)
- [[project_ai_use_case_builder]] — related: this capability could be offered as a use case
- [[feedback_copilot_studio_gotchas]] — extracted gotchas for quick reference
