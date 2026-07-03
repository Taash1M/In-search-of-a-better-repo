---
name: reference_servicenow_api
description: "ServiceNow Production REST API access — creds location, base URL, readable vs blocked tables, query patterns, and sc_item_option variable gotcha"
metadata:
  node_type: memory
  type: reference
  originSessionId: e0f7108b-700f-475d-b7fe-0541a1fb0e73
---

ServiceNow Production REST API (read-only service account, used for [[project_servicenow_claude_licenses]]).

- **Base URL:** `https://fortive.service-now.com` | Table API: `/api/now/table/<table>` | Stats: `/api/now/stats/<table>?sysparm_count=true`
- **Creds file (plaintext, user-maintained):** `<USER_HOME>/OneDrive - <ORG>\AI\Onboarding Tools\ServiceNow Credetials prod.txt` — user `flkbiapiuser` (BI API account). Dev instance: `https://fortivedev.service-now.com` (<USER> SSO).
- **Auth:** HTTP Basic. The password contains `^|` chars — single-quote it in bash: `curl -u 'flkbiapiuser:<pw>' ...`. Account is a **BI/reporting account** — broad read on task/RITM/sys_user but **ACL-scoped elsewhere**.

**Readable:** `sc_req_item`, `sc_task`, `task`, `sc_item_option` / `sc_item_option_mtom` (form variable VALUES — see gotcha below), `sys_user` (incl. `manager`, `title`, `department` — manager chain walkable), `cmn_location`, `cmn_department`.

**NOT readable (returns empty `{"result":[]}` with HTTP 200, not 403):** `rm_story` (and likely rm_* PM tables). Don't mistake the empty result for "record not found" — the account simply can't see the table.

## CRITICAL GOTCHA — Reading Form Variable Values (sc_item_option)

**Symptom:** All RITMs appear to have the same blob of values, or the blob contains completely unrelated records.

**Root cause:** `sc_item_option` is a **shared global table** of per-submission answer records. The `IN (sys_id1, sys_id2, ...)` batch query pattern returns records from the table in general — NOT filtered to your specific RITM's options. The 50-record limit silently returns unrelated rows from other submissions.

**Correct two-step pattern (confirmed working 2026-06-30):**

```python
# Step 1: get the sc_item_option sys_ids linked to this RITM
mtom = api(f"{BASE}/api/now/table/sc_item_option_mtom"
           f"?sysparm_query=request_item%3D{ritm_sysid}"
           f"&sysparm_fields=sc_item_option&sysparm_limit=50").get('result', [])
opt_ids = [row['sc_item_option']['value'] for row in mtom]

# Step 2: fetch each sc_item_option record INDIVIDUALLY — never use IN query
vals = []
for oid in opt_ids:
    v = api(f"{BASE}/api/now/table/sc_item_option/{oid}"
            f"?sysparm_fields=value&sysparm_display_value=all"
    ).get('result', {}).get('value', {}).get('display_value', '') or ''
    if v.strip():
        vals.append(v.strip())
blob = ' | '.join(vals)
```

**Why `IN` fails:** `sc_item_option` records are identified by a sys_id that is unique per submission-answer, but the REST `IN` filter seems to hit a caching/ACL layer that returns the first 50 records matching a broader scope. Individual GETs bypass this and return the exact record.

**The `sc_item_option_mtom` table** (the join table) has no `value` field itself — it only has `request_item` (RITM sys_id) and `sc_item_option` (FK to the answer record). The answer text is always in `sc_item_option.value`.

## General Gotchas

- Form-field **labels** (`item_option_new.question_text`) don't dot-walk through `sc_item_option_mtom` — come back blank. Workaround: pull all variable VALUES per RITM, concatenate into one blob, and keyword-search the blob (labels not needed to find content).
- Use `sysparm_display_value=all` to get both `display_value` and `value` (raw sys_id) per field.
- `python3` on this Windows box is a Windows Store stub (exits 49/non-functional). Use `python`. Bash `/tmp` != `C:\tmp` — scripts written to `C:\tmp` must be run with that absolute path.
- Catalog item sys_id for "Data And Analytics Request": `4f192d371bcbbd505e38ff3f034bcbe2`

## Reusable Script

Full working script (pull all RITMs, screen for Claude, resolve L1 chains, build XLSX):
`<USER_HOME>/OneDrive - <ORG>\AI\Claude Licenses\ServiceNow for Claude\pull_snow_claude_requests.py`

Run: `python pull_snow_claude_requests.py` from that folder.
