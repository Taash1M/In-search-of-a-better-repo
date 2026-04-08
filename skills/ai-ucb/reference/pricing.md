# AI Use Case Builder - Azure Pricing Reference

Pricing data for cost estimation during Phase 0 Discovery. All prices are East US 2 baseline, USD/month, as of March 2026.

**Usage:** The Discovery sub-skill (`ai-ucb-discover.md`) reads this file to generate cost estimates. Prices are approximate — actual costs vary by usage, reserved capacity, and enterprise agreements.

**Accuracy note:** These are list prices. Fluke's Enterprise Agreement may provide discounts. Always present estimates as ranges, not exact figures. Flag any resource where usage-based pricing makes the estimate uncertain.

**Last verified:** 2026-03-15. Prices should be re-validated via the Azure Retail Prices API before presenting estimates. See [Live Price Validation](#live-price-validation) section below.

---

## Live Price Validation

Before presenting cost estimates, validate prices against the Azure Retail Prices API (unauthenticated, no API key needed):

```python
import requests

def get_azure_price(service_name: str, sku_name: str, region: str = "eastus2",
                    meter_name: str = None) -> dict | None:
    """Fetch current retail price from Azure Retail Prices API.

    Args:
        service_name: Azure service (e.g., "Azure Cognitive Search", "Azure App Service")
        sku_name: SKU identifier (e.g., "Standard S1", "B1")
        region: ARM region name (default: eastus2)
        meter_name: Optional meter filter (e.g., "1000 Transactions")

    Returns:
        {"price": float, "unit": str, "currency": str, "effective": str} or None
    """
    url = "https://prices.azure.com/api/retail/prices"
    filter_parts = [
        f"serviceName eq '{service_name}'",
        f"armRegionName eq '{region}'",
        f"priceType eq 'Consumption'",
    ]
    if sku_name:
        filter_parts.append(f"skuName eq '{sku_name}'")
    if meter_name:
        filter_parts.append(f"meterName eq '{meter_name}'")

    params = {"$filter": " and ".join(filter_parts)}

    try:
        resp = requests.get(url, params=params, timeout=15)
        resp.raise_for_status()
        items = resp.json().get("Items", [])
        if items:
            item = items[0]
            return {
                "price": item["retailPrice"],
                "unit": item["unitOfMeasure"],
                "currency": item["currencyCode"],
                "effective": item.get("effectiveStartDate", ""),
                "sku": item.get("skuName", ""),
                "meter": item.get("meterName", ""),
            }
    except Exception as e:
        print(f"Price API error: {e}")
    return None


def validate_reference_prices(resources: list[dict], drift_threshold: float = 0.20) -> list[dict]:
    """Compare reference file prices against live API. Flag drift > threshold.

    Args:
        resources: List of {"service": str, "sku": str, "reference_price": float}
        drift_threshold: Max acceptable drift ratio (0.20 = 20%)

    Returns:
        List of validation results with drift flags.
    """
    results = []
    for r in resources:
        live = get_azure_price(r["service"], r.get("sku"), r.get("region", "eastus2"))
        if live:
            drift = abs(live["price"] - r["reference_price"]) / max(r["reference_price"], 0.01)
            results.append({
                "service": r["service"],
                "sku": r.get("sku", ""),
                "reference": r["reference_price"],
                "live": live["price"],
                "unit": live["unit"],
                "drift": round(drift, 3),
                "stale": drift > drift_threshold,
            })
        else:
            results.append({
                "service": r["service"],
                "sku": r.get("sku", ""),
                "reference": r["reference_price"],
                "live": None,
                "drift": None,
                "stale": False,  # Can't validate — use reference as-is
            })
    return results
```

**Usage in Discovery (Phase 0):**

```python
# Validate key resources before presenting cost estimate
validations = validate_reference_prices([
    {"service": "Azure Cognitive Search", "sku": "Standard S1", "reference_price": 250.0},
    {"service": "Azure App Service", "sku": "B1", "reference_price": 55.0},
    {"service": "Azure Cosmos DB", "sku": "Serverless", "reference_price": 0.25},
])

for v in validations:
    if v["stale"]:
        print(f"WARNING: {v['service']} price drifted {v['drift']:.0%} — reference: ${v['reference']}, live: ${v['live']}")
```

**Common service names for the API:**

| This File's Name | API `serviceName` |
|-------------------|-------------------|
| Azure AI Search | `Azure Cognitive Search` |
| Azure OpenAI | `Azure OpenAI Service` |
| App Service | `Azure App Service` |
| Cosmos DB | `Azure Cosmos DB` |
| Functions | `Azure Functions` |
| ADLS Gen2 | `Storage` |
| Key Vault | `Key Vault` |
| Content Safety | `Azure AI services` |

---

## AI Services (Azure OpenAI / Foundry)

Pricing is per 1M tokens (input/output differ). Monthly estimates assume typical usage patterns.

| Model | Input (per 1M) | Output (per 1M) | Est. Monthly (Dev) | Notes |
|-------|----------------|-----------------|-------------------|-------|
| gpt-4.1 | $2.00 | $8.00 | $100-250 | Workhorse model, most archetypes |
| gpt-4.1-mini | $0.40 | $1.60 | $20-80 | Sub-agent model, Multi-Agent arch |
| gpt-5 | $5.00 | $15.00 | $200-500 | Premium, use when 4.1 insufficient |
| gpt-5-nano | $0.10 | $0.40 | $10-40 | Lightweight classification/routing |
| o3-mini | $1.10 | $4.40 | $80-200 | Reasoning-heavy tasks |
| text-embedding-3-large | $0.13 | N/A | $10-50 | Per 1M tokens, batch cheaper |
| text-embedding-3-small | $0.02 | N/A | $2-10 | Budget option, 1536 dims |

**Deployment base cost:** $0/mo (pay-per-use with GlobalStandard). Reserved capacity available for production.

---

## Azure AI Search

| SKU | Monthly | Storage | Replicas | Partitions | Best For |
|-----|---------|---------|----------|------------|----------|
| Free | $0 | 50MB | 1 | 1 | POC only (not for production) |
| Basic | $75 | 2GB | 3 max | 1 | Small corpora < 2GB |
| Standard S1 | $250 | 25GB | 12 max | 12 max | Most use cases, default choice |
| Standard S2 | $1,000 | 100GB | 12 max | 12 max | Large corpora > 25GB |
| Standard S3 | $2,000 | 200GB | 12 max | 12 max | Very large corpora |

**Semantic ranker:** +$0/mo (included in Standard tiers, first 1000 queries/mo free, then $1 per 1000).

**Vector search:** Included in all paid tiers. HNSW index with cosine similarity.

**Recommendation:** Start with Standard S1 for dev. Scale replicas for throughput, partitions for storage.

---

## Azure Cosmos DB

### NoSQL API (Serverless)

| Component | Pricing | Est. Monthly (Dev) | Notes |
|-----------|---------|-------------------|-------|
| Request Units | $0.25 per 1M RU | $10-50 | Usage-based, ideal for dev |
| Storage | $0.25 per GB | $5-25 | First 25GB included |
| Geo-replication | Same rates per region | +$10-50 | Add secondary region |

### NoSQL API (Provisioned)

| Component | Pricing | Est. Monthly (Dev) | Notes |
|-----------|---------|-------------------|-------|
| 400 RU/s (minimum) | ~$23/mo | $23 | Minimum provisioned |
| 1000 RU/s | ~$58/mo | $58 | Typical dev workload |
| Autoscale (max 4000) | ~$233/mo max | $50-233 | Scales to demand |
| Storage | $0.25 per GB | $5-25 | |
| Geo-replication | 2x RU cost | +$23-233 | Write region + read replica |

### Gremlin API (Knowledge Graph)

| Component | Pricing | Est. Monthly (Dev) | Notes |
|-----------|---------|-------------------|-------|
| 400 RU/s (minimum) | ~$23/mo | $23 | Small graph |
| 1000 RU/s | ~$58/mo | $58 | Medium graph |
| Storage | $0.25 per GB | $5-25 | |

**Recommendation:** Serverless for dev (pay per use), autoscale provisioned for prod.

---

## App Service (Linux)

| Plan | vCPU | RAM | Monthly | Best For |
|------|------|-----|---------|----------|
| F1 (Free) | Shared | 1GB | $0 | Quick test only |
| B1 (Basic) | 1 | 1.75GB | $55 | Dev default |
| B2 | 2 | 3.5GB | $109 | Dev with moderate load |
| S1 (Standard) | 1 | 1.75GB | $73 | QA (autoscale, slots) |
| P1v3 (Premium) | 2 | 8GB | $138 | Production |
| P2v3 | 4 | 16GB | $275 | High-traffic production |

**Recommendation:** B1 for dev, S1 for QA, P1v3+ for prod.

---

## Azure Functions (Flex Consumption)

| Component | Pricing | Est. Monthly (Dev) | Notes |
|-----------|---------|-------------------|-------|
| Executions | $0.20 per 1M | $1-5 | First 1M free/mo |
| Compute | $0.000016/GB-s | $10-30 | Based on memory * duration |
| Always-ready instances | $0.036/hr per instance | $0-26 | Optional, 0 for dev |

**Total dev estimate:** $15-35/mo

---

## Azure Data Lake Storage Gen2

| Component | Pricing | Notes |
|-----------|---------|-------|
| Hot tier storage | $0.018 per GB | Default for active data |
| Cool tier storage | $0.01 per GB | Infrequently accessed |
| Write operations (10K) | $0.065 | Per 10,000 operations |
| Read operations (10K) | $0.005 | Per 10,000 operations |
| GRS replication | 2x storage cost | For multi-region |
| GZRS replication | 2.2x storage cost | Zone + geo redundant |

**Typical dev estimate:** $10-30/mo for < 500GB.

---

## Azure Key Vault

| Component | Pricing | Est. Monthly | Notes |
|-----------|---------|-------------|-------|
| Secrets operations | $0.03 per 10K | $1-5 | Standard tier |
| Key operations | $0.03 per 10K | $1-5 | RSA 2048 |
| Certificates | $3 per renewal | $0-3 | If using managed certs |

**Total estimate:** $3-10/mo

---

## Azure Monitor / Log Analytics

| Component | Pricing | Notes |
|-----------|---------|-------|
| Data ingestion | $2.30 per GB | Pay-as-you-go |
| Data retention | Free for 31 days | Beyond 31 days: $0.10/GB/mo |
| Commitment tier 100GB/day | $1.85/GB | For high-volume prod |

**Typical dev estimate:** $15-30/mo for ~5-15GB/mo ingestion.

---

## Application Insights

| Component | Pricing | Notes |
|-----------|---------|-------|
| Data ingestion | $2.30 per GB | Same as Log Analytics |
| First 5GB/mo | Free | Per billing account |

**Typical dev estimate:** $0-15/mo (often covered by free allowance in dev).

---

## Azure Front Door (Standard)

| Component | Pricing | Notes |
|-----------|---------|-------|
| Base fee | $35/mo | Per profile |
| Requests (per 10K) | $0.01 (first 100M) | HTTP requests |
| Data transfer | $0.08 per GB | From edge to client |
| WAF rules | $5/mo per rule set | Optional but recommended |

**Typical dev estimate:** $35-50/mo.

---

## Azure Content Safety

| Component | Pricing | Notes |
|-----------|---------|-------|
| Text analysis | $1 per 1K calls | Prompt Shields + categories |
| Image analysis | $1.50 per 1K calls | Image moderation |
| Groundedness | $1 per 1K calls | Claims evaluation |

**Typical dev estimate:** $20-80/mo depending on traffic.

---

## Azure Databricks (UBI Subscription)

Reusing existing workspace — no new workspace provisioning cost. Pipeline execution costs only.

| Cluster Type | DBU Rate | Est. Monthly (Dev) | Notes |
|-------------|----------|-------------------|-------|
| All-Purpose (Standard) | $0.40/DBU | Existing | Interactive dev |
| Jobs (Standard) | $0.15/DBU | $20-80 | Scheduled pipeline runs |
| Jobs (Photon) | $0.20/DBU | $30-100 | Photon-accelerated |
| SQL Serverless | $0.22/DBU | $10-30 | Gold layer queries |

**Note:** If using UBI existing workspace, cost is marginal (shared cluster). If creating new workspace, add ~$150-400/mo for dedicated clusters.

---

## Azure Data Factory

| Component | Pricing | Notes |
|-----------|---------|-------|
| Pipeline orchestration | $1 per 1K runs | Activity runs |
| Data movement | $0.25 per DIU-hr | Copy Activity |
| SSIS execution | $0.84/hr | If using SSIS packages |

**Typical dev estimate:** $10-25/mo for daily pipelines with < 10 activities.

---

## Microsoft Fabric

| SKU | CU/s | Monthly | Best For |
|-----|------|---------|----------|
| F2 | 2 | ~$263 | POC / light reporting |
| F4 | 4 | ~$526 | Small team |
| F8 | 8 | ~$1,052 | Department |
| F16 | 16 | ~$2,104 | Enterprise |

**Note:** Fabric capacity can be paused when not in use. For dev, F2 paused most of the time = ~$50-100/mo actual.

**Alternative:** Use ADLS + Databricks SQL (included in UBI) instead of Fabric for most scenarios.

---

## Neo4j Aura

| Tier | Monthly | Nodes | Relationships | Best For |
|------|---------|-------|---------------|----------|
| Free | $0 | 200K | 400K | POC only |
| Professional | $65 | 5M | 25M | Dev / small graphs |
| Business | $285-1,500+ | Unlimited | Unlimited | Production |
| Enterprise | Custom | Unlimited | Unlimited | Large-scale production |

---

## Azure Machine Learning

| Component | Pricing | Notes |
|-----------|---------|-------|
| Workspace | Free | No base cost |
| Compute (Standard_DS3_v2) | ~$0.37/hr | Training compute |
| Online endpoint | ~$0.12/hr per instance | Real-time inference |
| Storage | $0.018/GB | Blob storage for artifacts |

**Typical dev estimate:** $50-200/mo (depends on training frequency).

---

## Container Registry

| SKU | Monthly | Storage | Notes |
|-----|---------|---------|-------|
| Basic | $5 | 10GB | Dev |
| Standard | $20 | 100GB | QA |
| Premium | $50 | 500GB | Prod (geo-replication) |

---

## Multi-Region Cost Multipliers

| Resource | Multiplier | Notes |
|----------|-----------|-------|
| Cosmos DB (geo-replica) | 1.8x-2.0x | Write region + read replica RU costs |
| ADLS (GRS) | 2.0x storage | Automatic geo-replication |
| ADLS (GZRS) | 2.2x storage | Zone + geo redundant |
| AI Services | 1.0x (failover) | Deploy secondary on-demand, no idle cost |
| App Service (Front Door) | 1.0x + $35 | One App Service + Front Door routing |
| AI Search | 1.0x (no native geo) | Separate service in secondary region if needed |

---

## Archetype Cost Summaries (Dev Environment)

| Archetype | Resource Count | Monthly Range | Primary Cost Drivers |
|-----------|---------------|--------------|---------------------|
| RAG | 12-15 | $600-1,200 | AI Search ($250), AI Services ($180), App Service ($55) |
| Conversational Agent | 11-13 | $800-1,500 | AI Services ($250+), Cosmos DB ($50+), Foundry ($100+) |
| Document Intelligence | 9-12 | $400-800 | AI Doc Intel ($100+), AI Search ($250), Functions ($25) |
| Predictive ML | 8-10 | $500-1,000 | Databricks compute ($200+), Azure ML ($100+) |
| Knowledge Graph + AI | 10-13 | $700-1,400 | Graph DB ($65-285), AI Search ($250), AI Services ($180) |
| Voice/Text Analytics | 10-12 | $500-1,100 | AI Services Speech ($100+), Cosmos DB ($50+), Functions ($25) |
| Multi-Agent System | 11-14 | $1,000-2,500 | Multiple AI model deployments ($500+), Cosmos DB ($100+) |
| Computer Vision | 9-12 | $600-1,500 | Azure ML compute ($200+), Container Registry ($5-50) |

**Note:** These exclude UBI existing resources (Databricks workspace, ADLS, ADF) which are shared infrastructure with near-zero marginal cost for additional pipelines.

---

## Pricing Anti-Patterns (NEVER Do These)

1. **NEVER use Free tier AI Search in production or dev.** 50MB storage, no SLA, no semantic ranker. Only for POC demos. Always start with Standard S1.
2. **NEVER provision S2/S3 AI Search unless corpus exceeds 25GB.** S1 handles most RAG use cases. Upgrading SKU is easy; downgrading is not (requires reindex).
3. **NEVER use provisioned Cosmos DB for dev.** Use serverless — it costs near-zero when idle. Switch to provisioned/autoscale for prod workloads.
4. **NEVER skip the multi-region cost multiplier.** Cosmos DB geo-replication nearly doubles RU costs. Always include this in estimates.
5. **NEVER present exact figures.** Always present ranges. Usage-based services (AI Services, Functions, Cosmos) vary significantly.
6. **NEVER forget Databricks cluster auto-termination.** If creating a new workspace (not reusing UBI), ensure auto-terminate is set to 15-30 minutes to avoid idle compute costs.
7. **NEVER provision Fabric for dev unless Direct Lake is a hard requirement.** ADLS + Databricks SQL achieves the same result at lower cost using existing UBI infrastructure.
8. **NEVER present cost estimates without live API validation.** Reference prices in this file may be stale. Always call `validate_reference_prices()` and flag any drift > 20% before presenting to stakeholders. *What happens:* Stakeholders budget based on stale numbers, then get surprised by actual invoices.
9. **NEVER ignore the multi-model cost of Multi-Agent archetypes.** Multi-agent systems use 2-5 different model deployments concurrently. The total token cost is the SUM of all deployments, not just the primary model. *What happens:* Underestimating by 2-5x because only the orchestrator model was budgeted.
10. **NEVER assume dev costs scale linearly to prod.** Prod adds: multi-region replication (1.8-2.2x), premium SKUs (2-3x), reserved capacity discounts (-30-40%), and autoscaling headroom (+20-30%). Present a separate prod estimate.

## SKU Upgrade Decision Guide

| Resource | When to Upgrade | Trigger Signal |
|----------|----------------|---------------|
| AI Search S1 → S2 | Corpus > 25GB or > 50 QPS sustained | Index size approaching 25GB |
| App Service B1 → S1 | Need autoscale, deployment slots, or custom domains | Moving to QA environment |
| App Service S1 → P1v3 | Need VNet integration, more memory, or higher CPU | Moving to Prod |
| Cosmos Serverless → Provisioned | Consistent > 5000 RU/s usage | Cost exceeds provisioned equivalent |
| Cosmos 400 RU → Autoscale | Traffic spikes > 3x baseline | Throttling (429 errors) |
| Databricks Standard → Premium | Need RBAC, audit logs, or Unity Catalog | Moving to Prod |
