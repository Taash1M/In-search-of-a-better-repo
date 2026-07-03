---
name: ai-gov-policy
description: "<ORG> AI Governance Policy — Section 5.7 (User Responsibilities) authored, humanified, and published to SharePoint <ORG_ABBR>-InfoSec (2026-06-30)"
metadata: 
  node_type: memory
  type: project
  originSessionId: 3c3e29ce-c60d-48ed-92cd-f37edb2fcec8
---

## <ORG> AI Governance Policy

Canonical document: `<ORG> AI Gov Policy.docx` on SharePoint at `<ORG_PARENT>.sharepoint.com/sites/<ORG_ABBR>-InfoSec`.
Local working copy: `<USER_HOME>/OneDrive - <ORG>\AI\AI Governance\`.

**Why:** Policy previously covered org-level approval, security, legal, and risk but had no explicit individual user accountability section. <ORG_PARENT> governance requirements flagged the gap.

**How to apply:** Any future policy edits should follow the CLAUDE.md conventions in the working folder — clone reference paragraphs rather than creating from scratch, read text via `.//w:t`, verify additive-only with difflib before publishing.

## What was built (2026-06-30)

Added **Section 5.7 — User Responsibilities and Obligations When Using AI** (46 paragraphs):
- 5.7.1 Human Accountability — employees own outcomes from AI-assisted work
- 5.7.2 Verification of AI Outputs — must verify accuracy, completeness, bias, compliance before use
- 5.7.3 Protection of Company Information — data classification, privacy, IP, customer obligations
- 5.7.4 Transparency and Disclosure — disclose AI use where required by law/contract/policy
- 5.7.5 Reporting Responsibilities — escalation path for misuse, inaccurate outputs, incidents
- 5.7.6 Decision Framework — 6-question ethical checklist before acting on AI output

Also added cross-reference line in **AI Acceptable Use** section pointing to Section 5.7.

**Published:** User pasted content directly into the open SharePoint document (2026-06-30). Live and canonical.

## Graph API / SharePoint access facts

- Token: `az account get-access-token --resource https://graph.microsoft.com`
- Site ID: `<ORG_PARENT>.sharepoint.com,3261e17a-9f39-45d5-a7d3-d6bb5f8e555c,fac73700-0d4b-4207-afc9-c01d81b053af`
- Item ID: `01LFBTC6NGW6VQLQXGJBCJZ72H5RMRXPUV`
- PUT /content blocked when file is open in Word (returns "resource locked") — close first or use SharePoint MCP
- Best MCP option: `npx ms-sharepoint-mcp` or `@foodman/sharepoint-mcp --auth azcli` (reuses existing az login, no app registration needed)

## Open
- Confirm with template owner whether Heading 1 sections should eventually be numbered.
- Consider adding a SharePoint MCP server for direct uploads in future sessions.
