---
name: AI Next Steps Plan
description: 6-slide C-Suite deck — 7 strategic AI decisions + Steering Committee formation, 3 versions (v1 operational, v2 gold theme, v3 Veritas clean), sourced from Office Hours + Charter
type: project
originSessionId: faaf5843-504f-4b3d-9ee4-577c3fbf4d12
---
## Overview

Fluke AI Next Steps Plan — a C-Suite executive deck presenting 7 strategic decisions for AI rollout, Steering Committee formation, and a 90-day roadmap. Sourced from AI Office Hours meeting minutes (Apr 10, 2026) and the Fluke AI Charter (Mar 2026).

**Why:** The Office Hours meeting surfaced 5 key rollout questions with no clear decision authority. The Steering Committee fills the governance gap the Charter requires but doesn't explicitly create. Each of 7 open questions gets 2 options with justification and a clear recommendation.

**How to apply:** Build scripts in `C:\Users\tmanyang\OneDrive - Fortive\AI\Plan\`. Each version has its own build script and output PPTX.

## Versions

| Version | Build Script | Output File | Design Language |
|---------|-------------|-------------|-----------------|
| v1 | `rebuild_deck.py` (slides 13-15 of 15-slide deck) | `Fluke_2026_AI_Plan_Deck_v2.pptx` | Original Fortive blue theme |
| v2 | `build_next_steps.py` | `Fluke AI Next Steps Plan_v2.pptx` | Gold-accent C-Suite (dark header bars, gold recommendations) |
| v3 | `build_next_steps_v3.py` | `Fluke AI Next Steps Plan_v3.pptx` | Veritas clean (white bg, large titles, thin borders, FLUKE watermark) |

## Content (6 slides, all versions)

1. **Title** — AI Next Steps Plan, 7 Strategic Decisions badge
2. **Executive Summary** — 7 recommendation cards (4+3 grid) with foundation callout
3. **Governance** — Decision rights hub-spoke → Steering Committee → two meeting cadences
4. **Platform & Access** — Decisions 01-03 (AI UI, Access Tiering, Skills Library)
5. **Rollout & Governance** — Decisions 04-07 (Guardrails, Champions, Launch Format, Vendors)
6. **90-Day Roadmap** — 3 phases, milestones, governance/platform/rollout swim lanes, CTA

## 7 Decisions

| # | Area | Recommendation | Charter Pillar |
|---|------|---------------|----------------|
| 1 | AI UI Platform | Amazon Q Business | Secure by Default |
| 2 | Access Tiering | Competency-Based | AI-Literate Workforce |
| 3 | Skills Library | Centralized Repo | Shared AI Services |
| 4 | Guardrails | Phased Progressive | Secure by Default |
| 5 | AI Champions | Dedicated (~4-5/org) | Champion Network |
| 6 | May Launch | Demo Showcase | Enablement |
| 7 | Vendors | Multi-Vendor Rotation | Multi-Cloud |

## Meeting Cadences (added 2026-04-21)

- **AI Steering Committee**: Every 6 weeks — tool/access decisions, investment review, progress review, guardrail policy, use case pipeline, vendor strategy
- **Fluke AI Office Hours**: Monthly — use case demos, latest & greatest, tips & tricks, look ahead, open Q&A
- First meeting: April 23, 2026

## Veritas Clean Design (v3, 2026-04-21)

Inspired by user's reference slides (Veritas product deck — TIMELINE and DEPLOYMENT slides). Key traits:
- White backgrounds, no dark header bars
- Large bold black ALL-CAPS titles (34pt) top-left + "FLUKE" watermark (34pt, light gray #D4D4D4) top-right
- Thin blue accent line below header (0.025" height, Fortive blue #005EB8)
- Thin borders instead of filled panels — `add_bordered_rect()` with 1-1.5pt lines
- Dashed blue borders (`add_dashed_rect()` via XML `a:prstDash val="dash"`) for grouping boxes
- Gold (#D48B06) borders for recommended options, light gray (#E2E8F0) for non-recommended
- Minimal footer: thin gray line + small silver text
- Content palette: mostly monochrome (black/charcoal/gray/silver) + blue/gold accents only where meaningful

## AI Advisory Committee C-Suite Email (2026-04-24)

Separate deliverable built from Office Hours content + this deck's 7 decisions:
- **File**: `C:\Users\tmanyang\OneDrive - Fortive\AI\AI Advisory Committee\AI_Charter_Progress_Update_CLevel_April2026.docx`
- **Content**: Executive summary, 4 real use cases with time-savings metrics, 7 decisions table, governance structure, risk awareness, next steps
- **Sources**: Apr 10 + Apr 24 Office Hours transcripts + this PPTX
- **Apr 24 Office Hours key topics**: JD Giles channel coverage demo, per-user usage tracking need raised by JD and Eshwari, governance discussion

## Source Documents

- `C:\Users\tmanyang\OneDrive - Fortive\AI\Office Hours\4-10-2026\AI Office Hours — Meeting Minutes (April 10, 2026).docx`
- `C:\Users\tmanyang\OneDrive - Fortive\AI\Office Hours\4-24-2026\AI Office Hours (April 24, 2026).docx`
- `C:\Users\tmanyang\OneDrive - Fortive\AI\Charter\Fluke_AI_Charter_Updated_20260326.docx`

## QA Artifacts

- `qa_slides/` — v2 visual exports
- `qa_v3/` — v3 visual exports (slide_01.png through slide_06.png)
