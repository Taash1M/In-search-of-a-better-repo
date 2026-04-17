---
name: ubiquitous-language
description: "Extract a DDD-style ubiquitous language glossary from the current conversation, flagging ambiguities and proposing canonical terms. Saves to UBIQUITOUS_LANGUAGE.md. Use when user wants to define domain terms, build a glossary, harden terminology, create a ubiquitous language, standardize vocabulary, or mentions 'domain model', 'DDD', 'glossary', 'terminology', 'what do we call'. Trigger on: 'ubiquitous language', 'domain terms', 'glossary', 'terminology', 'define terms', 'what do we mean by'."
---

# Ubiquitous Language

**Source:** mattpocock/skills `ubiquitous-language` — adapted for Fluke AI team with pre-seeded domain terms.

Extract and formalize domain terminology from the current conversation into a consistent glossary, saved to a local file.

## Pre-Seeded Fluke AI Domain Terms

These terms have known ambiguity across the team. When encountered, apply these canonical definitions:

| Term | Canonical Definition | Aliases to Avoid |
|------|---------------------|-----------------|
| **Agent** | An autonomous LLM-powered process that perceives, reasons, and acts toward a goal | Bot, assistant, chatbot (unless specifically non-agentic) |
| **Skill** | A Claude Code markdown instruction file that extends Claude's capabilities for a specific domain | Plugin, command, prompt, template |
| **Tool** | A function or API that an agent can invoke during execution | Skill (when referring to MCP tools), function |
| **Account** | A Fluke customer organization in CRM/Dynamics | Customer (when referring to the CRM record specifically) |
| **Customer** | A person or organization that buys Fluke products | Account (when referring to the person, not the CRM record) |
| **Prospect** | A potential customer not yet in the sales pipeline | Lead (unless referring to Dynamics lead entity specifically) |
| **Hook** | A Claude Code PreToolUse/PostToolUse script that runs before/after tool execution | Guard, interceptor, middleware |
| **Node** | A Claude Code Azure AI Foundry deployment slot (node1/node2/node3) | Instance, endpoint, deployment (when referring to team allocation) |
| **Stream** | A UBI data pipeline covering Source→Landing→Bronze→Silver→Gold→PBI | Pipeline (when referring to UBI specifically), ETL |

## Process

1. **Scan the conversation** for domain-relevant nouns, verbs, and concepts
2. **Identify problems**:
   - Same word used for different concepts (ambiguity)
   - Different words used for the same concept (synonyms)
   - Vague or overloaded terms
3. **Propose a canonical glossary** with opinionated term choices
4. **Write to `UBIQUITOUS_LANGUAGE.md`** in the working directory using the format below
5. **Output a summary** inline in the conversation

## Output Format

Write a `UBIQUITOUS_LANGUAGE.md` file with this structure:

```md
# Ubiquitous Language

## [Domain Group 1]

| Term | Definition | Aliases to Avoid |
|------|-----------|-----------------|
| **Term** | One-sentence definition of what it IS | Words to avoid for this concept |

## Relationships

- A **Customer** can have one or more **Accounts** in CRM
- An **Agent** uses one or more **Tools** during execution

## Example Dialogue

> **Dev:** "When a **Customer** asks about their **Account**, does the **Agent** query Dynamics directly?"
> **Domain expert:** "No — the **Agent** queries Cosmos DB, which syncs from Dynamics nightly. The **Account** data in Cosmos is the source of truth for AI features."

## Flagged Ambiguities

- "account" was used to mean both a CRM entity and a user login — these are distinct: an **Account** is a customer record, while a **User** is an authentication identity.
```

## Rules

- **Be opinionated.** When multiple words exist for the same concept, pick the best one and list others as aliases to avoid.
- **Flag conflicts explicitly.** If a term is used ambiguously, call it out in "Flagged Ambiguities" with a clear recommendation.
- **Only include domain terms.** Skip module/class names unless they have domain meaning.
- **Keep definitions tight.** One sentence max. Define what it IS, not what it does.
- **Show relationships.** Use bold term names, express cardinality where obvious.
- **Group terms into multiple tables** when natural clusters emerge (by subdomain, lifecycle, or actor).
- **Write an example dialogue.** 3-5 exchanges between a dev and domain expert showing terms used precisely.
- **Incorporate pre-seeded terms.** Always include relevant pre-seeded Fluke terms from the table above. Override them if the conversation establishes a different consensus.

## Re-Running

When invoked again in the same conversation:

1. Read the existing `UBIQUITOUS_LANGUAGE.md`
2. Incorporate any new terms from subsequent discussion
3. Update definitions if understanding has evolved
4. Re-flag any new ambiguities
5. Rewrite the example dialogue to incorporate new terms
