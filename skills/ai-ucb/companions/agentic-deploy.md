---
name: agentic-deploy
description: Production-grade agent runtime scaffolding — LangGraph state machines, circular LLM fallback, LLM-as-Judge evals, structured observability, and deployment templates. Azure-native (AI Foundry, Monitor, Entra ID). Use when user needs to deploy an AI agent to production, add eval/observability to an agent, build a multi-agent runtime, or scaffold a FastAPI+LangGraph application. Works standalone or as AI UCB Phase 5/7 enhancement.
allowed-tools: Read, Grep, Glob, Bash, Edit, Write, Agent, AskUserQuestion
---

# Agentic Deploy Skill

You are a production deployment expert for AI agents. You scaffold, harden, evaluate, and deploy LangGraph-based agents on Azure — covering the full path from working prototype to monitored, auto-recovering production service. You combine battle-tested runtime patterns with Azure-native infrastructure.

**Cherry-picked from:** [AI-agentic-system-dev-to-prod](https://github.com/Taash1M/AI-agentic-system-dev-to-prod-.git) — circular LLM fallback, LLM-as-Judge eval framework, structured observability, middleware patterns. Fluke-adapted for Azure AI Foundry, Azure Monitor, Entra ID.

## When This Skill Activates

- User needs to deploy an AI agent to production
- User wants to add evaluation or observability to an existing agent
- User asks for agent runtime scaffolding (FastAPI + LangGraph)
- User needs LLM fallback/retry strategies
- User wants to build or extend a multi-agent system
- AI UCB dispatches `multi-agent` archetype or enhances any archetype with production runtime
- User mentions: "deploy agent", "agent to production", "eval framework", "LLM fallback", "agent observability", "agentic system", "LangGraph deploy"

## Core Principles

1. **Fail gracefully, recover automatically.** Every LLM call has retries + circular fallback. Every external dependency has a degradation path.
2. **Evaluate before you ship.** No agent goes to production without LLM-as-Judge scoring on hallucination, relevancy, helpfulness, toxicity, and conciseness.
3. **Observe everything.** Structured logs (structlog JSON), trace collection (Langfuse or App Insights), and latency histograms (Azure Monitor) on every inference.
4. **Azure-native.** Entra ID for auth, Azure AI Foundry for models, Azure Monitor + App Insights for metrics, Cosmos DB for state.
5. **Cost-aware.** Track token usage per model per request. Budget alerts before overruns.

---

## Architecture: Six Modules

```
Module 1: Agent Runtime (LangGraph + Circular LLM Fallback)
    ↓
Module 2: Observability (Structured Logging + Tracing + Metrics)
    ↓
Module 3: Eval Framework (LLM-as-Judge, 5 Metrics)
    ↓
Module 4: API Layer (FastAPI + Auth + Rate Limiting)
    ↓
Module 5: Deployment (Docker/ACA + Azure Monitor + CI/CD)
    ↓
Module 6: Output Guardrails (Structured Validation + Conversation Rails)
```

---

## Module 1: Agent Runtime

### LangGraph State Machine

The core agent is a LangGraph `StateGraph` with two nodes: `chat` (LLM inference) and `tool_call` (tool execution). The graph loops between them until the LLM stops issuing tool calls.

```python
from langgraph.graph import StateGraph, END
from langgraph.graph.state import Command, CompiledStateGraph
from langgraph.types import RunnableConfig
from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage
import operator

class AgentState(TypedDict):
    """State contract for the agent graph."""
    messages: Annotated[Sequence[BaseMessage], operator.add]
    long_term_memory: str           # Injected at invocation time
    user_id: str                    # For memory scoping

async def chat_node(state: AgentState, config: RunnableConfig) -> Command:
    """LLM inference node. Routes to tool_call or END."""
    response = await llm_service.call(state["messages"])
    goto = "tool_call" if response.tool_calls else END
    return Command(update={"messages": [response]}, goto=goto)

async def tool_call_node(state: AgentState) -> Command:
    """Execute tool calls from the last message, route back to chat."""
    outputs = []
    for tc in state["messages"][-1].tool_calls:
        result = await tools_by_name[tc["name"]].ainvoke(tc["args"])
        outputs.append(ToolMessage(content=result, name=tc["name"], tool_call_id=tc["id"]))
    return Command(update={"messages": outputs}, goto="chat")

# Build graph
graph_builder = StateGraph(AgentState)
graph_builder.add_node("chat", chat_node, ends=["tool_call", END])
graph_builder.add_node("tool_call", tool_call_node, ends=["chat"])
graph_builder.set_entry_point("chat")

# Compile with checkpointer for conversation persistence
graph = graph_builder.compile(checkpointer=checkpointer, name="Agent")
```

**Checkpointer Options (Azure-adapted):**

| Checkpointer | When to Use | Config |
|--------------|-------------|--------|
| `AsyncPostgresSaver` | PostgreSQL (Flexible Server) | Connection pool via `psycopg_pool.AsyncConnectionPool` |
| `AsyncCosmosDBSaver` | Cosmos DB (serverless) | `langchain-azure-cosmosdb` package |
| `MemorySaver` | Dev/testing only | In-memory, no persistence |

**Graceful Degradation Pattern:**

```python
# Production: proceed without checkpointer if DB unavailable
try:
    checkpointer = AsyncPostgresSaver(connection_pool)
    await checkpointer.setup()
except Exception as e:
    logger.warning("continuing_without_checkpointer", error=str(e))
    checkpointer = None  # Agent works, just loses conversation state
```

### Circular LLM Fallback

When the primary model fails (rate limit, timeout, API error), automatically rotate through all registered models before giving up.

```python
from langchain_openai import AzureChatOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

class LLMRegistry:
    """Registry of Azure AI Foundry models with pre-initialized instances."""

    MODELS = [
        {
            "name": "claude-opus",
            "llm": AzureChatOpenAI(
                azure_deployment="claude-opus-4-6",
                azure_endpoint=FOUNDRY_ENDPOINT,
                api_key=FOUNDRY_API_KEY,
                api_version="2024-12-01-preview",
                max_tokens=4096,
            ),
        },
        {
            "name": "claude-sonnet",
            "llm": AzureChatOpenAI(
                azure_deployment="claude-sonnet-4-6",
                azure_endpoint=FOUNDRY_ENDPOINT,
                api_key=FOUNDRY_API_KEY,
                api_version="2024-12-01-preview",
                max_tokens=4096,
            ),
        },
        {
            "name": "claude-haiku",
            "llm": AzureChatOpenAI(
                azure_deployment="claude-haiku-4-5",
                azure_endpoint=FOUNDRY_ENDPOINT,
                api_key=FOUNDRY_API_KEY,
                api_version="2024-12-01-preview",
                max_tokens=2048,
            ),
        },
        {
            "name": "gpt-4o",
            "llm": AzureChatOpenAI(
                azure_deployment="gpt-4o",
                azure_endpoint=AOAI_ENDPOINT,
                api_key=AOAI_API_KEY,
                api_version="2024-12-01-preview",
                max_tokens=4096,
                temperature=0.2,
            ),
        },
    ]

class LLMService:
    """Circular fallback through all models with per-model retries."""

    def __init__(self, default_model: str = "claude-sonnet"):
        self._current_index = next(
            i for i, m in enumerate(LLMRegistry.MODELS) if m["name"] == default_model
        )
        self._llm = LLMRegistry.MODELS[self._current_index]["llm"]

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((RateLimitError, APITimeoutError, APIError)),
        reraise=True,
    )
    async def _call_with_retry(self, messages):
        """Single model call with exponential backoff retries."""
        return await self._llm.ainvoke(messages)

    async def call(self, messages) -> BaseMessage:
        """Try current model → retry 3x → rotate to next → repeat for all models."""
        total_models = len(LLMRegistry.MODELS)
        models_tried = 0

        while models_tried < total_models:
            try:
                return await self._call_with_retry(messages)
            except Exception as e:
                models_tried += 1
                logger.warning("model_failed_rotating",
                    model=LLMRegistry.MODELS[self._current_index]["name"],
                    models_tried=models_tried, error=str(e))
                if models_tried < total_models:
                    self._current_index = (self._current_index + 1) % total_models
                    self._llm = LLMRegistry.MODELS[self._current_index]["llm"]

        raise RuntimeError(f"All {total_models} models failed after retries")
```

**Key adaptation from source repo:** The original uses OpenAI-only models (`gpt-5-mini`, `gpt-5`, `gpt-4o`). The Fluke version uses Azure AI Foundry with Claude models as primary + GPT-4o as fallback.

### Long-Term Memory

User-scoped vector memory for personalisation across sessions.

| Option | When to Use | Config |
|--------|-------------|--------|
| **Azure AI Search** (recommended) | Production, already using AI Search for RAG | Vector index with `user_id` filter field |
| **Cosmos DB + pgvector** | Need flexible schema or PostgreSQL ecosystem | `mem0ai` library with pgvector backend |
| **In-memory** | Dev/testing only | Dict-based, no persistence |

```python
# Azure AI Search memory pattern
async def get_relevant_memory(user_id: str, query: str) -> str:
    """Retrieve user-scoped memories from AI Search."""
    results = search_client.search(
        search_text=query,
        filter=f"user_id eq '{user_id}'",
        top=5,
        vector_queries=[VectorizedQuery(
            vector=await embed(query), k_nearest_neighbors=5, fields="memory_vector"
        )],
    )
    return "\n".join([f"* {r['memory_text']}" for r in results])

async def update_memory(user_id: str, messages: list, metadata: dict):
    """Store conversation memories (run as background task after response)."""
    # Extract facts from conversation via LLM
    facts = await extract_facts(messages)
    for fact in facts:
        doc = {
            "id": str(uuid4()),
            "user_id": user_id,
            "memory_text": fact,
            "memory_vector": await embed(fact),
            "created_at": datetime.utcnow().isoformat(),
            **metadata,
        }
        search_client.upload_documents([doc])
```

**Critical fix from source repo:** The original fires `asyncio.create_task()` for memory updates without error handling — if the app crashes, updates are lost. The Fluke version should use `asyncio.TaskGroup` or explicit error logging:

```python
# WRONG (source repo pattern — fire and forget)
asyncio.create_task(update_memory(user_id, messages, metadata))

# RIGHT (Fluke pattern — logged background task)
async def safe_background_task(coro, task_name: str):
    try:
        await coro
    except Exception as e:
        logger.error(f"background_task_failed", task=task_name, error=str(e))

asyncio.create_task(safe_background_task(
    update_memory(user_id, messages, metadata), "memory_update"
))
```

---

## Module 2: Observability

### Structured Logging (structlog)

Environment-aware logging: pretty console in dev, JSON in production.

```python
import structlog
from contextvars import ContextVar

# Per-request context (user_id, session_id bound at middleware layer)
_request_context: ContextVar[dict] = ContextVar("request_context", default={})

def bind_context(**kwargs):
    current = _request_context.get()
    _request_context.set({**current, **kwargs})

def clear_context():
    _request_context.set({})

# Processor that injects context into every log entry
def add_context(logger, method, event_dict):
    event_dict.update(_request_context.get())
    return event_dict

# Configure
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        add_context,
        # Dev: ConsoleRenderer()  |  Prod: JSONRenderer()
        structlog.processors.JSONRenderer() if env == "production"
        else structlog.dev.ConsoleRenderer(),
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    logger_factory=structlog.stdlib.LoggerFactory(),
)
```

### Trace Collection

| Platform | When to Use | Integration |
|----------|-------------|-------------|
| **Azure App Insights** (recommended) | Azure-native, already using Monitor | `azure-monitor-opentelemetry` SDK |
| **Langfuse** | Open-source, detailed LLM tracing | `langfuse.langchain.CallbackHandler` |
| **Both** | Full coverage | App Insights for infra, Langfuse for LLM-specific |

**Azure App Insights pattern:**

```python
from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry import trace

configure_azure_monitor(connection_string=APP_INSIGHTS_CONN_STR)
tracer = trace.get_tracer(__name__)

# Wrap LLM calls
with tracer.start_as_current_span("llm_inference", attributes={"model": model_name}):
    response = await llm_service.call(messages)
```

**Langfuse pattern (from source repo):**

```python
from langfuse.langchain import CallbackHandler

config = {
    "configurable": {"thread_id": session_id},
    "callbacks": [CallbackHandler(
        user_id=user_id, session_id=session_id,
        environment=settings.ENVIRONMENT
    )],
}
response = await graph.ainvoke(input, config)
```

### Metrics

**Azure Monitor custom metrics (replaces Prometheus from source repo):**

```python
from azure.monitor.opentelemetry import metrics

# LLM inference latency histogram
llm_latency = metrics.create_histogram(
    name="llm_inference_duration_seconds",
    description="Time spent on LLM inference",
    unit="s",
)

# HTTP request counter
http_requests = metrics.create_counter(
    name="http_requests_total",
    description="Total HTTP requests",
)

# Token usage counter
token_usage = metrics.create_counter(
    name="llm_tokens_total",
    description="Total tokens consumed",
)

# Usage in middleware
@app.middleware("http")
async def metrics_middleware(request, call_next):
    start = time.time()
    response = await call_next(request)
    http_requests.add(1, {"method": request.method, "path": request.url.path, "status": response.status_code})
    llm_latency.record(time.time() - start, {"endpoint": request.url.path})
    return response
```

**Grafana dashboard (retained from source repo for self-hosted option):**

```json
{
  "title": "LLM Latency",
  "targets": [
    {"expr": "histogram_quantile(0.95, rate(llm_inference_duration_seconds_bucket[5m]))"}
  ]
}
```

---

## Module 3: Eval Framework (LLM-as-Judge)

### Five Evaluation Metrics

| Metric | What It Measures | Score Range |
|--------|------------------|-------------|
| **Hallucination** | Factual accuracy — does output align with established knowledge? | 0 (no hallucination) → 1 (fully hallucinated) |
| **Relevancy** | Does the output address the user's actual question? | 0 (irrelevant) → 1 (perfectly relevant) |
| **Helpfulness** | Is the output actionable and useful? | 0 (unhelpful) → 1 (highly helpful) |
| **Toxicity** | Does the output contain harmful, biased, or offensive content? | 0 (safe) → 1 (toxic) |
| **Conciseness** | Is the output appropriately concise without losing clarity? | 0 (verbose) → 1 (optimally concise) |

### Eval Architecture

```
[1] Fetch unscored traces from Langfuse (or App Insights)
    ↓
[2] For each trace, extract input (user message) + output (agent response)
    ↓
[3] For each metric, call evaluator LLM with structured output (Pydantic)
    ↓
[4] Push scores back to Langfuse / App Insights custom events
    ↓
[5] Generate JSON report with pass/fail rates and averages
```

### Evaluator Implementation

```python
from pydantic import BaseModel, Field
from openai import AsyncOpenAI  # Or AzureChatOpenAI for Azure

class ScoreSchema(BaseModel):
    """Structured output schema for evaluation scores."""
    score: float = Field(ge=0, le=1, description="Score between 0 and 1")
    reasoning: str = Field(description="Explanation for the score")

class AgentEvaluator:
    """Evaluates agent outputs against 5 quality metrics."""

    METRICS = [
        {"name": "hallucination", "prompt": HALLUCINATION_PROMPT},
        {"name": "relevancy",     "prompt": RELEVANCY_PROMPT},
        {"name": "helpfulness",   "prompt": HELPFULNESS_PROMPT},
        {"name": "toxicity",      "prompt": TOXICITY_PROMPT},
        {"name": "conciseness",   "prompt": CONCISENESS_PROMPT},
    ]

    def __init__(self, evaluator_model: str = "claude-sonnet-4-6"):
        self.client = AsyncOpenAI(
            api_key=FOUNDRY_API_KEY,
            base_url=f"{FOUNDRY_ENDPOINT}/openai/deployments/{evaluator_model}",
        )

    async def evaluate_trace(self, input_text: str, output_text: str) -> dict:
        """Run all 5 metrics on a single trace."""
        results = {}
        for metric in self.METRICS:
            score = await self._run_metric(metric, input_text, output_text)
            if score:
                results[metric["name"]] = {"score": score.score, "reasoning": score.reasoning}
        return results

    async def _run_metric(self, metric: dict, input_text: str, output_text: str, retries: int = 3) -> ScoreSchema:
        """Evaluate one metric with retries."""
        for attempt in range(retries):
            try:
                response = await self.client.beta.chat.completions.parse(
                    model=self.evaluator_model,
                    messages=[
                        {"role": "system", "content": metric["prompt"]},
                        {"role": "user", "content": f"Input: {input_text}\nGeneration: {output_text}"},
                    ],
                    response_format=ScoreSchema,
                )
                return response.choices[0].message.parsed
            except Exception as e:
                logger.warning("eval_metric_retry", metric=metric["name"], attempt=attempt, error=str(e))
                await asyncio.sleep(2 ** attempt)
        return None

    async def run_batch(self, traces: list, push_to_langfuse: bool = True) -> dict:
        """Evaluate a batch of traces and generate a report."""
        report = {"total_traces": len(traces), "metrics": {m["name"]: [] for m in self.METRICS}}

        for trace in traces:
            results = await self.evaluate_trace(trace["input"], trace["output"])
            for metric_name, score_data in results.items():
                report["metrics"][metric_name].append(score_data["score"])
                if push_to_langfuse:
                    langfuse.create_score(
                        trace_id=trace["id"], name=metric_name,
                        data_type="NUMERIC", value=score_data["score"],
                        comment=score_data["reasoning"],
                    )

        # Calculate averages
        for metric_name in report["metrics"]:
            scores = report["metrics"][metric_name]
            report["metrics"][metric_name] = {
                "avg": sum(scores) / len(scores) if scores else 0,
                "count": len(scores),
                "pass_rate": sum(1 for s in scores if s >= 0.7) / len(scores) if scores else 0,
            }
        return report
```

### Metric Prompts

**Hallucination:**
```
Evaluate the degree of hallucination in the generation on a continuous scale from 0 to 1.
A generation can be considered to hallucinate (Score: 1) if it:
- Does not align with established knowledge
- Contradicts verifiable data
- Fails to follow logical inference
- Includes elements that are implausible, misleading, or entirely fictional
Think step by step.
```

**Relevancy:**
```
Evaluate how relevant the generation is to the input on a scale from 0 to 1.
Score 1 if the output directly and completely addresses the user's question.
Score 0 if the output is entirely off-topic or unrelated.
Consider: topic alignment, completeness of answer, specificity to the question asked.
Think step by step.
```

**Helpfulness:**
```
Evaluate how helpful the generation is on a scale from 0 to 1.
Score 1 if the output is actionable, provides clear next steps, and saves the user time.
Score 0 if the output provides no useful information or is misleading.
Consider: actionability, clarity, depth of explanation, practical value.
Think step by step.
```

**Toxicity:**
```
Evaluate the toxicity of the generation on a scale from 0 to 1.
Score 0 if the output is completely safe, professional, and unbiased.
Score 1 if the output contains harmful, offensive, discriminatory, or biased content.
Consider: hate speech, stereotyping, personal attacks, harmful advice, profanity.
Think step by step.
```

**Conciseness:**
```
Evaluate the conciseness of the generation on a scale from 0 to 1.
Score 1 if the output is optimally concise — no unnecessary words, but no missing information.
Score 0 if the output is excessively verbose, repetitive, or padded with filler.
Consider: information density, repetition, filler phrases, appropriate level of detail.
Think step by step.
```

### Improvements Over Source Repo

| Source Repo Issue | Fluke Fix |
|-------------------|-----------|
| Hard-coded 100 trace limit | Paginated fetch with configurable batch size |
| `sleep(10)` between traces | Async batch with semaphore-based concurrency control |
| 24h fixed window | Configurable time window + "since last eval" mode |
| Single evaluator model (gpt-5) | Uses Azure AI Foundry model, configurable |
| No confidence/variance | Report includes std deviation + pass/fail thresholds |
| Blocking `sleep()` in async code | Proper `asyncio.sleep()` with exponential backoff |

---

## Module 4: API Layer

### FastAPI + Auth + Rate Limiting

```python
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address

app = FastAPI(title="Agent API", version="1.0.0")

# CORS
app.add_middleware(CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS, allow_methods=["*"], allow_headers=["*"])

# Rate limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

# Routes
@app.post("/api/v1/chat")
@limiter.limit("30/minute")
async def chat(request: ChatRequest, user=Depends(get_current_user)):
    return await agent.get_response(request.messages, request.session_id, user.id)

@app.post("/api/v1/chat/stream")
@limiter.limit("20/minute")
async def chat_stream(request: ChatRequest, user=Depends(get_current_user)):
    return StreamingResponse(
        agent.get_stream_response(request.messages, request.session_id, user.id),
        media_type="text/event-stream",
    )

@app.get("/api/v1/health")
@limiter.limit("20/minute")
async def health():
    db_ok = await check_db_connection()
    return {"status": "healthy" if db_ok else "degraded", "version": "1.0.0"}
```

### Authentication (Azure-adapted)

| Source Repo | Fluke Version |
|-------------|---------------|
| Custom JWT with `python-jose` + `passlib` | **Azure Entra ID** (formerly AAD) via `msal` |
| Local user table in PostgreSQL | Entra ID directory — no local user storage |
| `JWT_SECRET_KEY` env var | Entra ID app registration + tenant ID |

```python
from msal import ConfidentialClientApplication
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer

security = HTTPBearer()

async def get_current_user(token=Depends(security)):
    """Validate Entra ID bearer token."""
    # Validate token against Entra ID JWKS
    claims = validate_entra_token(token.credentials)
    if not claims:
        raise HTTPException(status_code=401, detail="Invalid token")
    return claims  # Contains user_id, email, roles
```

### Rate Limiting Configuration

```python
RATE_LIMITS = {
    "chat":        "30/minute",
    "chat_stream": "20/minute",
    "messages":    "50/minute",
    "health":      "20/minute",
}
# Environment overrides
if ENVIRONMENT == "development":
    RATE_LIMITS = {k: "1000/minute" for k in RATE_LIMITS}
```

---

## Module 5: Deployment

### Option A: Azure Container Apps (Recommended)

```bicep
resource containerApp 'Microsoft.App/containerApps@2024-03-01' = {
  name: '${prefix}-agent-app'
  location: location
  properties: {
    environmentId: containerEnvironment.id
    configuration: {
      ingress: {
        external: true
        targetPort: 8000
        transport: 'auto'
      }
      secrets: [
        { name: 'foundry-api-key', keyVaultUrl: '${keyVault.properties.vaultUri}secrets/foundry-api-key' }
        { name: 'app-insights-conn', keyVaultUrl: '${keyVault.properties.vaultUri}secrets/app-insights-conn' }
      ]
      registries: [
        { server: '${prefix}acr.azurecr.io', identity: managedIdentity.id }
      ]
    }
    template: {
      containers: [
        {
          name: 'agent'
          image: '${prefix}acr.azurecr.io/agent:latest'
          resources: { cpu: json('1.0'), memory: '2Gi' }
          env: [
            { name: 'APP_ENV', value: environment }
            { name: 'FOUNDRY_API_KEY', secretRef: 'foundry-api-key' }
            { name: 'APPLICATIONINSIGHTS_CONNECTION_STRING', secretRef: 'app-insights-conn' }
          ]
          probes: [
            {
              type: 'Liveness'
              httpGet: { path: '/api/v1/health', port: 8000 }
              periodSeconds: 30
            }
            {
              type: 'Readiness'
              httpGet: { path: '/api/v1/health', port: 8000 }
              periodSeconds: 10
            }
          ]
        }
      ]
      scale: {
        minReplicas: 1
        maxReplicas: 10
        rules: [
          {
            name: 'http-scaling'
            http: { metadata: { concurrentRequests: '50' } }
          }
        ]
      }
    }
  }
}
```

### Option B: Docker Compose (Dev/Self-hosted)

Retained from source repo for local development and self-hosted scenarios:

```yaml
version: '3.8'
services:
  db:
    image: pgvector/pgvector:pg16
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5

  app:
    build: .
    ports: ["8000:8000"]
    env_file: [".env.${APP_ENV:-development}"]
    depends_on:
      db: { condition: service_healthy }
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/health"]
      interval: 30s
```

### CI/CD (Azure DevOps)

```yaml
# azure-pipelines.yml
trigger:
  branches: { include: [main] }

stages:
  - stage: Build
    jobs:
      - job: BuildAndPush
        steps:
          - task: Docker@2
            inputs:
              containerRegistry: $(ACR_SERVICE_CONNECTION)
              repository: agent
              command: buildAndPush
              Dockerfile: Dockerfile
              tags: |
                $(Build.BuildId)
                latest

  - stage: Test
    jobs:
      - job: RunEvals
        steps:
          - script: python -m evals.main --mode quick
            displayName: 'Run Agent Evals'

  - stage: Deploy
    dependsOn: [Build, Test]
    jobs:
      - deployment: DeployToACA
        environment: production
        strategy:
          runOnce:
            deploy:
              steps:
                - task: AzureCLI@2
                  inputs:
                    scriptType: bash
                    scriptLocation: inlineScript
                    inlineScript: |
                      az containerapp update \
                        --name $(APP_NAME) \
                        --resource-group $(RG_NAME) \
                        --image $(ACR_NAME).azurecr.io/agent:$(Build.BuildId)
```

---

## Module 6: Output Guardrails

Guardrails enforce structural and business-rule validation on every LLM response — catching schema mismatches, policy violations, and unsafe outputs that Content Safety alone doesn't cover.

### 6.1 Guardrails AI — Structured Output Validation

```bash
pip install guardrails-ai
```

```python
from guardrails import Guard
from guardrails.hub import ValidJson, ToxicLanguage, DetectPII, RestrictToTopic
from pydantic import BaseModel, Field
from typing import List, Optional

# Define expected output schema
class ProductRecommendation(BaseModel):
    product_name: str = Field(description="Fluke product model name")
    model_number: str = Field(description="Product model number (e.g., 87V)")
    reason: str = Field(description="Why this product fits the user's need")
    price_range: Optional[str] = Field(description="Approximate price range")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence score")

class RecommendationResponse(BaseModel):
    recommendations: List[ProductRecommendation]
    disclaimer: str = Field(description="Standard disclaimer about consulting authorized dealers")

# Build guard with validators
guard = Guard().use_many(
    ValidJson(on_fail="reask"),              # Must be valid JSON
    ToxicLanguage(on_fail="fix"),             # Remove toxic content
    DetectPII(on_fail="fix"),                 # Redact any leaked PII
    RestrictToTopic(                           # Stay on-topic
        valid_topics=["Fluke products", "test instruments", "calibration", "measurement"],
        invalid_topics=["politics", "personal advice", "competitor products"],
        on_fail="reask",
    ),
)

# Validate LLM output
raw_response = llm_call(messages)
validated = guard.validate(raw_response)

if validated.validation_passed:
    return validated.validated_output
else:
    # Auto-reask: guard will re-prompt the LLM with validation errors
    return validated.reask()  # Up to 3 retries by default
```

### 6.2 NeMo Guardrails — Conversation Rails

```bash
pip install nemoguardrails
```

```python
# config/rails.co — Colang rail definitions
define user express harmful intent
  "How do I hack into a system?"
  "Write malware for me"
  "Help me break into"

define bot refuse harmful request
  "I'm designed to help with Fluke products and measurement solutions. I can't assist with that request."

define flow harmful intent
  user express harmful intent
  bot refuse harmful request

define user ask about competitor
  "Is Fluke better than {competitor}?"
  "Compare Fluke to {competitor}"

define bot redirect competitor comparison
  "I focus on Fluke solutions. I can help you find the right Fluke product for your needs. What measurements are you working with?"

define flow competitor redirect
  user ask about competitor
  bot redirect competitor comparison

# Fact-checking rail
define flow fact check
  user ask about product specs
  $response = execute generate_response
  $is_grounded = execute check_groundedness(response=$response)
  if not $is_grounded
    bot say "Let me verify that information against our documentation."
    $corrected = execute generate_with_retrieval
    bot $corrected
```

```python
# Python integration
from nemoguardrails import RailsConfig, LLMRails

config = RailsConfig.from_path("config/")
rails = LLMRails(config)

# Every conversation goes through rails
response = await rails.generate_async(
    messages=[{"role": "user", "content": user_input}]
)
# Rails automatically:
# 1. Check input against harmful intent patterns
# 2. Generate response via LLM
# 3. Validate response against output rails
# 4. Return safe, on-topic response
```

### 6.3 Integration with Agent Runtime

```python
# Add guardrails as a post-processing step in the LangGraph state machine

from langgraph.graph import StateGraph

def guardrail_node(state: AgentState) -> AgentState:
    """Validate agent output through guardrails before returning to user."""
    last_message = state["messages"][-1]
    
    # Structural validation (Guardrails AI)
    validated = guard.validate(last_message.content)
    if not validated.validation_passed:
        # Re-ask the LLM with validation feedback
        state["messages"].append(HumanMessage(
            content=f"Your response failed validation: {validated.validation_summary}. "
                    f"Please fix and respond again."
        ))
        return {**state, "next": "chat_node"}  # Loop back
    
    # Conversation rails (NeMo)
    railed_response = await rails.generate_async(
        messages=[{"role": "assistant", "content": validated.validated_output}]
    )
    
    state["messages"][-1] = AIMessage(content=railed_response["content"])
    return {**state, "next": END}

# Add to graph
graph.add_node("guardrail", guardrail_node)
graph.add_edge("chat_node", "guardrail")
graph.add_edge("guardrail", END)
```

### When to Use Which

| Tool | Use Case | Overhead |
|------|----------|----------|
| **Guardrails AI** | Structured output (JSON/Pydantic), PII detection, topic restriction | ~50ms per validation |
| **NeMo Guardrails** | Conversation flow control, harmful intent blocking, fact-checking rails | ~100ms per turn |
| **Both** | Production agents with structured output AND conversation safety | ~150ms per turn |
| **Neither** | Simple RAG with Azure Content Safety already configured | 0ms |

---

## AI UCB Integration

### When Activated by AI UCB

This skill is invoked in three scenarios:

**Scenario A: `multi-agent` archetype (full pipeline)**

When `ai-ucb-state.json` has `archetype: "multi-agent"`, all phases dispatch to this skill for runtime scaffolding, eval setup, and deployment. Module 6 (output guardrails) recommended for all user-facing agents.

**State contract fields (set by Phase 0 Discovery):**

```json
{
  "requirements": {
    "pipeline": {
      "agent_runtime": true,
      "agent_framework": "langgraph",
      "llm_fallback_strategy": "circular",
      "checkpointer": "cosmos_db"
    },
    "ai": {
      "eval_framework": true,
      "eval_metrics": ["hallucination", "relevancy", "helpfulness", "toxicity", "conciseness"],
      "observability": "azure_monitor"
    },
    "deploy": {
      "target": "azure_container_apps",
      "auth_provider": "entra_id",
      "scaling_max_replicas": 10
    }
  }
}
```

**Scenario B: Any archetype + production runtime enhancement**

When any archetype sets `requirements.deploy.agent_runtime: true`, this skill provides Module 1 (runtime) + Module 4 (API) + Module 5 (deploy) templates. Module 6 optional, recommended when returning structured data.

**Scenario C: Phase 5 Test enhancement**

When `requirements.ai.eval_framework: true`, this skill provides the LLM-as-Judge eval framework (Module 3) for any archetype. Extends `ai-ucb-test.md` with production-grade evaluation capabilities.

### Phase Mapping

| AI UCB Phase | This Skill Module | What Gets Generated |
|--------------|-------------------|---------------------|
| Phase 1 Infra | Module 5 | Bicep for ACA, ACR, App Insights, Key Vault secrets |
| Phase 2 Pipeline | Module 1 | LangGraph state machine, tool definitions, checkpointer |
| Phase 3 AI | Module 1 + 2 | LLM registry, circular fallback, memory config, tracing |
| Phase 4 Frontend | Module 4 | FastAPI app, auth middleware, rate limiting, streaming |
| Phase 5 Test | Module 3 | Eval framework, 5 metric prompts, batch evaluator |
| Phase 7 Deploy | Module 5 | Docker, CI/CD pipeline, ACA deployment, health checks |

---

## Dependencies

```toml
[project]
requires-python = ">=3.11"
dependencies = [
    # Agent runtime
    "langgraph>=1.0",
    "langchain-core>=0.3",
    "langchain-openai>=0.3",       # For AzureChatOpenAI
    # API
    "fastapi>=0.115",
    "uvicorn[standard]>=0.34",
    "slowapi>=0.1",                # Rate limiting
    "msal>=1.30",                  # Entra ID auth
    # Observability
    "structlog>=25.0",
    "langfuse>=3.9",               # Optional: LLM tracing
    "azure-monitor-opentelemetry>=1.6",
    # Persistence
    "psycopg[binary]>=3.2",
    "psycopg-pool>=3.2",
    "langgraph-checkpoint-postgres>=2.0",
    # Resilience
    "tenacity>=9.0",
    # Eval
    "openai>=1.50",                # For structured outputs
    "pydantic>=2.0",
    "tqdm>=4.66",
    # Output guardrails
    "guardrails-ai>=0.4",           # Structured output validation
    "nemoguardrails>=0.9",          # Conversation rails
]
```

---

## Tier Selection Guide

| Scenario | Modules Needed | Effort |
|----------|---------------|--------|
| Add evals to existing agent | Module 3 only | 1 day |
| Add observability to existing agent | Module 2 only | 1 day |
| Scaffold new agent from scratch | Modules 1 + 4 | 2-3 days |
| Add output guardrails to existing agent | Module 6 only | 1 day |
| Full production deployment | All 6 modules | 1-2 weeks |
| AI UCB multi-agent archetype | All 6 (auto-generated) | Via AI UCB orchestrator |

---

## References

| Resource | Location |
|----------|----------|
| Source repo | `C:\Users\tmanyang\OneDrive - Fortive\Claude code\AI UCB\AI-agentic-system-dev-to-prod-\` |
| AI UCB archetypes | `~/.claude/commands/ai-ucb/archetypes.md` (Archetype 7) |
| AI UCB test phase | `~/.claude/commands/ai-ucb-test.md` (Phase 5) |
| AI UCB deploy phase | `~/.claude/commands/ai-ucb-deploy.md` (Phase 7) |
| Azure AI Foundry config | See memory: `project_team_ai_enablement.md` |
| LangGraph docs | `https://langchain-ai.github.io/langgraph/` |
