---
name: Document Extraction Skill
description: Unified doc-extract skill combining ContextGem, RAG-Anything, and agentic-doc patterns. Project dir: Claude code\Document extraction skill.
type: project
---

## Overview

Unified document extraction skill created 2026-04-07. Combines three frameworks:

1. **ContextGem** — Declarative LLM extraction with 7 concept types, aspects, pipelines, multi-model routing
2. **RAG-Anything** — Multimodal parsing (MinerU/Docling) with 4 modal processors, knowledge graph, VLM queries
3. **agentic-doc** — Production patterns: PDF splitting, parallel processing, retry with jitter, bounding box grounding

## Source Repos Analyzed

| Repo | Location | Key Takeaway |
|---|---|---|
| ContextGem (original) | `Claude code\contextgem\repo\` | Core extraction framework, 7 concept types, DocumentLLMGroup |
| ContextGem (Taash1M fork) | `Taashi_Github\18_ContextGem_Document_Extraction\` | PdfConverter, UBI examples, loosened deps |
| RAG-Anything | `Claude code\RAG\rag-anything\` | Multimodal processing, 4 modal processors, context extraction |
| agentic-doc | `Claude code\contextgem\agentic-doc\` | PDF splitting, parallel ThreadPool, tenacity retry, groundings |
| Chat-with-docs / DocsMind | `Claude code\contextgem\Chat-with-docs\` | Simple RAG app, less relevant for extraction skill |

## Skill Files

- **Main:** `~/.claude/commands/doc-extract.md` (~420 lines)
- **Reference:** `~/.claude/commands/doc-extract-reference.md` (~290 lines)
- **Replaces:** `doc-intelligence.md` (still exists for AI UCB integration, but doc-extract is the hands-on skill)

## Skill Judge Score

B+ grade (104/120). Improvements: added `when` field, failure consequences to NEVER rules, default choices section, "extract everything" handling pattern.

## Key Decision

**doc-extract vs doc-intelligence:** doc-extract is the hands-on extraction skill (ContextGem + RAG-Anything + production patterns). doc-intelligence stays as the AI UCB integration template (Tier 1/2/3 architecture, Azure AI Doc Intelligence, notebook generation).

## First Use Case

Engineering drawings from SharePoint: 20 PDFs in `Claude code\graphify\OneDrive_2026-04-07\Test Drawings\`. Chassis assemblies, keypads, schematics, datasheets. Will use vision extraction via ContextGem.
