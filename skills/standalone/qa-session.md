---
name: qa-session
description: "Interactive QA session where user reports bugs or issues conversationally, and the agent files GitHub issues. Explores the codebase in the background for context and domain language. Use when user wants to report bugs, do QA, file issues conversationally, do a QA round, review a feature, or mentions 'QA session', 'bug report', 'file an issue', 'something is broken', 'found a bug'. Trigger on: 'QA', 'bug', 'issue', 'broken', 'not working', 'regression', 'file issues'."
allowed-tools: Read, Grep, Glob, Bash, Edit, Write, Agent, AskUserQuestion
---

# QA Session

**Source:** mattpocock/skills `qa` — adapted for Fluke AI team with product labels and Azure context.

Run an interactive QA session. The user describes problems they're encountering. You clarify, explore the codebase for context, and file GitHub issues that are durable, user-focused, and use the project's domain language.

## Fluke Product Labels

When filing issues, apply the appropriate product label:

| Product | Label | Repos |
|---------|-------|-------|
| Pulse Sales / Account 360 | `pulse-sales` | Pulse Sales agent, Unified UI |
| Voice to Value (VoC F9) | `v2v` | Sales VoC F9 |
| TechMentor | `techmentor` | TechMentor agent |
| LLM Gateway | `llm-gateway` | LiteLLM proxy, team enablement |
| Claude Code Enablement | `claude-code` | Skills, hooks, MCP servers |
| UBI Platform | `ubi` | AzureDataBricks, ADF, Power BI |

## For Each Issue the User Raises

### 1. Listen and Lightly Clarify

Let the user describe the problem in their own words. Ask **at most 2-3 short clarifying questions** focused on:

- What they expected vs what actually happened
- Steps to reproduce (if not obvious)
- Whether it's consistent or intermittent

Do NOT over-interview. If the description is clear enough to file, move on.

### 2. Explore the Codebase in the Background

While talking to the user, kick off an Agent (subagent_type=Explore) in the background to understand the relevant area. The goal is NOT to find a fix — it's to:

- Learn the domain language used in that area (check UBIQUITOUS_LANGUAGE.md if it exists)
- Understand what the feature is supposed to do
- Identify the user-facing behavior boundary

This context helps you write a better issue — but the issue itself should NOT reference specific files, line numbers, or internal implementation details.

### 3. Assess Scope: Single Issue or Breakdown?

Before filing, decide whether this is a **single issue** or needs to be **broken down** into multiple issues.

Break down when:

- The fix spans multiple independent areas (e.g. "the form validation is wrong AND the success message is missing AND the redirect is broken")
- There are clearly separable concerns that different people could work on in parallel
- The user describes something that has multiple distinct failure modes or symptoms

Keep as a single issue when:

- It's one behavior that's wrong in one place
- The symptoms are all caused by the same root behavior

### 4. File the GitHub Issue(s)

Create issues with `gh issue create`. Do NOT ask the user to review first — just file and share URLs.

Issues must be **durable** — they should still make sense after major refactors. Write from the user's perspective.

#### For a Single Issue

```
gh issue create --title "<concise behavior description>" --label "<product-label>,bug" --body "$(cat <<'EOF'
## What Happened

[Describe the actual behavior the user experienced, in plain language]

## What I Expected

[Describe the expected behavior]

## Steps to Reproduce

1. [Concrete, numbered steps a developer can follow]
2. [Use domain terms from the codebase, not internal module names]
3. [Include relevant inputs, flags, or configuration]

## Additional Context

[Any extra observations from the user or from codebase exploration that help frame the issue — e.g. "this only happens when querying accounts with 5+ year history" — use domain language but don't cite files]
EOF
)"
```

#### For a Breakdown (Multiple Issues)

Create issues in dependency order (blockers first) so you can reference real issue numbers.

Use this template for each sub-issue:

```
## Parent Issue

#<parent-issue-number> (if you created a tracking issue) or "Reported during QA session"

## What's Wrong

[Describe this specific behavior problem — just this slice, not the whole report]

## What I Expected

[Expected behavior for this specific slice]

## Steps to Reproduce

1. [Steps specific to THIS issue]

## Blocked By

- #<issue-number> (if this issue can't be fixed until another is resolved)

Or "None — can start immediately" if no blockers.

## Additional Context

[Any extra observations relevant to this slice]
```

When creating a breakdown:

- **Prefer many thin issues over few thick ones** — each should be independently fixable and verifiable
- **Mark blocking relationships honestly** — if issue B genuinely can't be tested until issue A is fixed, say so. If they're independent, mark both as "None — can start immediately"
- **Create issues in dependency order** so you can reference real issue numbers in "Blocked by"
- **Maximize parallelism** — the goal is that multiple people (or agents) can grab different issues simultaneously
- **Classify HITL vs AFK** — mark each issue as agent-suitable (AFK) or requiring human judgment (HITL) based on the HITL/AFK classification rules from ai-ucb-discover

#### Rules for All Issue Bodies

- **No file paths or line numbers** — these go stale
- **Use the project's domain language** (check UBIQUITOUS_LANGUAGE.md if it exists)
- **Describe behaviors, not code** — "the sync service fails to apply the patch" not "applyPatch() throws on line 42"
- **Reproduction steps are mandatory** — if you can't determine them, ask the user
- **Keep it concise** — a developer should be able to read the issue in 30 seconds

After filing, print all issue URLs (with blocking relationships summarized) and ask: "Next issue, or are we done?"

### 5. Continue the Session

Keep going until the user says they're done. Each issue is independent — don't batch them.
