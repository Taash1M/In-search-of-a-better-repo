---
name: html-for-outlook-email
description: "DOCX copy-paste into Outlook loses formatting (wall of text). Generate HTML instead — browser Ctrl+A/C then paste preserves callouts, borders, colors, spacing."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 9764eafb-19b3-4862-9c84-3dbedda1e74e
---

When building documents intended for Outlook email body, generate HTML (not DOCX).

**Why:** DOCX copy-paste into Outlook strips callout boxes, colored borders, shading, and spacing — renders as a wall of text. HTML paste from browser preserves all formatting because Outlook's email renderer is HTML-native.

**How to apply:** When the user needs a formatted email notice/announcement:
1. Generate `.html` with inline CSS (Outlook respects inline styles)
2. Use simple CSS: `border-left` for callout boxes, `background-color` for shading, `font-weight: bold`, `margin`/`padding` for spacing
3. Font stack: `Aptos, Calibri, Arial, sans-serif`
4. Keep a DOCX version for records if needed, but the HTML is the paste source
5. Workflow: open HTML in browser → Ctrl+A → Ctrl+C → paste into Outlook new email

Related: [[feedback-no-pii-in-deliverables]] (names may be retained for internal comms per user override)
