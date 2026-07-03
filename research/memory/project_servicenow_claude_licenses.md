---
name: project_servicenow_claude_licenses
description: ServiceNow Claude access workstream — 30 RITMs (23 open), 20 net-new pending July additions cross-referenced vs June spend, Excel + L1 approval email built (2026-06-30).
metadata:
  node_type: memory
  type: project
  originSessionId: e0f7108b-700f-475d-b7fe-0541a1fb0e73
---

ServiceNow "Claude Licenses" workstream. Artifacts folder: `<USER_HOME>/OneDrive - <ORG>\AI\Claude Licenses\ServiceNow for Claude\`. Data pulled READ-ONLY from ServiceNow Production — see [[reference_servicenow_api]] for creds/table-access facts.

**Task 1 — Escalation (2026-06-24).** SCTASK1354578 → STRY0260370 (parent RITM0873057 / REQ0880466): request to change the AI-tool catalog form (approval routing L2→Eshwari→<ORG> AI Team; add Claude Code/Codex/Amazon Q/Other to the dropdown). Opened 23 Apr 2026, closed-complete 11 May (story created, handed to demand-mgmt per KB0013371); 18 Jun follow-up unanswered. Built escalation as DOCX + Outlook-ready HTML (14-row timeline from ticket journals + 4 dated asks). `rm_story` not readable by API account so STRY status not pulled — flagged.

**Task 2 — Consolidated Claude requester roster (refreshed 2026-06-30).** Source = catalog item "Data And Analytics Request" (sys_id `4f192d371bcbbd505e38ff3f034bcbe2`). Screened ALL 92 submissions (up from 73 on 24 Jun); 30 mention Claude (up from 11). 23 Open, 7 Closed-Incomplete. Output `Claude_Access_Requests_Consolidated.xlsx` (3 sheets: requests w/ dates+status, Approval Summary by L1, Notes). Script saved: `ServiceNow for Claude\pull_snow_claude_requests.py`.

**Open by L1 (2026-06-30):**
- Jabeen, Azra (Finance): 10 open
- Mulpuru, Eshwari (IT): 3 open
- Nowick, Neal (Operations): 2 open
- Hack, Jay (eMaint): 2 open
- Thuvara, Vineet (Product): 2 open
- Prentice, Sue-Ann (Marketing): 2 open
- Moore, Steven (Commercial Americas): 1 open
- Chillman, Alex (Engineering): 1 open

**L1 definition (key):** L1 = requester's HIGHEST manager before the President, NOT the direct manager. Valid L1 list = row 1 of the "Eligible" sheet in `...\Claude Licenses\Archive\Enterprise Licenses\Claude Users Access - <ORG>.xlsx` (Azra Jabeen/Finance, Neal Nowick/Ops, Jay Hack/eMaint, Steven Moore/Commercial, Alex Chillman/Eng, Katie Marquardt/HR, Sue-Ann Prentice/Mktg, Vineet Thuvara/Product, Kathryn Sweers/Legal, Parker Burke/CEO, Eshwari Mulpuru/IT). Resolved by walking `sys_user.manager` chain until hitting one. Gotcha: spreadsheet "Neal Norwick" = ServiceNow "Nowick, Neal" (alias both). Sansoucie chain tops at Olumide Soroye (President & CEO of a different OpCo) → no <ORG> L1, needs manual call.

**CRITICAL GOTCHA — sc_item_option variable values (discovered 2026-06-30):**
- Variable values live in `sc_item_option.value` — NOT in `sc_item_option_mtom` directly.
- Two-step join: `sc_item_option_mtom` (per RITM, gives list of option sys_ids) → `sc_item_option` (one record per option, has the value field).
- **Must fetch each `sc_item_option` record INDIVIDUALLY** — using a `sys_id IN (...)` batch query returns random unrelated records from the shared options table. The IN approach silently returns wrong data every time.
- The working pattern: `mtom?request_item=SYSID` → get opt_ids → loop `sc_item_option/OPT_SYSID` → collect `value.display_value`.

**Script:** `<USER_HOME>/OneDrive - <ORG>\AI\Claude Licenses\ServiceNow for Claude\pull_snow_claude_requests.py`
- Self-contained, reads creds from `ServiceNow Credetials prod.txt`, writes directly to `Claude_Access_Requests_Consolidated.xlsx` in same folder.
- Run: `python pull_snow_claude_requests.py`

---

**Task 3 — July 2026 net-new additions review (2026-06-30).**

Cross-referenced all 23 open RITMs against the 77 June active users (from `June 2026/<ORG> June 24 2026 spend Report.xlsx`). Result: **20 net-new users** pending provisioning (not yet in June spend), **2 already active** (open RITM but already provisioned: evan.nebeker, venkata.mahesh.nandam — no action needed).

**Neal Nowick email context (received 2026-06-30 05:18 AM):** Neal replied to the L1 nomination email declining to reconcile his list ("end of quarter, not going to hunt people down"). His direction: keep everyone currently active, follow up with individuals directly (re: Esven Carreno, Lloyd Hung who have no SNOW RITMs on file). Net result: no new nominations and no removals from Neal's org — only alex.wanamaker (RITM0889823, pre-existing approved RITM) advances.

**Net-new pending by L1 (July 2026):**
- Jabeen, Azra (Finance): 10 — marisa.buchanan, christine.mcgee, henry.ly, chiaki.yoshikawa, kerin.chun, riley.staheli, grace.abbott, tyler.montana, jeri.staheli, srushti.shah
- Mulpuru, Eshwari (IT): 2 — josh.ciaramitaro, li.huang
- Chillman, Alex (Engineering): 1 — vinay.hg
- Moore, Steven (Commercial Americas): 1 — brian.hunt
- Thuvara, Vineet (Product): 2 — tako.feron, filip.bras
- Hack, Jay (eMaint): 2 — matt.james, rucha.deshpande
- Prentice, Sue-Ann (Marketing): 1 — randy.tano
- Nowick, Neal (Operations): 1 — alex.wanamaker

**Deliverables saved to `<USER_HOME>/OneDrive - <ORG>\AI\Claude Licenses\July 2026\`:**
- `Claude_July2026_Pending_Additions.xlsx` — 9-tab workbook: summary tab (all 20 net-new grouped by L1, 2 already-active greyed) + 1 tab per L1 with Approve/Reject column for L1 to fill in
- `Email_L1_Approval_Request.html` — L1 approval request email template (open in browser, paste into Outlook); one email per L1, attach their tab

**Seat cap check:** 77 current + 20 pending = 97 — still within 150 cap. 53 seats remaining after additions.
