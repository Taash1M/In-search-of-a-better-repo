---
name: AI BI Tool
description: Internal AI-powered BI tool — multi-agent architecture (Supervisor + 5 Workers), SharePoint UI, PBI + OneDrive connectors, zero data storage, 10 project-specific agentic skills.
type: project
---

## Project Directory
`C:\Users\tmanyang\OneDrive - Fortive\Claude code\AI BI Tool\`

**Why:** New project started 2026-04-05 to build an internal BI assistant accessible via SharePoint. Users point at PBI models or OneDrive files, answer a 3-5 question interview, then conversationally create BI reports.
**How to apply:** All artifacts stored in this directory. Anton repo cloned as subfolder. Each capability wrapped as a dedicated agentic skill file.

## Architecture
Multi-agent: Supervisor (Sonnet) → Data Agent (Haiku, PBI+OneDrive), Analysis Agent (Sonnet), Visual Agent (Sonnet, Plotly+Fluke theme), Export Agent (Haiku, CSV+Excel), Session Agent (Haiku, Cosmos DB).

## Key Design Decisions
- **SharePoint interface** (SPFx web part, Streamlit iframe for MVP)
- **Zero data storage** — files stay in PBI/OneDrive, read in-memory via API
- **3-5 question interview** before any analysis
- **Export: CSV + beautified Excel + HTML** (not PPTX/DOCX for MVP)
- **10 project-specific agentic skills** — cherry-picked from existing skills but standalone
- **Per-user session recall** via Cosmos DB (metadata only, no raw data)

## 10 Agentic Skills (Planned)
`ai-bi-supervisor`, `ai-bi-auth`, `ai-bi-onedrive-connector`, `ai-bi-duckdb-analytics`, `ai-bi-fluke-theme`, `ai-bi-pbi-connector`, `ai-bi-dax-expert`, `ai-bi-interview`, `ai-bi-session`, `ai-bi-excel-export`

## Status
DESIGN phase (v0.2). Implementation roadmap: 5 phases over 10 weeks. Skills cherry-picked from: excel-create, ubi-dev, agentic-deploy, LLM Gateway, beautification skills.
