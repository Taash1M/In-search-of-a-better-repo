# Environment Variables Reference

Complete reference for all environment variables needed to run Claude Code on Fluke's Azure AI Foundry deployment.

## Core Variables (Required)

Every Claude Code installation needs these four variables set:

| Variable | Value | Purpose |
|----------|-------|---------|
| `CLAUDE_CODE_USE_FOUNDRY` | `1` | Switches Claude Code SDK from `api.anthropic.com` to Azure AI Foundry routing |
| `ANTHROPIC_FOUNDRY_RESOURCE` | `flk-team-ai-enablement-ai` | Azure AI Foundry resource name (East US 2) |
| `ANTHROPIC_DEFAULT_OPUS_MODEL` | `claude-code-<nodeN>` | Node-specific Opus deployment name |
| `ANTHROPIC_FOUNDRY_API_KEY` | `<node-specific-key>` | API key for the assigned node |

## Per-Node Values

| Variable | Node 1 | Node 2 | Node 3 |
|----------|--------|--------|--------|
| `ANTHROPIC_DEFAULT_OPUS_MODEL` | `claude-code-node1` | `claude-code-node2` | `claude-code-node3` |
| `ANTHROPIC_DEFAULT_SONNET_MODEL` | `claude-sonnet-4-6-node1` | `claude-sonnet-4-6-node2` | `claude-sonnet-4-6-node3` |
| `ANTHROPIC_DEFAULT_HAIKU_MODEL` | `claude-haiku-4-5-2-node1` | `claude-haiku-4-5-2-node2` | `claude-haiku-4-5-2-node3` |

API keys are node-specific. See settings templates in `../settings-templates/` for the full JSON configuration.

## Bash Setup (Git Bash / WSL / macOS)

Create `~/azure_setup.sh`:

```bash
# Claude Code — Azure AI Foundry Configuration
export CLAUDE_CODE_USE_FOUNDRY=1
export ANTHROPIC_FOUNDRY_RESOURCE="flk-team-ai-enablement-ai"
export ANTHROPIC_DEFAULT_OPUS_MODEL="claude-code-node2"  # Replace with your node
export ANTHROPIC_FOUNDRY_API_KEY="<your-api-key>"
```

Add to `~/.bashrc` or `~/.zshrc`:

```bash
source ~/azure_setup.sh
```

Reload: `source ~/.bashrc`

## PowerShell Setup

Add to your PowerShell profile (`$PROFILE`):

```powershell
$env:CLAUDE_CODE_USE_FOUNDRY = "1"
$env:ANTHROPIC_FOUNDRY_RESOURCE = "flk-team-ai-enablement-ai"
$env:ANTHROPIC_DEFAULT_OPUS_MODEL = "claude-code-node2"
$env:ANTHROPIC_FOUNDRY_API_KEY = "<your-api-key>"
```

## VS Code Extension

In VS Code Settings (Ctrl+,), search "Claude Code" and add environment variables:

```
CLAUDE_CODE_USE_FOUNDRY = 1
ANTHROPIC_FOUNDRY_RESOURCE = flk-team-ai-enablement-ai
ANTHROPIC_DEFAULT_OPUS_MODEL = claude-code-node2
ANTHROPIC_FOUNDRY_API_KEY = <your-api-key>
```

## LLM Gateway Variables (Excel Add-in, Node 4)

These are used by the Excel add-in, not Claude Code CLI:

| Variable | Value |
|----------|-------|
| Gateway URL | `https://flk-team-ai-llm-gateway.azurewebsites.net` |
| API Token | `flk-team-da6d8bfe-de40-49fc-8e69-6987f7b6a462` |

The gateway routes to shared model deployments (not node-specific).

## Validation

After setting variables, verify with:

```bash
claude
# Then inside the session:
/status
```

Expected output:
```
API provider: Microsoft Foundry
Model: claude-code-node2
```
