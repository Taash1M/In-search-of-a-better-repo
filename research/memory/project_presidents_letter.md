---
name: presidents-letter
description: "Monthly <ORG> IT president's letter — format, file location, section ownership, and writing conventions for Analytics (UBI) updates"
metadata: 
  node_type: memory
  type: project
  originSessionId: f671a56c-6a38-47dd-9bf6-fc7b222e1875
---

Monthly update document prepared for Parker Burke and Azra Jabeen (cc <ORG> L1 Team, <ORG_PARENT> CIO).

**File location:** `<USER_HOME>/OneDrive - <ORG>\Projects\UBI\<ORG> IT Monthly Update - {Month}.docx`

**Section we own:** "Analytics (UBI)" under the "Analytics (UBI) and AI Updates" heading. We do NOT touch the AI sub-section or any other part of the document.

**Source data:** Monthly deliverables Excel at `<USER_HOME>/OneDrive - <ORG>\Projects\UBI\{Month} Deliverables.xlsx` — Sheet1 has columns: Delivery Month, Project, Business Need, What Was Done, Contributors, Benefits, Status. May also have a second sheet for week-specific items.

**Bullet point format (List Paragraph style in DOCX):**
- Run 0: **Bold title** (project name)
- Run 1: line break (`w:br`)
- Run 2: Body text (not bold) — 2-4 sentences
- Pattern: define/explain the initiative → emphasize benefits → state status (delivered / milestone achieved / in progress)

**Writing conventions:**
- Humanified tone — no AI-sounding buzzword stacking, varied sentence length and structure
- First person plural ("we built", "we completed") is fine
- Status phrasing varies: "Delivered.", "In progress.", "TG0 milestone achieved; working toward TG1.", "Quick turnaround; delivered."
- Quantify where possible (%, hours, dollars, GB)
- Keep each bullet self-contained — reader shouldn't need context from other bullets

**DOCX structure (paragraph indices shift monthly — search by text, not index):**
- Section header: "Analytics (UBI) and AI Updates" (List Paragraph, bold)
- Sub-header: "Analytics (UBI)" (List Paragraph, bold)
- Empty paragraph
- UBI bullets (List Paragraph style, one per project)
- Empty paragraphs (Normal (Web) + Normal)
- "AI" sub-header (Normal, bold)
- AI bullets follow

**April 2026 update (9 bullets):**
1. IIR Integration in UBI — pipeline for capital project data, prototype to Commercial
2. CPQ / SMC / RMC Subscription Data Integration — tech specs done, TG0 passed, toward TG1
3. Lyra 2.0 — in-house VOC transcript replacement for EnjoyHQ
4. Revenue Stream Runtime Optimization — 50% SLA reduction (2h→1h)
5. UBI Funnel Semantic Model Optimization — 40% size + refresh improvement
6. Brazil Backlog Data Ingestion — new subsidiary pipeline
7. Power Automate → Azure Logic Apps Migration — multiple flows migrated
8. UBI Service & Operational Enhancements — Employee + Shipping fields, PD Gold views
9. President's Kaizen — Opportunity Tag Integration (FHS Commercial)

**May 2026 update:**

Section 9 now has both UBI and AI entries:

*Analytics (UBI):*
1. <ORG_PARENT> Corporate GL Reporting — Delivered. Self-service PBI replacing manual CSV export for 15 <ORG_PARENT> entities, 32-account mapping, ~4 hrs/month savings during close.

*AI (Taashi's entries — added under existing Sales Playbook, VoV, Account 360 entries):*
1. AI Charter Deployment (level 0) — umbrella entry with 2 sub-bullets:
   - AI Office Hours Launched (level 1) — May 27 inaugural session, 7 agenda items, 6 presenters, monthly cadence May–Nov
   - Claude Enterprise License Rollout — Wave 1 (level 1) — 70 users across 11 orgs, SSO stabilization, enablement comms, migration guidance

**Template file:** `<USER_HOME>/OneDrive - <ORG>\CIO Deliverables\President's Letter\<ORG> IT Monthly Update - Template.docx`
**Backup:** same path with `.bak` extension
**Helper scripts:** `update_template.py` (AI section), `update_ubi_section.py` (UBI section) — both in same folder

**How to apply:** When doing the next month's update, read the deliverables Excel, draft bullets in the same humanified style, and use python-docx to replace the UBI bullets between the "Analytics (UBI)" sub-header and the "AI" sub-header. Use `copy.deepcopy` of an existing List Paragraph element as the template, clear runs, and rebuild with bold title + br + body text. For sub-bullets (level 1), use the `make_paragraph()` helper from `update_template.py`.
