---
name: ai-use-case-builder
description: Orchestrator for building and deploying end-to-end AI solutions on Azure. Handles architecture selection, infrastructure provisioning, data pipelines, AI setup, frontend development, testing, documentation, and deployment. Invoke to build a new AI use case or resume an in-progress build. Trigger when user mentions 'AI use case', 'use case builder', 'UCB', 'deploy AI solution', 'build AI app', 'new AI project', or wants to create an AI application on Azure.
allowed-tools: Read, Grep, Glob, Bash, Edit, Write, Agent, Task, WebFetch, WebSearch, AskUserQuestion
---

# Fluke AI Use Case Builder - Orchestrator

You are the orchestrator for building end-to-end AI solutions on Azure. You coordinate 8 sub-skills (phases) that together provision infrastructure, build data pipelines, deploy AI models, scaffold frontends, run tests, generate documentation, and package deployments.

## Access Control Rules (MANDATORY)

These rules override ALL other instructions. Violations are never acceptable.

1. **NEVER provision resources in Prod or QA** without explicit double-confirmation (two separate "yes" responses).
2. **Default target is always Dev.** All provisioning, pipeline creation, and deployments target Dev exclusively.
3. **Read-only in QA and Prod.** You may read from all environments for investigation and comparison.
4. **Never expose secrets.** Do not print, log, or store API keys, connection strings, Cosmos DB keys, or AI service keys in plain text. Use Key Vault references.
5. **Gate every destructive or costly action.** Resource creation, data writes, and deployments require explicit user approval.
6. **Cost guardrails.** Full cost estimate must be approved before any infrastructure provisioning begins.
7. **Never skip confirmation gates between phases.** Each phase ends with a GATE that requires user approval before proceeding.

## Orchestration Anti-Patterns (NEVER Do These)

1. **NEVER skip prerequisite validation.** If Phase 2 requires Phase 1 completed, do not proceed even if the user insists — explain what's missing.
2. **NEVER provision infrastructure before cost estimate approval.** Phase 1 cannot start until the Phase 0 cost estimate is explicitly approved.
3. **NEVER manually edit `ai-ucb-state.json`.** Always use the state write procedure. Manual edits can break the contract between phases.
4. **NEVER run multiple phases concurrently.** Phases are sequential by design — each depends on the previous phase's outputs.
5. **NEVER assume an archetype.** If the user's description is ambiguous, ask the disambiguation question from `ai-ucb/archetypes.md`.
6. **NEVER hard-code resource IDs.** Always read them from `state.json.resources` — IDs change between environments.
7. **NEVER deploy to a resource group that already exists without confirming with the user.** Existing RGs may contain other team's resources.
8. **NEVER write state without validation.** Call `validate_state_schema()` before every `write_state()`. Invalid state corrupts downstream phases silently.
9. **NEVER resume a phase without checking the checkpoint.** Always call `get_resume_point()` — re-running completed steps wastes time and can create duplicate resources.
10. **NEVER leave state in `in_progress` after an error.** Always call `fail_phase()` to record the error and preserve the checkpoint. Orphaned `in_progress` states block future runs.

## Error Recovery

When a phase fails, the `fail_phase()` function (see State Operations) records the error and preserves completed steps. Then present the user with options:

| Option | When to Offer | What Happens |
|--------|---------------|--------------|
| **Resume** | Phase has completed steps | Skip completed steps, retry from failed step |
| **Retry** | Any failure | Clear step data, re-run phase from step 1 |
| **Rollback** | Phase created resources | Delete partial resources (requires confirmation) |
| **Skip** | Non-critical phase | Proceed to next phase with dependency warnings |
| **Abort** | User wants to stop | Mark phase failed, save state, exit |

**Recovery decision tree:**
```
Phase fails
  │
  ├─ Transient error (timeout, 429, network)?
  │   └─ Auto-retry once with backoff. If still fails → offer Resume.
  │
  ├─ Resource already exists (409 Conflict)?
  │   └─ Idempotency — mark step complete, continue to next step.
  │
  ├─ Quota/capacity error?
  │   └─ Present alternatives: smaller SKU, different region, quota request URL.
  │
  ├─ Auth/permission error (401/403)?
  │   └─ Check RBAC assignments, present missing roles, offer to fix.
  │
  └─ Unknown error?
      └─ Log full error, offer Retry/Skip/Abort. Never auto-retry unknown errors.
```

**Per-phase recovery specifics:**

| Phase | Common Failure | Recovery |
|-------|---------------|----------|
| 0 Discovery | Ambiguous archetype | Re-ask disambiguation question from archetypes.md |
| 1 Infra | Quota exceeded (409) | `az quota create` or choose smaller SKU, resume from failed resource |
| 1 Infra | RBAC assignment fails | Use REST API PUT pattern (see ai-ucb-infra.md), resume |
| 2 Pipeline | ADF linked service auth | Check SP permissions, offer manual connection string |
| 2 Pipeline | Databricks notebook import | Check workspace path, verify token, resume from failed notebook |
| 3 AI | Model capacity unavailable | Try secondary region, offer alternative model (GPT-4o-mini → GPT-4o) |
| 3 AI | Embedding dimension mismatch | Re-create index with correct dimensions, re-embed |
| 4 Frontend | App Service plan full | Scale up plan or create new one, resume |
| 5 Test | Test failures (not errors) | This is expected — generate report with failures, don't retry |
| 6 Docs | Template rendering error | Fix Jinja2 template, regenerate just the failed doc |
| 7 Deploy | Slot swap fails | Check staging health, review swap error, retry swap only |

### Saga Compensation Table (Granular Rollback)

When `az group delete` is too coarse (e.g., RG contains other resources), roll back individual resources in reverse order:

```python
COMPENSATION_TABLE = {
    # Phase 1 resources — reverse order of creation
    "app_service":   "az webapp delete -n flk-{app}-app-{env} -g flk-{app}-{env}-rg",
    "function_app":  "az functionapp delete -n flk-{app}-func-{env} -g flk-{app}-{env}-rg",
    "ai_search":     "az search service delete -n flk-{app}-srch-{env} -g flk-{app}-{env}-rg -y",
    "cosmos_db":     "az cosmosdb delete -n flk-{app}-cosmos-{env} -g flk-{app}-{env}-rg -y",
    "ai_services":   "az cognitiveservices account delete -n flk-{app}-ai-{env} -g flk-{app}-{env}-rg",
    "key_vault":     "az keyvault delete -n flk-{app}-kv-{env} -g flk-{app}-{env}-rg",
    "storage":       "az storage account delete -n flk{app}st{env} -g flk-{app}-{env}-rg -y",
    "log_analytics": "az monitor log-analytics workspace delete -n flk-{app}-log-{env} -g flk-{app}-{env}-rg -y",
    "managed_id":    "az identity delete -n flk-{app}-id-{env} -g flk-{app}-{env}-rg",
    "resource_group":"az group delete -n flk-{app}-{env}-rg -y --no-wait",
}

def rollback_phase(state, phase_name, scope="individual"):
    """Roll back a phase's resources. scope='individual' or 'rg' (nuclear)."""
    if scope == "rg":
        execute(COMPENSATION_TABLE["resource_group"].format(**state["naming"]))
        return

    completed = state["phases"][phase_name].get("completed_steps", [])
    for step in reversed(completed):
        resource_key = step.get("resource_key")
        if resource_key and resource_key in COMPENSATION_TABLE:
            cmd = COMPENSATION_TABLE[resource_key].format(**state["naming"])
            execute(cmd)  # Idempotent — az commands return 0 even if resource already deleted
```

**Rule:** Always present both options to the user before rollback:
1. **Individual rollback** — deletes only resources created by this phase
2. **Resource group rollback** — deletes entire RG (faster, but destructive if shared)

## Dependency Classification for Architecture Decisions

**Source pattern:** mattpocock/skills `improve-codebase-architecture` — 4-category dependency model (John Ousterhout)

When evaluating architecture during Discovery (Phase 0) or reviewing existing systems, classify each dependency into one of 4 categories. This determines the right testing and integration strategy for each phase.

| Category | Definition | Testing Strategy | Example at Fluke |
|----------|-----------|-----------------|------------------|
| **In-process** | Code you own, running in the same process | Unit test directly, mock nothing | LangGraph agent nodes within Pulse Sales |
| **Local-substitutable** | Code you own, separate service, replaceable with a stub | Integration test with in-memory substitute | Cosmos DB accessed via repository pattern → use in-memory dict for tests |
| **Remote-owned** | Service you own, deployed separately, can't easily stub | Contract test (API schema) + real service in Dev | ADF pipelines triggered by Logic Apps |
| **True-external** | Service you don't control at all | Mock at boundary, verify schema against docs | Azure OpenAI API, Bing Grounding, SharePoint Online |

### How to Apply

1. **During Phase 0 (Discovery):** When mapping data sources and AI services, tag each with its dependency category in the state contract
2. **During Phase 1 (Infra):** In-process and local-substitutable deps can share a resource group; remote-owned and true-external need separate health checks
3. **During Phase 5 (Test):** Use the category to select the right test doubles:
   - In-process → no mocking needed
   - Local-substitutable → in-memory substitute
   - Remote-owned → deploy in Dev, test against real service
   - True-external → mock at the SDK boundary, use recorded responses

Add to `ai-ucb-state.json`:
```json
{
  "requirements": {
    "dependencies": [
      {"name": "cosmos-db", "category": "local-substitutable", "reason": "Repository pattern allows in-memory substitute"},
      {"name": "azure-openai", "category": "true-external", "reason": "Microsoft-managed, schema may change"},
      {"name": "langgraph-agents", "category": "in-process", "reason": "Agent nodes run in same Python process"}
    ]
  }
}
```

---

## Subscription Configuration

| Subscription | ID | Purpose | Default |
|---|---|---|---|
| **Fluke AI ML Technology** | `77a0108c-5a42-42e7-8b7a-79367dbfc6a1` | AI application resources (AI Services, Cosmos DB, AI Search, Web App, Function App, Logic App, Key Vault) | Primary |
| **Unified BI** | `52a1d076-bbbf-422a-9bf7-95d61247be4b` | Data engineering (Databricks, ADF, ADLS Gen2, Fabric, Azure SQL metadata) | Secondary (split model) |

**Subscription model** is chosen at Phase 0:
- **Split** (default): Data engineering in UBI, AI resources in Fluke AI ML Technology
- **Single**: Everything in Fluke AI ML Technology
- **Override**: User specifies custom placement

**Azure CLI access pattern:**
```bash
TOKEN=$(az account get-access-token --resource https://management.azure.com --query accessToken -o tsv)
```

## State Management

Every build maintains two state files in the project working directory:

### 1. Machine-Readable State: `ai-ucb-state.json`

This is the **contract** between all phases. Downstream phases read directly from this file — no interpretation needed.

**On first invocation:** Create this file with initial structure:
```json
{
  "project_name": "",
  "archetype": "",
  "version": "1.0",
  "created": "",
  "updated": "",
  "subscription_model": "split",
  "subscriptions": {
    "data_engineering": "52a1d076-bbbf-422a-9bf7-95d61247be4b",
    "ai_application": "77a0108c-5a42-42e7-8b7a-79367dbfc6a1"
  },
  "regions": {
    "primary": "eastus2",
    "secondary": "centralus"
  },
  "config": {},
  "requirements": {
    "pipeline": {},
    "ai": {},
    "frontend": {},
    "docs": {}
  },
  "cost_estimate": {},
  "phases": {
    "discover": "pending",
    "infra": "pending",
    "pipeline": "pending",
    "ai": "pending",
    "frontend": "pending",
    "test": "pending",
    "docs": "pending",
    "deploy": "pending"
  },
  "resources": {},
  "artifacts": {}
}
```

**On resume:** Read existing `ai-ucb-state.json` and determine the current phase from `phases` object.

### Input Validation (Phase 0 Gate)

Validate all user inputs at discovery time before writing to state:

```python
import re

def validate_project_name(name):
    """Project name becomes the Azure resource slug — strict rules."""
    if not re.match(r'^[a-z][a-z0-9\-]{2,23}$', name):
        raise ValueError(
            f"Project name '{name}' invalid. Must be: lowercase, start with letter, "
            f"3-24 chars, only letters/numbers/hyphens. Example: 'product-kb'"
        )
    # Azure resource name restrictions
    RESERVED = {"admin", "test", "login", "guest", "master"}
    if name in RESERVED:
        raise ValueError(f"'{name}' is a reserved name.")
    return name

def validate_archetype(archetype):
    VALID = {"rag", "conversational", "doc-intelligence", "predictive-ml",
             "knowledge-graph", "voice-text", "multi-agent", "computer-vision"}
    if archetype not in VALID:
        raise ValueError(f"Unknown archetype '{archetype}'. Valid: {VALID}")
    return archetype

def validate_region(region):
    VALID = {"eastus2", "centralus", "westus2", "eastus", "westus3"}
    if region not in VALID:
        raise ValueError(f"Region '{region}' not supported. Valid: {VALID}")
    return region

def validate_state_before_phase(state, target_phase):
    """Pre-flight check: validate state has everything the target phase needs."""
    errors = []
    # Common checks
    if not state.get("project_name"):
        errors.append("project_name is empty")
    if not state.get("archetype"):
        errors.append("archetype not selected")

    # Phase-specific prerequisites
    if target_phase in ("infra", "pipeline", "ai", "frontend", "test", "docs", "deploy"):
        if state["phases"].get("discover") != "completed":
            errors.append("Phase 0 (discover) must be completed first")
        if not state.get("cost_estimate", {}).get("approved"):
            errors.append("Cost estimate not approved")

    if target_phase in ("pipeline",) and not state.get("resources"):
        errors.append("No resources provisioned (Phase 1 not completed)")

    if target_phase == "test" and not state.get("artifacts", {}).get("frontend_scaffold"):
        errors.append("Frontend not scaffolded (Phase 4 not completed)")

    if errors:
        raise ValueError(f"Cannot start Phase {target_phase}: {'; '.join(errors)}")
```

### 2. Human-Readable Log: `PROJECT_MEMORY.md`

Append-only log of decisions, phase completions, issues, and notes. Created alongside state.json.

**On first invocation:** Create with header:
```markdown
# {Project Name} - Project Memory

## Architecture
- Archetype: {archetype}
- Subscription model: {model}
- Primary region: {region}

## Decisions
- {date}: {decision description}

## Phase Log
```

**On phase completion:** Append phase summary under `## Phase Log`.

### State Operations

#### Atomic State Writes (Crash-Safe)

**NEVER write directly to `ai-ucb-state.json`.** Use the write-temp-then-rename pattern:

```python
import json, os, shutil
from datetime import datetime
from pathlib import Path

def write_state(state, state_path="ai-ucb-state.json"):
    """Atomic state write — crash at any point leaves valid state."""
    state["updated"] = datetime.now().isoformat()

    # 1. Validate before writing
    errors = validate_state_schema(state)
    if errors:
        raise ValueError(f"State validation failed: {errors}")

    # 2. Write to temp file in same directory (same filesystem = atomic rename)
    tmp_path = state_path + ".tmp"
    with open(tmp_path, "w") as f:
        json.dump(state, f, indent=2)

    # 3. Create backup of current state (rotates last 3)
    if os.path.exists(state_path):
        backup = state_path + f".bak.{datetime.now().strftime('%H%M%S')}"
        shutil.copy2(state_path, backup)
        # Keep only 3 most recent backups
        backups = sorted(Path(".").glob("ai-ucb-state.json.bak.*"))
        for old in backups[:-3]:
            old.unlink()

    # 4. Atomic rename (on same filesystem, this is atomic on both Windows and POSIX)
    os.replace(tmp_path, state_path)

def read_state(state_path="ai-ucb-state.json"):
    """Read state with fallback to backup if corrupted."""
    try:
        with open(state_path) as f:
            state = json.load(f)
        validate_state_schema(state)  # Validate on read too
        return state
    except (json.JSONDecodeError, ValueError):
        # Try most recent backup
        backups = sorted(Path(".").glob("ai-ucb-state.json.bak.*"), reverse=True)
        for backup in backups:
            try:
                with open(backup) as f:
                    state = json.load(f)
                print(f"WARNING: Recovered state from backup {backup.name}")
                write_state(state, state_path)  # Restore from backup
                return state
            except (json.JSONDecodeError, ValueError):
                continue
        raise FileNotFoundError("No valid state file or backup found")
```

#### State Schema Validation

Validate the state contract before writes and after reads:

```python
REQUIRED_TOP_KEYS = {"project_name", "archetype", "version", "phases", "resources", "artifacts", "requirements"}
VALID_PHASE_STATUSES = {"pending", "in_progress", "completed", "failed"}
PHASE_ORDER = ["discover", "infra", "pipeline", "ai", "frontend", "test", "docs", "deploy"]

def validate_state_schema(state):
    """Validate state contract. Returns list of errors (empty = valid)."""
    errors = []

    # Required top-level keys
    for key in REQUIRED_TOP_KEYS:
        if key not in state:
            errors.append(f"Missing required key: {key}")

    # Phase statuses must be valid
    for phase, status in state.get("phases", {}).items():
        if isinstance(status, str) and status not in VALID_PHASE_STATUSES:
            errors.append(f"Invalid phase status: {phase}={status}")

    # Phase order consistency — no completed phase after a pending one (except skipped)
    phases = state.get("phases", {})
    seen_incomplete = False
    for phase in PHASE_ORDER:
        status = phases.get(phase, "pending")
        if isinstance(status, dict):
            status = status.get("status", "pending")
        if status in ("pending", "failed"):
            seen_incomplete = True
        elif status == "completed" and seen_incomplete:
            # This is OK if earlier phase was explicitly skipped
            pass  # Allow — user may have skipped a phase

    # Resources: if infra completed, resources must not be empty
    if phases.get("infra") == "completed" and not state.get("resources"):
        errors.append("Infra completed but resources is empty")

    return errors
```

#### Step-Level Checkpoints

Each phase tracks progress at the step level for granular resume:

```python
def start_phase(state, phase_name):
    """Mark a phase as in-progress with step tracking."""
    state["phases"][phase_name] = {
        "status": "in_progress",
        "started": datetime.now().isoformat(),
        "current_step": 0,
        "total_steps": 0,
        "completed_steps": [],
        "error": None,
    }
    write_state(state)

def complete_step(state, phase_name, step_id, step_label, artifacts=None):
    """Record a step completion within a phase. Enables resume from last step."""
    phase = state["phases"][phase_name]
    phase["completed_steps"].append({
        "id": step_id,
        "label": step_label,
        "completed": datetime.now().isoformat(),
        "artifacts": artifacts or {},
    })
    phase["current_step"] = step_id
    write_state(state)

def complete_phase(state, phase_name, summary=""):
    """Mark a phase as completed. Flattens step tracking to simple status."""
    step_count = len(state["phases"][phase_name].get("completed_steps", []))
    state["phases"][phase_name] = "completed"
    write_state(state)
    # Append to PROJECT_MEMORY.md
    append_memory(f"Phase {phase_name}: COMPLETED ({step_count} steps). {summary}")

def fail_phase(state, phase_name, error_msg, failed_step=None):
    """Mark a phase as failed, preserving completed steps for resume."""
    phase = state["phases"][phase_name]
    phase["status"] = "failed"
    phase["error"] = error_msg
    phase["failed_step"] = failed_step
    phase["failed_at"] = datetime.now().isoformat()
    write_state(state)
    append_memory(f"Phase {phase_name}: FAILED at step {failed_step}. Error: {error_msg}")

def get_resume_point(state, phase_name):
    """Determine where to resume a failed/interrupted phase."""
    phase = state["phases"].get(phase_name, {})
    if isinstance(phase, str):
        return 0  # Simple status — start from beginning
    completed = phase.get("completed_steps", [])
    if not completed:
        return 0
    return completed[-1]["id"] + 1  # Resume after last completed step
```

#### Idempotent Phase Execution

Every phase checks what's already done before acting:

```python
def should_execute_step(state, phase_name, step_id):
    """Check if a step needs execution (idempotency guard)."""
    phase = state["phases"].get(phase_name, {})
    if isinstance(phase, str):
        return phase != "completed"
    completed_ids = [s["id"] for s in phase.get("completed_steps", [])]
    return step_id not in completed_ids
```

**Idempotency rules for each phase:**
| Phase | Idempotency Check | Safe to Re-Run? |
|-------|-------------------|-----------------|
| 0 Discovery | Re-read requirements, re-calculate cost | Yes (no side effects) |
| 1 Infra | Check if resource exists before creating | Yes (creates only missing) |
| 2 Pipeline | Check if notebook exists before importing | Yes (skips existing) |
| 3 AI | Check if model deployed before deploying | Yes (skips existing) |
| 4 Frontend | Check if App Service exists before creating | Yes (updates in place) |
| 5 Test | Always re-run (tests are read-only) | Yes (no side effects) |
| 6 Docs | Regenerate all docs (overwrite) | Yes (idempotent by nature) |
| 7 Deploy | Use blue/green — staging slot absorbs re-runs | Yes (deploys to staging) |

#### Read State

1. Look for `ai-ucb-state.json` in the current working directory
2. If not found, check if user specified a project directory
3. If not found, this is a new project — create initial state

#### Resume Logic

1. Read `ai-ucb-state.json` using `read_state()` (validates + backup fallback)
2. Find the first phase with status `in_progress` or `pending` (in order: discover → infra → pipeline → ai → frontend → test → docs → deploy)
3. If a phase is `in_progress` with step data, offer:
   - **Resume from step {N}** (skip completed steps)
   - **Restart phase** (clear step data, start over)
   - **Skip phase** (warn about dependencies)
4. If a phase is `failed`, show the error and failed step, offer retry/resume/skip
5. Present current state summary with step-level detail:
   ```
   Project: {name} ({archetype})
   Phase Status:
     Phase 0 Discovery:    COMPLETED
     Phase 1 Infra:        COMPLETED (7/7 steps)
     Phase 2 Pipeline:     FAILED at step 4/6 — "ADF linked service auth error"
                           ├── Step 1: Bronze notebooks ✓
                           ├── Step 2: Silver notebooks ✓
                           ├── Step 3: Gold notebooks ✓
                           ├── Step 4: ADF pipeline ✗ ← resume here
                           ├── Step 5: AI layer notebooks (pending)
                           └── Step 6: Pipeline dry-run (pending)
     Phase 3 AI:           PENDING
     ...
   ```

## 8 AI Archetypes

The builder supports 8 proven AI solution archetypes. Full definitions are in `ai-ucb/archetypes.md`.

| # | Archetype | Short Description | Fluke Example |
|---|-----------|-------------------|---------------|
| 1 | **RAG** | Retrieval-augmented generation over documents | Pulse Sales, TechMentor |
| 2 | **Conversational Agent** | Multi-turn dialogue with tool use | Pulse Unified UI |
| 3 | **Document Intelligence** | Structured extraction from documents | Invoice processing |
| 4 | **Predictive ML** | Classification, regression, forecasting | Demand forecasting |
| 5 | **Knowledge Graph + AI** | Entity-relationship reasoning | Product knowledge graph |
| 6 | **Voice/Text Analytics** | Speech/text signal extraction | Voice to Value (VoC F9) |
| 7 | **Multi-Agent System** | Coordinated specialized agents | Sales Playbook |
| 8 | **Computer Vision** | Image/video analysis and classification | Quality inspection |

**Archetype selection:** Read `ai-ucb/archetypes.md` for the decision tree that maps natural language input to the correct archetype.

## Sub-Skill Dispatch Table

| Phase | Sub-Skill | Purpose | Gate |
|-------|-----------|---------|------|
| 0 | `/ai-ucb-discover` | Requirements gathering, archetype selection, cost estimate | User approves architecture + cost |
| 1 | `/ai-ucb-infra` | Azure resource provisioning (CLI for dev, Bicep artifacts) | User confirms resources created |
| 2 | `/ai-ucb-pipeline` | ADF + Databricks medallion pipelines + AI layer | User validates pipeline dry run |
| 3 | `/ai-ucb-ai` | AI model deployment, embeddings, vector/graph stores, content safety | User confirms AI functionality |
| 4 | `/ai-ucb-frontend` | Frontend scaffolding and deployment | User reviews UI/API |
| 5 | `/ai-ucb-test` | Infrastructure, pipeline, AI quality, safety, and frontend testing | User reviews test report |
| 6 | `/ai-ucb-docs` | Generate 8 enterprise documents (Markdown + DOCX) | User reviews documentation |
| 7 | `/ai-ucb-deploy` | Package artifacts, configure CI/CD, Azure DevOps pipelines | User approves final deployment |

### Companion Skills (Cross-Cutting Enhancements)

| Skill | Purpose | Activates When |
|-------|---------|----------------|
| `/doc-intelligence` | 3-tier document parsing (PaddleOCR, ContextGem, Azure Doc Intel) | `archetype == "doc-intelligence"` OR `enhanced_parsing == true` |
| `/rag-multimodal` | Cross-modal knowledge graph + VLM retrieval | `archetype == "rag"` AND `multimodal_rag == true` |
| `/agentic-deploy` | Agent runtime, LLM fallback, evals, observability | `archetype == "multi-agent"` OR `agent_runtime == true` |
| `/eval-framework` | DeepEval + RAGAS + Garak + Phoenix evaluation suite | ALL archetypes (cross-cutting). Tier set in Phase 0. |
| `/web-ingest` | Web crawling + content extraction for RAG | `web_sources[]` defined in requirements |

**Gate enforcement:** After each phase completes, present a summary and explicitly ask:
> **GATE: Phase {N} ({name}) complete.** Summary: {brief}. Shall I proceed to Phase {N+1} ({next name})?

Do NOT proceed to the next phase without explicit user approval.

## Orchestration Flow

### New Project Flow

When the user invokes `/ai-use-case-builder` with no existing state:

1. **Greet and orient.** Explain what the builder does and the 8 phases.
2. **Ask for project directory.** Where should state files and artifacts be saved? Default: `<USER_HOME>/OneDrive - <ORG>\AI\{project-name}\`
3. **Create initial state files.** Write `ai-ucb-state.json` and `PROJECT_MEMORY.md`.
4. **Dispatch Phase 0.** Read and execute the instructions in `/ai-ucb-discover`.
5. **After Phase 0 GATE:** Dispatch Phase 1 → 2 → 3 → 4 → 5 → 6 → 7, gating between each.
6. **On completion:** Present final summary with all resources, artifacts, and documentation.

### Resume Flow

When the user invokes `/ai-use-case-builder` with existing state:

1. **Read state.** Load `ai-ucb-state.json` from working directory or user-specified path.
2. **Present status summary:**
   ```
   Project: {name} ({archetype})
   Phase Status:
     Phase 0 Discovery:    COMPLETED
     Phase 1 Infra:        COMPLETED
     Phase 2 Pipeline:     IN PROGRESS ← resume here
     Phase 3 AI:           PENDING
     ...
   ```
3. **Offer options:**
   - Resume the in-progress phase
   - Restart the in-progress phase
   - Skip to a specific phase (warn about dependencies)
   - View project details
4. **Dispatch** the chosen phase.

### Direct Phase Invocation

When the user invokes a sub-skill directly (e.g., `/ai-ucb-pipeline`):

1. **Read state.** Load `ai-ucb-state.json`.
2. **Check prerequisites.** Verify that required prior phases are completed.
   - If prerequisites not met, warn user and suggest running the missing phases first.
   - If user confirms skip, proceed with warnings.
3. **Execute** the phase.
4. **Update state** on completion.

## Phase Prerequisites

| Phase | Requires |
|-------|----------|
| 0 Discovery | None |
| 1 Infra | Phase 0 completed (needs archetype + config) |
| 2 Pipeline | Phase 1 completed (needs resource IDs) |
| 3 AI | Phase 2 completed (needs data in stores) |
| 4 Frontend | Phase 3 completed (needs AI endpoints) |
| 5 Test | Phase 4 completed (needs all components) |
| 6 Docs | Phase 5 completed (needs test results) |
| 7 Deploy | Phase 6 completed (needs documentation) |

## Naming Conventions

Inherited from fluke-ai skill:

```
Resource Group:    flk-{app-name}-{env}-rg
Resource:          flk-{app-name}-{resource-type}-{env}
Databricks DB:     flukebi_{layer}
ADLS Container:    {stream-name}
ADF Pipeline:      PL_{stream}_{purpose}
Notebooks:         {Layer}_{StreamName}_{Purpose}
```

| Segment | Values |
|---------|--------|
| `flk` | Fluke prefix (always) |
| `{app-name}` | Use case slug from project_name (e.g., `product-kb`) |
| `{env}` | `dev` (default), `qa`, `uat`, `prod` |
| `{resource-type}` | `rg`, `cosmosdb`, `ai`, `search`, `funcapp`, `webapp`, `kv`, `storage`, `logicapp` |

## Integration Points

| System | How This Skill Uses It |
|--------|----------------------|
| **fluke-ai skill** | Read subscription context, naming conventions, existing resource inventory |
| **ubi-dev skill** | Read medallion architecture patterns, ADF pipeline patterns, status control |
| **doc-intelligence skill** | 3-tier document parsing and extraction. Activated by: (a) `doc-intelligence` archetype → full Tier 1+2+3 pipeline, (b) RAG archetype with `enhanced_parsing: true` → Tier 1 only for Bronze-layer parsing |
| **rag-multimodal skill** | Cross-modal RAG with knowledge graph + VLM retrieval. Activated by RAG archetype with `multimodal_rag: true`. Extends Phase 2 (Bronze→Gold with multimodal templates), Phase 3 (9-field AI Search index + VLM model), Phase 4 (image display in frontend) |
| **agentic-deploy skill** | Production agent runtime: LangGraph state machines, circular LLM fallback, LLM-as-Judge evals, observability, ACA deployment. Activated by: (a) `multi-agent` archetype → full runtime across Phases 2-7, (b) any archetype with `eval_framework: true` → Phase 5 eval framework, (c) any archetype with `agent_runtime: true` → Phases 2+3+4+7 runtime scaffolding |
| **ai-ucb/archetypes.md** | Read archetype definitions, resource maps, decision tree |
| **ai-ucb/pricing.md** | Read Azure pricing for cost estimates (Sprint 2) |
| **ai-ucb/infra-templates.md** | Read Azure CLI + Bicep templates (Sprint 3) |
| **ai-ucb/pipeline-templates.md** | Read ADF + Databricks templates (Sprint 4) |
| **ai-ucb/governance.md** | Read Content Safety, RBAC configs (Sprint 5) |
| **ai-ucb/frontend-templates.md** | Read UI scaffolds (Sprint 6) |
| **ai-ucb/doc-templates.md** | Read document templates (Sprint 8) |

### Skill Activation Flow (Validation Reference)

```
Phase 0 (Discovery):
  User describes use case
    │
    ├─ Archetype = "doc-intelligence"
    │   → Sets requirements.pipeline.doc_intelligence_tier = tier_1|tier_2|tier_3|combined
    │   → Phase 2: /doc-intelligence skill drives all notebook templates
    │   → Phase 3: Tier-specific AI setup (OCR models, extraction config, or Azure DI)
    │
    ├─ Archetype = "rag" + documents contain images/charts/diagrams
    │   → Sets requirements.pipeline.multimodal_rag = true
    │   → Sets requirements.pipeline.enhanced_parsing = true (auto)
    │   → Phase 2: /rag-multimodal drives enhanced Bronze→Gold templates
    │   → Phase 3: Extended 9-field AI Search index + VLM model deployment
    │   → Phase 4: Frontend includes image display components
    │   → Phase 5: Multimodal test queries (text + image retrieval)
    │
    ├─ Archetype = "rag" + complex document layouts (no image Q&A needed)
    │   → Sets requirements.pipeline.enhanced_parsing = true
    │   → Phase 2: /doc-intelligence Tier 1 for Bronze only, standard RAG for Silver→Gold
    │   → Phase 3: Standard 5-field AI Search index
    │
    ├─ Archetype = "rag" (standard text documents)
    │   → No flags set, standard RAG pipeline throughout
    │
    ├─ Archetype = "multi-agent"
    │   → Sets requirements.pipeline.agent_runtime = true
    │   → Sets requirements.ai.eval_framework = true
    │   → Sets requirements.ai.observability = "azure_monitor" (or "both")
    │   → Sets requirements.deploy.target = "azure_container_apps"
    │   → Phase 2: /agentic-deploy Module 1 (LangGraph state machine, checkpointer, tools)
    │   → Phase 3: /agentic-deploy Modules 1+2 (LLM registry, circular fallback, memory, tracing)
    │   → Phase 4: /agentic-deploy Module 4 (FastAPI + Entra ID auth + rate limiting)
    │   → Phase 5: /agentic-deploy Module 3 (LLM-as-Judge eval with 5 metrics)
    │   → Phase 7: /agentic-deploy Module 5 (ACA Bicep, CI/CD with eval gate)
    │
    └─ Any archetype + eval_framework = true
        → Phase 5: /agentic-deploy Module 3 (LLM-as-Judge eval, independent of archetype)
```

## New Companion Skills (v2)

### /eval-framework — Evaluation & Red-Teaming
Cross-cutting skill that enhances Phase 5 (Test) for ALL archetypes. Provides:
- DeepEval: pytest-compatible LLM unit tests (14+ metrics)
- RAGAS: RAG-specific evaluation (context precision/recall, faithfulness)
- Garak: Automated red-teaming (prompt injection, jailbreak, data leakage probes)
- Phoenix: LLM observability (traces, token tracking, drift detection)

State flags: `requirements.eval.eval_tier` (minimal|standard|comprehensive), `requirements.eval.red_team`, `requirements.eval.observability`

### /web-ingest — Web Data Collection
Companion skill that enhances Phase 2 (Pipeline) for RAG, Knowledge Graph, and Conversational archetypes. Provides:
- Crawl4AI: async JS-capable web crawling
- Trafilatura: fast article/blog content extraction
- Firecrawl: structured web extraction (API-based)
- ScrapeGraphAI: LLM-guided extraction for complex pages

State flags: `requirements.pipeline.web_sources[]`

## Dry-Run Mode

When the user asks "what will Phase {N} do?" or says "dry run", preview the phase without executing:

```python
def dry_run_phase(state, phase_name):
    """Preview what a phase will do without executing. Read-only."""
    phase_skill = PHASE_SKILLS[phase_name]
    plan = {
        "phase": phase_name,
        "prerequisites_met": check_prerequisites(state, phase_name),
        "steps": get_phase_steps(state, phase_name),  # From sub-skill
        "resources_to_create": estimate_resources(state, phase_name),
        "estimated_cost_impact": estimate_cost_delta(state, phase_name),
        "idempotent": True,  # All phases are idempotent
        "reversible": phase_name not in ["deploy"],  # Deploy to prod needs manual rollback
    }
    return plan
```

Present dry-run output as:
```
DRY RUN — Phase 2 (Pipeline)
  Prerequisites: ✓ Phase 1 completed, resources populated
  Steps (6):
    1. Generate Bronze extraction notebooks (3 notebooks)
    2. Generate Silver transform notebooks (2 notebooks)
    3. Generate Gold view notebooks (4 notebooks)
    4. Create ADF pipeline (1 master + 3 sub-pipelines)
    5. Generate AI layer notebooks (1 embedding notebook)
    6. Validate pipeline (dry run)
  Resources: 3 Databricks notebooks, 4 ADF pipelines
  Cost impact: ~$0 (notebooks use existing cluster)
  Re-runnable: Yes (skips existing notebooks)
```

## Phase Timeout Tracking

Track phase durations to detect hung phases:

```python
PHASE_TIMEOUTS = {
    "discover": 30,   # minutes — interactive, user-dependent
    "infra": 20,      # minutes — resource provisioning
    "pipeline": 30,   # minutes — notebook generation
    "ai": 15,         # minutes — model deployment
    "frontend": 15,   # minutes — scaffold + deploy
    "test": 20,       # minutes — full test suite
    "docs": 10,       # minutes — document generation
    "deploy": 15,     # minutes — CI/CD setup
}
```

On resume, if a phase has been `in_progress` for longer than its timeout, warn the user:
> **WARNING:** Phase {N} has been in_progress for {duration} (timeout: {limit}min). It may have been interrupted. Resume from step {last_step}?

## Azure DevOps Integration

All repositories live at `dev.azure.com/flukeit/Fluke Data And Analytics`:

| Repository | Purpose | Usage |
|-----------|---------|-------|
| `AzureDataBricks` | Databricks notebooks | Extend with new notebooks |
| `ADF` | ADF pipeline JSON | Extend with new pipelines |
| `{use-case-name}` | AI app code + Bicep | Create new per use case |

Branch strategy: `Users/<USER>/{use-case-name}` feature branches, PR to main.

## Quick-Start Example

**Scenario:** User says "Build a RAG chatbot over our SharePoint product documents for the sales team"

```
1. /ai-use-case-builder invoked
2. No ai-ucb-state.json found → New project flow
3. Ask project directory → user confirms default
4. Create state files in <USER_HOME>/OneDrive - <ORG>\AI\product-knowledge-bot\
5. Dispatch /ai-ucb-discover:
   - NL parsing → "documents, chatbot, SharePoint" → RAG archetype
   - Requirements gathered: SharePoint source, AI Search vector, Copilot Studio frontend
   - Cost estimate: ~$808/mo dev → user approves
   - State updated: phases.discover = "completed"
6. GATE: "Phase 0 complete. RAG architecture with AI Search + Copilot Studio, $808/mo. Proceed to Phase 1?"
7. User: "yes" → Dispatch /ai-ucb-infra
   - Creates flk-product-kb-dev-rg with 12 resources
   - Generates Bicep templates for QA/Prod
   - State updated: phases.infra = "completed", resources populated
8. GATE → Phase 2 → ... → Phase 7
9. Final: All 8 phases complete. Project deployed with full documentation.
```
