# Docs: Training Materials and Onboarding Guides

## Overview

This folder tracks training materials and onboarding guides produced for the Fluke AI enablement program. The documents themselves are binary files (DOCX, PDF, PNG) stored on OneDrive — they are NOT committed to this git repo.

This README serves as the authoritative inventory: what documents exist, where they live on OneDrive, and how to regenerate them.

---

## Why Not in Git

Binary files (DOCX, PDF, PNG) are excluded from this repo for two reasons:

1. **Bloat.** Binary files do not delta-compress. Each version of a 2MB DOCX adds 2MB to git history permanently, even after deletion. For a repo intended to stay lean and fast to clone, this is unacceptable.

2. **Diffability.** Git diffs on binary files are unintelligible. Changes to a DOCX cannot be reviewed meaningfully in a PR. The generator scripts (Python source) are the reviewable artifact — the generated files are outputs, not sources.

OneDrive provides versioning, sharing, and backup for the binary files. Git provides versioning and review for the generator scripts.

---

## Document Inventory

| Document | Format | OneDrive Location |
|----------|--------|-------------------|
| Claude Code Onboarding (Node 2) | DOCX | `AI\Claude code deployment\docs\Training\` |
| Claude for Excel Quick Start Guide v3 | DOCX | `AI\Claude code deployment\docs\Training\` |
| Claude for Excel Quick Start Guide (Fluke branded) | PDF | `CIO Deliverables\Claude in Excel - L1 onboarding\` |
| Node 2 Onboarding Email (Jim/Peter/John) | DOCX | `AI\Claude code deployment\user-comms\` |
| Step-by-step screenshots (Steps 0-4) | PNG | `AI\Claude code deployment\docs\Training\` |
| Excel examples (Regional, Charts) | PNG | `AI\Claude code deployment\docs\Training\` |
| FAQ | TXT | `AI\Claude code deployment\docs\Training\` |

All OneDrive paths are relative to `C:\Users\tmanyang\OneDrive - Fortive\`.

---

## Generator Scripts

The DOCX and email documents are generated programmatically, not authored by hand. Generator scripts live on OneDrive alongside the output files (not in this repo, as they contain Fortive-specific content).

| Script | Output | OneDrive Location |
|--------|--------|-------------------|
| `generate_claude_code_onboarding_node2.py` | Claude Code Onboarding (Node 2) DOCX | `AI\Claude code deployment\docs\Training\` |
| `generate_claude_excel_guide_v3.py` | Claude for Excel Quick Start Guide v3 DOCX | `AI\Claude code deployment\docs\Training\` |
| `generate_node2_onboarding_email.py` | Node 2 Onboarding Email DOCX | `AI\Claude code deployment\user-comms\` |

All scripts use `docx_beautify.py` from the `modules/` folder and the `technical` or `executive` preset depending on audience.

---

## How to Regenerate Docs

To regenerate any document after content updates:

1. Update the content variables at the top of the generator script (user names, dates, node number, step descriptions).
2. Run the script from the OneDrive directory where it lives:

```bash
cd "C:\Users\tmanyang\OneDrive - Fortive\AI\Claude code deployment\docs\Training"
python generate_claude_code_onboarding_node2.py
```

3. Open the output DOCX in Word and verify formatting (cover page, section headers, tables, screenshots).
4. If the document is also distributed as PDF, export from Word using File > Export > Create PDF/XPS. Do not use a Python PDF converter — Word's export preserves formatting more faithfully.
5. Move the PDF to the CIO Deliverables folder if it is an L1 onboarding artifact.

Screenshots (PNG) are captured manually from the Claude Code UI and stored directly in the Training folder. They do not have a generator script.
