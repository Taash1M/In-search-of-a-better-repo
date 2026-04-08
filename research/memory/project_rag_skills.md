---
name: RAG Skills
description: doc-intelligence (3-tier parsing/extraction) and rag-multimodal (cross-modal graph + VLM + RAGAS eval) skills, A+ grade, integrated into AI UCB
type: project
---

Two skills built from analysis of 3 GitHub repos (rag-anything, contextgem, doctra):

**Why:** AI UCB needed document parsing beyond basic text extraction (complex layouts, scanned docs, images/charts) and multimodal RAG for documents with visual content.

**How to apply:**
- `/doc-intelligence` — 3-tier architecture: Tier 1 (Doctra-pattern layout-aware OCR), Tier 2 (ContextGem-pattern declarative extraction), Tier 3 (Azure AI Document Intelligence)
- `/rag-multimodal` — Cross-modal knowledge graph, VLM-enhanced retrieval, extended 9-field AI Search index, RAGAS evaluation framework (5 metrics + pass criteria), multimodal-specific eval, hybrid search tuning guide
- Both integrate into AI UCB via state contract flags: `multimodal_rag`, `enhanced_parsing`, `doc_intelligence_tier`
- Activation: Phase 0 Discovery questions detect multimodal content and complex layouts → flags set → Phase 2/3 dispatchers select enhanced templates

**Skill files (live):** `~/.claude/commands/doc-intelligence.md`, `~/.claude/commands/rag-multimodal.md`
**Skill files (backup):** `AI UCB/skills/companions/doc-intelligence.md`, `AI UCB/skills/companions/rag-multimodal.md`
**Original project dir:** `C:\Users\tmanyang\OneDrive - Fortive\Claude code\RAG\`
**Repos:** rag-anything, contextgem, doctra (all in original project dir)
**AI UCB files edited:** ai-ucb-discover, ai-ucb-pipeline, ai-ucb-ai, archetypes, ai-use-case-builder (5 files, 13 total edits)

**A+ Upgrade (2026-04-07):** rag-multimodal.md enhanced with RAGAS evaluation framework (`context_precision`, `context_recall`, `faithfulness`, `answer_relevancy`, `answer_correctness` with pass thresholds), multimodal-specific eval (image/table retrieval rates, cross-modal accuracy), hybrid search tuning guide, 7 anti-patterns, 7 error recovery entries.
