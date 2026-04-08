---
name: eval-framework
description: Comprehensive AI evaluation, red-teaming, and observability skill — DeepEval unit tests (14+ metrics), RAGAS RAG-specific metrics, Garak automated red-teaming, Phoenix LLM observability. Cross-cutting for all AI UCB archetypes. Use when user needs to evaluate LLM outputs, test RAG quality, red-team prompt safety, set up LLM observability, or run AI quality regression suites. Works standalone or as AI UCB Phase 5 enhancement.
allowed-tools: Read, Grep, Glob, Bash, Edit, Write, Agent, AskUserQuestion
---

# Evaluation Framework Skill

You are an AI evaluation and quality assurance specialist. You build comprehensive test suites that validate LLM outputs across correctness, safety, and performance — combining unit-test-style assertions (DeepEval), RAG-specific metrics (RAGAS), automated red-teaming (Garak), and production observability (Phoenix). Every AI system you touch ships with measurable quality guarantees.

**Cherry-picked from:** ai-engineering-toolkit catalog — DeepEval, RAGAS, Garak, Phoenix/Opik. Fluke-adapted for Azure AI Foundry, Azure Monitor, CI/CD via Azure DevOps.

## When This Skill Activates

- User needs to evaluate LLM output quality (hallucination, relevancy, faithfulness)
- User wants automated red-teaming / vulnerability scanning for prompt injection
- User needs RAG-specific evaluation (context precision, recall, answer similarity)
- User wants LLM observability (trace visualization, token tracking, latency analysis)
- User needs CI/CD-integrated evaluation (pytest-compatible test suites)
- AI UCB Phase 5 dispatches any archetype for quality testing
- User mentions: "eval", "evaluate", "red team", "test LLM", "RAG metrics", "hallucination test", "prompt injection test", "LLM observability", "RAGAS", "DeepEval", "Garak"

## Core Principles

1. **Test like software.** LLM outputs are testable. Use assertions, thresholds, and regression suites — not vibes.
2. **Measure what matters.** Different archetypes need different metrics. RAG needs faithfulness; agents need tool-use accuracy; chat needs toxicity screening.
3. **Red-team before you ship.** Every system gets automated adversarial probes. Finding vulnerabilities in testing is a feature; finding them in production is an incident.
4. **Observe in production.** Evaluation doesn't stop at deployment. Continuous monitoring catches drift, cost spikes, and quality degradation.
5. **Azure-native.** Use Azure AI Foundry as the judge model, Azure Monitor for metrics, Azure DevOps for CI/CD integration.

---

## Architecture: Four Modules

```
Module 1: DeepEval — Unit Tests for LLM Outputs
    ├─ 14+ built-in metrics (hallucination, answer relevancy, faithfulness, bias, toxicity, ...)
    ├─ pytest-style assertions: assert_test(test_case, [metric1, metric2])
    ├─ Synthetic test dataset generation from documents
    └─ CI/CD integration (Azure DevOps pipeline step)

Module 2: RAGAS — RAG-Specific Evaluation
    ├─ Context precision (are retrieved docs relevant?)
    ├─ Context recall (are all relevant docs retrieved?)
    ├─ Faithfulness (is the answer grounded in context?)
    ├─ Answer similarity (does the answer match expected?)
    ├─ Noise robustness (does irrelevant context degrade quality?)
    └─ Synthetic test set generation from your own documents

Module 3: Garak — Automated Red-Teaming
    ├─ Prompt injection probes (50+ attack patterns)
    ├─ Jailbreak detection (DAN, roleplay, encoding attacks)
    ├─ Data leakage probes (system prompt extraction, PII extraction)
    ├─ Hallucination probes (known-false claims)
    └─ Report generation with severity classification

Module 4: Phoenix — LLM Observability
    ├─ Trace collection (every LLM call: prompt, response, latency, tokens, cost)
    ├─ Embedding drift detection (are embeddings changing over time?)
    ├─ Dashboard templates (latency, error rate, token usage, cost)
    └─ Alert rules (quality degradation, cost spike, error rate)
```

---

## Module 1: DeepEval — Unit Tests for LLM Outputs

DeepEval provides pytest-compatible testing for LLM applications with 14+ built-in metrics.

### Installation

```bash
pip install deepeval
```

### Core Concepts

```python
from deepeval import assert_test
from deepeval.test_case import LLMTestCase
from deepeval.metrics import (
    HallucinationMetric,
    AnswerRelevancyMetric,
    FaithfulnessMetric,
    BiasMetric,
    ToxicityMetric,
    ContextualPrecisionMetric,
    ContextualRecallMetric,
    GEval,
)

# A test case captures one input → output pair with optional context
test_case = LLMTestCase(
    input="What is Fluke's return policy for multimeters?",
    actual_output="Fluke offers a 30-day return policy for all multimeters purchased directly.",
    expected_output="30-day return policy for direct purchases.",
    context=["Fluke Corporation offers a 30-day return policy for instruments purchased through authorized channels."],
    retrieval_context=["Fluke return policy document, page 3, section 2.1"],
)
```

### Metric Reference

| Metric | What It Measures | Threshold | Use For |
|--------|-----------------|-----------|---------|
| `HallucinationMetric` | Does output contain claims not in context? | < 0.3 | RAG, chat |
| `FaithfulnessMetric` | Is every claim in output traceable to context? | > 0.7 | RAG |
| `AnswerRelevancyMetric` | Does output address the input question? | > 0.7 | All |
| `ContextualPrecisionMetric` | Are retrieved docs relevant to the query? | > 0.7 | RAG |
| `ContextualRecallMetric` | Are all relevant docs retrieved? | > 0.7 | RAG |
| `BiasMetric` | Does output show gender, racial, or other bias? | < 0.3 | All |
| `ToxicityMetric` | Does output contain harmful/toxic content? | < 0.1 | All |
| `GEval` | Custom LLM-as-Judge with your own criteria | Configurable | Any |
| `SummarizationMetric` | Does summary capture key points faithfully? | > 0.7 | Summarization |
| `ToolCorrectnessMetric` | Did agent select the correct tool? | > 0.9 | Agents |
| `KnowledgeRetentionMetric` | Does agent maintain context across turns? | > 0.7 | Conversational |
| `ConversationalMetric` | Multi-turn coherence and relevance | > 0.7 | Conversational |
| `LatencyMetric` | Response time within acceptable range | < 5s | All |
| `CostMetric` | Token cost within budget | < $0.05/query | All |

### Test Suite Pattern

```python
# test_rag_quality.py — pytest-compatible, runs in CI/CD
import pytest
from deepeval import assert_test
from deepeval.test_case import LLMTestCase
from deepeval.metrics import (
    HallucinationMetric, FaithfulnessMetric,
    AnswerRelevancyMetric, ContextualPrecisionMetric,
)
from deepeval.dataset import EvaluationDataset

# Configure judge model (Azure OpenAI)
import os
os.environ["OPENAI_API_KEY"] = os.getenv("AZURE_OPENAI_API_KEY")
os.environ["OPENAI_API_BASE"] = os.getenv("AZURE_OPENAI_ENDPOINT")

# Define metrics with thresholds
hallucination = HallucinationMetric(threshold=0.3, model="gpt-4.1")
faithfulness = FaithfulnessMetric(threshold=0.7, model="gpt-4.1")
relevancy = AnswerRelevancyMetric(threshold=0.7, model="gpt-4.1")
precision = ContextualPrecisionMetric(threshold=0.7, model="gpt-4.1")

# Load test cases from JSON (generated or hand-crafted)
dataset = EvaluationDataset()
dataset.add_test_cases_from_json_file("test_cases.json")

@pytest.mark.parametrize("test_case", dataset)
def test_rag_quality(test_case: LLMTestCase):
    assert_test(test_case, [hallucination, faithfulness, relevancy, precision])
```

### Custom Metric via GEval

```python
from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCaseParams

# Custom metric: Does the response follow Fluke's brand voice?
brand_voice = GEval(
    name="Brand Voice Compliance",
    criteria=(
        "Evaluate whether the response follows Fluke Corporation's brand voice: "
        "professional, technically accurate, customer-focused, and confident "
        "without being arrogant. Deduct points for casual language, humor, "
        "or marketing hyperbole."
    ),
    evaluation_params=[
        LLMTestCaseParams.INPUT,
        LLMTestCaseParams.ACTUAL_OUTPUT,
    ],
    threshold=0.7,
    model="gpt-4.1",
)
```

### Synthetic Test Dataset Generation

```python
from deepeval.synthesizer import Synthesizer

synthesizer = Synthesizer(model="gpt-4.1")

# Generate test cases from your own documents
test_cases = synthesizer.generate_goldens_from_docs(
    document_paths=["data/fluke_return_policy.pdf", "data/fluke_calibration_guide.pdf"],
    max_goldens_per_document=10,
    include_expected_output=True,
)

# Save for CI/CD
dataset = EvaluationDataset(test_cases=test_cases)
dataset.save_as_json("test_cases.json")
```

---

## Module 2: RAGAS — RAG-Specific Evaluation

RAGAS provides specialized metrics for RAG pipelines that go beyond generic LLM evaluation.

### Installation

```bash
pip install ragas
```

### Core Metrics

```python
from ragas import evaluate
from ragas.metrics import (
    context_precision,       # Are retrieved docs relevant?
    context_recall,          # Are ALL relevant docs found?
    faithfulness,            # Is answer grounded in context?
    answer_relevancy,        # Does answer address the question?
    answer_similarity,       # Does answer match expected?
    answer_correctness,      # Factual accuracy
    context_entity_recall,   # Do retrieved docs contain expected entities?
    noise_robustness,        # Does irrelevant context degrade quality?
)
from datasets import Dataset

# Prepare evaluation dataset
eval_data = {
    "question": [
        "What is the accuracy of the Fluke 87V?",
        "How do I calibrate a Fluke 376 FC?",
        "What certifications does the Fluke ii900 have?",
    ],
    "answer": [
        "The Fluke 87V has a DC accuracy of ±0.05%.",
        "Connect to PC via Fluke Connect app, follow calibration wizard.",
        "The ii900 is certified to IEC 61010-1 CAT II 600V.",
    ],
    "contexts": [
        ["Fluke 87V specs: DC voltage accuracy ±0.05% + 1 digit."],
        ["Fluke 376 FC calibration: Use Fluke Connect software, select instrument, run wizard."],
        ["Fluke ii900 certifications: IEC 61010-1 CAT II 600V, IP 54."],
    ],
    "ground_truth": [
        "DC accuracy is ±0.05% + 1 digit",
        "Use Fluke Connect app calibration wizard",
        "IEC 61010-1 CAT II 600V",
    ],
}

dataset = Dataset.from_dict(eval_data)
result = evaluate(
    dataset,
    metrics=[
        context_precision,
        context_recall,
        faithfulness,
        answer_relevancy,
        answer_correctness,
    ],
)
print(result)  # DataFrame with per-question scores
print(result.to_pandas().describe())  # Aggregate stats
```

### RAGAS Synthetic Test Generation

```python
from ragas.testset.generator import TestsetGenerator
from ragas.testset.evolutions import simple, reasoning, multi_context
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
from langchain_community.document_loaders import DirectoryLoader

# Load source documents
loader = DirectoryLoader("data/", glob="**/*.pdf")
documents = loader.load()

# Configure Azure OpenAI for generation
generator_llm = AzureChatOpenAI(
    azure_deployment="gpt-4.1",
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2024-10-01",
)
embeddings = AzureOpenAIEmbeddings(
    azure_deployment="text-embedding-3-large",
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
)

# Generate diverse test set
generator = TestsetGenerator.from_langchain(generator_llm, generator_llm, embeddings)
testset = generator.generate_with_langchain_docs(
    documents,
    test_size=50,
    distributions={simple: 0.4, reasoning: 0.3, multi_context: 0.3},
)

# Export for DeepEval or standalone use
testset.to_pandas().to_csv("ragas_testset.csv", index=False)
```

### RAGAS Metric Thresholds by Archetype

| Metric | RAG | Conversational | Doc Intelligence | Knowledge Graph | Multi-Agent |
|--------|-----|----------------|-----------------|-----------------|-------------|
| Context Precision | > 0.75 | > 0.65 | > 0.80 | > 0.70 | > 0.65 |
| Context Recall | > 0.75 | > 0.60 | > 0.85 | > 0.70 | > 0.60 |
| Faithfulness | > 0.80 | > 0.70 | > 0.90 | > 0.75 | > 0.70 |
| Answer Relevancy | > 0.75 | > 0.75 | > 0.80 | > 0.70 | > 0.70 |
| Answer Correctness | > 0.70 | > 0.65 | > 0.85 | > 0.65 | > 0.60 |

---

## Module 3: Garak — Automated Red-Teaming

Garak is an LLM vulnerability scanner that probes for prompt injection, jailbreak, data leakage, and hallucination vulnerabilities.

### Installation

```bash
pip install garak
```

### Probe Categories

| Category | What It Tests | Probe Count | Severity |
|----------|--------------|-------------|----------|
| `encoding` | Unicode/encoding-based injection | ~15 | High |
| `dan` | "Do Anything Now" jailbreak variants | ~20 | Critical |
| `knowledgegraph` | Known-false factual claims | ~30 | Medium |
| `leakreplay` | System prompt extraction attempts | ~10 | Critical |
| `lmrc` | Language model risk cards | ~40 | High |
| `malwaregen` | Malicious code generation requests | ~10 | Critical |
| `packagehallucination` | Non-existent package recommendations | ~10 | Medium |
| `promptinject` | Direct prompt injection patterns | ~50 | Critical |
| `realtoxicityprompts` | Toxicity-inducing prompts | ~20 | High |
| `snowball` | Gradual constraint relaxation | ~15 | High |
| `xss` | Cross-site scripting via LLM | ~10 | High |

### Scanning Configuration

```python
# garak_config.yaml — Red-team scan configuration
---
plugins:
  # Critical probes — run on EVERY deployment
  probes:
    - promptinject.HijackHateHumansMini
    - promptinject.HijackKillHumansMini
    - dan.Dan_11_0
    - dan.Dan_6_0
    - leakreplay.LiteratureCloze80
    - encoding.InjectBase64
    - encoding.InjectROT13

  # Extended probes — run before production promotion
  extended_probes:
    - knowledgegraph.Wedge
    - malwaregen.Pypi
    - packagehallucination.Python
    - realtoxicityprompts.RTPBlank
    - snowball.GraphConnectivity
    - xss.MarkdownImageExfil

  # Detectors
  detectors:
    - always.Pass
    - toxicity.ToxicityScorer
    - mitigation.MitigationBypass

# Target configuration for Azure OpenAI
generators:
  - rest.RestGenerator:
      uri: "{AZURE_OPENAI_ENDPOINT}/openai/deployments/gpt-4.1/chat/completions?api-version=2024-10-01"
      headers:
        api-key: "{AZURE_OPENAI_API_KEY}"
        Content-Type: "application/json"
      req_template: '{"messages": [{"role": "user", "content": "$INPUT"}]}'
      response_json_field: "choices.0.message.content"
```

### Running Garak Scans

```bash
# Quick scan (critical probes only, ~5 minutes)
garak --model_type rest \
  --probes promptinject,dan,leakreplay,encoding \
  --report_prefix flk_{app}_quick_scan

# Full scan (all probes, ~30 minutes)
garak --model_type rest \
  --probes all \
  --report_prefix flk_{app}_full_scan

# Parse results
python -c "
import json
with open('garak_runs/flk_{app}_quick_scan.report.jsonl') as f:
    results = [json.loads(line) for line in f]
    total = len(results)
    passed = sum(1 for r in results if r.get('passed', False))
    print(f'Red-team results: {passed}/{total} probes defended ({passed/total*100:.0f}%)')
    failed = [r for r in results if not r.get('passed', False)]
    for f in failed:
        print(f'  FAIL: {f[\"probe_classname\"]} — {f.get(\"detector_classname\", \"\")}')
"
```

### Garak Report Template

```
RED-TEAM REPORT — {project_name}
===================================
Scan Date: {timestamp}
Target: {model_deployment}
Probe Set: {critical|extended|full}

SUMMARY
  Total Probes: {total}
  Defended:     {passed} ({pct}%)
  Vulnerable:   {failed} ({pct}%)

CRITICAL FINDINGS (must fix before production)
| # | Probe | Category | Severity | Description |
|---|-------|----------|----------|-------------|
| 1 | {probe} | {category} | CRITICAL | {description} |

HIGH FINDINGS (should fix before production)
| # | Probe | Category | Severity | Description |
|---|-------|----------|----------|-------------|

MEDIUM FINDINGS (monitor in production)
| # | Probe | Category | Severity | Description |
|---|-------|----------|----------|-------------|

RECOMMENDATIONS
1. {recommendation_1}
2. {recommendation_2}
```

---

## Module 4: Phoenix — LLM Observability

Phoenix (by Arize AI) provides trace collection, embedding analysis, and drift detection for LLM applications.

### Installation

```bash
pip install arize-phoenix opentelemetry-api opentelemetry-sdk
```

### Trace Collection Setup

```python
import phoenix as px
from phoenix.trace.openai import OpenAIInstrumentor
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor

# Launch Phoenix (local dashboard at http://localhost:6006)
session = px.launch_app()

# Instrument OpenAI/Azure OpenAI calls
OpenAIInstrumentor().instrument()

# Every LLM call now automatically captures:
# - Input prompt (full messages array)
# - Output response (full completion)
# - Latency (ms)
# - Token usage (prompt_tokens, completion_tokens, total_tokens)
# - Model name
# - Temperature, top_p, and other params
# - Error info (if any)
```

### Azure Monitor Integration

```python
# Send Phoenix traces to Azure Application Insights
from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry.instrumentation.openai import OpenAIInstrumentor

configure_azure_monitor(
    connection_string=os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING"),
)
OpenAIInstrumentor().instrument()

# Now all LLM traces appear in App Insights alongside infrastructure metrics
```

### Dashboard KQL Queries

```kql
// LLM latency percentiles (last 24h)
dependencies
| where timestamp > ago(24h)
| where name contains "openai" or name contains "chat/completions"
| summarize p50=percentile(duration, 50), p95=percentile(duration, 95),
            p99=percentile(duration, 99), avg_dur=avg(duration)
| project p50=round(p50, 0), p95=round(p95, 0), p99=round(p99, 0), avg=round(avg_dur, 0)

// Token usage by model (last 7d)
customMetrics
| where timestamp > ago(7d)
| where name == "llm.token.usage"
| extend model = tostring(customDimensions["model"])
| summarize total_tokens=sum(value) by model, bin(timestamp, 1d)
| render timechart

// Error rate by deployment (last 24h)
dependencies
| where timestamp > ago(24h)
| where name contains "openai"
| summarize total=count(), errors=countif(success == false) by bin(timestamp, 1h)
| extend error_rate = round(100.0 * errors / total, 1)
| render timechart

// Embedding drift detection (cosine similarity to baseline)
customMetrics
| where timestamp > ago(7d)
| where name == "embedding.drift.cosine_similarity"
| summarize avg_similarity=avg(value) by bin(timestamp, 1h)
| where avg_similarity < 0.85  // Alert threshold
```

### Alert Rules

```python
# Alert: LLM error rate > 5% in 15-minute window
alert_rules = [
    {
        "name": "LLM Error Rate High",
        "query": """
            dependencies
            | where timestamp > ago(15m)
            | where name contains "openai"
            | summarize total=count(), errors=countif(success == false)
            | extend error_rate = 100.0 * errors / total
            | where error_rate > 5
        """,
        "severity": "Sev2",
        "action": "Notify #ai-ops channel",
    },
    {
        "name": "LLM Latency P95 > 10s",
        "query": """
            dependencies
            | where timestamp > ago(15m)
            | where name contains "openai"
            | summarize p95=percentile(duration, 95)
            | where p95 > 10000
        """,
        "severity": "Sev3",
        "action": "Auto-scale or failover",
    },
    {
        "name": "Token Budget Alert",
        "query": """
            customMetrics
            | where timestamp > ago(1h)
            | where name == "llm.token.usage"
            | summarize hourly_tokens=sum(value)
            | where hourly_tokens > 500000
        """,
        "severity": "Sev3",
        "action": "Notify cost owner",
    },
]
```

---

## AI UCB Integration

### State Contract Flags

```json
{
  "requirements": {
    "eval": {
      "eval_tier": "standard",          // "minimal" | "standard" | "comprehensive"
      "red_team": true,                  // Enable Garak scanning
      "observability": true,             // Enable Phoenix/App Insights tracing
      "synthetic_test_size": 50,         // Number of synthetic test cases
      "custom_metrics": []               // Additional GEval criteria
    }
  }
}
```

### Tier Selection Guide

| Tier | DeepEval | RAGAS | Garak | Phoenix | When to Use |
|------|----------|-------|-------|---------|-------------|
| `minimal` | 4 core metrics, 10 test cases | Faithfulness + relevancy only | Critical probes only (~5 min) | App Insights only | Dev/prototype, fast iteration |
| `standard` | 8 metrics, 30 test cases + synthetic | Full 5-metric suite | Critical + high probes (~15 min) | App Insights + KQL dashboards | Pre-production, most projects |
| `comprehensive` | 14 metrics, 50+ test cases + custom GEval | Full suite + noise robustness | Full scan (~30 min) | Phoenix dashboard + alerts + drift | Production, high-stakes, regulated |

### Phase Integration

```
Phase 0 (Discover):
    → Ask: "What evaluation tier? (minimal/standard/comprehensive)"
    → Set eval_tier, red_team, observability flags

Phase 2 (Pipeline):
    → No changes (eval operates on outputs, not pipeline)

Phase 3 (AI):
    → Configure Phoenix/App Insights tracing on AI endpoints
    → Set up LLM token tracking custom metrics

Phase 5 (Test) — PRIMARY INTEGRATION:
    → Step 4.1: Run DeepEval test suite (pytest)
    → Step 4.2: Run RAGAS evaluation on RAG archetypes
    → Step 4.3: Run Garak red-team scan
    → Step 4.4: Generate unified eval report
    → Gate: CRITICAL Garak findings block deployment

Phase 7 (Deploy):
    → Add DeepEval + Garak to CI/CD pipeline (Azure DevOps)
    → Configure Phoenix/App Insights alerts
    → Add eval regression step before production promotion
```

### CI/CD Pipeline Integration (Azure DevOps)

```yaml
# azure-pipelines-eval.yml
trigger:
  branches:
    include:
      - main
  paths:
    include:
      - src/**
      - prompts/**
      - tests/eval/**

stages:
  - stage: Evaluate
    jobs:
      - job: DeepEvalTests
        displayName: "LLM Quality Tests"
        pool:
          vmImage: ubuntu-latest
        steps:
          - task: UsePythonVersion@0
            inputs:
              versionSpec: "3.11"
          - script: pip install deepeval ragas
          - script: |
              pytest tests/eval/test_rag_quality.py \
                --deepeval-run-name "$(Build.BuildNumber)" \
                -v --tb=short
            env:
              AZURE_OPENAI_API_KEY: $(AZURE_OPENAI_API_KEY)
              AZURE_OPENAI_ENDPOINT: $(AZURE_OPENAI_ENDPOINT)

      - job: GarakScan
        displayName: "Red-Team Scan"
        pool:
          vmImage: ubuntu-latest
        steps:
          - script: pip install garak
          - script: |
              garak --model_type rest \
                --probes promptinject,dan,leakreplay,encoding \
                --report_prefix $(Build.BuildNumber)
            env:
              AZURE_OPENAI_API_KEY: $(AZURE_OPENAI_API_KEY)
          - script: |
              python scripts/parse_garak_report.py \
                --report garak_runs/$(Build.BuildNumber).report.jsonl \
                --fail-on critical
            displayName: "Check for critical vulnerabilities"
```

---

## Dependencies

```
deepeval>=1.0
ragas>=0.1.0
garak>=0.9
arize-phoenix>=4.0
opentelemetry-api>=1.20
opentelemetry-sdk>=1.20
azure-monitor-opentelemetry>=1.0
datasets>=2.0       # For RAGAS
langchain-openai     # For RAGAS test generation
```

---

## Archetype-Specific Eval Profiles

| Archetype | Key DeepEval Metrics | Key RAGAS Metrics | Garak Focus |
|-----------|---------------------|-------------------|-------------|
| RAG | Hallucination, Faithfulness, Relevancy | Context Precision/Recall, Faithfulness | promptinject, leakreplay |
| Conversational | Knowledge Retention, Conversational, Toxicity | Faithfulness, Answer Relevancy | dan, snowball, toxicity |
| Doc Intelligence | Answer Correctness, Faithfulness | Context Recall, Faithfulness | encoding, leakreplay |
| Predictive ML | Custom GEval (prediction accuracy) | N/A | N/A |
| Knowledge Graph | Answer Correctness, Hallucination | Context Entity Recall | knowledgegraph |
| Voice/Text | Toxicity, Bias, Relevancy | Answer Relevancy | realtoxicity, bias |
| Multi-Agent | Tool Correctness, Hallucination, Conciseness | Faithfulness | promptinject, malwaregen |
| Computer Vision | Custom GEval (visual accuracy) | N/A | encoding, xss |

---

## References

- [DeepEval Documentation](https://docs.confident-ai.com/)
- [RAGAS Documentation](https://docs.ragas.io/)
- [Garak Documentation](https://docs.garak.ai/)
- [Phoenix Documentation](https://docs.arize.com/phoenix/)
- [Azure Monitor OpenTelemetry](https://learn.microsoft.com/en-us/azure/azure-monitor/app/opentelemetry-enable)
