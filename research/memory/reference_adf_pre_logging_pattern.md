---
name: adf-pre-logging-pattern
description: "UBI ADF Pre_Logging intentional-RAISERROR control-flow pattern — 'Failed' dependency IS the normal execution path, not an error path"
metadata:
  node_type: memory
  type: reference
  originSessionId: current
---

# UBI ADF Pre_Logging — Intentional Failure Pattern

**Discovered 2026-06-29 while researching SO Backlog ADF topology.**

## The pattern

In `FlukeUBI_Source_DataPull_Stream.json` (and likely all stream pipelines):

```
Execute FlukeUBI_Pre_Logging_Activity  (root — runs unconditionally)
    │
    └──► Read_Source_Config  dependsOn: ["Failed"]
              │
              └──► Pull_Source_Data ForEach  dependsOn: ["Succeeded"]
```

`Read_Source_Config` depends on `Execute FlukeUBI_Pre_Logging_Activity` with condition **"Failed"** — this looks like an error path but is actually **the normal execution path**.

## Why it works this way

Inside `FlukeUBI_Pre_Logging_Activity.json`:
1. Calls `etl.usp_GetStatusFlag` (Lookup)
2. **If stream is ready to run (StatusFlag=0):** executes `RAISERROR('Raised Error on purpose to execute other tasks', 16, 1)` — **deliberate failure**
3. **If stream already running (StatusFlag=1 or -1):** also raises error to block double-running
4. **If stream complete (StatusFlag=2):** succeeds with no error → pipeline stops gracefully

The RAISERROR makes the parent `Execute FlukeUBI_Pre_Logging_Activity` activity report "Failed", which satisfies the `"Failed"` dependency condition on `Read_Source_Config`, triggering it on the normal path.

## Rule for wiring new activities

- Any new activity that should run in the **normal processing flow** must be downstream of `Read_Source_Config` (Succeeded) or `Pull_Source_Data` (Succeeded) — NOT downstream of `Execute FlukeUBI_Pre_Logging_Activity`
- If you wire a new activity after `Execute FlukeUBI_Pre_Logging_Activity` with condition `"Succeeded"`, it will **only fire when the stream is blocked** (StatusFlag=2), not on normal runs
- Filter Activities, dedicated Copy Activities, etc. must go after `Read_Source_Config` (Succeeded)

## Implication for §8.3 in SO Backlog plan

`Filter_ExcludeONT01` correctly wired after `Read_Source_Config` (Succeeded) — this IS the active execution path. No further confirmation needed from pipeline owner.

Related: [[ubi-platform-key-facts]] · [[project_so_backlog_optimization]]
