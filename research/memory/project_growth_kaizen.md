---
name: project-growth-kaizen
description: "Growth Kaizen Key Account Scorer — Copilot Studio agent, custom wide HTML canvas, Azure Static Web App hosting plan"
metadata: 
  node_type: memory
  type: project
  originSessionId: 01d64ad3-a7df-4a7e-a861-68e9f05b05e8
---

## Growth Kaizen — Key Account Scorer Agent

**Requestor**: Sue-Anne (International Markets President's Kaizen team)
**Project folder**: `<USER_HOME>/OneDrive - <ORG>\ADHOC\Kaizen\Growth Kaizen`
**Agent folder**: `<USER_HOME>/OneDrive - <ORG>\Claude code\copilot-studio-agents\key-account-scorer\`

### Custom Wide Chat Canvas (2026-06-04)
- **Problem**: Default Copilot Studio demo site chat widget is 450x520px — too narrow for the 7-column scoring table
- **Solution**: Custom HTML page using Bot Framework Web Chat SDK with Direct Line secret authentication
- **File**: `key-account-scorer-wide.html` in project folder
- **Key settings**: `--chat-width: 900px`, `--chat-height: 700px`, `bubbleMessageMaxWidth: 850`
- **Auth method**: Direct Line secret (from Settings > Security > Web channel security), embedded in HTML
- **Size presets**: Wide (900x700), Extra Wide (1100x750), Full Page, Default (450x520)
- **Fluke branding**: Navy blue header, teal accents, KAS avatar initials

### Hosting Decision
- **Decision**: Azure Static Web App (Option 2) for Kaizen team access
- **Why:** Single shareable URL, free tier, no download required for users, ~5 min setup. Static Web App connects to same Copilot Studio agent via Direct Line — all AI processing happens server-side in Copilot Studio.
- **How to apply:** Deploy the single HTML file to Azure Static Web App, share URL with Kaizen team

### Agent Response Time
- Web browsing is enabled (`gptCapabilities.webBrowsing: true`) — the AI researches companies online before scoring, which adds 30-60s per account
- Sonnet 4.6 model with 7-criteria scoring + confidence labeling + source citation adds processing time
- Expected: 30-90 seconds for a full account score with web research

### Deliverables Created (2026-06-04)
1. `key-account-scorer-wide.html` — Custom wide chat canvas with Fluke branding
2. `Key Account Scorer - How It Works.docx` — 2-page A4 landscape infographic (architecture + how-to)
3. `chat_widget_research.md` — Research report on widget resize + DOCX/Excel export options

### Agent v3 — C3 Future Potential Enhancement (2026-06-04)
- C3 now uses structured 3 sub-criteria: Company Size (sites + geographic scope), Portfolio Alignment (Fluke product family count), Investment Activity (capital/contracts/growth)
- Fluke product catalog embedded in instructions (Industrial, Calibration, Networks)
- Commercial barrier flagging: score normally, flag barriers, user decides
- Penetration logic removed — purely external company profile now
- 10/5/1 scoring guardrail reinforced (Sonnet used intermediate values on first test)
- DirectLine test PASS: Rolls-Royce scored correctly (C3=10 with sub-criteria, all scores 10/5/1)
- **GitHub repo**: `Taashi-Manyanga_fortive/custom-copilot-scoring-agent` (private)

### Next Steps
- [x] Complete E2E testing of scoring flow in wide canvas (done 2026-06-04 via DirectLine)
- [x] Deploy HTML to Azure Static Web App (done 2026-06-04)
- [ ] Share URL with Kaizen team
- [ ] DOCX export via Power Automate + Document Output (future)

Related: [[project-copilot-studio-agents]]
