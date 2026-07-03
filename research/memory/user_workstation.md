---
name: user-workstation
description: "Dell laptop specs (64 GB RAM), typical running apps, known bloatware, memory pressure patterns"
metadata: 
  node_type: memory
  type: user
  originSessionId: ae264719-d3c1-4dc1-a2a0-91e65c9ad9e2
---

## Hardware
- **Model**: Dell laptop (Windows 11 Enterprise 10.0.26100)
- **RAM**: 64 GB (63.7 GB visible)
- **Typical usage**: 40 GB used (~64% utilization), Memory Compression active at 7+ GB

## Typical Running Apps (by memory footprint)
| App | Typical MB | Notes |
|---|---|---|
| Edge + WebView2 | ~6,200 (79 processes) | Biggest offender — tabs accumulate |
| Claude Desktop | ~2,000 (10 processes) | Multiple windows/conversations |
| svchost (system) | ~2,400 (112 processes) | Can't reduce |
| Explorer | ~1,500 (5 instances) | 2 user sessions (<USER> + <ADMIN_USER>) + extras |
| Outlook | ~1,000 | Memory leak over long sessions — restart reclaims |
| Chrome | ~850 | Secondary browser |
| Dropbox | ~820 (9 processes) | Sync agent |
| PowerPoint | ~500 | Open decks |
| Teams | ~365 | Background |
| OneDrive | ~300 | Sync agent |

## Known Bloatware (safe to kill)
- **Dell TechHub** (3 agents: Instrumentation, DataManager, Analytics) — ~573 MB, restarts on its own
- **Power Automate Desktop** (UIFlowService + PAD.Console.Host + PAD.AutomationServer + Microsoft.Flow.RPA.LogShipper) — ~500 MB, not actively used for RPA flows. **Killed 2026-06-17**.
- **WavesSysSvc64** — ~228 MB, audio enhancement service

## Security Software (cannot kill)
- **MsMpEng** (Defender) — ~315 MB
- **CSFalconService** (CrowdStrike) — ~175 MB
- **MsSense** (Defender ATP) — ~228 MB
- **ZScaler** (ZSATunnel + ZSAUpm + ZSATray) — ~370 MB combined

## Memory Pressure Indicators
- Memory Compression process at 7+ GB = RAM under pressure
- When used RAM exceeds ~45 GB, noticeable slowdowns
- Quick wins to free 3-4 GB: kill Dell TechHub + Power Automate + close Edge tabs
- Outlook restart reclaims ~300-500 MB leaked memory

## Accounts
- **<ADMIN_USER>**: Admin account (Claude Code runs here)
- **<USER>**: Standard account (Outlook, Office apps, Docker, Python)
- Both sessions run simultaneously, each with its own Explorer process
