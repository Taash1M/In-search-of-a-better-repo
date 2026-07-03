---
name: Q1 Start Deck
description: Q1+Q2 Strat data slides (donut, initiative cards, Fabric); Q2 update done — status-grouped + 2 strat-grouped variants, awaiting user pick (2026-06-26)
type: project
originSessionId: aa210407-a09e-461f-aa2f-83d0e2fa4475
---
## Q2 UPDATE (2026-06-26)

Reused the Q1 2-slide design to build the **Q2 data slides** for the broader `<ORG> IT 2026 Strat _Q2.pptx` deck.

- **Source**: `<USER_HOME>/OneDrive - <ORG>\AI\Strat\Data\Q2\Apr-May-June Deliverables.xlsx` — 3 tabs (Sheet1, May-Week2, June), ~24 deliverables w/ cross-tab dupes. Treated **"Done"="Completed"**. ~19 completed, ~11 in-flight.
- **File is OneDrive-locked** → `cp` to `%TEMP%` before openpyxl (shutil.copy hits PermissionError; `cp` works).
- **Excel cp**: `<USER_HOME>/AppData\Local\Temp\q2_data.xlsx`.

### Deliverables built (all in `…\AI\Strat\Data\Q2\`)
1. **`Drafted Q2.pptx`** (status-grouped, 2 slides) — UPDATED IN PLACE from Q1 leftover content. S1 Q2 Delivered: KPI 19/4/40%, 5 marquee highlights (UBI Funnel 8.8→5GB & 20→12min, Revenue stream 50% SLA, Account 360 Neo4j + Account Search AI, <ORG_PARENT> GL + Kaizen, AI GPT/Claude + 6 integrations), recomputed category bars (OpEff 8/12, BizEnable 7/13, FinAcc 1/2, CostOpt 3/5). S2 Q3–Q4 Roadmap: rebuilt 12-card grid clean (removed orphan Q1 shapes), KPI 10/2/1/13, Fabric callout. Footers → Q2 / Apr–Jun 2026.
2. **`Q2 Strat-Grouped (2-slide).pptx`** — NEW. 2 slides, 2 pillars each, full-text badges.
3. **`Q2 Strat-Grouped (1-slide).pptx`** — NEW. 1 slide, 4 pillars side-by-side, status dots + legend.

### Strategic buckets (used in both strat-grouped variants, 6 projects each, capped)
- **Infrastructure & Platform** (navy 1B4F72): UBI Funnel opt✓, Revenue stream 50%✓, MS Fabric(Planning), ADB Unity Catalog(Ideation), Azure Resource cleanup, Power Automate→Logic Apps
- **Business Enablement & Commercial** (green 1E8449): <ORG_PARENT> GL✓, President's Kaizen✓, IIR✓, SMC/RMC, Growth IQ, Inventory Rec Tool
- **AI & Advanced Analytics** (purple 7D3C98): GPT/Claude✓, Account 360 Neo4j✓, Account Search AI✓, Tech Mentor✓, Account 360 P2, VoV Phase 2
- **Data Integrations & Operations** (gold B9770E): TMO✓, WIP Jobs CoC✓, CSAT rewire✓, Employee/Shipping✓, Brazil Backlog, eMaint

### Status
**AWAITING USER PICK** among the 3 drafts. After pick → inject winner into `<ORG> IT 2026 Strat _Q2.pptx` **slides 19–20** (currently still carry Q1 content). User explicitly said NOT to inject yet.
- Build scripts: `%TEMP%\build_q2.py` (status-grouped in-place edit), `%TEMP%\build_q2_strat.py` (both strat variants).
- Backup of pre-edit Drafted Q2: `%TEMP%\Drafted_Q2_BACKUP.pptx`.
- 1-slide gotcha FIXED: 4 narrow columns can't fit bucket name + count chip on one line → overlap; use 2-line centered header (`show_count=False`) + taller header (HH 0.58).
- All variants passed programmatic layout QA (0 OOB, 0 overlap, 0 tiny-text) + PNG visual check.

## Overview

Update the "Data Related Slides" (24 & 25) in the Q1 strategy deck with content from the March impact deliverables Excel, plus a visual upgrade. Three standalone variation PPTXs built with an executive summary slide, then a focused 2-slide update (Q1 Summary + Q2-Q4 Upcoming) with UBI Data Coverage donut chart and initiative cards.

**Why:** Current slides show UBI-pipeline projects in a plain table. Need to reflect broader AI & Data team accomplishments with an executive-grade look.

**How to apply:** PptxGenJS (Node.js) for slide creation, python-pptx for injection/analysis and programmatic layout QA. Consulting-style design (McKinsey/BCG action titles, 60-30-10 color rule).

## Key Facts

- **Project dir**: `<USER_HOME>/OneDrive - <ORG>\AI\EM\Q1 Start Deck\`
- **PPTX**: `<ORG> IT 2026 Strat _Q1.pptx` (25 slides, 16:9) — original deck, not yet modified
- **Target insert file**: `<ORG> IT 2026 Data_Updates for _Q1.pptx` — final destination, not yet touched
- **Excel source**: `Data and AI Updates_March impact deliverables.xlsx`
  - "Slide Data Review" tab: Raw extraction of 18 projects from slides 24-25
  - "Improved Draft" tab: Rewritten content grouped by category with color-coded sections
- **Target slides**: 24 ("UBI - 2026 Q1 Results") and 25 ("UBI - 2026 Q2-Q4 Initiatives")
- **Created**: 2026-04-08
- **Status**: Q1 Summary + Q2-Q4 Upcoming 2-slide PPTX built, 3-stage QA passed (2026-04-10)

## Deliverables (all in project dir)

- **`Q1_Summary_and_Q2Q4_Upcoming.pptx`** (185KB) — 2-slide focused update (2026-04-10)
  - **Slide 1 (Q1 Summary)**: Action title, 3 KPI cards (8 delivered, 4 categories, $5-6K savings), 5 delivered highlights, DOUGHNUT chart for UBI Data Coverage (Oracle EBS 40%, CRM 13%, Contact Center 8%, VOC 8%, Subsidiary 9%, Financial 17%, Not Yet Covered 5% red), 4 category delivered bars
  - **Slide 2 (Q2-Q4 Upcoming)**: Action title, 4 KPI cards (7 in progress, 1 UAT, 2 discovery, 1 Fabric), 11 initiative cards in 2-column layout with status badges, MS Fabric callout bar (Business Enablement + Infrastructure Stabilization)
  - 3-stage QA passed: content, programmatic layout (0 OOB, 0 margin, 0 overlap, 0 tiny-text), visual bounds check
- **`Variation1_TableByCategory.pptx`** — 7 slides (Title → Exec Summary → 5 category table slides)
- **`Variation2_ByStatus.pptx`** — 10 slides (Title → Exec Summary → Section dividers + Delivered/In Progress/Discovery)
- **`Variation3_VisualCards.pptx`** — 8 slides (Title → Exec Summary → KPI dark slide → Category card slides)
- **`ExecSummary_Slide.pptx`** — Standalone exec summary, also injected as slide 2 into all 3 variations

## Build Scripts (all in %TEMP%)

- **`build_q1_updated_slides.js`** — ~440 lines, Q1 Summary + Q2-Q4 Upcoming (latest, 2026-04-10)
- **`build_variations_v2.js`** — ~500 lines, builds all 3 variations from 18-project data array
- **`build_exec_summary.js`** — ~300 lines, light consulting-grade executive summary
- **`inject_exec_summary.py`** — python-pptx XML manipulation to insert exec summary as slide 2
- **`render_slides.py`** — PowerPoint COM automation for PNG export at 1920x1080

## Design Specs

- **Layout**: LAYOUT_WIDE (13.333" × 7.5"), 0.6" margins
- **Palette**: Navy #1B3A5C, Gold #FFC000, category-specific colors
- **Fonts**: Arial Black (headers), Arial (body)
- **Status colors**: Delivered #1E8449, In Progress #2E86C1, UAT #17A589, Discovery #F39C12, Ongoing #5B6770

## New Column Structure

| Column | Source | Approx Width |
|--------|--------|-------------|
| Project | Topic/Project from Detailed Status | ~2.0" |
| Project Description | Key Points column | ~3.5" |
| Key Deliverables | Deliverable column | ~3.5" |
| Benefit | Bucket label + brief note (composed) | ~3.3" |

## Pending Work

1. **User review** — Review Q1 Summary + Q2-Q4 Upcoming PPTX for content/direction accuracy
2. **Final insert** — Merge chosen slides into `<ORG> IT 2026 Data_Updates for _Q1.pptx`
3. **Variation selection** — Original 3 variations still available if user wants different format

## Content Scope

- **18 existing slide projects**: Five 9, VOC, FRS, SSD, Purchase Reqs, VT, Landauer, UBI Costs, IIR, PLM, SCADA, SMC/RMC, Emaint, Brazil, TMO, Databricks (all rewritten in exec techno-functional tone)
- **8 AI & Data Excel projects**: Not yet merged — only SMC/RMC overlaps
- **Benefit categories**: Operational Efficiency, Business Enablement, Financial Accuracy, Cost Optimization (with Cost Avoidance merged in)

### Decisions Made (2026-04-09)

1. **Slide titles**: Keep "UBI Data Team" — scope is data
2. **All 18 projects rewritten** in executive techno-functional tone matching Executive Summary tab style
3. **Grouped by category** with color-coded sections in the "Improved Draft" tab

## QA Fixes Applied (for reference if rebuilding)

- **Q1 Updated (2026-04-10)**: Programmatic layout QA caught S2 last initiative card at 7.58" (OOB), footer at 7.40" (margin violation). Fixed: cardH 0.78→0.66, rowGap 0.10→0.05, dynamic callout positioning, footer y adjusted. Re-run: 0 issues.
- V1: Fixed row heights (use 1.05" fixed, not dynamic), status column top-aligned
- V2: Added column headers on every content slide, "(cont.)" for split categories, max 4 rows/page
- V3: Always 3 columns, explicit text arrays for KPI colors, thicker category bars (0.10"), distinct UAT color
- Exec Summary: Light white bg, no issues found in QA

## File Access Note

Excel file may be locked by OneDrive/Excel — copy to `<USER_HOME>/AppData\Local\Temp\q1_data.xlsx` before reading with openpyxl.
