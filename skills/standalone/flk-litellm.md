# LiteLLM Gateway Deployment Skill for Azure App Service

You are an expert at deploying and configuring LiteLLM proxy gateways on Azure App Service, specifically for routing Claude models through Azure AI Foundry to clients like Claude for Excel/PowerPoint.

## Why LiteLLM Is Needed

Azure AI Foundry exposes Claude models via the Anthropic Messages API at:
```
https://<resource>.services.ai.azure.com/anthropic/v1/messages
```

However, clients like the **Claude for Excel/PowerPoint add-in** require OpenAI-compatible endpoints:
- `GET /v1/models` — health/model discovery
- `POST /chat/completions` — inference (OpenAI format)
- `GET /health/liveliness` — liveness probe

Azure AI Foundry returns **HTTP 404 `api_not_supported`** for these endpoints. LiteLLM bridges the gap by translating OpenAI-format requests into Anthropic Messages API calls.

## Architecture

```
Claude for Excel/PowerPoint Add-in
    |
    | POST /chat/completions (OpenAI format)
    | GET /v1/models
    | Authorization: Bearer <LITELLM_MASTER_KEY>
    v
Azure App Service (Linux, B1)
    |
    | Custom Docker image: litellm-gateway:v1
    | LiteLLM proxy with baked-in config.yaml
    |
    | POST /anthropic/v1/messages (Anthropic format)
    | x-api-key: <AZURE_AI_API_KEY>
    v
Azure AI Foundry (AI Services resource)
    |
    | Claude Opus 4.6, Sonnet 4.6, Haiku 4.5
    v
Anthropic (via Azure backbone)
```

## What Works

### 1. Custom Docker Image with Baked-In Config (PROVEN)

Build a custom image that copies `config.yaml` into the image at build time. This is the **only reliable method** for Azure App Service.

**Dockerfile:**
```dockerfile
FROM ghcr.io/berriai/litellm:main-latest

# Bake config into the image - bypasses Azure App Service /home/ mount issues
COPY config.yaml /app/config.yaml

# Override CMD to use the baked-in config
CMD ["--config", "/app/config.yaml", "--port", "4000"]
```

**config.yaml:**
```yaml
model_list:
- model_name: claude-opus-4-6
  litellm_params:
    model: azure_ai/claude-opus-4-6
    api_base: https://<your-resource>.services.ai.azure.com/anthropic
    api_key: os.environ/AZURE_AI_API_KEY
    extra_headers:
      x-api-key: os.environ/AZURE_AI_API_KEY
- model_name: claude-sonnet-4-6
  litellm_params:
    model: azure_ai/claude-sonnet-4-6
    api_base: https://<your-resource>.services.ai.azure.com/anthropic
    api_key: os.environ/AZURE_AI_API_KEY
    extra_headers:
      x-api-key: os.environ/AZURE_AI_API_KEY
- model_name: claude-haiku-4-5
  litellm_params:
    model: azure_ai/claude-haiku-4-5
    api_base: https://<your-resource>.services.ai.azure.com/anthropic
    api_key: os.environ/AZURE_AI_API_KEY
    extra_headers:
      x-api-key: os.environ/AZURE_AI_API_KEY
litellm_settings:
  drop_params: true
```

**Build and push via ACR cloud build (no local Docker needed):**
```bash
# Create temp build context
mkdir /tmp/litellm-gateway
# Place Dockerfile and config.yaml in the directory

# Build in ACR cloud
az acr build \
  --registry <your-acr> \
  --image litellm-gateway:v1 \
  --file Dockerfile \
  /tmp/litellm-gateway
```

### 2. Azure AI Foundry Config Format (CRITICAL)

The `azure_ai/` provider prefix is required. LiteLLM automatically appends `/v1/messages` to the `api_base`.

| Field | Value | Notes |
|-------|-------|-------|
| `model` | `azure_ai/<deployment-name>` | Prefix is mandatory. Deployment name from AI Foundry. |
| `api_base` | `https://<resource>.services.ai.azure.com/anthropic` | Ends with `/anthropic`, NOT `/anthropic/v1/messages` |
| `api_key` | `os.environ/AZURE_AI_API_KEY` | LiteLLM resolves env vars at runtime |
| `extra_headers.x-api-key` | `os.environ/AZURE_AI_API_KEY` | Azure AI Foundry requires this header (not just `Authorization`) |

**Source:** [Anthropic support article](https://support.claude.com/en/articles/13945233-use-claude-for-excel-and-powerpoint-with-an-llm-gateway#h_6b54f11c4f) and LiteLLM docs at `litellm/docs/my-website/docs/providers/azure_ai.md`.

### 3. `drop_params: true` (REQUIRED)

The Claude for Excel add-in sends OpenAI-specific parameters that Claude doesn't support. Without `drop_params: true`, LiteLLM returns validation errors.

```yaml
litellm_settings:
  drop_params: true
```

### 4. LiteLLM Docker Entrypoint Behavior

The official LiteLLM image uses:
- **ENTRYPOINT:** `docker/prod_entrypoint.sh` (runs `exec litellm "$@"`)
- **CMD:** `["--port", "4000"]`

Azure App Service's **startup command replaces CMD only** (not ENTRYPOINT). So the startup command becomes arguments to the `litellm` CLI:

```
Startup command: --config /app/config.yaml --port 4000
Effective: litellm --config /app/config.yaml --port 4000
```

### 5. App Service Environment Variables

| Variable | Value | Purpose |
|----------|-------|---------|
| `AZURE_AI_API_KEY` | API key from AI Foundry | Resolved by `os.environ/AZURE_AI_API_KEY` in config |
| `LITELLM_MASTER_KEY` | Any secure string (e.g., `flk-team-<uuid>`) | Bearer token clients use to authenticate to the gateway |
| `WEBSITES_PORT` | `4000` | Tells App Service which port the container listens on |

### 6. Health Endpoints

| Endpoint | Method | Auth Required | Purpose |
|----------|--------|---------------|---------|
| `/health/liveliness` | GET | No | Liveness probe (returns `"I'm alive!"`) |
| `/v1/models` | GET | Yes (Bearer token) | Model discovery (Excel add-in calls this) |
| `/chat/completions` | POST | Yes (Bearer token) | Inference (OpenAI format) |
| `/v1/chat/completions` | POST | Yes (Bearer token) | Inference (with v1 prefix) |

## What Does NOT Work

### 1. `/home/` Volume Mount on Azure App Service (BROKEN)

**Symptom:** Files uploaded via Kudu VFS API (`PUT /api/vfs/home/config.yaml`) return HTTP 204 success, and `GET` returns the content correctly — but the file is **invisible inside the running container**.

**Root cause:** Azure App Service mounts `/home/` as an Azure Files share for custom Docker containers. This mount is unreliable — the container's filesystem and the Kudu SCM site see different views of `/home/`.

**Evidence:**
- Kudu VFS PUT returns 204, GET returns the YAML content
- Container logs: `Config file not found: /home/config.yaml`
- Kudu command API (`POST /api/command`) runs in the SCM container, not the app container — `ls /home/` shows the file there but the app container cannot see it

**Fix:** Bake the config into the Docker image. Do NOT rely on `/home/` for config files.

### 2. Kudu Command API Shell Limitations

The Kudu `/api/command` endpoint does NOT support:
- Pipes (`|`)
- Redirects (`>`, `>>`)
- Chained commands (`&&`, `||`)
- Complex shell constructs

It treats the entire command string as a single executable. Python one-liners with escaping also get mangled.

**Fix:** Use `az acr build` for image builds. Use App Service configuration for env vars. Don't try to run complex scripts via Kudu.

### 3. LiteLLM Without Config File (Prisma Migration Loop)

If LiteLLM starts without a `--config` flag or valid config file, it falls back to database mode and triggers Prisma migrations. Without a PostgreSQL database configured, it enters a timeout/retry loop:

```
Running prisma migrate deploy
Attempt 1 timed out
Running prisma migrate deploy
...
```

The container eventually starts but with no models configured — all inference requests fail.

**Fix:** Always provide a valid config file. The baked-in image approach ensures this.

### 4. Direct Azure AI Foundry Connection from Excel Add-in

The Claude for Excel/PowerPoint add-in cannot connect directly to Azure AI Foundry because:
- It calls `GET /v1/models` for health check — Foundry returns 404
- It sends OpenAI-format requests — Foundry expects Anthropic format
- The `api_not_supported` error has no workaround on the Foundry side

**Fix:** LiteLLM proxy is required.

### 5. `CONFIG_FILE_PATH` Environment Variable

LiteLLM's `proxy_server.py` checks for `CONFIG_FILE_PATH` env var, but this only works if the file actually exists on disk. On App Service with the `/home/` mount issue, setting `CONFIG_FILE_PATH=/home/config.yaml` fails the same way as `--config /home/config.yaml`.

**Fix:** Bake config into the image at a path that's part of the image filesystem (e.g., `/app/config.yaml`).

## Step-by-Step Deployment Procedure

### Prerequisites
- Azure subscription with AI Services resource (Claude models deployed)
- Azure Container Registry (ACR) — any tier
- Azure App Service Plan (Linux, B1 minimum)

### Step 1: Prepare Build Context

```bash
mkdir /tmp/litellm-gateway
```

Create `Dockerfile`:
```dockerfile
FROM ghcr.io/berriai/litellm:main-latest
COPY config.yaml /app/config.yaml
CMD ["--config", "/app/config.yaml", "--port", "4000"]
```

Create `config.yaml` with your model deployments (see format above).

### Step 2: Build and Push to ACR

```bash
# Enable ACR admin user (needed for App Service pull)
az acr update --name <acr-name> --admin-enabled true

# Build in the cloud (no local Docker needed)
az acr build \
  --registry <acr-name> \
  --image litellm-gateway:v1 \
  --file Dockerfile \
  /tmp/litellm-gateway
```

### Step 3: Create App Service (if not exists)

```bash
# Create App Service Plan
az appservice plan create \
  --name <plan-name> \
  --resource-group <rg> \
  --sku B1 \
  --is-linux

# Create Web App
az webapp create \
  --name <app-name> \
  --resource-group <rg> \
  --plan <plan-name> \
  --deployment-container-image-name <acr-name>.azurecr.io/litellm-gateway:v1
```

### Step 4: Configure Container and Environment

```bash
# Set container image
az webapp config container set \
  --name <app-name> \
  --resource-group <rg> \
  --docker-custom-image-name <acr-name>.azurecr.io/litellm-gateway:v1 \
  --docker-registry-server-url https://<acr-name>.azurecr.io \
  --docker-registry-server-user <acr-admin-user> \
  --docker-registry-server-password <acr-admin-password>

# Set environment variables
az webapp config appsettings set \
  --name <app-name> \
  --resource-group <rg> \
  --settings \
    AZURE_AI_API_KEY="<your-api-key>" \
    LITELLM_MASTER_KEY="<your-master-key>" \
    WEBSITES_PORT="4000"

# Set startup command
az webapp config set \
  --name <app-name> \
  --resource-group <rg> \
  --startup-file "--config /app/config.yaml --port 4000"
```

### Step 5: Restart and Verify

```bash
# Full restart (stop + start ensures new image is pulled)
az webapp stop --name <app-name> --resource-group <rg>
az webapp start --name <app-name> --resource-group <rg>

# Wait 2-3 minutes for image pull and startup
# First pull takes ~4 minutes for the ~1.2GB LiteLLM image
```

### Step 6: Test

```bash
# Health check
curl https://<app-name>.azurewebsites.net/health/liveliness

# Model list
curl -H "Authorization: Bearer <master-key>" \
  https://<app-name>.azurewebsites.net/v1/models

# Inference test
curl -X POST https://<app-name>.azurewebsites.net/chat/completions \
  -H "Authorization: Bearer <master-key>" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude-sonnet-4-6",
    "messages": [{"role": "user", "content": "Say hello"}],
    "max_tokens": 50
  }'
```

## Claude for Excel/PowerPoint Configuration

Once the gateway is running, configure the Claude add-in:

1. Open Excel or PowerPoint
2. Go to the Claude add-in settings
3. Select **"Use enterprise gateway"** (or "LLM Gateway")
4. Enter:
   - **Gateway URL:** `https://<app-name>.azurewebsites.net`
   - **API Key / Token:** The `LITELLM_MASTER_KEY` value
5. Select model (e.g., `claude-sonnet-4-6`)
6. Test the connection

## Updating Models

To add or change model deployments:

1. Update `config.yaml` locally
2. Rebuild the image:
   ```bash
   az acr build --registry <acr> --image litellm-gateway:v2 --file Dockerfile /tmp/litellm-gateway
   ```
3. Update App Service:
   ```bash
   az webapp config container set --name <app> --resource-group <rg> \
     --docker-custom-image-name <acr>.azurecr.io/litellm-gateway:v2
   ```
4. Restart:
   ```bash
   az webapp stop --name <app> --resource-group <rg>
   az webapp start --name <app> --resource-group <rg>
   ```

## Load Balancing Multiple Deployments

LiteLLM supports multiple deployments under the same `model_name` for load balancing. Useful when you have per-deployment rate limits:

```yaml
model_list:
- model_name: claude-opus-4-6
  litellm_params:
    model: azure_ai/claude-opus-4-6-node1
    api_base: https://<resource>.services.ai.azure.com/anthropic
    api_key: os.environ/AZURE_AI_API_KEY
    extra_headers:
      x-api-key: os.environ/AZURE_AI_API_KEY
- model_name: claude-opus-4-6
  litellm_params:
    model: azure_ai/claude-opus-4-6-node2
    api_base: https://<resource>.services.ai.azure.com/anthropic
    api_key: os.environ/AZURE_AI_API_KEY
    extra_headers:
      x-api-key: os.environ/AZURE_AI_API_KEY
```

LiteLLM automatically round-robins requests across deployments with the same `model_name`.

## Monitoring and Troubleshooting

### Check Container Logs

```bash
# Docker platform logs (pull status, start/stop)
# Via Kudu API:
TOKEN=$(az account get-access-token --resource https://management.azure.com --query accessToken -o tsv)
curl -H "Authorization: Bearer $TOKEN" \
  "https://<app>.scm.azurewebsites.net/api/logs/docker"
# Returns JSON list of log file URLs — GET each URL for content

# Application logs (LiteLLM output)
# Look for files named *_default_docker.log
```

### Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `Config file not found: /home/config.yaml` | `/home/` mount invisible to container | Bake config into image |
| `Running prisma migrate deploy` (loop) | No config file, LiteLLM defaults to DB mode | Provide valid config |
| `api_not_supported` (404 from Foundry) | Client hitting Foundry directly | Route through LiteLLM |
| Health timeout on first deploy | Image pulling (~4 min for 1.2GB) | Wait longer, check docker.log |
| `401 Unauthorized` on inference | Wrong `LITELLM_MASTER_KEY` | Check `Authorization: Bearer <key>` |
| Model not found | `model_name` in config doesn't match request | Names are case-sensitive |

### Cost

- **Azure App Service B1:** ~$13/month
- **ACR Basic:** ~$5/month
- **Claude inference:** Per-token pricing through Azure AI Foundry

## Fluke Team Deployment Reference

| Resource | Value |
|----------|-------|
| App Service | `flk-team-ai-llm-gateway` |
| Resource Group | `flk-team-ai-enablement-rg` |
| ACR | `flkdockerregistry` |
| Image | `flkdockerregistry.azurecr.io/litellm-gateway:v1` |
| AI Services | `flk-team-ai-enablement-ai` |
| Gateway URL | `https://flk-team-ai-llm-gateway.azurewebsites.net` |
| Health Check | `https://flk-team-ai-llm-gateway.azurewebsites.net/health/liveliness` |
| Models | claude-opus-4-6, claude-sonnet-4-6, claude-haiku-4-5 |
| Subscription | Fluke AI ML Technology (`77a0108c-5a42-42e7-8b7a-79367dbfc6a1`) |

## Key Lessons Learned

1. **Never rely on Azure App Service `/home/` mount for Docker containers.** The mount is unreliable and files written via Kudu are invisible to the app container.
2. **Always bake config into the Docker image.** This is the only 100% reliable method.
3. **Use `az acr build` for cloud builds.** No local Docker Desktop needed.
4. **The `extra_headers` with `x-api-key` is mandatory** for Azure AI Foundry — the standard `Authorization` header alone is insufficient.
5. **`drop_params: true` is required** when clients send OpenAI-specific parameters.
6. **First image pull takes ~4 minutes** on B1. Don't panic if health check times out initially.
7. **Stop + Start (not just Restart)** is needed to force a new image pull on App Service.
8. **LiteLLM without config enters Prisma migration mode** — always provide a config file.
9. **The Kudu command API is extremely limited** — no pipes, no redirects, no chaining. Don't try to use it for complex operations.
10. **`api_base` ends with `/anthropic`** — LiteLLM appends `/v1/messages` automatically. Do NOT include the full path.
