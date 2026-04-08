# Configurations

Everything needed to configure a Claude Code installation to work with Fluke's Azure AI Foundry
deployment — environment variables, settings files, security hooks, RBAC provisioning, and the
LLM Gateway for the Excel add-in integration.

**Sections:**
1. [Azure AI Foundry Architecture](#azure-ai-foundry-architecture)
2. [Node Architecture](#node-architecture)
3. [Environment Variables](#environment-variables)
4. [Settings Templates](#settings-templates)
5. [Hooks](#hooks)
6. [RBAC Provisioning](#rbac-provisioning)
7. [LLM Gateway (node4 / Excel)](#llm-gateway-node4--excel)
8. [Sync Workflow](#sync-workflow)
9. [Gotchas](#gotchas)

---

## Azure AI Foundry Architecture

Fluke's Claude Code deployment runs through **Azure AI Foundry**, not the Anthropic API directly.
All traffic routes through an Azure AI Services resource in East US 2.

| Field | Value |
|---|---|
| Resource name | `flk-team-ai-enablement-ai` |
| Resource group | `flk-team-ai-enablement-rg` |
| Subscription | Fluke AI ML Technology (`77a0108c-5a42-42e7-8b7a-79367dbfc6a1`) |
| Region | East US 2 |
| Base URL | `https://flk-team-ai-enablement-ai.services.ai.azure.com/anthropic` |
| API version | `2025-12-01` (required — older versions fail) |
| Auth header | `x-api-key` (NOT `api-key` — see [Gotchas](#gotchas)) |

**Shared deployments** (available across all nodes):

| Deployment name | TPM |
|---|---|
| `claude-opus-4-6` | 750 |
| `claude-sonnet-4-6` | 1,625 |
| `claude-haiku-4-5` | 100 |

---

## Node Architecture

Users are partitioned into **4 nodes** to isolate quota and throughput. Nodes 1–3 each have
dedicated model deployments; node4 routes through the LLM Gateway instead.

| Node | Users | Model Deployments | Use Case |
|---|---|---|---|
| node1 | 5 | `claude-code-node1`, `claude-sonnet-4-6-node1`, `claude-haiku-4-5-2-node1` | General coding |
| node2 | 8 | `claude-code-node2`, `claude-sonnet-4-6-node2`, `claude-haiku-4-5-2-node2` | General coding |
| node3 | 6 | `claude-code-node3`, `claude-sonnet-4-6-node3`, `claude-haiku-4-5-2-node3` | General coding |
| node4 | 12 | Shared deployments via LLM Gateway | Excel add-in (L1 users) |

**Total: 27 users across 4 nodes.**

Each node1–3 user gets a node-specific API key that maps to that node's deployments. The
`claude-code-<nodeN>` deployment is the primary Opus-class model used by Claude Code for reasoning;
haiku handles lightweight summarization and routing tasks.

---

## Environment Variables

Set these four variables for each node1–3 user. Substitute `<nodeN>` with `node1`, `node2`, or
`node3` as appropriate.

```bash
export CLAUDE_CODE_USE_FOUNDRY=1
export ANTHROPIC_FOUNDRY_RESOURCE="flk-team-ai-enablement-ai"
export ANTHROPIC_DEFAULT_OPUS_MODEL="claude-code-<nodeN>"
export ANTHROPIC_FOUNDRY_API_KEY="<node-specific-key>"
```

`CLAUDE_CODE_USE_FOUNDRY=1` switches Claude Code from the Anthropic API to the Foundry endpoint.
Without it, Claude Code will attempt to reach `api.anthropic.com` directly, which will fail in the
Fluke network context.

In practice, these variables live inside the `settings.json` (or `settings.local.json`) `env` block
rather than being set at the shell level — see [Settings Templates](#settings-templates).

---

## Settings Templates

Three JSON templates live in `settings-templates/`, one per coding node:

```
configurations/
  settings-templates/
    settings_template_node1.json
    settings_template_node2.json
    settings_template_node3.json
```

**What each template contains:**

```json
{
  "env": {
    "CLAUDE_CODE_USE_FOUNDRY": "1",
    "ANTHROPIC_FOUNDRY_API_KEY": "<node-specific-key>",
    "ANTHROPIC_FOUNDRY_BASE_URL": "https://flk-team-ai-enablement-ai.services.ai.azure.com/anthropic",
    "ANTHROPIC_DEFAULT_OPUS_MODEL": "claude-code-<nodeN>",
    "ANTHROPIC_DEFAULT_HAIKU_MODEL": "claude-haiku-4-5-2-<nodeN>",
    "ANTHROPIC_DEFAULT_SONNET_MODEL": "claude-sonnet-4-6-<nodeN>",
    "ANTHROPIC_FOUNDRY_REGION": "eastus2"
  },
  "model": "claude-code-<nodeN>"
}
```

The top-level `"model"` key sets Claude Code's default model to the node's Opus deployment. The
three `ANTHROPIC_DEFAULT_*_MODEL` variables let Claude Code route sub-tasks to the right tier
automatically (e.g., haiku for cheap summarization passes).

**Installation steps for a new user:**

1. Copy the correct node template to `~/.claude/settings.json` (or `settings.local.json` if you
   want to layer it over a shared `settings.json`).
2. Replace `ANTHROPIC_FOUNDRY_API_KEY` with the user's node-specific key (retrieve from
   Azure AI Foundry portal or from the key vault).
3. Run `claude` — it will authenticate via Foundry on first use.

---

## Hooks

Three Python security hooks live in `configurations/hooks/`. They run automatically during every
Claude Code session via the `hooks` configuration in `settings.json`.

**Installation:**

```bash
cp configurations/hooks/*.py ~/.claude/hooks/
```

Then add the following to `~/.claude/settings.json` (merge with any existing `hooks` block):

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          { "type": "command", "command": "python ~/.claude/hooks/secret-scanner.py" },
          { "type": "command", "command": "python ~/.claude/hooks/dangerous-command-blocker.py" }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Edit|Write|MultiEdit|Bash",
        "hooks": [
          { "type": "command", "command": "python ~/.claude/hooks/change-logger.py" }
        ]
      }
    ]
  }
}
```

> **Python path:** Use `python` (not `python3`) on Windows with Python 3.12.

---

### Hook 1: `secret-scanner.py`

**Trigger:** PreToolUse on Bash  
**Action:** Blocks the command (exit code 2) if a `git commit` would include files containing
secrets.

Scans all staged files against **30+ regex patterns** before any commit proceeds. Pattern
categories:

- AWS Access/Secret keys
- Anthropic API keys (`sk-ant-api*`)
- OpenAI API keys
- Google API keys and OAuth tokens
- Stripe live and test keys
- GitHub / GitLab personal access tokens
- Databricks personal access tokens (`dapi*`)
- Azure generic keys
- **Azure AI Foundry / Cognitive Service keys** (marked `critical` — specific to our deployment)
- Azure Storage connection strings (marked `critical`)
- SQL Server and database connection strings
- Hugging Face tokens
- npm and PyPI tokens
- Generic API key / secret key / access token patterns
- Hardcoded passwords
- RSA/DSA/EC/OpenSSH private keys
- Database connection strings (mysql/postgres/mongodb)
- JWT tokens
- Slack tokens
- SendGrid API keys

**Skip logic:** Binary files, lock files (`package-lock.json`, `poetry.lock`, etc.),
`node_modules/`, `.git/`, and `venv/` directories are excluded. Lines where the match appears in a
comment that contains the word "example" or "placeholder" are also skipped.

**How to bypass a false positive:** Add `# example` or `# placeholder` on the same line as the
pattern. The commit will then proceed.

**Output on block:**

```
SECRET SCANNER: Potential secrets detected!

Found 1 potential secret(s):
  Critical: 1

[CRITICAL] Azure AI Service Key
   File: config.py:14
   Match: ANTHROPIC_FOUNDRY_API_KEY = "5RjMe...

COMMIT BLOCKED: Remove secrets before committing

How to fix:
  1. Use environment variables or Azure Key Vault
  2. Use Databricks secrets: dbutils.secrets.get(scope, key)
  3. For false positives: add "example" or "placeholder" in a comment on the same line
```

---

### Hook 2: `dangerous-command-blocker.py`

**Trigger:** PreToolUse on Bash  
**Action:** Three-tier response: block catastrophic commands (exit 2), block critical-path
operations (exit 2), warn on suspicious patterns (exit 0 with stderr message).

**Level 1 — Catastrophic (always blocked):**
Commands that could cause irreversible system damage, including `rm` on `/` or `~`, `rm -rf` with
wildcards, `dd` disk operations, filesystem formatting (`mkfs`, `fdisk`), fork bombs, direct disk
writes (`> /dev/sda`), and `chmod 777 /`.

**Level 2 — Critical path protection (blocked):**
`rm` or `mv` targeting:
- `.claude/` — Claude Code configuration directory
- `.git/` — Git repository
- `node_modules/`
- Any `.env` file
- `package.json` / `package-lock.json` / `requirements.txt`
- `AzureDataBricks/` or `ADF/` directories (Fluke-specific)
- Any `settings.json` file

**Level 3 — Suspicious patterns (warning only, command still runs):**
Chained `rm` commands, `rm` with wildcards, `find -delete`, and `xargs rm`. The warning prints to
stderr and the command proceeds (`exit 0`).

**How to run a blocked command anyway:** Execute it manually in your own terminal session, outside
of Claude Code.

---

### Hook 3: `change-logger.py`

**Trigger:** PostToolUse on Edit, Write, MultiEdit, Bash  
**Action:** Appends a row to `~/.claude/critical_log_changes.csv` for every file mutation.
Never blocks execution (always exits 0).

**CSV schema:**

| Column | Content |
|---|---|
| `timestamp` | `YYYY-MM-DD HH:MM:SS` |
| `tool` | `Edit`, `Write`, `MultiEdit`, or `Bash` |
| `file_path` | Absolute path of modified file (or `-` for Bash commands) |
| `action` | `modified`, `created`, or `executed` |
| `details` | First 200 characters of Bash command (empty for file tools) |

Read-only Bash commands (cat, ls, grep, git status, git log, git diff, etc.) are silently skipped
and not logged.

**Use case:** Review `~/.claude/critical_log_changes.csv` after a session to audit exactly what
Claude Code touched. Especially useful after long autonomous sessions or when debugging unexpected
file changes.

---

## RBAC Provisioning

When onboarding a new user, grant them the **Azure AI User** role on the AI Services resource.

**Role details:**

| Field | Value |
|---|---|
| Role name | Azure AI User |
| Role definition ID | `53ca6127-db72-4b80-b1b0-d745d6d5456d` |
| Scope | `/subscriptions/77a0108c-5a42-42e7-8b7a-79367dbfc6a1/resourceGroups/flk-team-ai-enablement-rg/providers/Microsoft.CognitiveServices/accounts/flk-team-ai-enablement-ai` |

**Bug:** `az role assignment create --scope` returns a `MissingSubscription` error on the Fluke AI
ML Technology subscription. Do not waste time debugging this — it is a known platform quirk.

**Workaround — use the REST API directly:**

**Step 1: Resolve email to Object ID**

```bash
az ad user show --id user@fluke.com --query id -o tsv
```

**Step 2: Get a management plane bearer token**

```bash
TOKEN=$(az account get-access-token \
  --resource https://management.azure.com/ \
  --query accessToken -o tsv)
```

**Step 3: Generate a UUID for the assignment**

```bash
ASSIGNMENT_ID=$(python -c "import uuid; print(uuid.uuid4())")
```

**Step 4: PUT the role assignment via REST**

```bash
SCOPE="/subscriptions/77a0108c-5a42-42e7-8b7a-79367dbfc6a1/resourceGroups/flk-team-ai-enablement-rg/providers/Microsoft.CognitiveServices/accounts/flk-team-ai-enablement-ai"
ROLE_DEF_ID="53ca6127-db72-4b80-b1b0-d745d6d5456d"
PRINCIPAL_OID="<oid-from-step-1>"

curl -s -X PUT \
  "https://management.azure.com${SCOPE}/providers/Microsoft.Authorization/roleAssignments/${ASSIGNMENT_ID}?api-version=2022-04-01" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{
    \"properties\": {
      \"roleDefinitionId\": \"${SCOPE}/providers/Microsoft.Authorization/roleDefinitions/${ROLE_DEF_ID}\",
      \"principalId\": \"${PRINCIPAL_OID}\"
    }
  }"
```

**Step 5: Provide credentials to the user**

Give the new user their node-specific settings template (with the API key filled in) and the
installation steps from [Settings Templates](#settings-templates).

---

## LLM Gateway (node4 / Excel)

Node4 users (Excel add-in, L1 users) do not get a direct Foundry API key. Instead they authenticate
to a shared gateway that proxies to the shared Foundry deployments.

| Field | Value |
|---|---|
| Gateway URL | `https://flk-team-ai-llm-gateway.azurewebsites.net` |
| Token | `flk-team-da6d8bfe-de40-49fc-8e69-6987f7b6a462` |
| Routes to | Shared deployments (`claude-opus-4-6`, `claude-sonnet-4-6`, `claude-haiku-4-5`) |
| Container registry | `flkdockerregistry` ACR |
| Image version | v5 (all 4 gateway nodes) |

**Usage tracking:** A DuckDB instance runs on VM `llm-usage-duckdb-vm` (Standard\_B2ms) with a 12-hour
cron schedule. Usage data is exposed in Power BI via direct Delta read. See the LLM Gateway Usage
Tracking project memory for full schema and PBI report details.

**Node4 user setup:** Provide the gateway URL and token. The Excel add-in is pre-configured to use
this endpoint — no `settings.json` changes needed on the client side.

---

## Sync Workflow

The live files are in `~/.claude/`. This repo holds the canonical reference copies. Keep them in
sync after any changes.

| Live location | Repo location |
|---|---|
| `~/.claude/hooks/secret-scanner.py` | `configurations/hooks/secret-scanner.py` |
| `~/.claude/hooks/dangerous-command-blocker.py` | `configurations/hooks/dangerous-command-blocker.py` |
| `~/.claude/hooks/change-logger.py` | `configurations/hooks/change-logger.py` |
| `~/.claude/settings.json` | `configurations/settings-templates/settings_template_node<N>.json` |

**After editing a hook locally:**

```bash
cp ~/.claude/hooks/<hook-name>.py "C:/Users/tmanyang/OneDrive - Fortive/Claude code/In search of a more perfect repo/configurations/hooks/<hook-name>.py"
```

**After editing a settings template:**

The templates in the repo use the real API key (retrieve from portal to refresh). When sharing with
a new user, copy the correct node template, fill in the key, and send it — do not commit keys to
the repo.

---

## Gotchas

**1. Foundry project must exist before Anthropic deployments.**
The Azure AI Foundry project resource (`flk-team-ai-enablement-ai`) must be fully provisioned
before any Anthropic model deployments can be created under it. If you try to create deployments
against a resource that does not yet have a project, the portal and CLI will succeed but the
deployments will silently fail to activate.

**2. API version `2025-12-01` is required.**
Older API versions (e.g., `2024-02-01`) do not support the Anthropic model family on Foundry. If
you get `ModelNotFound` or `UnsupportedOperation` errors, check that `ANTHROPIC_API_VERSION` or the
SDK default resolves to `2025-12-01`.

**3. The API key header is `x-api-key`, not `api-key`.**
Azure AI Services uses `api-key` for its own models (OpenAI, etc.). The Anthropic endpoint
specifically requires `x-api-key`. The Claude Code SDK handles this correctly when
`CLAUDE_CODE_USE_FOUNDRY=1` is set — but if you are building a custom integration or testing with
curl, use `-H "x-api-key: <your-key>"` and not `-H "api-key: <your-key>"`.

**4. `az role assignment create --scope` fails on this subscription.**
Do not attempt to use the Azure CLI for RBAC on the Fluke AI ML Technology subscription. Use the
REST API PUT workaround described in [RBAC Provisioning](#rbac-provisioning).

**5. Settings file precedence.**
Claude Code reads `~/.claude/settings.json` first, then `~/.claude/settings.local.json`, then
`<project>/.claude/settings.json`. If a user has conflicting model or env settings at multiple
levels, the most specific file wins. When troubleshooting unexpected model routing, check all three
locations.

**6. Use `python`, not `python3`, in hook commands on Windows.**
The hooks are installed on Windows with Python 3.12. The binary is registered as `python`. Hooks
configured with `python3` will fail silently (the hook process will not start, and no error is
surfaced to the user).
