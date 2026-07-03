---
name: Daily Access Request Scan Workflow
description: Repeatable workflow to scan Outlook inbox for Claude Code access requests and update the tracking DOCX — explorer.exe trick, DASL filters, python-docx table manipulation
type: reference
originSessionId: dcc84167-b07b-42e7-8e3d-d14ad0f99f66
---
## Daily Workflow (3 steps)

### Step 1: Scan Outlook Inbox
Use `scan_inbox.py` via the explorer.exe cross-session trick:

```
# Files (already exist):
<USER_HOME>/OneDrive - <ORG>\AI\Claude code deployment\requests\scan_inbox.py
<USER_HOME>/OneDrive - <ORG>\AI\Claude code deployment\requests\run_scan.bat

# Launch from <ADMIN_USER> session:
explorer.exe "<USER_HOME>/OneDrive - <ORG>\AI\Claude code deployment\requests\run_scan.bat"

# Wait ~15-20 seconds, then read results:
cat "<USER_HOME>/OneDrive - <ORG>\AI\Claude code deployment\requests\scan_results.log"
```

The script searches Inbox for emails with "claude", "Claude Code", "CLI access", "LLM access", "AI Access" in subject or body, received in 2026. Returns up to 100 results sorted newest-first with sender, date, subject, TO, and 300-char body preview.

### Step 2: Identify New Access Requests
Compare scan results against the current DOCX table. Look for:
- Direct requests ("I would like access", "requesting access", "please enable", "can you provide claude code to")
- Forwarded requests from Eshwari Mulpuru (CC'd people = the requestees)
- Teams chat notifications (from `system-notification@<ORG_PARENT>.com`) containing access requests

Filter OUT:
- Setup guide thread replies (existing team members)
- Microsoft PIM notifications
- Outlook Reaction Digests
- EOD status updates
- Meeting accepted/declined notifications
- Internal team discussions (no new access request)

### Step 3: Update the DOCX
**File**: `requests/Claude_Code_Access_Requests_Summary.docx`

Use python-docx to:
1. Read current table state
2. Add new rows (copy XML from template row, update cell text)
3. Sort: Fulfilled first (chronologically), then Pending (chronologically)
4. Update header stats (P1: total requests count, P8: pending seats breakdown, P11: recommendation seats)
5. Save

**Sort function:**
```python
from datetime import datetime
def parse_date(d):
    return datetime.strptime(d.strip() + ' 2026', '%b %d %Y')

def sort_key(row):
    status = row['cells'][4]
    date_val = parse_date(row['cells'][1])
    return (0 if status.startswith('Fulfilled') else 1, date_val)
```

**Paragraphs to update:**
- P1: `As of {date} | {N} distinct access requests | {M} new since last update`
- P8: `Estimated New Seats Needed: {X} pending ({breakdown})`
- P9: `Demand Trend: March: 2 requests | April: {N} requests — ...`
- P11: `Fulfill pending requests ({X} seats) to maintain momentum...`

### Seat Count Rules
- Default: 1 seat per requester unless email body says otherwise
- Check CC line for group requests (Eshwari's pattern: CC = the people to enable)
- Check body for "+N more" language (e.g., Moeller "+4 more for FP&A" = 5 total)
- Check body for team lists (e.g., Bridges "5 people + himself" = 6)
- "We are requesting" without a count = 1 (conservative)

### Key Gotchas
- python-docx run manipulation: find runs containing target text, replace `run.text`
- When adding rows: `deepcopy` the XML from an existing row, update `w:t` elements
- Sort requires removing all data rows from `tbl_elem`, then re-appending in order
- Paragraphs with `FP&A`: the `&` can get mangled — always verify after save
- The explorer.exe trick: exit code 1 is normal (explorer returns immediately), poll the log file

## Current State (2026-05-28)
- **26 total requests**: 12 fulfilled (~21 seats), 12 pending (~23 seats), 2 routed to GitHub Copilot
- **Fulfilled**: Knabe(1), Bergstrom(1), Erickson(1), Moeller(5), Johnston(1), Kalra(1), Eshwari team(6), Treg(1), Nebeker(1), Hartmann(1), Kathleen Wang(1), **Rachel King(5)** (moved from Pending May 28)
- **Pending**: Cornely(1), Schultz(2), Bridges(6), McNeal(1), Straka(1), Poondla(1), Schuster(1), Johnson(1), Pilla(1), Jack Henry(1), **Venkata Mahesh Nandam(1)** (new May 28), **Marco Rossi(1)** (new May 28)
- **Routed to GitHub Copilot**: Andy Nguyen, Todd Tomlinson (+Sandeep)
- **Undocumented SG additions**: Joe Seefried, Gavin Smith, Kathleen Wang (all node-3, no request on file)
- **Enterprise rollout**: <ORG_PARENT> signed enterprise Claude contract with Anthropic. Wave 1 (<ORG>, FHS, <ORG_PARENT> corporate) live May 26, Wave 2 (Gordian, ISC, ServiceChannel, Censis) May 27, Accruent+Provation May 28
- **Enterprise workbook**: `Enterprise Licenses/Claude Users Access - <ORG>.xlsx` — 70 Wave 1 users across 11 orgs (Eligible/Blocked/Wave 1 tabs)
- **Enablement notice**: `Enterprise Licenses/Claude Code enablement notice.docx` — consultant-grade 2-pager with FAQ for C-Suite/Directors
- **Also check**: .msg files and .docx files in the requests folder for non-email submissions
- **Eshwari directive (Apr 22)**: All CLI requests should be routed through her for approval
