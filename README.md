# In Search of a More Perfect Repo

> Master synchronization repository for Claude Code skills, hooks, configurations, memory, and reusable modules — designed to keep multiple Claude Code installations in sync across devices and accounts.

## Why This Repo Exists

Claude Code stores its configuration across several local directories: `~/.claude/commands/` for skills, `~/.claude/hooks/` for safety scripts, `~/.claude/projects/` for memory, and environment variables for API routing. When you work across multiple machines, accounts, or fresh installations, recreating this setup from scratch is painful and error-prone.

This repo is the single source of truth. Every skill, hook, configuration template, memory file, and reusable module lives here. A new Claude Code installation can be fully operational in minutes by pulling from this repo and running the sync script.

## Quick Start — New Device Setup

```bash
# 1. Clone the repo
git clone https://github.com/Taash1M/In-search-of-a-better-repo.git
cd In-search-of-a-better-repo

# 2. Copy skills to Claude Code commands directory
cp -r skills/ai-ucb/orchestrator/*.md    ~/.claude/commands/
cp -r skills/ai-ucb/sub-skills/*.md      ~/.claude/commands/
cp -r skills/ai-ucb/companions/*.md      ~/.claude/commands/
cp -r skills/ai-ucb/reference/*.md       ~/.claude/commands/ai-ucb/
cp -r skills/standalone/*.md             ~/.claude/commands/
cp -r skills/document/*.md               ~/.claude/commands/
cp -r skills/knowledge-graph/*.md        ~/.claude/commands/

# 3. Copy hooks
cp configurations/hooks/*.py             ~/.claude/hooks/

# 4. Copy memory files (adjust project path as needed)
cp -r research/memory/*.md               ~/.claude/projects/<your-project>/memory/

# 5. Set environment variables (see configurations/environment/README.md)
# Copy the appropriate node template from configurations/settings-templates/
```

## Quick Start — Sync Changes Back

After improving a skill, adding a hook, or updating a memory file locally:

```bash
cd /path/to/In-search-of-a-better-repo

# Copy updated files back from your local Claude Code installation
cp ~/.claude/commands/my-updated-skill.md  skills/<appropriate-subfolder>/

# Commit and push
git add -A
git commit -m "Update my-updated-skill with new patterns"
git push
```

On your other devices, simply `git pull` to get the latest.

## Repository Structure

```
.
├── README.md                    ← You are here
├── PROJECT_MEMORY.md            ← Living project memory for this repo
│
├── skills/                      ← 41 Claude Code skill files (.md)
│   ├── README.md                ← Skill framework architecture and creation guide
│   ├── ai-ucb/                  ← AI Use Case Builder system (21 files)
│   │   ├── README.md            ← UCB architecture, phases, archetypes, state contract
│   │   ├── orchestrator/        ← Main orchestrator skill
│   │   ├── sub-skills/          ← 8 phase-specific sub-skills
│   │   ├── companions/          ← 5 companion skills (RAG, eval, deploy, etc.)
│   │   └── reference/           ← 7 reference/template files
│   ├── standalone/              ← 11 general-purpose skills
│   │   └── README.md            ← Catalog with purpose, triggers, capabilities
│   ├── document/                ← 7 document creation/extraction skills
│   │   └── README.md            ← Document pipeline: extract → beautify → diagram → export
│   └── knowledge-graph/         ← 2 graphify skill files
│       └── README.md            ← KG extraction architecture
│
├── configurations/              ← Hooks, settings, environment setup
│   ├── README.md                ← Full setup guide for Claude Code on Azure AI Foundry
│   ├── hooks/                   ← 3 Python safety scripts (secret scanner, command blocker, change logger)
│   ├── settings-templates/      ← Per-node settings.json templates (node1, node2, node3)
│   └── environment/
│       └── README.md            ← Environment variable reference for all nodes + gateway
│
├── research/                    ← Memory files and cross-project learnings
│   ├── README.md                ← Memory system design and usage guide
│   ├── memory/                  ← 23 memory .md files (index + 17 project + 5 feedback)
│   └── learnings/
│       └── README.md            ← Distilled patterns, anti-patterns, and gotchas
│
├── modules/                     ← Reusable Python modules
│   ├── README.md                ← Module API reference and usage patterns
│   ├── docx_beautify.py         ← Document beautification (48 functions, 4 presets, 4 palettes)
│   └── azure_diagrams.py        ← Azure architecture diagrams (78+ icons, 5 output presets)
│
└── docs/                        ← Training materials and onboarding guides
    └── README.md                ← Document inventory with OneDrive references
```

## What Syncs and What Doesn't

| Content | Syncs via this repo | Why |
|---------|:-------------------:|-----|
| Skills (`.md` in `~/.claude/commands/`) | Yes | Core Claude Code capabilities — must be identical across devices |
| Hooks (`.py` in `~/.claude/hooks/`) | Yes | Safety guardrails — every installation needs these |
| Memory files (`.md` in `~/.claude/projects/.../memory/`) | Yes | Project context and decisions — portable across conversations |
| Settings templates (`.json`) | Yes | Node-specific API routing — copy and customize per device |
| Python modules (`.py`) | Yes | Shared utilities for document generation and diagrams |
| Training docs (`.docx`, `.pdf`, `.png`) | No | Binary files — referenced by OneDrive path in `docs/README.md` |
| Source repo clones (contextgem, graphify, etc.) | No | Too large — referenced by path in relevant READMEs |
| `CLAUDE.md` project files | No | Machine-specific paths and project context |
| User-specific settings (individual `.json`) | No | Only templates synced — customize locally per user/device |

## Sync Workflow

```
Device A (primary)                    GitHub                         Device B (secondary)
─────────────────                    ──────                         ─────────────────────
Improve skill locally          →     git push               →      git pull
Add new hook                   →     git push               →      git pull + cp to ~/.claude/hooks/
Update memory after session    →     git push               →      git pull
New device setup               ←     git clone              ←      (run Quick Start above)
```

## File Counts

| Section | Files | Description |
|---------|------:|-------------|
| Skills | 41 | `.md` skill files across 5 subfolders |
| Configurations | 6 | 3 hooks (`.py`) + 3 settings templates (`.json`) |
| Research | 23 | Memory `.md` files (1 index + 17 project + 5 feedback) |
| Modules | 2 | Python modules (`docx_beautify.py`, `azure_diagrams.py`) |
| READMEs | 10 | Detailed documentation for each section |
| **Total** | **82** | |

## Section Deep Dives

Each section has its own detailed README. Start with whichever is most relevant:

- **[Skills README](skills/README.md)** — How the skill framework works, how to create and evaluate skills, the A+ quality methodology
- **[AI UCB README](skills/ai-ucb/README.md)** — The flagship 21-file AI Use Case Builder system
- **[Configurations README](configurations/README.md)** — Azure AI Foundry setup, RBAC, hooks, LLM Gateway
- **[Research README](research/README.md)** — The memory system: types, when to save, how it persists across conversations
- **[Modules README](modules/README.md)** — Python modules for document beautification and Azure diagrams

## Maintenance

- **Sync frequency**: After any significant skill improvement, hook change, or memory update
- **Branch strategy**: `main` only — this is a personal sync repo, not a team development repo
- **Commit messages**: Describe what changed and why (e.g., "Upgrade rag-multimodal to A+ with RAGAS eval framework")
- **Review cycle**: Monthly audit — remove stale memory files, update skill inventory, verify all files still exist at referenced paths
