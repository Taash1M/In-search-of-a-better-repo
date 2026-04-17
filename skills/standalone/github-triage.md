---
name: github-triage
description: "Triage GitHub issues through a label-based state machine with interactive grilling sessions. Use when user wants to triage issues, review incoming bugs or feature requests, prepare issues for an AFK agent, manage issue workflow, or review what needs attention. Trigger on: 'triage', 'issue triage', 'what needs attention', 'review issues', 'incoming bugs', 'ready for agent', 'needs-triage'."
allowed-tools: Read, Grep, Glob, Bash, Edit, Write, Agent, AskUserQuestion
---

# GitHub Issue Triage

**Source:** mattpocock/skills `github-triage` — adapted for Fluke AI team with product labels and HITL/AFK classification.

Triage issues in the current repo using a label-based state machine. Infer the repo from `git remote`. Use `gh` for all GitHub operations.

## Labels

| Label | Type | Description |
|-------|------|-------------|
| `bug` | Category | Something is broken |
| `enhancement` | Category | New feature or improvement |
| `pulse-sales` | Product | Pulse Sales / Account 360 |
| `v2v` | Product | Voice to Value (VoC F9) |
| `techmentor` | Product | TechMentor AI assistant |
| `llm-gateway` | Product | LLM Gateway / LiteLLM |
| `claude-code` | Product | Claude Code enablement |
| `ubi` | Product | UBI data platform |
| `needs-triage` | State | Maintainer needs to evaluate this issue |
| `needs-info` | State | Waiting on reporter for more information |
| `ready-for-agent` | State | Fully specified, ready for AFK agent (Claude Code can handle) |
| `ready-for-human` | State | Requires human implementation (HITL) |
| `wontfix` | State | Will not be actioned |

Every issue should have exactly **one** state label, **one** category label, and **one** product label. If an issue has conflicting state labels, flag the conflict and ask the maintainer which state is correct before doing anything else.

## State Machine

| Current State | Can Transition To | Who Triggers | What Happens |
|--------------|-------------------|-------------|--------------|
| `unlabeled` | `needs-triage` | Skill (on first look) | Issue needs maintainer evaluation |
| `unlabeled` | `ready-for-agent` | Maintainer (via skill) | Well-specified and agent-suitable. Write agent brief. |
| `unlabeled` | `ready-for-human` | Maintainer (via skill) | Requires human implementation. Write task summary. |
| `unlabeled` | `wontfix` | Maintainer (via skill) | Spam, duplicate, or out of scope. Close with comment. |
| `needs-triage` | `needs-info` | Maintainer (via skill) | Underspecified. Post triage notes + questions for reporter. |
| `needs-triage` | `ready-for-agent` | Maintainer (via skill) | Grilling complete, agent-suitable. Write agent brief. |
| `needs-triage` | `ready-for-human` | Maintainer (via skill) | Grilling complete, needs human. Write task summary. |
| `needs-triage` | `wontfix` | Maintainer (via skill) | Maintainer decides not to action. Close with comment. |
| `needs-info` | `needs-triage` | Skill (detects reply) | Reporter replied. Surface for re-evaluation. |

An issue can only move along these transitions. The maintainer can override any state directly (see Quick Override), but flag unusual transitions.

## Invocation

The maintainer invokes `/github-triage` then describes what they want. Examples:

- "Show me anything that needs my attention"
- "Let's look at #42"
- "Move #42 to ready-for-agent"
- "What's ready for agents to pick up?"
- "Are there any unlabeled issues?"

## Workflow: Show What Needs Attention

Query GitHub and present a summary grouped into three buckets:

1. **Unlabeled issues** — new, never triaged
2. **`needs-triage` issues** — maintainer needs to evaluate
3. **`needs-info` issues with new activity** — reporter has commented since last triage notes

Display counts per group. Within each group, show issues **oldest first**. For each issue: number, title, age, product label, one-line summary.

## Workflow: Triage a Specific Issue

### Step 1: Gather Context

Before presenting anything to the maintainer:

- Read the full issue: body, all comments, all labels, reporter, date
- If there are prior triage notes, parse them to understand what's already established
- **Spawn an Explore agent in the background** to understand the relevant codebase area — learn domain language, feature behavior, and user-facing boundaries
- Check if this issue matches a previously rejected concept

### Step 2: Present Recommendation

Tell the maintainer:

- **Category:** bug or enhancement, with reasoning
- **Product:** which product label applies
- **State:** where this issue should go, with reasoning
- **HITL/AFK assessment:** whether this can be handled by a Claude Code agent (AFK) or requires human judgment (HITL), with reasoning
- Brief summary of relevant codebase context

Then wait for direction. The maintainer may:
- Agree → apply labels
- Want to flesh it out → start grilling session
- Override → apply their choice

### Step 3: Bug Reproduction (bugs only)

Attempt to reproduce before grilling:
- Read reporter's reproduction steps
- Explore relevant code paths
- Try to reproduce (run tests, trace logic)
- Report findings to maintainer

### Step 4: Grilling Session (if needed)

Interview the maintainer to build a complete specification:
- Ask questions one at a time with recommended answers
- If a question can be answered by exploring the codebase, explore instead of asking
- Resume from prior triage notes — never re-ask resolved questions

Goal: reach a point where you can write a complete agent brief with:
- Clear summary of desired behavior
- Concrete acceptance criteria
- Key interfaces that may need to change
- Clear boundary of what's out of scope

### Step 5: Apply the Outcome

Show the maintainer a **preview** of exactly what will be posted and which labels applied/removed. Only proceed on confirmation.

- **ready-for-agent** — post agent brief comment with acceptance criteria
- **ready-for-human** — post task summary explaining why it needs human implementation
- **needs-info** — post triage notes with progress + specific questions for reporter
- **wontfix** — post polite explanation, close the issue

## Quick State Override

When the maintainer explicitly says to move an issue to a specific state, trust their judgment and apply directly. Still show confirmation of what you're about to do.

## Needs Info Output

```markdown
## Triage Notes

**What we've established so far:**

- point 1
- point 2

**What we still need from you (@reporter):**

- question 1
- question 2
```

## Resuming Previous Sessions

1. Read all comments to find prior triage notes
2. Parse what was already established
3. Check if reporter answered outstanding questions
4. Present updated picture: "Here's where we left off, and here's what's new"
5. Continue from where it stopped — do not re-ask resolved questions
