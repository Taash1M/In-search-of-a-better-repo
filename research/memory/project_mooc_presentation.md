---
name: MSIS 511 MOOC Presentation
description: Master's group presentation — MOOCs will NOT disrupt UW, Team 5 Purple, v3 FINAL with 16 slides (12 main + 4 appendix), 551 shapes, 3-stage QA passed (2026-04-21)
type: project
originSessionId: faaf5843-504f-4b3d-9ee4-577c3fbf4d12
---
## Overview

MSIS 511 case presentation arguing that MOOCs will NOT disrupt the University of Washington's business model. Technology augments and supports UW's existing model.

**Why:** Assignment from UW professor — analyze whether technology will disrupt top institutions. Our team argues the "will not disrupt" position.

**How to apply:** Project dir `<USER_HOME>/OneDrive\Taashi M\UW\Q4\511\`. Research in `research/` subdirectory. Build script generates PPTX using Veritas clean design adapted with UW colors (Purple #4B2E83, Gold #B7A57A).

## Team
- **Course**: MSIS 511, Q4
- **Team**: 5 Purple
- **Members**: Taashi Manyanga (+ others TBD)
- **Position**: MOOCs will NOT disrupt UW

## Deliverables (2026-04-21)
- **v1**: `MOOC_Presentation_v1.pptx` — 12 slides, 542 shapes, text-only, scored 82/100
- **v2**: `MOOC_Presentation_v2.pptx` — 12 slides, 467 shapes, 4 charts integrated, speaker notes on all slides, 3-stage QA passed
- **v3 FINAL**: `MOOC_Presentation_v3.pptx` — 16 slides (12 main + 4 appendix), 551 shapes, slide numbers on all slides, 4 external-source appendix charts, 3-stage QA passed
- **PDFs**: `MOOC_Presentation_v2.pdf`, `MOOC_Presentation_v3.pdf`
- **Charts (original 4)**: `charts/` — completion_rates.png, platform_valuations.png, uw_applications.png, jtbd_radar.png
- **Charts (appendix 4)**: `charts/` — bls_education_pays.png, reich_science_2019.png, uw_revenue.png, paper_ceiling.png
- **Build scripts**: `build_mooc_v1.py`, `build_mooc_v2.py`, `build_mooc_v3.py`, `charts/make_appendix_charts.py`
- **QA exports**: `qa_slides/` (v1), `qa_slides_v2/` (v2), `qa_slides_v3/` (v3)

## v2 → v3 Improvements (FINAL)
- Added slide numbers (1-16) on all slides in bottom-right corner
- Added 4 appendix slides (slides 13-16) with published external data visualizations:
  - **A: BLS Education Pays** — Earnings & unemployment by education level (BLS 2024)
  - **B: The MOOC Pivot** — Reich & Ruipérez-Valiente (Science, 2019) completion/retention decline
  - **C: UW Revenue Diversification** — FY2025 pie chart from UW Annual Financial Report
  - **D: The Paper Ceiling** — Harvard/BGI (2024) skills-based hiring rhetoric vs. reality
- Each appendix slide has: APPENDIX header label, gold divider, chart (left), key findings (right), insight box (bottom), full source citation, speaker notes
- PhD-level rubric gap: "all visuals self-created" — RESOLVED with 4 external published sources

## v1 → v2 Improvements
- Added 4 matplotlib charts (completion rates, platform valuations, UW applications, JTBD radar)
- Added Agenda + Thesis slide (slide 2)
- Condensed opposition from 6 to 4 arguments
- Added speaker notes on all 12 slides
- Added risk acknowledgment section (slide 10)
- Added COVID Q&A (6 total anticipated questions)
- Reduced text density throughout
- PhD-level rubric gap: "no images" — RESOLVED

## Research Library (6 files, 2026-04-21)
1. `01_general_articles.md` — 6 articles (NYT, CNBC, WSJ, IHE, Digitopoly)
2. `02_pro_disruption_articles.md` — 6 opposition articles with counterarguments
3. `03_anti_disruption_articles.md` — 5 supporting articles + 2 supplemental
4. `04_uw_specific_strengths.md` — Rankings, $1.73B research, enrollment, Seattle ecosystem
5. `05_mooc_data_and_trends.md` — Completion rates, platform failures, credential value
6. `06_disruption_theory_and_history.md` — Christensen framework, 180 years of precedent, employer data

## Key Arguments (6 pillars)
1. **Disruption theory doesn't apply** — Horn (Christensen's co-author) says selective universities are exempt
2. **UW serves 8 jobs, MOOCs serve 1** — JTBD framework: credential, research, network, experience, career, civic, identity
3. **MOOC data is damning** — 3% completion (declining), 52% never start, 12% return rate
4. **Disruptors failed** — 2U bankrupt, Udacity sold at 92% loss, Coursera stock -80%
5. **Employers prefer degrees** — 71% unfamiliar with MOOCs, <1 in 700 hires from degree removal
6. **180 years of precedent** — Radio, TV, CD-ROM, internet all predicted to disrupt education, none did

## Rubric Categories
Structure, Content, Analysis (quant+qual), Research, Q&A, Slide mechanics (titles, team info), Slide quality (text/image balance, readability)
