---
name: azure-monitor-token-metrics
description: "Azure Monitor metrics confirmed working for Anthropic Claude on AI Services — InputTokens/OutputTokens/TotalTokens + cache metrics. Use \"Models\" category (NOT \"Azure OpenAI\" category). Per-deployment per-minute granularity. No per-user dimension — correlate with diagnostic logs."
metadata: 
  node_type: memory
  type: reference
  originSessionId: 299fcb4e-617b-4e0d-917e-5e3f613c64fb
---

Azure Monitor metrics for token tracking on `flk-team-ai-enablement-ai` AI Services resource.

**Why:** AAD-authenticated users bypass LiteLLM, so usage_logger.py never fires. Azure Monitor metrics provide exact per-deployment token counts that can be correlated with diagnostic logs for per-user allocation.

**How to apply:** When building token/cost reports for AAD users, query these metrics instead of estimating from duration. Implementation plan at `Usage Tracking/Azure_Monitor_Token_Correlation_Plan.md`.

## Two Metric Families (CRITICAL — use the right one)

| Family | Metrics | Works for Claude? |
|--------|---------|-------------------|
| **Azure OpenAI** (legacy) | `ProcessedPromptTokens`, `GeneratedTokens`, `TokenTransaction` | **NO** — GPT only, confirmed zero for Claude |
| **Models** (correct) | `InputTokens`, `OutputTokens`, `TotalTokens` | **YES** — live data confirmed 2026-06-16 |

## Anthropic-Specific Cache Metrics (also working)

| Metric | Description | Volume (48h sample) |
|--------|-------------|---------------------|
| `cacheReadInputTokens` | Prompt cache reads | 473M on node2, 64M on node3 |
| `ephemeral5mInputTokens` | 5-min ephemeral cache | 48M on node2, 6.7M on node3 |
| `ephemeral1hInputTokens` | 1-hour cache | Zero (not used) |

## Query Pattern

```
GET https://management.azure.com{resourceId}/providers/microsoft.insights/metrics
  ?api-version=2024-02-01
  &metricnames=InputTokens,OutputTokens,TotalTokens,cacheReadInputTokens
  &timespan=PT48H
  &interval=PT1H
  &aggregation=Total
  &$filter=ModelDeploymentName eq '*'
```

Auth: ARM token via `az account get-access-token --resource https://management.azure.com`

## Dimensions Available

ModelDeploymentName, ModelName, ModelVersion, ApiName, Region — **NO per-user dimension** (no objectId, principalId, or callerIp).

## Per-User Allocation Strategy

1. Metrics give exact tokens per deployment per hour
2. Diagnostic logs give per-request caller identity + timestamp + deployment
3. Join on deployment + hour → allocate tokens proportionally (by request count or duration)
4. Accuracy: ~90-95% (vs ~50-80% for duration estimation)

## Scripts

- `Claude-Code-POC-ETL/investigate_azure_metrics.py` — metric definitions + token queries
- `Claude-Code-POC-ETL/investigate_cache_metrics.py` — cache metrics + 7-day trends

## Long-term: APIM AI Gateway

APIM with `llm-emit-token-metric` policy gives 100% exact per-request per-user tokens. Confirmed GA for Claude at Build 2026. Basic v2 ~$145/mo. See [[project_llm_usage_tracking]] for implementation plan.
