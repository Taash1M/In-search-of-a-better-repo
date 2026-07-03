---
name: gl-investigation-inc1555542
description: "GL INC1555542 — accounts 410120/410150/410700 mis-mapped Expense→Revenue; root cause Oracle source + no Silver override; fix CASE WHEN ACCOUNT LIKE '4%'; 5 artifacts + 330-row GL/Revenue STM delivered"
metadata: 
  node_type: memory
  type: project
  originSessionId: 26203117-c07b-47a6-b7d2-fc239094e124
---

# GL Investigation (INC1555542)

- Accounts 410120, 410150, 410700 incorrectly mapped as Expense instead of Revenue
- Root cause: Oracle source misconfiguration + no Silver-layer override
- Fix: `CASE WHEN ACCOUNT LIKE '4%' THEN 'Revenue'` in `Refresh_DimGlAccount.sql`
- Delivered: `<USER_HOME>/OneDrive - <ORG>\ADHOC\UBI\GL INC1555542\` (5 artifacts)
- GL/Revenue STM completed: 330 rows x 45 columns, 15 table groups

Related: [[ubi-platform-key-facts]] · [[alex-b-fortive-gl]]
