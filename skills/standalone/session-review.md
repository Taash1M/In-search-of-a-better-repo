---
name: session-review
description: "Scan the current conversation for lessons learned and route them to the right persistence target (skill files, CLAUDE.md, memory). Use at the end of a productive session or when the user asks to capture what was learned. Priority: corrections > repeated guidance > new knowledge > preferences."
allowed-tools: Read, Grep, Glob, Write, Edit, Task
---

# Session Review Skill

Extract lessons from the current conversation and route them to the correct persistence target. This ensures corrections and discoveries survive across sessions.

## Task Tracking

At the start, use TaskCreate for each phase:
1. Scan conversation for lessons
2. Classify and prioritize
3. Route to targets
4. Apply updates

Mark each task in_progress when starting and completed when done.

## Step 1: Scan Conversation for Lessons

Scan the full conversation with this priority order:

### Priority 1: Corrections (Highest Value)
User explicitly said "no", "stop", "not like that", "wrong", "don't do that", or rejected a tool use with corrective feedback. These are the most valuable lessons — they reveal what Claude got wrong.

### Priority 2: Repeated Guidance
Instructions the user gave more than once. If the user had to repeat themselves, Claude didn't internalize it the first time.

### Priority 3: Skill-Shaped Knowledge
Domain expertise, patterns, or decision frameworks that emerged during the session. Things like: "when X happens, always do Y" or "this API works differently than expected."

### Priority 4: New Workflows
Multi-step procedures that worked successfully. Novel sequences of actions that the user validated.

### Priority 5: Preferences
Formatting, naming, style, tool choices, communication preferences.

### Priority 6: Failure Modes
Approaches that failed, with what worked instead. The failure context is as valuable as the fix.

### Priority 7: Domain Knowledge
Facts Claude didn't have — external system configurations, team conventions, business rules not in code.

For each lesson, record:
- **What:** The lesson itself (one sentence)
- **Evidence:** Quote or reference from conversation
- **Priority:** 1-7 from above
- **Stability:** Will this remain true next session? (Yes/No/Likely)

### Exclusion Criteria

Do NOT extract:
- Lessons that are session-specific and won't apply next time
- Information already documented in CLAUDE.md or existing skills
- One-time debugging solutions (the fix is in the code; the commit has the context)
- Speculative patterns (tried once, not validated)
- Code patterns derivable by reading current project state

## Step 2: Classify and Prioritize

For each extracted lesson, determine the routing target.

### Routing Rules (Mandatory — Apply in Order)

**Rule 1 (Hard Constraint):** If the lesson corrects, refines, or adds a guardrail to a SPECIFIC SKILL's behavior, route to THAT SKILL. Not to memory. Not to CLAUDE.md. The skill itself.

**Rule 2:** If the lesson is about project architecture, conventions, or environment configuration, route to the relevant PROJECT_MEMORY.md.

**Rule 3:** If the lesson is about user preferences, work style, or collaboration approach, route to auto memory (user or feedback type).

**Rule 4:** If the lesson is domain knowledge not tied to a specific skill or project, route to auto memory (project or reference type).

### Routing Hierarchy (When Ambiguous)

| Conflict | Winner | Reason |
|---|---|---|
| Skill vs. CLAUDE.md | Skill | Skills are loaded on-demand; CLAUDE.md is always loaded |
| Skill vs. Memory | Skill | Skills are authoritative for their domain |
| CLAUDE.md vs. Memory | CLAUDE.md for rules; Memory for knowledge | Rules in CLAUDE.md, discoverable facts in memory |
| Memory vs. Nothing | Memory | If stable and non-obvious, save it |

## Step 3: Route to Targets

For each lesson, determine the exact target file:

### Skill Targets
Check which skills were invoked or referenced in this session:
- `<ADMIN_HOME>/.claude\commands\ubi-dev.md`
- `<USER_HOME>/OneDrive - <ORG>\Claude code\Document Beautification\docx-beautify.md`
- `<USER_HOME>/OneDrive - <ORG>\Claude code\Presentation Beautification\pptx-beautify.md`
- Other skills in `<ADMIN_HOME>/.claude\commands\`

### Project Memory Targets
- `<USER_HOME>/OneDrive - <ORG>\Projects\MDM\Customer Data\Customer Data Matching and Linking\PROJECT_MEMORY.md`
- `<USER_HOME>/OneDrive - <ORG>\Projects\UBI\CPQ - SMC and RMC\PROJECT_MEMORY.md`
- `<USER_HOME>/OneDrive - <ORG>\Claude code\Presentation Beautification\PROJECT_MEMORY.md`
- `<USER_HOME>/OneDrive - <ORG>\Claude code\Document Beautification\PROJECT_MEMORY.md`
- Other PROJECT_MEMORY.md files in active project directories

### Auto Memory Target
- `<ADMIN_HOME>/.claude\projects\C--windows-system32\memory\`

## Step 4: Apply Updates

Present the proposed updates to the user before applying:

```markdown
## Session Review: <N> Lessons Found

### Proposed Updates

| # | Lesson | Priority | Target | Action |
|---|---|---|---|---|
| 1 | <lesson> | P1 Correction | ubi-dev.md | Add to Rules section |
| 2 | <lesson> | P2 Repeated | docx-beautify.md | Add to Gotchas |
| 3 | <lesson> | P5 Preference | feedback memory | New memory file |
```

Wait for user confirmation before applying. Apply with the Edit tool for existing files, Write tool for new memory files.

### Update Format

**For skill files:** Add to the most relevant section (Rules, Gotchas, Conventions). Use the existing formatting style. Do not restructure the skill.

**For PROJECT_MEMORY.md:** Add to the appropriate section. Include date.

**For auto memory:** Follow the memory system format (frontmatter with name, description, type + content body).

## Rules

- NEVER add lessons that are already documented in the target file. Read the target first.
- NEVER save session-specific details (file paths being debugged, temporary workarounds).
- NEVER save lessons the user explicitly said were wrong or temporary.
- Corrections (Priority 1) are ALWAYS worth saving. If in doubt about other priorities, skip.
- If a lesson applies to multiple targets, save to the MOST SPECIFIC target only (skill > project > memory).
- Keep lesson descriptions concise — one sentence for the rule, one sentence for the why.
- Do not batch all lessons into one giant edit. Apply each update separately so the user can review.
- If no lessons are found, say so. Do not manufacture lessons to fill the report.
