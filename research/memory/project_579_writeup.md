---
name: MSIS 579 Case Write-Up & Presentations
description: MSIS 579 final — IKEA case analysis (4 angles × JTBD), two-pass write-up workflow, 4 PPTX presentations (v3 design system, 16 slides each), masters-deliverable skill created
type: project
originSessionId: ae50e3e1-9553-4e26-a884-435a65a1bea9
---
## Overview

MSIS 579 (Strategic Management of Technology & Innovation), UW Q4 2026. Final project: IKEA case analysis across 4 angles using JTBD framework. Deliverables include write-ups (DOCX) and presentations (PPTX) for each angle.

**Why:** This project established a repeatable two-pass write-up workflow and a comprehensive presentation generation pipeline that can be generalized into reusable skills.

**How to apply:** When the user asks for a case write-up or presentation, follow the workflow patterns from this project. The masters-deliverable skill (`<USER_HOME>/OneDrive\Taashi M\UW\Q4\579\Final\SKILL.md`) packages the complete workflow.

## Key Files

- **Project folder**: `<USER_HOME>/OneDrive\Taashi M\UW\Q4\579\Final\`
- **Masters-deliverable skill**: `SKILL.md` in Final folder (shareable v2.0)
- **4 PPTX presentations** (16 slides each, all QA-passed 2026-05-03):
  - `Angle_A_RoomArchitect_Assembly\IKEA_Presentation_Angle_A.pptx`
  - `Angle_B_RoomArchitect_Wayfinding\IKEA_Presentation_Angle_B.pptx` (user manually rebuilt as design reference)
  - `Angle_C_VirtualInfluencers_Assembly\IKEA_Presentation_Angle_C.pptx`
  - `Angle_D_VirtualInfluencers_Wayfinding\IKEA_Presentation_Angle_D.pptx`

## 4 Case Angles

| Angle | Innovation | Strategy | Hero Score |
|-------|-----------|----------|------------|
| A | RoomArchitect (AR room planner) | Assembly Instructions | 4.60 |
| B | RoomArchitect (AR room planner) | Wayfinding Navigation | 4.40 |
| C | Virtual Influencers (AI brand reps) | Assembly Instructions | 3.65 |
| D | Virtual Influencers (AI brand reps) | Wayfinding Navigation | 3.85 |

## v3 Design System (Proven)

White backgrounds, all Calibri, #005EB8 blue top bar, #D48B06 gold accents, #E2E8F0 light borders, minimal tables, no watermarks.

**Font hierarchy** (from user's manual Angle B rebuild):
- S1 title: 28pt
- Content titles (S2-S15): 20pt
- Subtitles/labels: 14pt
- Stat callouts: 36pt
- Market size numbers: 24pt
- Hero scores (S1, S16): 48pt
- Q&A title (S16): 34pt

## Write-Up Workflow

1. Discovery: extract instructions, rubric, structural guide
2. Research: deep case research → fact sheet with data points
3. V1: generate with python-docx → PhD reviewer scores per rubric dimension
4. V2: address every gap → final DOCX

## Quality Rules (Proven)

1. Always lead with the answer (recommendation in first paragraph)
2. Anchor every claim in data (market size, growth rates, share trends)
3. Rank framework dimensions by impact, don't just list
4. Steel-man alternatives before dismissing
5. Quantify success metrics (specific KPI targets)
6. Assign ownership and resources to every recommendation
7. Pin-cite exhibits (specific panels, rows, columns)
8. Create urgency (show cost of inaction)

## Masters-Deliverable Skill

Created `SKILL.md` (shareable v2.0) — packages the complete workflow for producing submission-ready case deliverables. Supports DOCX write-ups, PPTX presentations, or both. Enforces 8 write-up rules and 6 presentation rules, runs PhD-reviewer scoring against rubric, bakes anti-AI-prose rules into writing. Dependencies: python-docx, python-pptx, pdfplumber, matplotlib.

Also promoted to userSettings as `masters-writing-skill`. Reused for MSIS 550 case competition (2026-05-26): Anthropic vs. Google, Mode C (PPTX + DOCX), 3 frameworks, V1→PhD review→V2 pipeline. Score improved from 86 (B+) to 93 (A). See [[MSIS 550 Case Competition]].
