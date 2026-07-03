---
name: ai-office-hours
description: "<ORG> AI Office Hours monthly series (May-Nov 2026), 3 PPTX versions (Veritas/Illustrated/Full Illustrated), 17 GPT Image 2 panels, <ORG> Template + Aptos fonts"
metadata: 
  node_type: memory
  type: project
  originSessionId: 43db1c10-1225-4bdf-aa6d-83b8b22a433b
---

## Overview

<ORG> AI Office Hours — monthly internal sessions for AI enablement, guidance, and community. First session May 27, 2026. 3rd Tuesday of every month through November 2026, 9:00-10:00 AM PST.

**Why:** Employees face 6 friction points with AI adoption (The Spark, Tool Overload, Request Chaos, The Black Hole, Zero Visibility, Governance Gap). Office Hours provide structured resolution for each through onboarding, role-based guidance, standard processes, visible pipelines, monthly metrics, and audit-ready governance.

**How to apply:** Deck content is reusable for future sessions. Update schedule dates and agenda items per session. The <ORG> Template + Veritas Clean design system is the standard for all <ORG> AI presentations going forward.

## June 17 (Session 2) Meeting Minutes — DONE (2026-06-22)

Built the June 17 minutes the SAME way as May 27 (email-body DOCX + full minutes DOCX→PDF) but with an
**executive / less-loud** treatment per user: SAME <ORG> palette (navy/blue/green/gold) used SPARINGLY —
KPI cards unified to light bg + navy value + one thin blue rule (was 6 saturated fills), highlight cards
white with thin left navy rule (was filled gray), hairline table grid, no hero image, more whitespace,
green/gold only tiny accents. Generator: `17-Jun-2026/Meeting Minutes/generate_meeting_docs.py`. Source =
the full session TRANSCRIPT `17-Jun-2026/<ORG> AI Office Hours (Monthly).docx` + `Agenda_June_17.pptx`.
Content (transcript-accurate, no May leakage): Amazon Quick (agentic-AI+BI on QuickSight) + Kiro
spec-driven dev (Hassnain Rizvi/Yang Chen/Brian Dooley), Julian Knabe Claude-in-Excel (M&A model ~10min,
churn, gray-market) + daily workflow, 4 approved tools + <ORG_PARENT> monthly Claude-license window bottleneck,
eMaint deferred, next session July. Outputs: `Fluke_AI_Office_Hours_June_Email_Body.docx` +
`_June_Full_Minutes.docx` + `.pdf`. OPEN: confirm July session date; KPIs are transcript-derived (no chat-
export metrics like May). docx2pdf (Word COM) used for PDF.

## Key Files

- **Project folder**: `<USER_HOME>/OneDrive - <ORG>\AI\Office Hours\27-May-2026\`
- **<ORG> Template**: `<USER_HOME>/OneDrive - <ORG>\AI\Office Hours\Fluke_Template.pptx` (10 layouts, Aptos fonts)
- **Original deck**: `<USER_HOME>/OneDrive - <ORG>\AI\Office Hours\Fluke_AI_Office_Hours_27_May.pptx` (5 slides, pre-restyle)

## 3 PPTX Versions (14 slides each, all QA-passed 2026-05-27)

| Version | File | Size | Description |
|---------|------|------|-------------|
| V1 | `Fluke_AI_Office_Hours_VERITAS.pptx` | 1.4 MB | Veritas Clean, text-only |
| V2 | `Fluke_AI_Office_Hours_ILLUSTRATED.pptx` | 7.4 MB | Veritas + 10 GPT Image 2 panels on 8 key slides |
| V3 | `Fluke_AI_Office_Hours_FULL_ILLUSTRATED.pptx` | 13.2 MB | Every slide illustrated, 17 GPT Image 2 panels |

## Scripts

| Script | Purpose |
|--------|---------|
| `generate_veritas.py` | V1 Veritas Clean builder |
| `generate_illustrated.py` | V2 builder (10 images on 8 slides) |
| `generate_full_illustrated.py` | V3 builder (17 images on all slides) |
| `generate_images.py` | 10 base GPT Image 2 illustrations |
| `generate_images_v3.py` | 7 additional illustrations for V3 |
| `validate.py` | 3-stage QA (content, layout, cross-version) |

## Design System (<ORG> Template + Veritas Clean)

- **Base template**: `Fluke_Template.pptx` (Blank layout idx 9)
- **Fonts**: Aptos (body), Aptos Display (titles) — NOT Calibri
- **Palette**: NAVY `#0F172A`, BLUE `#0066CC`, GREEN `#5BB12F`, GOLD `#EEB000`, Card fill `#F0F2F5`, Light gray `#E2E8F0`
- **Veritas pattern**: White bg, `v_header()` (20pt title, 12pt subtitle, blue accent line at y=1.15, "<ORG>" watermark right), `v_footer()` (gray line at y=7.05, 8pt text)
- **Safe zone**: x=0.60 to x=12.73, y=0.00 to y=7.30
- **Reference script**: `<USER_HOME>/OneDrive - <ORG>\AI\Plan\build_next_steps_v3.py` (Veritas on <ORG> template)
- **OneDrive lock workaround**: Copy template to `template_base.pptx` before python-pptx opens it

## 14-Slide Structure

| # | Title | V2 Image | V3 Image |
|---|-------|----------|----------|
| 1 | Title | No | title_hero.png |
| 2 | Agenda (7 items, 2-col) | No | agenda_plan.png |
| 3 | Section: Why We Are Here | section_why.png (center) | section_why.png |
| 4 | The Problem (1-3) | spark/tool_overload/request_chaos (3 stacked right) | same |
| 5 | The Problem (4-6) | black_hole/zero_visibility/governance_gap (3 stacked right) | same |
| 6 | The Solution (6 pain→fix) | solution.png (right panel) | same |
| 7 | Section: What to Expect | No | section_expect.png |
| 8 | Intro & Session Details | No (schedule on right) | calendar.png (bottom) |
| 9 | AI at <ORG> (TechMentor) | ai_at_fluke.png (right panel) | same |
| 10 | Where We Are Today | metrics.png (right panel) | same |
| 11 | Monthly Format (4 pillars) | No | monthly_pillars.png |
| 12 | Next Steps & Resources | No | next_steps_path.png |
| 13 | Q&A | No | No |
| 14 | Thank You | No | thank_you_close.png |

## 6 Pain Points → Solutions

1. **The Spark** → Clear onboarding path and hands-on demos each session
2. **Tool Overload** → Role-based guidance: which tool fits your job
3. **Request Chaos** → Standard process, single channel, tracked requests
4. **The Black Hole** → Visible pipeline with SLAs and accountability
5. **Zero Visibility** → Monthly metrics dashboard and adoption tracking
6. **Governance Gap** → Audit-ready: requests, approvals, data sensitivity reviewed

## Schedule Data

May 27 (Session 1), Jun 17, Jul 15, Aug 19, Sep 16, Oct 21, Nov 18

## Agenda (May 27 Session)

1. Intro & Session Details — Taashi Manyanga
2. AI at <ORG> Showcase — Richard Feng (TechMentor video)
3. Business AI Projects — Ryan Bryson & Evan Nebeker
4. IT AI / GitHub Copilot — Kevin Davison
5. Microsoft AI Presentation — Microsoft Team
6. Q&A and Discussion — All
7. AI Resources & Next Steps — Taashi Manyanga

## QA Results (2026-05-27)

All 3 versions passed 3-stage validation:
- Stage 1 Content: 14 slides, 11/11 data points, 14/14 speaker notes
- Stage 2 Layout: All shapes in bounds, Aptos fonts confirmed
- Stage 3 Cross-version: Speaker notes 100% match, data points match
- Font flags on S9/S10 (24-30pt) are intentional stat callouts inside KPI cards

## GPT Image 2 Generation

- 17 total images (10 base + 7 V3-only), all 1536x1024 high quality
- ~200s per image, sequential generation
- Total generation time: ~50 min across 2 batches
- Style: "Flat 2D corporate illustration, white background, muted blue and gray tones, no text or words, professional consulting style"

## June 17 Session (Session 2) — 2026-06-16

**Folder:** `<USER_HOME>/OneDrive - <ORG>\AI\Office Hours\17-Jun-2026\`
**File:** `Agenda_June_17.pptx` — single agenda slide built from `template_base.pptx` (<ORG> CIO deck template)
**Design:** Gold circles (#FFC000), Aptos Slab SemiBold numbers (24pt), Aptos SemiBold titles (20pt), gold separator lines (#EEB000), background image from template

### Agenda (6 items)

| # | Topic | Speaker |
|---|-------|---------|
| 1 | Intro & Session Details | Taashi Manyanga |
| 2 | AWS AI Tools & Roadmap | Amazon Team |
| 3 | AI in Modeling & Daily Workflow | Julian Knabe |
| 4 | eMaint Award-Winning AI Use Case | eMaint Team |
| 5 | Q&A and Discussion | All Participants |
| 6 | AI Resources & Next Steps | Taashi Manyanga |

**Changes from May:** Dropped from 7 to 6 items. Replaced Microsoft Team/Richard Feng/Ryan Bryson/Kevin Davison with Amazon Team, Julian Knabe, and eMaint Team. Used CIO template design (not Veritas Clean) per user preference.

Related: [[Presentation Beautification Skill Project]], [[gpt-image-2-azure]], [[Team AI Enablement]], [[illustrated-panels-over-emoji]]
