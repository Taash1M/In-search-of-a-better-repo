---
name: MSIS 579 Case Write-Up
description: Masters-level case write-up workflow for MSIS 579 — two-pass generation (v1→PhD review→v2), JTBD framework, python-docx academic formatting. Seed for generic write-up skill.
type: project
---

## Overview

MSIS 579 (Strategic Management of Technology & Innovation), UW Q4 2026. Assignment 1: Sephora case analysis using JTBD framework.

**Why:** This project established a repeatable two-pass write-up workflow that can be generalized into a skill for any masters-level or professional write-up.

**How to apply:** When the user asks for a case write-up, strategy memo, or structured analysis document, follow the workflow in the project memory file. The full pattern library (8 quality rules, framework reference, rubric template, format presets) lives in the project folder.

## Key Files

- **Project memory**: `C:\Users\tmanyang\OneDrive\Taashi M\UW\Q4\579\PROJECT_MEMORY.md` — full workflow, quality patterns, code snippets, skill evolution notes
- **Final output**: `Assignment_1_Sephora_Case_FINAL.docx`
- **V2 generator**: `generate_case_v2.py` (reference implementation)
- **Assignment materials**: `Assignment 1/` subfolder (instructions, rubric, structural guide)

## Workflow Summary

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

## Planned Skill

Target: `masters-writeup.md` — generic skill covering academic case write-ups, professional strategy memos, and executive briefs. Three format presets (academic/professional/executive). PROJECT_MEMORY.md has full spec.
