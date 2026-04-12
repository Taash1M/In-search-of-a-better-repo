---
name: EM Leadership Forum
description: 45-min AI presentation — Bold Signal Light design, 3 PPTX + 3 HTML versions, native shapes, 10 diagrams, QA complete
type: project
originSessionId: aa210407-a09e-461f-aa2f-83d0e2fa4475
---
## Overview

Deliverables for an EM Leadership Forum presentation on Agentic AI at Fluke. Audience: **Techno-Functional leaders** (mixed technical + executive). Target: **45 minutes**.

**Why:** Leadership needs a high-impact presentation covering AI direction, 90-day accomplishments, deployed agents, Claude Code enablement, and forward-looking initiatives.

**How to apply:** PptxGenJS (Node.js) for PPTX creation, standalone HTML for animated versions. Bold Signal Light design system (McKinsey/BCG grade).

## Key Facts

- **Project dir**: `C:\Users\tmanyang\OneDrive - Fortive\AI\EM\Leadership Forum\`
- **Build script**: `C:\Users\tmanyang\AppData\Local\Temp\build_lf_v2.js` (~1800 lines)
- **Created**: 2026-04-08
- **Status**: All 6 deliverables complete — 3 PPTX (QA R2 passed) + 3 HTML (animated). Pending user review (2026-04-10)

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

**Shared HTML features:** Single-file (zero deps), Arrow/Space/Escape nav, touch swipe, 16:9 responsive, yellow progress bar, slide counter, fade-up stagger animations (80ms), crossfade transitions (300ms), prefers-reduced-motion support.

## Key Architectural Decisions

1. **Native PPTX shapes** for architecture diagrams (editable, no overlap) instead of PNG images
2. **Agent Portfolio** rebuilt as native 3x2 card grid (replaced overlapping PNG)
3. **Current State** rebuilt with native mini-agent cards (2x3 grid)
4. **Claude Code Architecture** — 4-tier layered diagram with KPI sidebar, all native shapes
5. **Removed content duplication** in V2: slideWhatBuilt + slideScaling cut (covered by slideClaudeCodeUsage)

## QA History

- **QA R1**: Identified duplicate badges, CRM callout, agent portfolio overlap → fixed
- **QA R2**: 12 V2 + 8 V3 + 1 V1 issues → all fixed:
  - Demo slide fonts 9.5→11pt
  - Scorecard title renamed (no PNG duplication)
  - Emerging: compact cards, 5 bullets each, callout bar
  - Architecture Direction: desc 9→10.5pt
  - V2 dedup: 28→26 slides
  - CRM Opportunity: tightened to 4.6" card
  - Claude Code Arch: vertically centered KPIs
  - Vibe/MCP: added MCP definition content
  - Foundations: wider MCP diagram
  - TechMentor: 5 bullets at 11pt

## Source Materials

1. `AI Applicability Direction at Fluke.docx` — Strategy doc
2. `last 90 days and detailed videos.pptx` — 9 initiatives/4 pillars
3. `Recommended 30 minute flow.docx` — CIO-level flow
4. `info.docx` — Detailed content per section
5. `Overarching presentation prompt.txt` — Theme

## Visual Assets

**10 Diagrams** (`diagrams/`): task_vs_agentic, ai_applicability, claude_code_architecture, mcp_hub_spoke, agent_portfolio, ninety_day_scorecard, agentic_evolution_arrow, rpa_vs_agentic, salesforce_vs_dynamics, oracle_fusion_agents

**13 Images** (`images/`): Unsplash contextual photos (analytics, voice, manufacturing, coding, etc.)

**Videos** (`Videos/`): account360_release1.mp4 (5:04), vov_pilot.mp4 (4:29) — clip recs: A360 0:25-2:30, V2V 1:30-3:30

## Placeholder Sections (User to Provide)

- Claude Code business user use cases
- Fusion SAAS Fluke-specific plans

## Original Versions (archived)

- `v1_recommended_flow.pptx` (13 slides), `v2_original_plan.pptx` (27 slides), `v3_merged.pptx` (22 slides)
- Build script: `build_pptx.py` (python-pptx, 1174 lines)
