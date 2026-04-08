---
name: Daily Report (Weekly Close-Out)
description: Weekly project status reports for 8 active projects. DOCX close-out + Excel carry-forward format. Fluke-branded. Executive Summary redesigned for C-suite.
type: project
---

## Location
- **Weekly reports**: `C:\Users\tmanyang\OneDrive - Fortive\ADHOC\UBI\Daily Report\`
- **Updates / working versions**: `C:\Users\tmanyang\OneDrive - Fortive\ADHOC\UBI\Daily Report\Updates\`

## Reports Generated
- **2026-03-27 DOCX close-out**: `2026-03-27/Daily_Update_20260327.docx` — final DOCX-format report
- **2026-03-29 Excel carry-forward**: `2026-03-29/Daily_Update_20260329.xlsx` — beautified Excel with 4 sheets (Executive Summary, Detailed Status, Next Steps, Change Log)
- **March impact deliverables**: `Updates/Data and AI Updates_March impact deliverables.xlsx` — user-refined version of the C-suite Executive Summary

## Generator Scripts
- `generate_daily_update_20260327.py` — DOCX generator (python-docx, Fluke branding)
- `generate_daily_excel_20260329.py` — Excel generator (openpyxl, carry-forward format)
- `build_exec_summary.py` — Executive Summary redesign script (openpyxl)

## Executive Summary Redesign (2026-03-31)
- **Purpose**: C-suite / president's letter — show only high-impact deliverables, not full project list
- **Columns**: Delivery Month | Project | Business Need | What Was Done | Contributors | Benefits | Status
- **March 2026 entries** (6 rows): AI Charter, FRS Salesforce→UBI, Power Automate Use Case, Inventory Recommendation Tool, Fleet Dashboard, Claude Code Enablement
- **Delivered projects** sourced from `summary info.xlsx` (separate file with Project #, Name, Description, Business Benefit, Business POC, Status)
- **Status styling**: Delivered=dark green, On Track=green, In Progress=blue (white bold text)

## 8 Active Projects (as of 2026-03-29)
1. AI Charter
2. Claude Code Enablement
3. AI Backlog
4. Account Linkage (MDM)
5. UBI Projects (CPQ SMC/RMC)
6. Procurement Kaizen
7. AI Delivery Plan
8. AI Acceleration

## Format
- **DOCX**: Landscape, Calibri, Fluke Yellow (#FFC600), 3 sections (Executive Summary, Detailed Status, Key Next Steps)
- **Excel**: 4 sheets, status badge coloring (Green/Blue/Amber/Red), dropdown validation for Status column, carry-forward design for weekly updates
- **Executive Summary**: 7-column impact table, alternating row shading, landscape print-ready
