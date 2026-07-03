---
name: project_claude_code_opus_relabel
description: "claude-code→Opus relabel COMPLETE; content-analysis sprint plan APPROVED v3.1; 2-hr timeout deployed; runbook ~60-min limit = not configurable (2026-06-29)"
metadata: 
  node_type: memory
  type: project
  originSessionId: a8fc746d-720a-4b46-b803-5585ff36821e
---

## ✅ COMPLETE (2026-06-28) — deployed, QA-certified, merged, cron live
**Final deployed code md5 `b892a081`** (BUILD_STAMP etl-relabel-content-v4) — prod blob == on-VM == git HEAD (G-DEPLOY 4-way). deltalake bumped **1.5.0→1.6.1** (rollback: <VM_HOME>/pip_freeze.pre-relabel.txt). Prod E2E run 4cba8dcf status=success; **Final QA 13/13 PASS** + **PBI model-name validation 7/7 PASS**. Merged **feature→dev→main** (PR #2, #3; origin/main @72267c3) — feature→dev→main is now the UNIVERSAL standard ([[feedback_github_feature_dev_main]]). **cron re-enabled byte-exact** (`0 */6 * * *`). Result: claude-code=0 / opus=17,810 in fact; cc=0 across per_user/agg/audit/**content_analytics**/**content_alerts**/diag; dim_models claude-code row→"Claude Code (Opus)".

### Scope grew during execution (3 bugs found + fixed beyond the original relabel):
1. **Bronze/Silver/content-Silver dedup** — pre-existing `DELTA_MULTIPLE_SOURCE_ROW_MATCHING` (same request_id in N source blobs, e.g. 8e69089c×3). Fixed via `_dedup_rows_by_request_id` before every request_id MERGE; made **content-preserving + idempotent** (richest-payload survivor by total-order, NOT keep-last-on-input) per user direction.
2. **Content tables** carried `azure_ai/claude-code-nodeX` (relabel plan scoped content out on a literal-only Phase-0 count; final QA caught it). Added `_normalize_model_key` (strip azure_ai/+node → _get_model_key → fold cc→opus) at content-silver derivation + G-CONTENT-ALERTS fail-closed block. Existing rows relabeled via standalone `results/relabel_content_tables.py` (NO content re-analysis, idempotent: 124→0 / 14→0).
3. **node21 suffix-strip corruption** (`-node2`.replace on node21→claude-code1) + **smoke-blob scanner pollution** (delta_smoke/ scanned as source → Bronze dup) — both fixed.

**Deliverables:** 42 TDD tests; `results/{g_deploy_check,validate_pbi_model_names,relabel_content_tables}.py`; plans CLAUDE_CODE_RELABEL_EXECUTION_PLAN(v5) + FINAL_QA_VALIDATION_PLAN(v4) + per-round reviews + final_qa_EXECUTION_RESULT.md.
**July follow-up still pending:** [[project_diag_cost_opus_july]] (diag CLI cost+token coeff Sonnet→Opus).
**Op note:** TWO schedulers — VM cron (6h, disabled/re-enabled here) AND Azure Automation runbook (12h, starts/deallocates VM; ran deployed code unattended at 07:03 success).

## 📋 BACKLOG (open follow-ups — see `claude-code-relabel/docs/BACKLOG.md`)
1. **Content-Analysis Sprint — PLAN APPROVED v3.1 (2026-06-29), ready to build.** Plan: `claude-code-relabel/docs/plans/CONTENT_ANALYSIS_SPRINT_EXECUTION_PLAN.md`. QA gate PASS. Phase A (incremental): Delta read-back A0 → cost proxy filter → analyze fresh only → explicit list-concat reassembly. ~$7/month vs ~$180/month; ~6–8min normal run vs ~42min today. Phase B (coverage): prompt_injection_jailbreak HIGH (BOTH module-level + _derive_severity local dicts L1631-1633), tool-call text preserved, escalation_reason fallback in _normalize_analysis after Fix 1, PII false-positive carve-out for CLAUDE.md context, HAIKU_API_KEY→ANALYSIS_API_KEY. Key: response_format:json_object is OpenAI-specific — NOT supported by Anthropic endpoint. **Phase A directly resolves the runbook ~60-min timeout failure for normal runs.** Build via data-engineering skill, feature→dev→main.
2. **Runbook timeout — partially mitigated (2026-06-29).** Root cause: `Invoke-AzVMRunCommand` has a hard Azure service-side ~60-min limit — **NOT configurable, cannot be increased**. Mitigation 1: 2-hour bash `timeout` added to `run_etl.sh` (committed to feature/claude-code-opus-relabel, deployed to `_scripts/run_etl.sh` blob md5 e478d81b). Mitigation 2: Phase A cuts normal runs to ~6-8min (limit never hit). Full fix (deferred): switch runbook step 3 to async RunCommand API (`PUT /runCommands/{name}`) + poll `job_runs`. **Original:** Runbook mislabels long runs as failed + deallocates VM mid-run. Each ETL run re-runs Sonnet content analysis on the SAME ~500 content blobs (`Analyzed: 500 rows` every run, ~$1 + ~35min each), even though most were already analyzed prior runs. This is the main driver of the ~50min runtime AND the runbook's ~60-min RunCommand timeout (item 2). **Fix:** mark records already analyzed (e.g. an `analyzed_at`/`analysis_run_id` flag or a content-analysis watermark in content_silver) and have each run analyze ONLY fresh/un-analyzed records. Cuts cost + runtime dramatically and is what makes the runbook reliable. (`_analyze_batch` ~L1772; analysis writes work_appropriateness_score/safety_category/etc. into content_silver — those cols already exist, so "analyzed" can be detected by them being non-null.)
2. **Runbook mislabels long runs as `Pipeline: failed` + deallocates VM mid-run — MEDIUM.** `Invoke-LLMUsageETL` step 3 uses synchronous `Invoke-AzVMRunCommand` (Azure ~60-min RunCommand service limit). A full ETL (~50min, longer w/ content analysis) can hit the limit → the call throws → catch sets pipelineStatus='failed' → step 4 deallocates the VM before the ETL writes its job_runs row. NOT an ETL failure (direct run = exit 0/status=success; idempotent re-run proven). **Fix:** launch the wrapper async (`-AsJob`) and poll job_runs for terminal status, OR gate deallocate on a fresh job_runs success row — and item 1 (incremental analysis) shrinks runtime so the timeout stops being hit. Pre-existing, not from the relabel work.
3. **July: diag CLI cost+token coeff Sonnet→Opus** — [[project_diag_cost_opus_july]].

---
## (historical — original plan/build trail below)

## Claude-Code → Opus Relabel (Gold-layer attribution fix) — 2026-06-27

**Goal:** `model_key='claude-code'` (CLI Opus usage, ~$16.7K) attributes to `claude-opus-4-6` across all Gold consumers. **$0 cost impact** (real rows already Opus-priced via `_get_rates` fallback; diag cost+token coeffs deliberately FROZEN at Sonnet this period — see [[project_diag_cost_opus_july]]). Zero PBI schema change. See [[project_llm_usage_tracking]].

**Project dir:** `AI\Claude code deployment\claude-code-relabel\` (plan `docs/plans/CLAUDE_CODE_RELABEL_EXECUTION_PLAN.md` APPROVED v5; reviews round1-5; `results/baseline_pre_relabel.json` + `g_deploy_check.py`; `tests/test_claude_code_relabel.py`).

### Plan: data-dev-planning, 5 adversarial rounds → CLEAN (well past 2-round floor)
r1: 5 P0s (tautological conservation; fail-open dedup pattern; G-DIAG shared sonnet branch; content tables uncovered; deltalake-1.5.0 overwrite). r2: 0 P0, fold-in-vs-fail-closed contradiction + null-unsafe mask + G-NAME-can't-be-a-measure. r3: G-NAME no concrete mechanism (diag watermark) + global-degraded blast radius. r4: SA+EA clean, 3 DE P3s. r5: all 3 personas CLEAN.

### The 6 changes (live ETL `claude-code-poc-etl/llm_usage_etl_v2.py`, branch `feature/claude-code-opus-relabel`)
- **G-FACT**: prefix+null-safe relabel (`startswith('claude-code')→claude-opus-4-6`, catches the `claude-code1` node21-corruption) folded into the Gold Fact dedup pandas frame; ONE atomic `_write_overwrite` on BOTH dupe paths; **fail-closed via `stats['relabel_failures']`** (the dedup READ stays non-blocking/self-healing); fresh-handle verify = claude-code 0 + directed conservation (INV-1).
- **G-DIAG**: split the fused sonnet/claude-code diag branch → dedicated `claude-code→opus` arm ABOVE sonnet; cost CASE + token CASE UNCHANGED (frozen).
- **G-DIM**: `claude-code` dim row KEPT, relabeled to Opus display/family/rates (childless post-fix = G7 canary; renders in no visual).
- **G-NAME**: dedicated fail-closed block (after diag MERGE, before per_user) relabels `diagnostic_user_activity.model_name` `claude-code*→opus`, full read/overwrite, rowcount-preserving verify; runs every run OUTSIDE the watermark + non-blocking diag wrapper. (Phase-0 found prod model_name had `claude-code-node1/node21`.)
- **L2065 stripper**: `re.sub(r'-node-?\d+$','',...)` fixes the `claude-code-node21→claude-code1` substring-`.replace` bug.
- **finalize**: `if relabel_failures: status='failed' + sys.exit(1)` — distinct from the preserved non-blocking `degraded` path (so the 12h runbook contract is unchanged for unrelated phases).
- BUILD_STAMP → `etl-claude-code-opus-relabel-v1`.

### Phase-0 baseline (read-only prod, key via ARM listKeys on flkaienablement):
Gold Fact: claude-code **15,374 / $15,662.72 / 1,315,577,885 tok**; opus 2,436 / $950.50 / 69,864,255. **Conservation target: opus_post = 17,810 / $16,613.22 / 1,385,442,140** (verified on real baseline, INV-1 PASS). content_analytics/content_alerts claude-code = **0** (G-CONTENT scoped OUT). Silver claude-code = 15,797 (untouched, G6). fact NULL/blank model_key = 0.

### Status (2026-06-28): SMOKE PASS + full-QA PASS; prod deploy BLOCKED by pre-existing Bronze bug (being fixed).
- **deltalake bumped 1.5.0→1.6.1 on prod VM** (rollback pin: `pip_freeze.pre-relabel.txt`). **cron DISABLED** (backup `crontab.pre-relabel-backup`) — must re-enable after a clean prod run.
- **Smoke (delta_smoke prefix, real prod-scale data) PASS**: G-FACT relabeled 15,374 cc→opus, G1 conservation OK (opus +15,374), G-NAME 7 model_name rows relabeled / 207,163 preserved. Exit 0.
- **Scanner-pollution incident + fix**: smoke wrote `delta_smoke/` into the same `litellm-logs` container; the main usage scanner skip-list (L2097) didn't exclude it → its `_delta_log/*.json` got parsed as source → Bronze dup error. FIXED: added `delta_smoke/`+`_scripts_smoke/` to skip-list (commit 565dd3c) + regression test (17 tests). Smoke trees deleted.
- **Final relabel artifact md5 `311245000108c97bfa142300d5cfad62`** (branch `feature/claude-code-opus-relabel`, commits 064816f + 565dd3c). **Full qa-gate PASS, 0 findings, all 8 DoD items verified.** Prod blob `_scripts/llm_usage_etl_v2.py` currently holds this (deployed); old prod blob was `8bb67505` (rollback ref).
- **PROD RUN BLOCKED — pre-existing Bronze bug (NOT the relabel):** Bronze MERGE on request_id (L2148, untouched baseline code) hits `DELTA_MULTIPLE_SOURCE_ROW_MATCHING` because request_id `8e69089c-3db3-4901-8749-6a744b7ef810` appears in **3 source blobs** (gateway double-logged, same second, diff microsec). Bronze does NO source-dedup before MERGE (violates NEVER-rule #1). Fails baseline code too. **Prod Gold/Bronze/watermark all intact + pre-relabel** (fail-closed worked: fact 26634, cc 15374, bronze 27455, wm clean).
**Next:** Bronze-dedup fix delegated to agent (plan→data-engineering). After Bronze fixed → re-run prod ETL (completes relabel) → verify G0-G7 + conservation vs baseline → **re-enable cron** → Phase 5 PBI refresh → Phase 6 PR/merge.
