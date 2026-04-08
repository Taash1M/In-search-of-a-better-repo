# Taashi Research Skill — 4-Phase Deep Research Methodology

## Overview

This skill implements a systematic 4-phase deep research methodology for transforming unstructured research questions into comprehensive, source-backed analysis. Extracted from DeerFlow's deep-research capability and adapted for Claude Code's tool-based execution model.

**Invoke with:** `/taashi-research <research question>`

## When to Use

Use this skill when you need:
- **Vendor or technology evaluation** — comparing platforms, evaluating OSS frameworks, assessing tools
- **Architecture decision support** — choosing between design patterns, cloud services, migration strategies
- **Data quality research** — industry standards, best practices, regulatory requirements
- **Market or competitive analysis** — product landscapes, pricing models, adoption trends
- **Technical deep dives** — understanding a new protocol, framework, or methodology

Do NOT use for simple factual lookups (just use WebSearch), code generation, or tasks where you already have sufficient context.

## Execution Protocol

When this skill is invoked, execute ALL four phases sequentially. Do not skip phases. Report progress at each phase boundary.

### Phase 1: Broad Exploration

**Goal:** Establish the landscape. Understand the full scope before diving deep.

**Steps:**
1. Decompose the research question into 3-5 distinct search queries targeting different angles:
   - Primary topic definition and overview
   - Key players, products, or implementations
   - Recent developments (append "2025 2026" to queries)
   - Criticisms, limitations, or alternatives
   - Industry or domain-specific perspectives
2. Execute all searches using WebSearch (parallel where possible)
3. Build a **Topic Map** — list of key themes, entities, and sub-topics discovered
4. Identify **Knowledge Gaps** — areas where initial results are thin or contradictory

**Checkpoint:** Report the Topic Map and Knowledge Gaps to the user before proceeding.

**Budget:** 3-5 WebSearch calls

### Phase 2: Deep Dive

**Goal:** Fill knowledge gaps and develop detailed understanding of critical sub-topics.

**Steps:**
1. For each knowledge gap from Phase 1, craft targeted search queries
2. For the most authoritative sources found, use WebFetch to read full content
3. Look specifically for:
   - Technical specifications, architecture details, implementation patterns
   - Quantitative data (benchmarks, pricing, adoption metrics)
   - Expert opinions, case studies, real-world experiences
   - Official documentation or whitepapers
4. Build a **Fact Registry** — structured collection of verified facts with source attribution

**Checkpoint:** Report key findings so far. Ask if user wants to redirect focus.

**Budget:** 5-8 WebSearch calls + 3-5 WebFetch calls

### Phase 3: Diversity and Validation

**Goal:** Challenge assumptions, find counter-arguments, ensure balanced coverage.

**Steps:**
1. For each major finding from Phase 2, search for:
   - Counter-arguments or criticisms
   - Alternative perspectives (different industries, regions, company sizes)
   - Recent changes that might invalidate older information
2. Cross-reference key facts across multiple sources
3. Flag facts with only a single source or that are contradicted
4. Assign confidence levels:
   - **HIGH** — Confirmed by 3+ independent sources
   - **MEDIUM** — Confirmed by 2 sources or from one highly authoritative source (official docs, Gartner, Forrester, MSFT Learn)
   - **LOW** — Single source, unverified, or contradicted

**Budget:** 3-5 WebSearch calls

### Phase 4: Synthesis Check

**Goal:** Ensure completeness and coherence. Fill remaining gaps. Produce final report.

**Steps:**
1. Review the full Fact Registry against the original research question
2. Check: Does the research answer ALL aspects of the original question?
3. Check: Are there logical gaps in the narrative?
4. If gaps remain, conduct 1-2 targeted final searches
5. Synthesize findings into the structured report format below

**Budget:** 0-2 WebSearch calls

## Output Format

Structure EVERY deep research output exactly as follows:

```markdown
# Deep Research Report: [Topic]

**Date:** [YYYY-MM-DD]
**Research Question:** [Original question verbatim]
**Confidence Level:** [HIGH/MEDIUM/LOW — overall assessment]
**Search Depth:** [N] searches, [N] page fetches across 4 phases

## Executive Summary
[3-5 sentences capturing the key findings and recommendation. A busy executive should be able to read only this section and understand the answer.]

## Key Findings

### Finding 1: [Title]
- **Detail:** [Explanation with specific data points]
- **Evidence:** [Source with URL]
- **Confidence:** [HIGH/MEDIUM/LOW]

### Finding 2: [Title]
[... repeat for all major findings, typically 5-10]

## Comparison Matrix (if applicable)
| Dimension | Option A | Option B | Option C |
|-----------|----------|----------|----------|
| Cost | ... | ... | ... |
| Scalability | ... | ... | ... |
| Ease of Use | ... | ... | ... |
| Maturity | ... | ... | ... |
| Fit for Fluke/UBI | ... | ... | ... |

## Counter-Arguments and Risks
- [Counter-argument 1 with source]
- [Counter-argument 2 with source]
- [Risk or limitation that should be considered]

## Knowledge Gaps
- [Areas where information was insufficient or contradictory]
- [Topics that need further investigation or hands-on testing]

## Sources
1. [URL] — [Brief description of source and what it contributed]
2. [URL] — [...]
[... all sources used, typically 10-20]

## Recommendation
[Clear, actionable recommendation based on findings. Include next steps.]
```

## Quality Rules

1. **Source preference hierarchy:** Official documentation > Peer-reviewed/analyst reports (Gartner, Forrester, ThoughtWorks) > Established tech blogs (Microsoft Learn, AWS docs, SQLBI) > Community content (Stack Overflow, Reddit, Medium). When community content is the primary source, flag confidence as MEDIUM or LOW.

2. **Recency bias correction:** Always check publication dates. Flag any source older than 2 years. For fast-moving topics (AI, cloud services), prefer sources from the last 12 months.

3. **No hallucinated sources:** Every URL in the Sources section must come from an actual WebSearch or WebFetch result. Never fabricate a URL.

4. **Iterative refinement:** If the user says "go deeper on Finding N", trigger additional Phase 2 searches on that specific sub-topic and update the report.

5. **Balanced coverage:** Every recommendation must acknowledge at least one counter-argument or risk. One-sided analysis is incomplete analysis.

## Typical Session Metrics

| Metric | Typical Range |
|--------|--------------|
| Total searches | 12-20 across all phases |
| Page fetches | 3-8 for most valuable sources |
| Duration | 5-15 minutes |
| Token usage | 3-5x a standard query |
| Findings | 5-10 key findings |
| Sources | 10-20 unique sources |

## Integration with Other Skills

After completing research, suggest relevant follow-up actions:
- **docx-beautify** — Convert the research report to professional DOCX: `/docx-beautify`
- **ubi-dev** — If research relates to UBI platform decisions, apply findings in context
- **ai-use-case-builder** — If research evaluates an AI use case, feed into the UCB workflow
- **powerbi-desktop** — If research relates to PBI capabilities, apply to skill knowledge

## Examples

### Example 1: MDM Vendor Evaluation
```
/taashi-research Evaluate Informatica MDM vs Reltio vs custom Spark-based MDM (Splink) for customer data matching at enterprise scale (4M+ records). Consider cost, scalability, implementation effort, and accuracy.
```

### Example 2: UBI Architecture Decision
```
/taashi-research Should UBI migrate from Azure Data Factory + Databricks to Microsoft Fabric for ETL orchestration? Consider feature parity, migration effort, cost impact, and team readiness.
```

### Example 3: Data Quality Standards
```
/taashi-research What are industry best practices for data quality scoring in master data management, specifically for customer data with name/address matching? Include ISO standards and scoring frameworks.
```

### Example 4: AI Platform Comparison
```
/taashi-research Compare Azure AI Foundry vs AWS Bedrock vs Google Vertex AI for enterprise LLM deployment. Focus on Claude model availability, cost, security, and integration with existing Azure infrastructure.
```

### Example 5: Open Source Framework Evaluation
```
/taashi-research Evaluate DeerFlow vs CrewAI vs AutoGPT vs LangGraph for multi-agent AI orchestration. Consider code quality, community health, extensibility, and production readiness.
```
