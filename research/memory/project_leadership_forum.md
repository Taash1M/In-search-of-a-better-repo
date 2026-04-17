---
name: EM Leadership Forum
description: 45-min AI presentation — Bold Signal Light design, 28-slide deck, checkpoint 3 final (2026-04-16)
type: project
originSessionId: aa210407-a09e-461f-aa2f-83d0e2fa4475
---
## Overview

Deliverables for an EM Leadership Forum presentation on Agentic AI at Fluke. Audience: **Techno-Functional leaders** (mixed technical + executive). Target: **30-45 minutes**.

**Why:** Leadership needs a high-impact presentation covering AI direction, 90-day accomplishments, deployed agents, Claude Code enablement, and forward-looking initiatives.

**How to apply:** python-pptx for PPTX creation. Bold Signal Light design system (McKinsey/BCG grade). Veritas Suite visual quality standards.

## Key Facts

- **Project dir**: `C:\Users\tmanyang\OneDrive - Fortive\AI\EM\Leadership Forum\`
- **Interview results**: `rebuild_plan_interview.md` (complete slide-by-slide spec for all 23 slides)
- **Created**: 2026-04-08
- **Status**: Full 25-slide deck built (2026-04-15). Architecture bubble fix validated + applied (2026-04-16). Agent Portfolio slide populated (2026-04-16).

## Build Progress (2026-04-14 → 2026-04-16)

1. ~~Visual quality level-setting~~ — COMPLETE
2. ~~Content level-setting (interview)~~ — COMPLETE
3. ~~Visual proofs~~ — COMPLETE (4 key patterns validated)
4. ~~Slide-by-slide construction~~ — COMPLETE (25 slides, both v4 + D1 decks)
5. ~~Architecture bubble connector fix~~ — COMPLETE (2026-04-16): PIL aspect-ratio-aware fitting, margin column bubbles (LEFT=0.13, RIGHT=6.95), thin dotted connectors, validated on slide 9 test
6. ~~Pillar bar repositioning~~ — COMPLETE (bar_y 5.5→6.1 on slides 6-7)
7. ~~Manual edit persistence~~ — COMPLETE (2026-04-16): User hand-corrected bubble positions on slides 9-13,20; reverse-engineered img_fx/fy from PPTX and persisted to build script. Slides 15+17 converted from conceptual labels to actual agent names.
8. ~~Agent Portfolio slide~~ — COMPLETE (2026-04-16): 16 agents across 3 products (PS/V2V/TM), grouped by 6 reusable patterns (Intake & Routing, Data Retrieval, Quality Review, Planning, Synthesis & Response, Citation & Provenance). SHARED badges, product-colored pills, bottom panel "Why Agentic AI Over Traditional RAG?" with 4 numbered advantages.

## Checkpoint: "A Good Base" (2026-04-16)

All 25 slides built, bubble connectors validated via manual correction loop, pillar bars repositioned, PDFs generated. Build script produces output matching user's hand-corrected PPTX. Both v4 (D2 diagrams) and D1 (Azure diagrams) decks at 1.83 GB with embedded videos.

## Checkpoint 3: Final Slide Order (2026-04-16)

User's final manual reorder persisted. Key changes from checkpoint 2:
1. **4 Pillars** moved from position 24 → position 9 (right after Best Practices)
2. **LLM Gateway Arch** moved from position 14 → position 23 (after Claude Code Intro)
3. **Claude Code Arch** moved from position 23 → position 24 (after LLM Gateway)
4. **Slide 5 (4c)**: Arrow indicator moved to bottom of capability spectrum, "Increasing Capability" label moved above spectrum
5. **Slide 16 (TechMentor)**: 3 manual connector rectangles added

Backups: `checkpoint2_backup/` (11 scripts), `checkpoint3_backup/` (2 main build scripts)

## Post-Checkpoint: Agent Portfolio Populated (2026-04-16)

Slide 12 replaced placeholder with `build_slide_9_agent_portfolio()` in both v4 and D1 scripts. 3x2 card grid with color-coded pattern groups, product badges, SHARED indicators. Both decks rebuilt + PDFs regenerated.

## 3 Agentic AI Deep-Dive Slides Added (2026-04-16)

Synthesized from external reference deck `Agentic-AI-The-Next-Frontier-in-Intelligent-Systems.pptx` (5 slides, 16"x9"). Content adapted to Bold Signal Light design system and inserted after Industry Framing (slide 4):
- **Slide 4b** `build_slide_4b_defining_agentic()` — 3 characteristic cards (Autonomous Perception, Goal-Oriented Reasoning, Continuous Learning Loop) + Perceive-Reason-Act-Learn cycle diagram
- **Slide 4c** `build_slide_4c_agentic_advantages()` — Left: 5-level capability spectrum (RPA→Chatbots→RAG→Workflow→Agentic), Right: 2x2 advantage cards
- **Slide 4d** `build_slide_4d_design_principles()` — 6 numbered principles in 3x2 grid with colored separator lines + italic "At Fluke:" examples linking each principle to actual agent implementations

Both v4 and D1 decks now **28 slides** each. PDFs regenerated.

## Final Slide Inventory (28 slides — checkpoint 3 order)

| Pos | Function | Slide Title |
|-----|----------|-------------|
| 1 | Title | The Era of Agentic AI |
| 2 | Advert | Presentation Journey |
| 3 | Agenda | Presentation Agenda |
| 4 | 4b | Defining Agentic AI |
| 5 | 4c | Why Agentic AI? (spectrum + cards) |
| 6 | 4 | Industry Framing: Task→Agentic |
| 7 | 4d | Design Principles (3x2 grid) |
| 8 | 7 | Best Practices: Agents & MCP |
| 9 | **14** | **4 Pillars: AI Applicability** (moved from 24) |
| 10 | 5a | 90-Day Progress |
| 11 | 8 | 90-Day Scorecard: 8/9 |
| 12 | 5b | Agentic Design Patterns |
| 13 | 6a | Pulse Sales Architecture |
| 14 | 6b | V2V Architecture |
| 15 | 9 | Agent Portfolio |
| 16 | 10a | TechMentor Architecture |
| 17 | 10b | TechMentor Video |
| 18 | 11a | Pulse Sales Deep-Dive |
| 19 | 11b | Pulse Sales Video |
| 20 | 12a | V2V Deep-Dive |
| 21 | 12b | V2V Video |
| 22 | 13a | Claude Code Intro |
| 23 | **6c** | **LLM Gateway Architecture** (moved from 14) |
| 24 | **13b** | **Claude Code Architecture** (moved from 23) |
| 25 | 15 | Oracle Fusion / CRM |
| 26 | 16 | Pricing & Operating Model |
| 27 | 17 | Forward Look: Q2/Q3/Q4 |
| 28 | 18 | Thank You / Key Takeaways |

## Architecture Reference Files (extracted 2026-04-15)

| Source File | Key Components | For Slide |
|-------------|---------------|-----------|
| `Tech Mentor Architecture and flow diagrams.pptx` | 5 LangGraph agents, CosmosDB, 3 data sources (Depot repair, VOC tool, SKYNET), retry loops | 10a |
| `Pulse Sales Basic conceptual Architecture.pptx` | 7 agents, dual-path routing (general/specific), parallel Order/Oppty paths, Fabric+Delta Lake | 11a |
| `V2V Basic Architecture and code Flow.pptx` | 4 LLM agents (Search Query, Query Analyzer, Reviewer, Synthesizer), Cosmos DB vector search, 10 functions | 12a |
| `LLM_Gateway_What_Was_Deployed_20260324.docx` | 4 figures: E2E flow, protocol translation, resource landscape, access control | 6c, 13b |
| `last 90 days and detailed videos.pptx` | 9 initiatives (8 complete), 5 agents with video links | 5a, 5b |
| `Fluke IT 2026 Strat _Q1.pptx` slide 22 | 17 initiatives (9 Q2, 3 Q3, 4 Q4) across 4 pillars | 17 |

## Diagram Engine Selection (Proven 2026-04-14)

All 4 engines confirmed working with test renders:

| Visual Type | Primary Engine | Status |
|-------------|---------------|--------|
| Sequence diagrams (swim lanes, lifelines) | **Mermaid CLI (mmdc)** v11.12.0 | Tested — color-coded phase boxes, UML lifelines, numbered steps |
| Flowcharts / decision trees | **Mermaid CLI** with custom `style` directives | Tested — dual-path branching, diamond decisions, color-coded paths |
| Gantt / timelines | **Mermaid CLI** `gantt` or **matplotlib** | Tested — wave-grouped bars, status colors (done/active/planned) |
| Architecture (Azure services) | **azure_diagrams** `quick_architecture()` | Proven in Phase 2 PPTX |
| Architecture (generic systems) | **D2** v0.7.1 with styled classes + grid layouts | Proven in Phase 2 PPTX |
| Data charts (bar, donut, line) | **matplotlib** 3.10.8 | Available, customizable |
| KPI cards / dashboards | **python-pptx** native shapes | Proven in Phase 2 PPTX |
| SVG→PNG conversion | **cairosvg** 2.9.0 (with MSYS2 DLLs at `C:\Users\tmanyang\tools\cairo-dlls`) | Works for matplotlib/Mermaid SVGs; NOT for D2 SVGs (embedded WOFF fonts) |

**Key learning**: Mermaid CLI was available but underutilized — stronger than D2 for sequence diagrams and flowcharts. D2 remains better for architecture/structural diagrams with nested containers.

**Visual quality standard (proven 2026-04-14):** Veritas Suite deck (44 slides) analyzed for design patterns. Sample slide 18 adaptation built and validated — "Agentic AI Technology Stack at Fluke" (`sample_veritas_slide18.pptx`). Key proven patterns:
- **Icon strip with bracket connectors** — colored circles, horizontal bracket bar + vertical drops, FLOWCHART_EXTRACT triangle arrowheads rotated 90°
- **Numbered vertical timeline** — navy circles (1,2,3) connected by gray line, title + description to right
- **Hierarchy tags** — rounded rect work items with color-coded borders per level (Agent → Skill → Tool)
- Build script: `sample_slide18_adaptation.py`

**Mermaid CLI location**: `C:\Users\adm-tmanyang\AppData\Roaming\npm\mmdc`
**D2 location**: `C:\Users\tmanyang\tools\d2\d2-v0.7.1\bin\d2.exe`

## Design System: Bold Signal Light — Fluke Edition

- **Palette**: Fluke Yellow #FFC000 (primary accent), Navy #003366 (depth), White #FFFFFF (backgrounds)
- **Fonts**: Arial Black (headers), Arial (body)
- **Layout**: LAYOUT_WIDE (13.333" × 7.5"), 0.6" margins
- **Style**: Light backgrounds, split-panel hero (left white / right navy), yellow accent bars, rounded cards, consulting-grade action titles
- **Inspired by**: frontend-slides (12 presets) + banana-slides (golden yellow theme)
- **Status colors**: Green #28A745, Blue #005EB8, Red #DC3545, Purple #8040C0, Oracle #C74234

## 3 PPTX Versions (Bold Signal v2)

| Version | File | Slides | Focus |
|---------|------|--------|-------|
| V1 | `v1_bold_signal.pptx` | 15 | CIO recommended flow, 30 min |
| V2 | `v2_bold_signal.pptx` | 26 | Full 7-section plan, 45 min |
| V3 | `v3_bold_signal.pptx` | 23 | Merged best-of-both |

## 3 HTML Versions (animated, complete)

| Version | File | Slides | Size | Features |
|---------|------|--------|------|----------|
| V1 | `v1_bold_signal.html` | 15 | ~65KB | Crossfade, stagger animations, responsive |
| V2 | `v2_bold_signal.html` | 26 | ~82KB | Inline SVG diagrams (MCP, Oracle), overview grid |
| V3 | `v3_bold_signal.html` | 23 | ~76KB | Mouse wheel nav, glow progress bar |

## Source Materials (5 docs)

1. `Overarching presentation prompt.txt` — thesis: agentic AI transforming business, products, pricing
2. `info.docx` (updated 2026-04-12) — 8-section narrative talk track (most recent source)
3. `Recommended 30 minute flow.docx` — 9-section timed blueprint with 2 video slots
4. `AI Applicability Direction at Fluke.docx` — strategic direction doc (not finalized strategy)
5. `last 90 days and detailed videos.pptx` — 9 initiatives across 4 pillars, 5 named agents

## Content Summary (from source docs)

**Narrative Arc (maps to 30-min flow):**
1. Industry framing: Task AI → Agentic AI
2. Fluke's current state: task-based, assistive, deliberately disciplined
3. Foundations before agents: architecture > models, cloud-first, MCP
4. Internal-first delivery: PM acceleration, engineering productivity, agent swarms
5. Customer-facing evolution: invisible, embedded, outcome-driven
6. Pricing/operating model: per-user → consumption-based

**Named Agents (6):** Pulse Sales, Voice-to-Value (V2V), TechMentor, AskFlukie, Lyra, Depot Repair

**4 Pillars:** Support Revenue Generation, Customer Experience, Workforce Productivity, Adoption & Governance

**Hard Numbers:**
- $2M+ first-year TechMentor impact ($500K ECAL PDBL + $800K EVL labor + $700K AFL revenue)
- $40M service business target (TechMentor context)
- ~4K accounts linked via IIR
- 5Y account history expansion
- 27 Claude Code users, 4 nodes, 41 skills, $13/mo
- 8/9 initiatives completed, 1 in-progress

**Quotable Lines:**
- "Task AI to Workflow AI"
- "Human-in-the-loop to Human-on-the-loop"
- "Don't scale agents until the plumbing is right"
- "Customers don't want AI features. They want outcomes."
- "The era of agentic AI is not about replacing people — it's about redesigning work."

## Version Differences Summary

| Dimension | V1 (15 slides) | V2 (26 slides) | V3 (23 slides) |
|-----------|----------------|-----------------|-----------------|
| Framing | Concise keynote | Full timed briefing | Hybrid merge |
| Industry video | Yes (placeholder) | Removed | Removed |
| Agent deep-dives | No | Yes (4 slides + LIVE DEMO) | Yes (3 slides) |
| Oracle Fusion/CRM | No | Yes (2 sections) | Yes (merged) |
| Customer/Pricing | Yes | Removed | Removed |
| Priority Workflows (PM/Eng/Swarms) | Yes | Removed | Removed |
| Placeholders | None | 1 (Business User Use Cases) | 1 (trimmed) |

## Visual Assets

**10 Diagrams** (`diagrams/`): task_vs_agentic, ai_applicability, claude_code_architecture, mcp_hub_spoke, agent_portfolio, ninety_day_scorecard, agentic_evolution_arrow, rpa_vs_agentic, salesforce_vs_dynamics, oracle_fusion_agents + `gen_diagrams.py`

**14 Images** (`images/`): Unsplash contextual photos. Only 4 used in decks: analytics_dashboard.jpg, voice_analytics.jpg, manufacturing_floor.jpg, coding_developer.jpg

**Videos** (`Videos/`): account360_release1.mp4 (5:04), vov_pilot.mp4 (4:29) — clip recs: A360 0:25-2:30, V2V 1:30-3:30

**Test renders** (2026-04-14, temporary): test_seq.png, test_gantt.png, test_intake.png, test_flow.png — can be deleted

## Placeholder Sections (User to Provide)

- Claude Code business user use cases
- Fusion SAAS Fluke-specific plans

## QA History

- **QA R1**: Identified duplicate badges, CRM callout, agent portfolio overlap → fixed
- **QA R2**: 12 V2 + 8 V3 + 1 V1 issues → all fixed (font sizes, dedup, compact cards, etc.)

## Original Versions (archived)

- `v1_recommended_flow.pptx` (13 slides), `v2_original_plan.pptx` (27 slides), `v3_merged.pptx` (22 slides)
- Build script: `build_pptx.py` (python-pptx, 1174 lines)
