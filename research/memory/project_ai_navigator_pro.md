---
name: ai-navigator-pro
description: "AI Navigator Pro — enterprise AI onboarding app, SNOW integration live (4 modules), Supabase self-hosted, E2E validated, deploying on Pulse"
metadata: 
  node_type: memory
  type: project
  originSessionId: d8a16674-fc1f-40b3-803f-51b3df5414ad
---

Enterprise AI tool onboarding and governance platform — conversational mind-map that guides users to pre-approved AI tools with risk/compliance tracking.

**Why:** Streamline AI tool adoption across the enterprise with built-in governance, ServiceNow integration, and leadership analytics.

**How to apply:** This is an active project. Use the repo structure and tech stack details below to inform all development decisions.

## Deployment & Auth Decisions (2026-05-17)
- **Hosting**: Deploying on Pulse platform (local/internal) — NOT Lovable Cloud or Cloudflare Workers
- **SSO**: Already in place on `ai.fluke.com` — consume existing auth (Azure AD / Entra ID), don't build new
- **ServiceNow**: Integration live with `flkbiapiuser` against `fortivedev.service-now.com` (dev)
- **Scope**: Code changes only — SNOW integration complete (Step 1), SSO token consumption next

## Location
- **Source repo**: `<USER_HOME>/OneDrive - <ORG>\AI\Onboarding Tools\ai-navigator-pro\`
- **Deploy repo**: `<USER_HOME>/OneDrive - <ORG>\AI\Onboarding Tools\ai-navigator-pro-deploy\`
- **GitHub (source)**: `https://github.com/taashim-eng/ai-navigator-pro`
- **GitHub (deploy)**: `https://github.com/Taashi-Manyanga_fortive/ai-navigator-pro-deploy` (private)
- **Integration plan**: `docs/integration-plan-v2.0.md` (supersedes v1.2)

## Tech Stack
- **Frontend**: React 19 + TanStack Start (SSR, file-based routing) + Vite 7
- **Styling**: Tailwind CSS 4 + Radix UI primitives
- **Flow Viz**: XYFlow React (interactive mind-map decision tree)
- **Backend**: TanStack server functions (createServerFn)
- **Database**: Supabase (PostgreSQL) — self-hosted project `xoxvegmdshyxeueechjl`
- **Deployment**: Pulse platform (local/internal)
- **Charts**: Recharts (insights dashboard)
- **Scaffolding**: Built with Lovable.dev

## Supabase (self-hosted, 2026-05-19)
- **Project ID**: `xoxvegmdshyxeueechjl`
- **Dashboard**: `https://supabase.com/dashboard/project/xoxvegmdshyxeueechjl`
- **Direct DB**: `db.xoxvegmdshyxeueechjl.supabase.co:5432`
- **Migrations**: 5 applied via `npx supabase db push` (direct connection, NOT pooler)
- **Tables**: sessions, session_events, recommendations, tools, snow_tasks, audit_logs — all CRUD verified
- **Keys**: `sb_publishable_*` (anon) + `sb_secret_*` (service role) in `.env`
- **Gotcha**: Pooler connection fails ("Tenant not found") — use direct connection for migrations

## ServiceNow Integration — E2E Validated (2026-05-19)
- **Credentials**: `flkbiapiuser` / password in `.env`, works on BOTH prod and dev
- **Dev instance**: `fortivedev.service-now.com` (cloned 2026-02-08), full read+write confirmed
- **Prod instance**: `fortive.service-now.com`, read confirmed, sys_user ACL-filtered (empty)
- **Catalog item**: `sys_id=4f192d371bcbbd505e38ff3f034bcbe2` = "Data And Analytics Request"
- **Application service**: `356abe9cdb07470044e9f15aaf961944` = "Business Intelligence (FLK)"
- **Variable names** (confirmed via API):
  - `itss_std_vsvar_requested_for` (sys_user sys_id, mandatory)
  - `itss_std_vsvar_urgency` ("1"/"2"/"3", optional)
  - `application_service` (cmdb_ci_service sys_id, mandatory)
  - `type_of_request` ("Fluke AI" | "Fluke ML", mandatory)
  - `request_category` ("1"=AI Frontend, "2"=AI Backend, "3"=O365 CoPilot, "4"=PBI CoPilot, "5"=ML Model)
  - `itss_std_vsvar_business_justification` (free text, mandatory)
- **E2E tested**: order_now → REQ → RITM, state updates, user lookup by email, manager resolution via `sysparm_display_value=all`
- **Tool-to-category mapping**: m365-copilot→"3", claude-code/github-copilot/amazon-q→"2", all others→"1"
- **Gotchas**: dept/manager/location are references (need display_value=all), opened_by is always API user (requested_for is correct), delete returns 403 (close instead), sys_user empty on prod
- **<USER> on dev**: 50 roles (itil, snc_platform_rest_api_access), 13 groups (FLK-AI-Dev, FLK_BI_L1/L2, FLK_Data_Analytics_Approvers)

## ServiceNow REST Client — Implementation Complete (2026-05-19)
- **Architecture**: Facade pattern with mock fallback (checks `isSnowConfigured()` at call time)
- **4 new modules**:
  - `servicenow.types.ts` — shared types (SnowUser, SnowTask, SnowTaskInput, API record shapes, TOOL_CATEGORY_MAP)
  - `servicenow.rest.ts` — low-level REST client (fetch + Basic Auth, 15s timeout, user lookup, catalog order, RITM fetch)
  - `servicenow.mapper.ts` — pure transforms (raw API → app types)
  - `servicenow.server.ts` — facade (real client if SNOW_* env vars present, else mock fallback)
- **TanStack naming convention**: `.server.ts` suffix excludes from client bundle; `.client.ts` suffix is reserved for client-only modules (caused build failure until renamed to `.rest.ts`)
- **Dynamic imports**: facade uses `await import()` for both client and mock (tree-shaking)
- **2 modified files**: `navigator.functions.ts` (switched imports, updated field mapping), `results.$sessionId.tsx` (removed mock badge)

## E2E Validation Results (2026-05-19)
1. Supabase REST API: 200 OK with service role key
2. All 6 tables: CRUD operations verified (create session → update identity → insert event → insert recommendation → insert audit log → cleanup)
3. SNOW user lookup: returns name/dept/title/manager.email/location for <USER>
4. SNOW catalog order: creates REQ0862455 + RITM0853920 on dev
5. TypeScript: `tsc --noEmit` zero errors
6. Build: `npm run build` succeeds in 6.3s
7. Dev server: boots on port 8080

## Key Architecture
- **Tag-based scoring**: answers accumulate weighted tags that match tool capabilities (`scoring.ts`)
- **9 pre-approved tools**: M365 Copilot, Claude Desktop (bundle: AI+Code+Cowork), ChatGPT, GitHub Copilot, Amazon Q, Gemini, Claude AI, Claude Chatbot
- **Perplexity replaced by Claude Desktop** (2026-05-20): bundled tool (Claude AI + Code + Cowork), Enterprise license required, 15 capabilities, SNOW category "2" (AI Backend)
- **5 Supabase migrations**: schema evolution (tables → RLS tightening → audit logs)
- **ServiceNow**: Real integration via REST client, mock fallback when SNOW_* env vars absent
- **Zero auth (MVP)**: anonymous-friendly, RLS hardened in v3 → SSO already live on ai.fluke.com

## Key Files
- `src/lib/engine/scoring.ts` — recommendation scoring algorithm
- `src/lib/engine/tools.ts` — 9-tool catalog seed data
- `src/lib/engine/questions.ts` — decision tree + branching logic
- `src/lib/navigator.functions.ts` — server-side session lifecycle
- `src/lib/integrations/servicenow.server.ts` — SNOW facade (real + mock fallback)
- `src/lib/integrations/servicenow.rest.ts` — SNOW REST client (Basic Auth, fetch)
- `src/lib/integrations/servicenow.mapper.ts` — SNOW response mappers
- `src/lib/integrations/servicenow.types.ts` — shared SNOW types
- `src/lib/integrations/servicenow.mock.ts` — mock fallback (preserved)
- `src/routes/navigator.tsx` — mind-map flow UI
- `src/routes/results.$sessionId.tsx` — recommendation card + SNOW task display
- `src/routes/insights.tsx` — leadership analytics dashboard
- `supabase/migrations/` — 5 migration files
- `docs/integration-plan-v2.0.md` — validated implementation plan

## Database Tables
- **sessions** — user request flows (email, department, job function, use case, snow_task_number)
- **session_events** — answer breadcrumbs (node_id, question_id, answer JSONB)
- **recommendations** — ranked tools per session (tool_id, score, rank, reasoning)
- **tools** — 9 approved tools catalog (capabilities[], risk_rating, licensing)
- **snow_tasks** — ServiceNow integration (task_number, sys_id, state, payload with ritmNumber)
- **audit_logs** — governance trail (actor_email, entity_type, action)

## Routes
- `/` — landing page
- `/navigator` — interactive mind-map flow
- `/catalog` — browse all tools with risk filters
- `/results/:sessionId` — recommendation card with reasoning + SNOW request info
- `/insights` — leadership analytics dashboard

## Deliverables (2026-05-20)
- `AI_Navigator_Pro_What_Was_Deployed.docx` — 9-section architecture doc (cover, TOC, embedded D2 diagram, tables, code blocks, status tables)
- `AI_Navigator_Pro_Deployment_Deck.pptx` — **14-slide** deck:
  - S1-2: Problem statement + process flow (before/after)
  - S3-10: Title, what deployed, architecture diagram, SNOW detail, how to test, E2E results, prod checklist, tech stack
  - S11-12: Cartoon strip (emoji + speech bubbles, white panels/dark borders)
  - S13-14: **GPT Image 2 illustrated panels** (12 AI-generated scenes, consultant-grade) — user prefers Options C/D
- `AI_Navigator_Pro_Architecture_Infographic.docx` — landscape DOCX with D2 dataflow diagram + 6 step annotations
- `AI_Navigator_Pro_Infographic_v2.docx` — A4 landscape, D2 grid layout (3x3, 1.94:1 ratio), 15-22pt fonts
- `ai-navigator-dataflow.png` / `.svg` — D2 end-to-end dataflow (horizontal, elk layout)
- `ai-nav-infographic-v2.png` — D2 grid-layout infographic (4972x2558, dagre layout)
- Build scripts: `build_pptx.py`, `build_docx.py`, `build_infographic.py`, `build_infographic_v2.py` in `docs/deliverables/`

## GPT Image 2 for PPTX Illustrations (2026-05-20)
- **Endpoint**: `https://codevsclaude46-resource.services.ai.azure.com`
- **Deployment**: `gpt-image-2` (Azure AI Foundry)
- **API**: `/openai/deployments/gpt-image-2/images/generations?api-version=2025-04-01-preview`
- **Credentials file**: `<USER_HOME>/OneDrive - <ORG>\Claude code\Presentation Beautification\gpt image to text 2 credentials.txt`
- **Settings**: `size=1536x1024`, `quality=high`, `output_format=png`, returns `b64_json`
- **Timing**: ~170s per image, 3 parallel threads works well
- **Style prompt suffix**: "Clean flat 2D corporate illustration, minimalist style, white background, muted blue and gray color palette, professional consulting presentation quality, isometric perspective, no text"
- **12 panels generated**: 6 problem scenes + 6 solution scenes, saved to `%TEMP%\ai_nav_panels\`

## Pending
- Move source repo to Fortive GitHub (`Taashi-Manyanga_fortive`)
- Sign into Supabase with Fortive GitHub EMU account
- Deploy on Pulse platform
- SSO token consumption (Azure AD / Entra ID)
- Prod SNOW credentials (currently dev-only)
