---
name: msis-550-case-competition
description: "Anthropic vs. Google case competition — 14-slide deck (Veritas + Illustrated versions), DOCX write-up, 3 frameworks (Porter/Envelopment/VRIO), Contextual Moat-First recommendation, 4-member team"
metadata: 
  node_type: memory
  type: project
  originSessionId: 43db1c10-1225-4bdf-aa6d-83b8b22a433b
---

## Overview

MSIS 550 (Product Leadership), UW Foster School of Business Q4 2026. Case competition: "Anthropic vs. Google: Defending Claude Against Bundled Envelopment." 4-member team, 9-minute presentation + 3-minute Q&A.

**Why:** Case competition deliverable requiring academic rigor + presentation quality. Used masters-writing-skill (Mode C: both PPTX + DOCX) through full 8-step workflow including PhD reviewer pass.

**How to apply:** Project dir `<USER_HOME>/OneDrive\Taashi M\UW\Q4\550\`. Reusable patterns for future case competitions: V1→PhD review→V2 pipeline, Veritas + Illustrated dual-version approach, 3-stage validation.

## Key Files

- **Project folder**: `<USER_HOME>/OneDrive\Taashi M\UW\Q4\550\`
- **Case PDF**: `Case 5 - Anthropic vs Google.pdf` (24 pages, 8 exhibits)
- **Assignment**: `Assignment.docx` (10-12 slides, 9 min, 4 members)
- **Rubric**: `Presentation evaluation guide - student ver550.26.pdf` (5 dimensions x 20%)

## Deliverables (2026-05-26)

| File | Description | Size |
|------|-------------|------|
| `Anthropic_vs_Google_VERITAS.pptx` | Veritas Clean design, 14 slides | 82 KB |
| `Anthropic_vs_Google_ILLUSTRATED.pptx` | Veritas + 6 GPT Image 2 panels | 3,079 KB |
| `Anthropic_vs_Google_CaseCompetition_FINAL.pptx` | Original V2 design | 86 KB |
| `Anthropic_vs_Google_WriteUp_FINAL.docx` | Supporting DOCX write-up | 51 KB |
| `images/` | 6 GPT Image 2 illustrations (1536x1024) | ~3 MB total |

## Build Scripts

- `generate_deck_v1.py` / `generate_deck_v2.py` — V1 and V2 FINAL PPTX
- `generate_writeup_v1.py` / `generate_writeup_v2.py` — V1 and V2 FINAL DOCX
- `generate_veritas.py` — Veritas Clean redesign (all 14 slides)
- `generate_illustrated.py` — Veritas + GPT Image 2 panels (6 illustrations embedded)
- `generate_images.py` — GPT Image 2 generation (6 images, ~170s each)
- `validate_pptx.py` — 3-stage QA (content + layout + cross-version comparison)

## Strategic Analysis

- **Frameworks**: Porter's Five Forces, Platform Envelopment (Eisenmann et al., 2011), VRIO (Barney, 1991)
- **Recommendation**: "Contextual Moat-First" strategy
  - Phase 1 (M1-8): MCP + Claude Code under Rahul Patil (CTO)
  - Phase 2 (M9-18): Enterprise defense under Raj Gupta (Sales)
  - Explicitly forgone: price matching, Workspace accounts, Pentagon revenue
- **Key data**: $14B ARR, $2.5B Claude Code, $3B burn, $80B infrastructure, $200M Pentagon loss, Harbridge scores Google 3.85 vs Anthropic 3.70
- **KPIs**: 85%+ retention, $4B+ Claude Code ARR, 500+ MCP accounts

## PhD Review Scores

- V1: 86/100 (B+) — 5 gaps identified
- V2 FINAL: 93/100 (A) — all gaps addressed (decision triggers, retention math, before/after Five Forces, MCP priorities, failure scenarios)

## Validation Results (2026-05-26)

Both Veritas and Illustrated: **PASS** (0 critical issues)
- Data points: 30/30 found in both
- Exhibits: 8/8 referenced in both
- Speaker notes: 14/14 slides in both
- Layout violations: 0 in both
- Cross-version notes match: 11/14 identical

## Slide Allocation (4 members)

- Member 1 (slides 1-3): Problem Definition, Recommendation, Porter's Five Forces
- Member 2 (slides 4-6): VRIO, Segmentation 2x2, Three Alternatives
- Member 3 (slides 7-9): Evaluation Matrix, Phase 1 Roadmap, Phase 2 + Partnerships
- Member 4 (slides 10-12): Impact, Risks, Closing

Related: [[MSIS 579 Case Write-Up & Presentations]], [[Presentation Beautification Skill Project]], [[gpt-image-2-azure]], [[illustrated-panels-over-emoji]]
