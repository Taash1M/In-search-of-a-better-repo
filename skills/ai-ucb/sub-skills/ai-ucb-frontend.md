---
name: ai-ucb-frontend
description: Phase 4 Frontend sub-skill for the AI Use Case Builder. Generates frontend scaffolds (Streamlit, React/Next.js, Copilot Studio, Power Apps, API-only) based on archetype and audience. Reads requirements.frontend from ai-ucb-state.json. Configures App Service deployment, authentication, and environment variables. Invoke standalone or via orchestrator. Trigger when user mentions 'frontend', 'web app', 'Streamlit', 'React', 'Copilot Studio', 'Power Apps', 'chat interface', 'API endpoint', or 'UI scaffold'.
allowed-tools: Read, Grep, Glob, Bash, Edit, Write, Agent, AskUserQuestion
---

# AI Use Case Builder - Phase 4: Frontend (Archetype-Aware)

You are the Frontend Engineering agent. Your job is to generate frontend scaffolds, configure deployment, and wire the UI to the AI backend services configured in Phase 3.

**Key integration:** This phase consumes the AI Services endpoints, AI Search index, Cosmos DB connection, and Content Safety configuration from Phases 1-3. The frontend must use Key Vault references for all secrets — never hardcoded values.

## Access Control (Inherited)

1. **NEVER hard-code API keys, connection strings, or endpoints in frontend code.** Use environment variables backed by Key Vault.
2. **NEVER deploy frontend to production capacity.** Dev deployments use B1/B2 App Service plans.
3. **NEVER expose system prompts in client-side code.** System prompts are server-side only.
4. **NEVER bypass authentication in user-facing apps.** Entra ID is the default for internal apps.

## Prerequisites

- Phase 3 (AI Setup) must be `completed` in `ai-ucb-state.json`
- Required state: `requirements.frontend`, `resources` (AI Services, AI Search, Cosmos DB, App Service, Key Vault)

## Frontend Flow

### Step 1: Read Contract and Validate

```python
state = read_json("ai-ucb-state.json")
frontend = state["requirements"]["frontend"]
resources = state["resources"]
archetype = state["archetype"]

# Fail fast
assert frontend.get("type"), "Frontend type required"
assert frontend.get("audience"), "Target audience required"
assert frontend.get("auth_method"), "Auth method required"
```

### Step 2: Frontend Type Dispatcher

```
switch(frontend.type):
  "streamlit"       → Streamlit app scaffold [FULL]
  "react"           → React/Next.js scaffold [FULL]
  "copilot-studio"  → Copilot Studio configuration + Power Automate flows [FULL]
  "power-apps"      → Power Apps solution with Dataverse + Power Automate AI integration [FULL]
  "gradio"          → Gradio rapid-prototype UI [NEW]
                      pip install gradio
                      Best for: quick demos, internal tools, data science teams
                      Deployment: App Service (Python) or HuggingFace Spaces
  "api-only"        → Function App with OpenAPI [FULL]
```

**Recommendation engine** (if user hasn't chosen):

| Archetype | Audience | Recommended Frontend | Rationale |
|-----------|----------|---------------------|-----------|
| RAG | internal-data-team | Streamlit | Fast to build, Python-native |
| RAG | internal-business | React | Polished UI, chat + search |
| RAG | m365-users | Copilot Studio | Native Teams/Outlook integration |
| Conversational | internal-business | React | Rich chat with tool calling |
| Conversational | m365-users | Copilot Studio | M365 channel distribution |
| Doc Intelligence | internal-data-team | Streamlit | Upload + viewer workflow |
| Predictive ML | internal-business | React | Dashboard + prediction UI |
| Knowledge Graph | internal-data-team | React | Graph visualization needs JS |
| Voice/Text | internal-business | React | Audio player + analytics |
| Multi-Agent | any | React | Complex multi-panel UI |
| Computer Vision | internal-data-team | Streamlit | Image upload + annotation |
| any | internal-data-science | Gradio | Fastest prototype, Python-native |
| any | internal-demo | Gradio | Quick demo with streaming chat |
| any | external-customer | React | Production-grade required |
| any | api-consumer | API-only | No UI needed |

### Step 3: Generate Frontend Scaffold

**Read** `ai-ucb/frontend-templates.md` for all template code.

#### 3a. Streamlit [FULL]

Generate the following files:

```
{app}/frontend/
├── app.py                  # Main Streamlit application
├── requirements.txt        # Python dependencies
├── .env.template           # Environment variable template
├── startup.sh              # App Service startup command
└── utils/
    ├── ai_client.py        # AI Services wrapper (chat + embeddings)
    ├── search_client.py    # AI Search wrapper (hybrid search)
    └── auth.py             # Entra ID authentication helper
```

**Feature selection** from `requirements.frontend.features[]`:

| Feature | Streamlit Component | AI Backend |
|---------|-------------------|------------|
| `chat` | `st.chat_message` + `st.chat_input` | AI Services Chat Completions + AI Search retrieval |
| `search` | `st.text_input` + `st.expander` results | AI Search hybrid query |
| `upload` | `st.file_uploader` | Blob Storage → trigger re-indexing |
| `dashboard` | `st.metric` + `st.plotly_chart` | Cosmos DB analytics queries |
| `admin` | `st.sidebar` with config controls | Key Vault / AI Search management |
| `analytics` | `st.dataframe` + download button | Log Analytics KQL queries |

#### 3b. React/Next.js [FULL]

Generate the following scaffold:

```
{app}/frontend/
├── package.json
├── next.config.js
├── Dockerfile              # Multi-stage build
├── .env.template
├── app/
│   ├── layout.tsx          # Root layout with auth provider
│   ├── page.tsx            # Home page
│   ├── chat/page.tsx       # Chat interface (if feature: chat)
│   ├── search/page.tsx     # Search interface (if feature: search)
│   └── api/
│       ├── chat/route.ts   # Chat API route (server-side)
│       ├── search/route.ts # Search API route (server-side)
│       └── upload/route.ts # Upload API route (server-side)
├── components/
│   ├── ChatInterface.tsx   # Streaming chat with source citations
│   ├── SearchBar.tsx       # Hybrid search input
│   ├── ResultsList.tsx     # Search results with source attribution
│   ├── SourcePanel.tsx     # Document source viewer
│   └── AuthButton.tsx      # Entra ID sign-in
└── lib/
    ├── ai-client.ts        # AI Services SDK wrapper
    ├── search-client.ts    # AI Search SDK wrapper
    └── auth-config.ts      # MSAL configuration
```

#### 3c. Copilot Studio [FULL]

Generate configuration guide + Power Automate flow definitions + custom connector spec:

```
{app}/frontend/
├── COPILOT_SETUP_GUIDE.md      # Step-by-step Copilot Studio configuration
├── topics/                     # Topic flow designs (YAML descriptions)
│   ├── greeting.yaml           # Welcome topic with adaptive card
│   ├── main-query.yaml         # AI-powered Q&A topic
│   ├── escalation.yaml         # Human handoff via Omnichannel
│   └── feedback.yaml           # CSAT feedback collection
├── connectors/
│   ├── ai-backend-connector.md # Custom connector documentation
│   └── openapi-spec.yaml       # OpenAPI 3.0 spec for Function App backend
├── flows/
│   ├── ai-query-flow.json      # Power Automate: user query → Function App → response
│   ├── doc-upload-flow.json    # Power Automate: file upload → Blob → reindex trigger
│   └── feedback-flow.json      # Power Automate: feedback → Dataverse logging
└── adaptive-cards/
    ├── result-card.json        # Adaptive card for AI response with source citations
    └── upload-card.json        # File upload card (if doc-intelligence archetype)
```

**Setup guide content:**
1. Create Copilot in Copilot Studio (copilotstudio.microsoft.com)
2. Configure Generative AI: connect to Azure OpenAI via custom connector
3. Import topics from YAML definitions (manual creation guided by YAML)
4. Create Power Automate cloud flows for backend integration
5. Configure authentication (Entra ID SSO for Teams channel)
6. Deploy to channels: Teams, SharePoint, custom website embed
7. Enable analytics and conversation transcripts

**Custom connector pattern:**
- Base URL: Function App from api-only scaffold (Step 3e)
- Auth: API Key header (`x-functions-key`)
- Actions: `/chat` (POST), `/search` (GET), `/upload` (POST)
- Response schema matches adaptive card data binding

**Power Automate flow pattern:**
- Trigger: "When Copilot Studio calls a flow" (Copilot Studio connector)
- Action 1: HTTP POST to Function App `/chat` endpoint
- Action 2: Parse JSON response (response text + sources array)
- Action 3: Return to Copilot Studio (response text for display)
- Error handling: Try/Catch scope with fallback message

#### 3d. Power Apps [FULL]

Generate solution design + Dataverse schema + Power Automate flows + Power Fx formulas:

```
{app}/frontend/
├── POWERAPPS_SETUP_GUIDE.md    # Solution package and canvas/model-driven design
├── solution/
│   ├── solution-manifest.json  # Power Platform solution metadata
│   └── components.md           # Component inventory (forms, views, flows)
├── dataverse/
│   ├── schema.yaml             # Dataverse table definitions (entities + relationships)
│   ├── ai_query_log.yaml       # Query log table (user, query, response, timestamp, rating)
│   └── ai_document.yaml        # Document table (if doc-intelligence: name, status, extracted_fields)
├── flows/
│   ├── ai-query-flow.json      # Power Automate: form submit → Function App → Dataverse log
│   ├── doc-process-flow.json   # Power Automate: upload → Blob → AI pipeline → status update
│   └── scheduled-refresh.json  # Power Automate: scheduled reindex/retrain trigger
├── screens/
│   ├── HomeScreen.md           # Main navigation (gallery of recent queries/predictions)
│   ├── QueryScreen.md          # AI query interface (text input + response display)
│   ├── ResultsScreen.md        # Detailed results with source citations
│   └── AdminScreen.md          # Admin: model status, index health, usage metrics
└── formulas/
    └── power-fx-snippets.md    # Reusable Power Fx formulas for AI integration
```

**Dataverse schema pattern:**
- `ai_query_log` table: query_text, response_text, sources (multiline), confidence, created_by, created_on, rating (choice: helpful/not helpful)
- `ai_document` table (doc-intelligence): file_name, blob_url, status (choice: pending/processing/complete/error), extracted_json (multiline), processed_on
- Relationships: ai_query_log N:1 systemuser, ai_document N:1 systemuser

**Power Fx integration pattern:**
```
// Call Power Automate flow from canvas app
Set(varLoading, true);
Set(varResponse,
    AIQueryFlow.Run(TextInput_Query.Text).response
);
Set(varSources,
    ParseJSON(AIQueryFlow.Run(TextInput_Query.Text).sources)
);
Set(varLoading, false);
```

**Deployment:** Power Platform solution export → target environment import via `pac solution import`

#### 3e. API-Only [FULL]

```
{app}/frontend/
├── function_app.py         # Azure Function App entry point
├── functions/
│   ├── chat/               # Chat completion endpoint
│   │   └── __init__.py
│   ├── search/             # Search endpoint
│   │   └── __init__.py
│   └── health/             # Health check endpoint
│       └── __init__.py
├── requirements.txt
├── host.json
├── local.settings.json.template
└── openapi.yaml            # OpenAPI 3.1 specification
```

#### 3f. Gradio [FULL]

Generate the following files:

```
{app}/frontend/
├── app.py                  # Main Gradio application
├── requirements.txt        # Python dependencies (gradio, openai)
├── .env.template           # Environment variable template
└── startup.sh              # App Service startup command
```

**Gradio chat scaffold:**

```python
# Gradio chat scaffold
import gradio as gr
import os
from openai import AzureOpenAI

client = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2024-10-01",
)

def chat(message, history):
    messages = [{"role": "system", "content": "You are a helpful Fluke product assistant."}]
    for h in history:
        messages.append({"role": "user", "content": h[0]})
        messages.append({"role": "assistant", "content": h[1]})
    messages.append({"role": "user", "content": message})
    
    response = client.chat.completions.create(
        model="gpt-4.1", messages=messages, stream=True
    )
    partial = ""
    for chunk in response:
        if chunk.choices[0].delta.content:
            partial += chunk.choices[0].delta.content
            yield partial

demo = gr.ChatInterface(
    chat, title="{project_name}", theme=gr.themes.Soft(),
    examples=["What Fluke multimeter is best for HVAC?", "How do I calibrate my Fluke 87V?"],
)
demo.launch(server_name="0.0.0.0", server_port=8000)
```

**Feature selection** from `requirements.frontend.features[]`:

| Feature | Gradio Component | AI Backend |
|---------|-----------------|------------|
| `chat` | `gr.ChatInterface` with streaming | AI Services Chat Completions + AI Search retrieval |
| `search` | `gr.Textbox` + `gr.Dataframe` results | AI Search hybrid query |
| `upload` | `gr.File` + `gr.Button` | Blob Storage upload → trigger re-indexing |

### Step 3g: Retrieval Integration Module (All Python Frontends)

For Streamlit, Gradio, and API-only scaffolds, generate a `retrieval.py` module that wires to the AI Search index configured in Phase 3:

```python
# {app}/frontend/utils/retrieval.py
"""Retrieval module — hybrid search against Azure AI Search index."""
import os
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizableTextQuery
from azure.core.credentials import AzureKeyCredential

def get_search_client():
    return SearchClient(
        endpoint=os.environ["AZURE_SEARCH_ENDPOINT"],
        index_name=os.environ["AZURE_SEARCH_INDEX"],
        credential=AzureKeyCredential(os.environ["AZURE_SEARCH_KEY"]),
    )

def hybrid_search(query: str, top_k: int = 5, filters: str = None):
    """Hybrid (keyword + vector + semantic reranker) search.
    Returns list of {content, source, score} dicts."""
    client = get_search_client()
    results = client.search(
        search_text=query,
        vector_queries=[
            VectorizableTextQuery(
                text=query,
                k_nearest_neighbors=top_k,
                fields="content_vector",
            )
        ],
        query_type="semantic",
        semantic_configuration_name="default",
        filter=filters,
        top=top_k,
        select=["content", "title", "source", "page"],
    )
    return [
        {
            "content": r["content"],
            "title": r.get("title", ""),
            "source": r.get("source", ""),
            "page": r.get("page", ""),
            "score": r["@search.score"],
        }
        for r in results
    ]

def build_context(query: str, top_k: int = 5):
    """Build context string from search results for LLM prompt."""
    sources = hybrid_search(query, top_k=top_k)
    if not sources:
        return "", []
    context = "\n---\n".join(
        [f"[Source: {s['source']}, Page {s['page']}]\n{s['content']}" for s in sources]
    )
    return context, sources
```

**Wire into Streamlit app.py:**
```python
from utils.retrieval import build_context

# Inside chat handler:
context, sources = build_context(user_message)
messages = [
    {"role": "system", "content": f"Answer using ONLY the context below.\n\n{context}"},
    *history,
    {"role": "user", "content": user_message},
]
# Display sources in expander after response
with st.expander(f"Sources ({len(sources)} documents)"):
    for s in sources:
        st.markdown(f"**{s['title']}** — {s['source']}, p.{s['page']} (score: {s['score']:.2f})")
```

### Step 3h: Health Endpoints (All Frontend Types)

Generate health endpoints for App Service probes:

```python
# {app}/frontend/utils/health.py
"""Three-tier health check for App Service probes."""
import os, time, httpx

async def check_dependency(name: str, url: str, timeout: float = 5.0):
    try:
        async with httpx.AsyncClient() as client:
            start = time.time()
            r = await client.get(url, timeout=timeout)
            latency_ms = (time.time() - start) * 1000
            return {"name": name, "status": "up", "latency_ms": round(latency_ms, 1)}
    except Exception as e:
        return {"name": name, "status": "down", "error": str(type(e).__name__)}

async def readiness_check():
    """Check all AI dependencies are reachable."""
    checks = []
    # AI Services
    endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT", "")
    if endpoint:
        checks.append(await check_dependency(
            "ai_services", f"{endpoint}/openai/deployments?api-version=2024-10-01"))
    # AI Search
    search_endpoint = os.environ.get("AZURE_SEARCH_ENDPOINT", "")
    if search_endpoint:
        checks.append(await check_dependency(
            "ai_search", f"{search_endpoint}/indexes?api-version=2024-07-01"))

    all_up = all(c["status"] == "up" for c in checks)
    return {"status": "ready" if all_up else "degraded", "checks": checks}
```

**For Streamlit** — add health page at `pages/health.py`:
```python
import streamlit as st, asyncio, json
from utils.health import readiness_check

st.set_page_config(page_title="Health", page_icon="🏥")

# Return JSON for App Service probe (query param ?format=json)
params = st.query_params
if params.get("format") == "json":
    result = asyncio.run(readiness_check())
    st.json(result)
else:
    st.header("System Health")
    result = asyncio.run(readiness_check())
    for check in result["checks"]:
        status = "✅" if check["status"] == "up" else "❌"
        st.write(f"{status} **{check['name']}** — {check.get('latency_ms', 'N/A')}ms")
```

**For API-only / React backend** — add health routes:
```python
# FastAPI / Function App health routes
@app.get("/health/live")
async def liveness():
    return {"status": "ok"}  # Am I running?

@app.get("/health/ready")
async def readiness():
    result = await readiness_check()
    status_code = 200 if result["status"] == "ready" else 503
    return JSONResponse(content=result, status_code=status_code)
```

**Configure App Service health probe:**
```bash
az webapp config set --name flk-{app}-app-dev \
  --resource-group flk-{app}-dev-rg \
  --generic-configurations '{"healthCheckPath": "/health/ready"}'
```

**Probe mapping:**
| Endpoint | Probe Type | Failure Action |
|----------|-----------|----------------|
| `/health/live` | Liveness | Restart container |
| `/health/ready` | Readiness | Remove from load balancer |

**Rule:** Never put dependency checks in liveness probes — cascading restarts when a dependency is slow.

### Step 3i: Security Hardening (All Frontend Types)

#### Input Sanitization (Server-Side)

```python
# {app}/frontend/utils/security.py
"""Input/output sanitization for LLM-powered apps."""
import re, html

# Block known prompt injection patterns
INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?previous\s+instructions",
    r"you\s+are\s+now\s+",
    r"system\s*prompt",
    r"repeat\s+(your|the)\s+(system|initial)\s+(prompt|instructions)",
    r"<script",
    r"javascript:",
]

def sanitize_input(text: str, max_length: int = 4000) -> str:
    """Sanitize user input before sending to LLM. Raises ValueError on injection."""
    if not text or not text.strip():
        raise ValueError("Empty input")
    text = text[:max_length]
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            raise ValueError("Input contains disallowed pattern")
    return text.strip()

def sanitize_output(text: str) -> str:
    """Sanitize LLM output before rendering to user."""
    # Strip any leaked API keys / secrets
    text = re.sub(r'(sk-[a-zA-Z0-9]{20,})', '[REDACTED]', text)
    text = re.sub(r'(eyJ[a-zA-Z0-9_-]{50,})', '[REDACTED]', text)  # JWT tokens
    # Strip SSN, phone numbers in output (defense against PII leakage)
    text = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', '[SSN-REDACTED]', text)
    return text
```

#### Output Rendering (Client-Side)

**React** — use `react-markdown` with `rehype-sanitize`:
```tsx
import ReactMarkdown from 'react-markdown';
import rehypeSanitize from 'rehype-sanitize';

function ChatMessage({ content }: { content: string }) {
  return (
    <ReactMarkdown
      rehypePlugins={[rehypeSanitize]}
      allowedElements={['p', 'strong', 'em', 'ul', 'ol', 'li', 'code', 'pre', 'h1', 'h2', 'h3', 'a', 'table', 'thead', 'tbody', 'tr', 'th', 'td']}
      urlTransform={(url) => url.startsWith('javascript:') ? '' : url}
    >
      {content}
    </ReactMarkdown>
  );
}
```

**Streamlit** — always use default (safe) rendering:
```python
# SAFE: default markdown rendering (no HTML execution)
st.markdown(sanitize_output(response))

# NEVER: st.markdown(response, unsafe_allow_html=True)
```

#### MSAL Authentication Wiring

**Streamlit** — use `msal-streamlit-authentication`:
```python
# {app}/frontend/utils/auth.py
from msal_streamlit_authentication import msal_authentication
import os

def require_auth():
    """Block unauthenticated access. Returns user token."""
    token = msal_authentication(
        auth={
            "clientId": os.environ["AAD_CLIENT_ID"],
            "authority": f"https://login.microsoftonline.com/{os.environ['AAD_TENANT_ID']}",
        },
        cache={"cacheLocation": "sessionStorage"},
        login_request={"scopes": [f"api://{os.environ['AAD_CLIENT_ID']}/.default"]},
    )
    if not token:
        import streamlit as st
        st.warning("Please sign in to continue.")
        st.stop()
    return token
```

### Step 4: Authentication Configuration

**Dispatched by `requirements.frontend.auth_method`:**

| Auth Method | Implementation | Configuration |
|-------------|---------------|---------------|
| `entra-id` | MSAL.js (React) / msal-streamlit (Streamlit) / Function middleware | App Registration in Entra ID, redirect URIs, API permissions |
| `api-key` | Header validation in API routes | Key stored in Key Vault, rotated quarterly |
| `anonymous` | No auth (internal tools behind VPN only) | App Service access restrictions by IP/VNet |

For `entra-id` (default for internal apps):

```bash
# Create App Registration
az ad app create --display-name "flk-{app}-dev" \
  --sign-in-audience AzureADMyOrg \
  --web-redirect-uris "https://flk-{app}-dev.azurewebsites.net/.auth/login/aad/callback"

# Enable App Service Authentication (EasyAuth)
az webapp auth update --name flk-{app}-app-dev \
  --resource-group flk-{app}-dev-rg \
  --enabled true \
  --action LoginWithAzureActiveDirectory \
  --aad-client-id {app-registration-client-id}
```

### Step 5: Environment Variables Setup

```bash
# Configure App Service settings (Key Vault references)
az webapp config appsettings set --name flk-{app}-app-dev \
  --resource-group flk-{app}-dev-rg \
  --settings \
    AZURE_OPENAI_ENDPOINT="@Microsoft.KeyVault(SecretUri=https://flk-{app}-kv-dev.vault.azure.net/secrets/ai-services-endpoint)" \
    AZURE_OPENAI_KEY="@Microsoft.KeyVault(SecretUri=https://flk-{app}-kv-dev.vault.azure.net/secrets/ai-services-key)" \
    AZURE_SEARCH_ENDPOINT="@Microsoft.KeyVault(SecretUri=https://flk-{app}-kv-dev.vault.azure.net/secrets/ai-search-endpoint)" \
    AZURE_SEARCH_KEY="@Microsoft.KeyVault(SecretUri=https://flk-{app}-kv-dev.vault.azure.net/secrets/ai-search-key)" \
    AZURE_SEARCH_INDEX="{index-name}" \
    COSMOS_ENDPOINT="@Microsoft.KeyVault(SecretUri=https://flk-{app}-kv-dev.vault.azure.net/secrets/cosmos-endpoint)" \
    CONTENT_SAFETY_ENDPOINT="@Microsoft.KeyVault(SecretUri=https://flk-{app}-kv-dev.vault.azure.net/secrets/content-safety-endpoint)" \
    DEPLOYMENT_NAME="{model-deployment-name}" \
    EMBEDDING_DEPLOYMENT="{embedding-deployment-name}"
```

### Step 6: Deployment Configuration

**App Service deployment for Streamlit:**

```bash
# Configure startup command
az webapp config set --name flk-{app}-app-dev \
  --resource-group flk-{app}-dev-rg \
  --startup-file "startup.sh"

# startup.sh content:
# python -m streamlit run app.py --server.port 8000 --server.address 0.0.0.0

# Deploy via zip
cd {app}/frontend && zip -r deploy.zip . -x "*.env" "__pycache__/*"
az webapp deployment source config-zip --name flk-{app}-app-dev \
  --resource-group flk-{app}-dev-rg \
  --src deploy.zip
```

**App Service deployment for React/Next.js:**

```bash
# Build and deploy via Docker
docker build -t flk-{app}-frontend:dev .
az acr login --name flk{app}acrdev
docker tag flk-{app}-frontend:dev flk{app}acrdev.azurecr.io/frontend:latest
docker push flk{app}acrdev.azurecr.io/frontend:latest

az webapp config container set --name flk-{app}-app-dev \
  --resource-group flk-{app}-dev-rg \
  --container-image-name flk{app}acrdev.azurecr.io/frontend:latest
```

**Function App deployment for API-only:**

```bash
cd {app}/frontend
func azure functionapp publish flk-{app}-func-dev --python
```

### Step 7: Channel Configuration

For `requirements.frontend.channels[]`:

| Channel | Configuration | Frontend Types |
|---------|--------------|----------------|
| `web` | App Service URL (default for all) | Streamlit, React, API-only |
| `teams` | Copilot Studio → Teams channel publish | Copilot Studio |
| `outlook` | Copilot Studio → Outlook integration | Copilot Studio |
| `sharepoint` | Copilot Studio → SharePoint page embed | Copilot Studio |
| `api` | Function App URL + API Management | API-only |

### Step 8: Smoke Testing

```bash
# Health check
curl -s https://flk-{app}-app-dev.azurewebsites.net/health | jq .

# For Streamlit: verify app loads
curl -s -o /dev/null -w "%{http_code}" https://flk-{app}-app-dev.azurewebsites.net/

# For API-only: test chat endpoint
curl -s -X POST https://flk-{app}-func-dev.azurewebsites.net/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, what can you help me with?"}'

# For React: verify build output
curl -s -o /dev/null -w "%{http_code}" https://flk-{app}-app-dev.azurewebsites.net/
```

### Step 9: Present Report and Gate

```
FRONTEND REPORT — {project_name}
===================================

Archetype: {archetype}
Frontend Type: {type}
Template Status: FULL (all frontend types production-ready)

Generated Files:
| # | File | Purpose |
|---|------|---------|
{file_list}

Features:
{feature_list}

Authentication: {auth_method}
  App Registration: {client_id or "N/A"}
  EasyAuth: {enabled/disabled}

Deployment:
  App Service: flk-{app}-app-dev
  URL: https://flk-{app}-app-dev.azurewebsites.net
  Startup: {startup_command}
  Status: {deployed/pending}

Channels: {channel_list}

Smoke Test Results:
  Health Check: {pass/fail}
  UI Load: {pass/fail}
  API Response: {pass/fail}

```

Update state: `phases.frontend = "completed"`, `artifacts.frontend_scaffold`

Ask:
> **GATE: Phase 4 Frontend complete.** {type} scaffold generated with {feature_count} features. Shall I proceed to Phase 5 (Testing)?

---

## Frontend Anti-Patterns (NEVER Do These)

1. **NEVER call AI Services directly from client-side JavaScript.** All AI calls must go through server-side API routes. Client-side calls expose API keys in browser network tab.
2. **NEVER render raw model output without sanitization.** Always escape HTML in model responses to prevent XSS from adversarial prompt injection.
3. **NEVER stream responses without Content Safety pre-check.** Run Prompt Shields on the user input BEFORE sending to the model, not after streaming completes.
4. **NEVER use `st.secrets` for production Streamlit apps.** Use App Service environment variables with Key Vault references. `st.secrets` stores in `.streamlit/secrets.toml` which is a file on disk.
5. **NEVER deploy without CORS configuration.** Restrict `Access-Control-Allow-Origin` to your specific domain. Never use `*` in production.
6. **NEVER skip the loading/thinking state in chat interfaces.** Users need visual feedback that the AI is processing. Streaming responses should show token-by-token.
7. **NEVER build custom auth when Entra ID + EasyAuth is available.** App Service Authentication handles token validation, refresh, and session management. Don't reinvent it.
8. **NEVER deploy Streamlit/React without health check endpoints.** App Service needs a health probe path for monitoring and auto-restart.
9. **NEVER use `dangerouslySetInnerHTML` or `unsafe_allow_html=True` for LLM output.** LLMs can be manipulated to output JavaScript/HTML via prompt injection. Always use a sanitizing renderer.
10. **NEVER put system prompts in client-side code.** System prompts must live server-side. Client sends only user messages; server assembles full prompt with system context + retrieval results.
11. **NEVER skip input sanitization.** Every user message must pass through `sanitize_input()` before reaching the LLM. Prompt injection surged 340% in 2025 — this is the #1 OWASP LLM vulnerability.
12. **NEVER generate a frontend scaffold without the retrieval module.** A chat UI without `retrieval.py` is just a GPT wrapper. The retrieval module is what makes it a RAG application.

## Error Recovery

| Error | Recovery |
|-------|---------|
| App Service 502 Bad Gateway | Check startup command, verify Python/Node version, review App Service logs |
| Streamlit timeout on load | Increase `SCM_COMMAND_IDLE_TIMEOUT`, check dependency install time |
| MSAL redirect loop | Verify redirect URI matches App Registration, check tenant ID |
| Function App cold start slow | Enable always-on (B1+), consider premium plan for sub-second starts |
| CORS errors in browser | Add origin to App Service CORS settings or API route headers |
| Key Vault reference not resolving | Verify App Service has Key Vault Secrets User role, check secret URI format |
| Docker build fails | Check multi-stage build, verify node/python versions, check .dockerignore |
