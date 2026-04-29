---
name: Keep large skills intact — no progressive disclosure splits
description: User decision to keep large skill files (1,000-3,000 lines) as single files with decision trees instead of splitting into core + reference files. Only split if context limits hit in practice.
type: feedback
originSessionId: 7c4fba2f-c973-46e1-8703-9a22ae2dc987
---
Keep large skill files intact with decision trees at the top instead of splitting into core + reference files.

**Why:** Skills are slash commands loaded on-demand (pay-per-use), not ambient context. A 2,885-line skill uses ~2% of Opus 4.6's 200k context window — negligible for single-skill invocations. Splitting adds file management overhead without meaningful context savings.

**How to apply:** When evaluating skills on the Skill Judge rubric, do not penalize D5 (Progressive Disclosure) for file length alone. Instead ensure: (1) decision tree at top routes to the right section, (2) clear section headings so Claude can skip irrelevant content, (3) file stays under ~4,000 lines. Only recommend splitting if the user reports context pressure from multi-skill sessions.
