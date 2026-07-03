---
name: project-aws-twin
description: "AWS Twin of PLM Drawing Graph-RAG — BDA→Claude two-pass for 15 FGs into separate Neo4j vs prod. Plan v3.6 FINAL. EXECUTING (2026-06-20): Phase 0 done, Phase 1 manifest QA-PASS (751 docs), smoke PASS, **BDA Pass-1 FULL RUN COMPLETE 624/624 PDF, 0 fail, ~$186**, Phase 3 Claude next. 58 non-PDF=reuse-prod. PLUS ETL pipeline productionization: plan CONVERGED v9, Phases 0(deployed)/1/2 built+qa-gated, STOPPED at Phase-0 deploy per user stop line."
metadata:
  node_type: memory
  type: project
  originSessionId: d0518511-12b3-40f2-a588-f406002e059b
---

## AWS Twin — PLM Drawing Extraction (BDA + Claude)

Twin of the production PLM Drawing Graph-RAG project, built on the validated **two-pass pattern**:
**AWS BDA for document processing (split/classify/figure-crops/bbox) → Claude for semantic enrichment**.
Re-processes docs for the **15 in-scope FGs**, loads into a **separate Neo4j graph**, compares
side-by-side vs production. Twin front-end deferred.

**Parent folder:** `<USER_HOME>/OneDrive - <ORG>\AI\Technical Validation\AWS\`

### Folder structure (built 2026-06-19)
`config/{blueprints,ground_truth}`, `src/{common,extract,load,compare}`, `data/{bronze,silver,gold}`,
`results/bda_baseline`, `tests`, `deliverables-scripts`, `docs/{plans,reviews,reports}`, `costs/`,
`secrets/` (gitignored), `README.md`, (future) `PROJECT_MEMORY.md`.

### The plan
`docs/plans/AWS_TWIN_EXECUTION_PLAN.md` — **FINAL v3.4**. Phases: 0 Governance/setup (fail-closed G0
pre-egress gate) → 1 Manifest (TDD) → 2 BDA Pass-1 → 2.5 schema mapping gate → 3 Claude Pass-2 → 4
load (4a nodes `build_fresh_graph.py` → 4b USES `load_uses_edges.py`) → 5 validate G0–G6 → 6 dual-DB
diff → 7 run-ledger/tests → 8 doc suite (6 docs) → 9 local GitHub repo.

### 3-persona review loop (the deliverable method)
SA + EA + Principal DE reviewed in parallel each round, severity P0–P3, **looped until a full round had
zero P0–P3**. 5 rounds: R1 found governance + comparison-validity P0s; R2 found second-order issues the
R1 fixes introduced; R3 found issues in newly-added scope; R4 (DE read real loader code) found the plan
cited a **superseded loader** + wrong field names; R5 converged (SA/EA clean, DE 2 P2+1 P3 on corpus
shape polymorphism) → all fixed → **v3.4 converged at P0=P1=P2=P3=0**. Reviews in `docs/reviews/round{1-5}_consolidated.md`.

### Key technical decisions
- **Grain:** one `Drawing` per source file, filename-based `drawing_number` per
  `build_fresh_graph.py._resolve_drawing_number(use_pdf_stem=True)` (NOT `load_jason_graph.py`, which is
  superseded and collapses to one Drawing per component). BDA splits → child `Section` nodes, never Drawings.
- **USES quantity** is CSV-sourced identical in both graphs → loader sanity (G5) only, **excluded from
  twin-vs-prod quality scoring** (avoids tautological "win").
- **Richness metric** computed over the count/`*_text` props prod actually persists; structured-array
  depth compared from silver JSON, not graph nodes.
- **G1 accepts the full union of observed field shapes** across the real 843-file corpus (bom_items/
  general_notes/cross_references can each be list|dict|list[dict]|str|None) → 0-false-quarantine fixture.
- **Infographic** uses **Amazon Nova Canvas** on Bedrock — see [[reference-gpt-image-not-on-bedrock]].

### AWS env
Account `161643475055`, us-east-2, <ORG_PARENT> SSO (`<USER>@<ORG_DOMAIN>`). BDA project
`flk-ai-plmproject-techvalidation` (`72a21e628fc6`), S3 `flk-plm-drawings-ai-techval`. Current SSO role
is `AdministratorAccess` — plan calls for a dedicated **least-privilege role** before execution.

### Cost tracking (built 2026-06-19)
- `costs/` subfolder: `rate_card.json` (editable USD rates), `executions/aws_costs_YYYY-MM-DD.jsonl`
  (granular per-action ledger), `reports/`, `rollup_costs.py`.
- **Hook**: `~/.claude/hooks/aws-cost-tracker.py` (PostToolUse on Bash, wired into settings.json) —
  detects AWS CLI/boto/BDA/Bedrock/S3 commands, estimates cost from rate card, appends granular JSONL.
  Non-blocking, never guesses volume (logs `needs_actuals:true` when units unknown).
- Today's report: `costs/reports/cost_rollup_2026-06-19.md` — est. **$7.65** (BDA tests + optimization).
- Estimates only; reconcile vs Cost Explorer on tags `<ORG_ABBR>-PLM-Drawings-AI`/`env=techval-twin`.

### QA Gate (built + validated 2026-06-19)
- **Sub-agent** `~/.claude/agents/qa-gate.md` (read-only, `subagent_type: "qa-gate"`) — terminal
  per-artifact acceptance check; emits `QA-GATE-VERDICT-V1` sentinel + ```json verdict
  `{gate,artifact,artifact_type,verdict,findings,accept_rule}`. PASS only if zero blocker/major.
- **Enforcer hook** `~/.claude/hooks/qa-gate-enforcer.py` (SubagentStop) — FAIL-dominant, fail-CLOSED on
  FAIL/PASS-with-blocker/unparseable-gate-run/error; allows non-gate agents. Ledger `~/.claude/qa_gate_ledger.ndjson`.
- Validated over 3 persona rounds (~29 cases). Wired into plan §5.1 (per-phase map) + the data-dev-planning skill.

### EXECUTION STATUS (as of 2026-06-20)
Plan **v3.6 FINAL**; executing, agent overseeing plan-faithful execution. `EXECUTION_STATUS.md` is the
live status doc.

**Phase 0 (G0 governance) — DONE via owner POC bypass.** Owner ("God-Level") authorized a Phase-0
bypass for the POC (recorded honestly in `config/phase0_approval.json` as `overall_status:
BYPASSED_POC` + `poc_bypass{}`, expiry 2026-12-31; NOT a faked sign-off). `src/common/check_g0.py`
machine-enforces G0 and honors the bypass (returns APPROVED). ITAR/EAR flagged for parallel
trade-compliance confirm; PII still stripped from deliverables regardless. Revisit before any
production (non-POC) use.

**Phase 1 (manifest) — DONE + QA-gate PASS.** `src/extract/build_manifest.py`.
- **Scope was wrong on first build (673 docs) — user caught it ("~850").** Root cause: built from the
  Heather extraction *queues* (incomplete reachable set, 3 gaps). **Fixed: re-sourced from the
  authoritative `flkt28may2026_BOM_to_file.xlsx` (sheet Data).** Correct scope = **751 distinct docs /
  504 components / 688 PDF + 63 non-PDF / 7,331 pages**, 0 missing on disk. Gate test reconciles
  manifest == BOM_to_file (0 src-only/man-only). See `docs/reports/doc_scope_RESOLUTION.md`.
- **Validated vs the existing prod graph** (read-only): `src/compare/prod_baseline.py` →
  `data/gold/prod_baseline_15fg.json`. 463 prod-only components, **0 document-bearing** → manifest
  misses no extractable doc. (`docs/reports/manifest_vs_prod_reconciliation.md`.)

**Phase 1.5 SMOKE TEST — DONE.** 1 FG (3460387), 11 docs → BDA 11/11 Success, ~$0.77. Proved the
S3→BDA→poll→ledger seam. Runner `src/extract/run_bda_pass1.py` (G0-gated, sha256-keyed idempotent,
job-state `data/bronze/bda_jobstate.json`, cost-ceiling abort, ledger `costs/executions/bda_pass1_ledger.ndjson`).

**Phase 2 BDA Pass-1 FULL RUN — ✅ COMPLETE (2026-06-20).** **624/624 distinct PDF docs Success,
0 failures/quarantine, ~$186 est.** (PDF target = 624 distinct sha256; the 63 non-PDF are reuse-prod,
out of the BDA denominator.) Idempotent + checkpointed run, survived multiple interruptions/SSO expiries
via the resume. Output in `twin/bronze/output/<sha256>/`. **Next:** Phase 3 Claude Pass-2 enrichment.

**58 non-PDF docs — RESOLVED = reuse production extractions (option C, 2026-06-19/20).** Probed
extensively: BDA natively accepts only PDF/TIF/DOCX (live-rejected FRM/FM/DWG/DOC/PPTX/FM5/TXT/ZIP).
- **Claude vision on Bedrock** extracts well from any *rendered* image (TIF, legible DWG); bottleneck is
  render fidelity, not the model.
- **Amazon Rekognition** = OCR only, no structure, OCRs FrameMaker app chrome — not the bridge.
- **No AWS service** (BDA/Textract/Rekognition) and **no GCP service** (Gemini/Document AI; "nano
  banana" = Gemini image *generator*, not a parser) renders DWG or FM — render must be ODA (DWG) or
  Adobe FrameMaker (FM) off-cloud.
- **OSS:** FrameMaker binary has NO OSS reader (Adobe-only, confirmed). DWG twin-native raster is
  *possible* via ezdxf PyMuPDF backend but render-sizing is finicky (DPI×large-units → billion-px or
  too-small); not worth POC time since prod already extracted all 8 DWGs' text losslessly (ODA→ezdxf
  text entities). Reports: `nonpdf_conversion_solution.md`, `nonpdf_vision_vs_rekognition.md`,
  `nonpdf_amazon_fm_answer.md`, `dwg_twin_native_status.md`, `dwg_fm_oss_research.md`,
  `gcp_gemini_dwg_fm_assessment.md`.

**Twin Neo4j (Phase 4) — pending.** Local Docker on the `<USER>` session (daemon not reachable from
<ADMIN_USER> admin shell — user must start the container when Phase 4 begins).

### ETL Pipeline productionization (separate from the Twin run — cloud-native S3-medallion ETL)
Parallel workstream: a **production ETL/orchestration pipeline** that cloud-natives the proven
`run_bda_pass1.py` POC. Plan: `etl-pipeline/docs/plans/PLM_ETL_PIPELINE_EXECUTION_PLAN.md`.
- **Plan CONVERGED v9** — 7 rounds 3-persona review (zero P0–P3) + terminal qa-gate PASS (twice: v6.1,
  then v9 after the S3-medallion layer was added per user). Arch: S3 medallion (`source/→bronze/→silver/
  →gold/` under a frozen `date=` housekeeping partition), Step Functions Standard + Lambda/Fargate +
  Distributed Map, DynamoDB `(sha256,blueprint_version)` sole idempotency authority, BDA Pass-1 + Claude
  Pass-2, Neo4j load. Full idempotence, content-addressed date-free bronze, cost-admission gate.
- **BUILD (supervised, phased, 2026-06-20):** user chose phased+supervised, stop after Phase-0 deploy.
  Each phase: build agent (told to activate `data-engineering` skill + follow the plan) → independent
  qa-gate → fix-on-FAIL → re-gate.
  - **Phase 0 (CFN foundation) — DEPLOYED ✅.** `etl-pipeline/src/iac/phase0_foundation.yaml`, stack
    `flk-plm-etl-poc-foundation` (us-east-2, CREATE_COMPLETE, 16 resources). Working bucket
    `flk-plm-etl-poc` (SSE-KMS, BPA all, TLS-only, tier-tagged lifecycle), retained bucket
    `flk-plm-etl-poc-retained-161643475055` (SEPARATE CMK, durable-decrypt, Retain), DynamoDB
    `flk-plm-etl-poc-state` (PK sha256/SK blueprint_version, PITR, CMK, on-demand), least-priv ExecRole
    + OperatorPolicy (prefix-scoped Put source/Get gold). **qa-gate caught a lifecycle data-loss bug**
    (unfiltered bronze 30d rule reaping silver/gold) → fixed (tier=bronze tagfilter + regression test).
    **First deploy ROLLED BACK** — org SCP `p-dlr97uhu` denies `config:PutConfigurationRecorder` (this
    is an AWS **Control Tower** account w/ baseline recorder). Fix: removed self-managed Config recorder
    infra, kept `RequiredTagsRule` (attaches to org recorder, `config:PutConfigRule` NOT denied — confirmed
    on redeploy) made robustly-optional via `CreateConfigRule` flag; documented as forced deviation.
  - **Phase 1 (Lambdas + TDD) — BUILT + qa-gate PASS.** `etl-pipeline/src/lambdas/` (manifest, upload,
    claude_enrich, neo4j_load, validate, contract). 92 tests, RED→GREEN via fault injection. Carries the
    `tier=` object-tag contract (Phase-0 lifecycle dep).
  - **Phase 2 (ASL state machine) — BUILT + qa-gate PASS (after 2 blockers).** `etl-pipeline/src/
    statemachine/` (plm_etl.asl.json, mock_executor.py, validate_asl.py). **qa-gate caught 2 blockers**:
    resume/REPOLL path non-runnable (`$.bda.invocationArn` never seeded on resume → live job quarantined
    not re-polled) + tests masking it. Fixed (SeedRepollContext state + interpreter resolves Task
    Parameters + RED→GREEN re-proven). 116 tests.
- **qa-gate ENHANCED (2026-06-20):** plan-compliance is now a first-class always-on blocker (locates the
  governing execution plan, treats it as authoritative spec, flags material drift) — see
  [[feedback-agents-use-skills]].
- **GOLD-PATH BUILD + DEPLOY (2026-06-20, user lifted stop line → "go all the way to Gold this run"):**
  Built+qa-gated then DEPLOYED the full live pipeline for a fresh-FG smoke on **Parent Item 2538815**
  (137 docs/86 comps/118 PDF/900 pages, ~$41 BDA + ~$7-9 Claude = ~$48-50, fresh = genuine first-spend).
  Deployed stacks (us-east-2, all CREATE_COMPLETE): `flk-plm-etl-poc-foundation` (phase0),
  `-vpc` (VPC+2 private subnets+NAT+SG→Aura), `-images` (ECR+CodeBuild, both Stage5/6 images built
  tag `run2538815-1`), `-taskdefs` (ECS Stage5/6), `-pipeline` (phase12: 10 Lambdas + full-Gold ASL +
  ECS cluster). Neo4j = **Aura CLOUD** (`neo4j+s://e23c24ac…`, creds in Secrets Manager
  `plm/neo4j/creds-43Ev6N`, local copy shredded). G0 approval mounted via Lambda layer
  `flk-plm-etl-poc-approval` at `/opt/approval/`; live `APPROVAL#phase0-poc-bypass` DynamoDB item active.
- **THE RUNTIME-GAP SAGA (key lesson):** moto-mocked build gates CANNOT see IAM/bucket-policy/SFN-service-
  integration denials, so the live run failed repeatedly, one gap per execution. After 5 sequential
  failures, ran an **exhaustive IAM-simulator audit across all 5 stacks** which found 4 MORE gaps in one
  pass. Total gaps found+fixed: (1) aws_io PutObject missing SSE-KMS header; (2) lambda-exec missing
  s3:PutObjectTagging; (3) ECS task role missing PutObjectTagging; (4) DistributedMap ResultWriter +
  (later) BDA output blocked by bucket SSE-deny → NotResource carve-out for `bronze/map_results/*` +
  `bronze/bda/*`; (5) sfn-exec missing states:StartExecution/Describe/Stop (Distributed Map launches
  child execs); (6) bedrock:GetDataAutomationStatus must be scoped to `data-automation-invocation/*` not
  project/profile; (7) Claude model-id triple-mismatch — code/grant/reality all differed; real id =
  `us.anthropic.claude-sonnet-4-5-20250929-v1:0`, and the `us.` cross-region profile needs the FM ARN
  granted in us-east-1/2 + us-west-2. ALL fixed in templates+code, 235 tests green. **LESSON: for AWS
  deploys, add a deployed-config IAM-simulator audit as a mandatory gate BEFORE first spend — see
  [[feedback-aws-runtime-permission-audit]].**
- **THE MAP ROOT-CAUSE BUG (gap #8, a real LOGIC bug not a perm):** after the 7 IAM/policy gaps were
  fixed, the Map finally launched children — and ALL 117 failed identically with `States.Runtime: JSONPath
  '$.ddb.Item' not found`. Root cause: `GetItemState` (DynamoDB GetItem on a brand-NEW (sha256,bpver))
  returns NO `Item` key, and the ASL `ResumeDecision` Payload `"item.$":"$.ddb.Item"` dereferences a
  missing path → fatal uncatchable States.Runtime BEFORE the Lambda runs (Catch[States.ALL] doesn't catch
  input-processing errors). The resume Lambda was correctly built for `item=None`→CLAIM_AND_INVOKE, but
  the ASL never reached it. **Mocked tests structurally couldn't catch this** (they invoked the handler
  with item=None directly, bypassing the ASL JSONPath dereference). FIX: ASL now passes the whole `$.ddb`
  container (always exists) and the handler extracts `.get("Item")` safely; +4 regression tests (239 total).
  **LESSON: the IAM-simulator audit must be paired with a live single-doc smoke that exercises the real
  ASL JSONPath/state-transition wiring, not just mocked handler unit tests.**
- **ETL Gold run (A) — BDA Map fully SUCCEEDED, failed at Stage 4 (gate held, no corruption):** exec
  `run-2538815a-retry5` cleared preflight→G0→manifest→worklist→G_cost→**Distributed Map BDA Pass-1
  117/117 succeeded, 0 failed** (real ~$41 BDA spend, all output landed) → **Stage 4 Claude enrich
  returned enriched_count=0 / schema_ok=false → G_schema_pii_Choice correctly fail-closed.** Root cause =
  the enrich gaps below (esp. max_tokens). Gates held; no bad data advanced; BDA output valid+reusable.
- **Twin Pass-2 (B) — local runner, NOT cloud:** `run_pass2_enrich.py` runs on the laptop (calls Bedrock
  API); only the model inference is in AWS. Stops if laptop sleeps/SSO expires (same as BDA Pass-1).
  63 non-PDF reuse-prod records written to silver ($0); PDF enrich was held for QA before any spend.
- **ENRICH-PATH QA SAGA — 6 findings across BOTH code paths (the local runner + the Stage-4 Lambda share
  the enrich logic, so fixes applied to both):** qa-gate on the Pass-2 runner found 2 blockers + 3 majors;
  a re-gate found a 6th. (1/B1) **multi-subdoc BDA splits silently truncated to sub-doc 0** — ~13% of PDFs
  are BDA-split into 2-4 distinct-content sub-docs; reader took only sub-doc 0 → ~80 drawings enriched from
  a fraction of content, passes schema = silent corruption. FIX: collect ALL standard_output/<N>/result.json
  + aggregate via field-merge. (2/B2) **duplicate BDA job folders per sha** → pin canonical via recorded
  invocationArn. (3/M1) **3 non-PDF re-enriched + overwrite reuse-prod** → skip non-PDF + reuse-prod key.
  (4/M2) **no throttle retry** → adaptive(8) Bedrock client + per-doc quarantine-continue. (5/M3)
  **max_tokens=65536 > Sonnet-4.5's 64000 → ValidationException on first invoke (THIS is why Stage-4
  enriched 0)** → 64000. (6) re-gate caught the Lambda path **missing the stop_reason==max_tokens
  truncation gate** the runner had (a truncated-but-parseable record would write to silver as complete) →
  added; both paths now quarantine truncation. ALL fixed, RED→GREEN, **251 etl-pipeline + 45 AWS tests green,
  re-gate PASS.** Lambda bundle repackaged (35.9 KiB) — **needs redeploy before A resumes.**
- **NEXT:** redeploy the Stage-4 enrich Lambda code (claude_enrich.py + aws_io.py changed), then RESUME A
  from Stage 4 (BDA done, no re-spend — enrich→Neo4j Aura→gold) AND run B (the 627-doc ~$50.65 enrichment).
- **GAP #9 — BDA Pass-1 never actually ran in the deployed pipeline; the Map "117/117 succeeded" was a
  MIRAGE (forensic QA, 2026-06-21).** `bronze/bda/` was empty + 0 COMPLETED after a "successful" Map. Root
  cause: `bedrock:InvokeDataAutomationAsync` got **AccessDenied** on every child → CostAborted→rollback to
  PENDING (so children "succeed" with disposition COST_ABORTED, cost counter net $0). **$0 BDA spent across
  the whole retry lineage.** The `us.data-automation-v1` CROSS-REGION system profile is IAM-authorized
  against the profile ARN in whichever region BDA routes the job to — observed denials on us-east-1,
  us-east-2 AND **us-west-1** for the same logical profile (non-deterministic, undocumented home-region set).
  Granting regions one-at-a-time failed twice. **FIX: region-WILDCARD on the pinned profile id** —
  `arn:aws:bedrock:*:<acct>:data-automation-profile/us.data-automation-v1` (+ `data-automation-invocation/*`
  for GetDataAutomationStatus). Still least-privilege (exact profile id, not an action/account wildcard).
  QA = simulator sweep across us-east-1/2 + us-west-1/2 → all `allowed`. Resume logic confirmed CORRECT
  (QUARANTINED→re-claim). **LESSON: `us.`/`global.` cross-region inference profiles (BDA AND
  Bedrock model) need region-wildcard IAM on the pinned profile ARN; per-region enumeration is a trap.**
- **GAP #10 — BDA cannot read/write a customer-CMK S3 bucket (the REAL blocker; doc-confirmed).** After
  the IAM region fix, every child still got `BedrockDataAutomationRuntime.AccessDeniedException: Access
  Denied. Check S3 URIs and read/write permissions`. Tried: granting the caller `sfn-exec` role on the
  WorkingCmk key policy (kms:Decrypt/GenerateDataKey, verified `allowed` via simulator) — STILL denied.
  **Root cause: BDA accesses S3 as a Bedrock SERVICE PRINCIPAL that our customer CMK does not trust, and
  InvokeDataAutomationAsync has NO serviceRole param to redirect it.** The proven 624/624 manual run
  worked only because its bucket (`flk-plm-drawings-ai-techval`) is **AES256** (no KMS principal needed),
  no bucket policy. **FIX (user chose, fast): set the working bucket DEFAULT encryption to AES256** and
  carve `bronze/docs/*` + `bronze/bda/*` (BDA input+output) out of the CMK-deny policy; the deny still
  FORCES explicit SSE-KMS-CMK on all PAYLOAD prefixes (silver/gold — Lambdas set the header via
  `aws_io._sse_args`), and `copy_object` now defaults `sse_kms=False` so bronze/docs lands AES256.
  So PII payloads stay CMK-encrypted; only the BDA I/O area is AES256 (matching the proven run). 252
  tests green, phase0 redeployed (working bucket = AES256 confirmed), Lambda bundle refreshed.
  **LESSON: Amazon BDA (and likely other Bedrock async S3-output features) writes via a service principal
  that can't use a customer CMK and exposes no service-role param — use an AES256 prefix for BDA I/O, or
  grant the Bedrock service principal on the CMK (unverified). Don't put BDA I/O behind a customer CMK.**
- **GAP #11 = THE ACTUAL ROOT CAUSE (found by E2E QA isolation test, FIXED, CONFIRMED working):** none of
  the IAM/KMS/AES256 work was the real blocker — it was a **producer/consumer S3 KEY-CONTRACT MISMATCH**.
  The upload Lambda WRITES `bronze/docs/<sha256>.<ext>` (e.g. `.pdf`) but the ASL InvokeBDA READ the input
  as `bronze/docs/<sha256>` (NO extension) → 404 → BDA surfaces a missing input as its GENERIC
  `AccessDeniedException: Access Denied. Check S3 URIs` (which sent us chasing IAM/KMS for ~6 runs). The
  qa-gate PROVED it with an isolation test: same admin caller, no-ext key → AccessDenied; `.pdf` key →
  SUCCESS + full BDA output. FIX: add `ext` to the worklist row (manifest.build_worklist, =
  `os.path.splitext(doc_path)[1]`), thread it through the Map ItemSelector, and change InvokeBDA input URI
  to `States.Format('.../bronze/docs/{}{}', $.sha256, $.ext)`. Also added `ext` to WORKLIST_FIELDS. 252
  tests green. **retry10 CONFIRMED THE FIX: BDA output prefixes landing (20+ and climbing, was stuck at 0
  for 5 runs), COMPLETED climbing (9+, was 0) — real BDA spend now succeeding.** LESSON: BDA's "Access
  Denied. Check S3 URIs" is a GENERIC authz/missing-input message — ALWAYS verify the input object exists
  at the EXACT key first (the cheap check) before chasing IAM/KMS. The earlier IAM/KMS/AES256 fixes were
  still necessary groundwork (real gaps), but the extension bug was the wall.
- **Downstream silver/gold all simulate `allowed`** (E2E QA): Stage 4 enrich (lambda-exec InvokeModel on
  the dated sonnet profile + S3+tag+KMS), Stage 5/6 Fargate (read silver, write+tag gold, Neo4j secret,
  KMS). One minor: flk-plm-etl-poc-exec has a DEAD BedrockInvokeModel grant referencing a nonexistent
  opus-4-8 profile (Stage5/6 never call Bedrock) — cleanup, non-blocking.
- **retry10: BDA fully landed (118 outputs, Map 117/117) but FAILED at Stage 4 enrich** — the entire
  silver→gold half had NEVER run with real data. Per user "no whack-a-mole", ran a SCOPED E2E QA of the
  whole silver→gold half against the real BDA output → found **9 issues in one pass** (2 blockers + 6
  majors + 2 minors); ALL infra clean (IAM/Bedrock/secret/network simulate allowed) — every finding was
  CODE LOGIC. Headline: (B1) `_invoke_claude` naked `json.loads` on fenced/prefaced Claude output →
  parse error on ~every doc; (B2) `_read_bda_markdown` read wrong path — real markdown is at
  `document.representation.markdown` (not top-level), was shipping 29KB raw JSON; (M3) `_component_id`
  never stamped (worklist lacks it) → schema-invalid; (M4) **run-wide `schema_ok` flag failed the WHOLE
  pipeline on ONE bad doc** (must be per-item); (M5) PII gap — uppercase PERSONNEL + names in free-text
  not redacted → leak to gold; (M6) Neo4j grain inverted (MERGE on bare drawing_number collapses
  distinct drawings — plan wants {cid}__{pdf_stem}); (M7) reconcile silently drops route=QUARANTINE shas;
  (m8) Stage5 exits 0 on empty load; (m9) no orphan-Drawing-node check.
- **Batch-fixed all 9 across BOTH code paths (Lambda + local runner), re-QA PASS, 284 etl + 52 AWS tests.**
  Key designs: robust `parse_claude_json` (strip fences/extract braces/quarantine-not-crash); read nested
  markdown; stamp `_component_id` from manifest join; per-item quarantine + `{schema_ok,pii_clean,
  enriched_count,quarantined_count}` (ASL Choice proceeds on COMPLETED set, fails only on governance
  breach/threshold); case-insensitive+recursive PII + free_text_fields drop; grain = filename-based
  `{cid}__{pdf_stem}` MERGE on `grain_key`, Claude value kept as `extracted_drawing_number`, + a
  `(Component)-[:HAS_DRAWING]->(Drawing)` edge; reconcile universe = ALL manifest shas.
- **Redeploy:** Lambda bundle + ASL re-embedded; Stage5/6 containers rebuilt via CodeBuild (tag
  `run2538815-3`; hit + fixed the `:latest` immutable-tag trap — buildspec now pushes only the versioned
  tag); task-defs → revision `:2`; phase12 repointed.
- **STATUS: retry11 LIVE** — full silver→gold with the 9 fixes, monitored by cron (job b46d089a, 20 min).
  Then spend B (Twin Pass-2 enrichment ~$50.65). LESSON: when a whole downstream half is unproven, scope-QA
  it against REAL upstream output in ONE pass and batch-fix — don't re-run-and-discover one bug at a time.
- **Doc-count note:** worklist=117 distinct sha (manifest dedup) vs 118 expected vs 116 in source/docs —
  reconcile coverage (sha dedup vs dropped/quarantined doc); flagged minor by the Map QA.
- **retry12 (Stage-4 re-arch: per-sha DistributedMap + drawing/spec classifier) FAILED at Stage4 Map
  ResultWriter** — `States.ResultWriterFailed` / S3 PutObject **explicit-deny** on
  `silver/map_results/*/manifest.json`. BDA Map SUCCEEDED (118 outputs); Stage-4 Map died at ResultWriter
  *init* (the test-manifest write) BEFORE any per-sha child ran (silver stuck at 4). ROOT CAUSE = the
  CMK-deny bucket policy (`DenyWrongKmsKey`+`DenyUnencryptedPut` in `phase0_foundation.yaml`) carved out
  `bronze/map_results/*` (Stage 2/3's ResultWriter prefix) but NOT `silver/map_results/*` (the NEW Stage-4
  ResultWriter prefix). SFN native ResultWriter `s3:putObject` sends NO SSE header → trips the deny. **NEW
  LESSON (extends gap #11 / the Map-ResultWriter SSE carve-out rule): when you add a NEW DistributedMap
  whose ResultWriter writes under a NEW prefix, that prefix needs the SAME `NotResource` carve-out in BOTH
  deny statements — it is execution-control metadata, not a PII payload.** The fix is request-header-only;
  `silver/<sha>.json` payloads stay CMK-forced (verified by negative probe).
- **FIX DEPLOYED (2026-06-21):** added `${WorkingBucket.Arn}/*/silver/map_results/*` to both deny
  `NotResource` lists; CFN `flk-plm-etl-poc-foundation` UPDATE_COMPLETE. Change-set preview = only
  WorkingBucketPolicy changed for real (no resource replacement, no new IAM/KMS grants — ExecRole/Operator
  policy doc re-eval was ResourceAttribute/Never). Pre-spend gate **part (b) PASS**: positive probe
  (header-less PUT to `silver/map_results/` SUCCEEDS) + negative control (header-less PUT to plain
  `silver/` still DENIED). L17 two-paths check: the bucket policy lives ONLY in `phase0_foundation.yaml`
  (the two phase12 embedded files have 0 copies — only ResultWriter path refs). **retry13 LIVE** — 118 BDA
  shas skip via idempotency; proving silver climbs past 4 + spec→component_spec routing → Stage5/6 → gold.
- **STALE-ARTIFACT flag:** `src/statemachine/plm_etl.asl.json` + `_audit_deployed_asl.json` still show
  Stage 4 as a plain Lambda invoke (not the deployed DistributedMap) — reconcile so the next diagnosis
  isn't misled.

### ETL Gold COMPLETE (2026-06-22) — twin pipeline proven E2E
- **gold/_COMPLETE written, all gates PASS, qa-gate certified.** 118 BDA → 116 silver (36 drawings + 80
  specs) → Neo4j twin (36 Drawing + 85 Component, validated=true) → gold_population=86 (36 drawings + 50
  component_specs). reconcile 136/136 (116 completed + 18 declared-skipped + 2 quarantined), G4 orphan=0,
  G5 drift=0. The 116→86 delta is NOT loss (qa-gate verified): specs collapse by _component_id (80→49
  distinct) +1 sha-dedup fan-out (two byte-identical 1,140,692-byte PDFs share a sha → fanned to both
  component_ids per SA-14). Stage-4 drawing/spec classifier PROVEN (36/80 split).
- **CRITICAL INCIDENT — secret pointed at PROD, not a twin:** `plm/neo4j/creds` = Aura instance `e23c24ac`
  ("LPM Tech Validation Instance") which already holds the 20,347-node PRODUCTION PLM graph. Every Stage-5
  attempt this saga wrote into PROD (caught at 4 junk nodes + 1 reversible constraint swap; FULLY REVERTED:
  deleted our 2 Drawing/2 Component, dropped my drawing_grain_key_unique, re-created prod's drawing_unique;
  prod back to 820 Drawings + its June-19 LoadEvents untouched). **LESSON: a twin MUST verify it is NOT
  writing into a populated foreign graph.** Added the **twin-isolation guard** to neo4j_load.py — Stage 5
  refuses to write if the target has foreign Drawing nodes (no grain_key); override env ALLOW_FOREIGN_GRAPH=1.
- **Twin = local Docker Neo4j** (`plm-twin`, neo4j:5, bolt://127.0.0.1:7687) — the one free Aura slot was
  taken by prod, and only paid Aura tiers were API-creatable. Stage 5/6 run LOCALLY (Fargate can't reach
  localhost) via `etl-pipeline/run_stage5_local_twin.py` + `run_stage6_local_twin.py` (patch
  get_secret_json→local creds, _driver_security_kwargs→{} for no-TLS local, set WORKING_CMK_ARN for gold S3).
- **Stage 5/6 batch fixes (9 bugs, all proven by the green run):** neo4j driver TLS-scheme (`encrypted=` is
  illegal with neo4j+s:// → `_driver_security_kwargs` scheme-aware, both Stage5+Stage6 sites); P0-2 empty-graph
  MIRAGE gate (Stage6 reads/writes/counts component-specs + nonempty assertion); P1-2 USES edges scoped to
  manifest components; P1-3 missing-silver fail-closed + tuple return; P0-3 reconcile silver_landed fallback;
  P2-4 per-row qty parse. 318+8 tests, qa-gate PASS. Plus: ECR image run2538815-5, taskdefs:4, pipeline
  stack ecs:RunTask → revision-WILDCARD (was pinned :3 → AccessDenied on bump), Stage4 ResultWriter
  silver/map_results/* CMK-deny carve-out.
- **AWS Fargate Stage 5/6 path is DEPLOYED but UNVALIDATED** against a real twin (can't reach local Docker);
  for an AWS-native twin, provision a reachable Neo4j (paid Aura / in-VPC) and the deployed pipeline runs as-is.
- **SECURITY:** Aura API key + console login + instance passwords sit plaintext in OneDrive
  `AI/Technical Validation/Neo4j/` (`AWS Twin.txt`, `Neo4j credentials.txt`) — recommend rotating/securing.

### Twin Pass-2 enrichment — SANITY-CHECKED, ready to spend (2026-06-22)
- **DISTINCT workload from the ETL run above.** This is the ORIGINAL Twin Phase 3: Claude semantic
  enrichment over the 624-doc BDA Pass-1 markdown, in bucket `flk-plm-drawings-ai-techval` (twin/bronze),
  NOT the ETL `flk-plm-etl-poc`. Runner: `AWS/src/extract/run_pass2_enrich.py`.
- **Dry-run verified:** 624 BDA-completed docs, 0 already enriched, 624 pending. EST $50.44 (in 4.33M tok
  @ $3/M + out 2.5M tok @ $15/M, Sonnet). `--max-cost $60` ceiling allows it. Matches the ~$50.65 estimate.
- **Pre-spend checks ALL GREEN:** (a) G0 AUTHORIZED; (b) enrich_state.json = 63 COMPLETED, ALL `reuse-prod`
  (the 63 non-PDF prod-merges) → the 624 BDA docs are genuinely pending, NO double-spend; (c) Pass-1 input
  present (4,106 result.json in twin bucket); (d) model `us.anthropic.claude-sonnet-4-5-20250929-v1:0`
  ACTIVE in us-east-2 (matches runner CLAUDE_MODEL_ID exactly); (e) caller = AdministratorAccess (Bedrock OK).
- **Runner safety:** invoke_claude RAISES unless `--i-understand-this-spends`; idempotent resume (content-hash
  + PROMPT_VERSION p2-v1 cache key, should_enrich skips COMPLETED); temp 0; cost-ceiling abort; ledger NDJSON;
  reuses the PROD prompt verbatim (apples-to-apples). Modality caveat: feeds BDA markdown, not page images.
- **Recommended run:** smoke ONE small FG first (smallest = 3460387 @ 15 docs) with --i-understand-this-spends,
  verify silver lands + schema, THEN `--all --max-cost 60 --i-understand-this-spends`. NOT yet executed (user
  go/no-go pending). manifest=1,180 doc-edge rows / 15 FGs; 624 distinct BDA docs in the enrich path.

### Pass-2 SMOKE PASSED + read_timeout bug (2026-06-22)
- **Smoke FG 3460387: 12/12 docs enriched, all stop_reason=end_turn + schema_valid, 0 truncated, $0.87,
  no PII.** avg $0.073/doc → extrapolated 624-doc full run ~$45 (under the $50 estimate + $60 ceiling).
- **BUG found+fixed mid-smoke (the bloodiest kind — silent):** `invoke_claude`'s boto3 client set adaptive
  retries (8 attempts) but **NO `read_timeout`**. With non-streaming `invoke_model` + max_tokens=64000, any
  doc whose generation exceeds botocore's **default 60s read_timeout** throws ReadTimeout → the adaptive
  retry SILENTLY RE-INVOKES (re-spending) → manifests as a hang with frozen ledger + 2 stuck python procs.
  Doc 1 was fast (<60s) so the first smoke "passed" at 1 doc then hung on doc 2. **FIX:** `Config(
  read_timeout=900, connect_timeout=10, retries={...})` in run_pass2_enrich.py invoke_claude. 57 pass2 tests
  green. LESSON (add to aws-dev): a long-generation Bedrock invoke_model MUST set read_timeout > max gen time;
  the 60s default + retries = silent multi-spend hang. Idempotent resume confirmed (doc1 not re-spent).
- **READY for full run:** `python src/extract/run_pass2_enrich.py --all --max-cost 60 --i-understand-this-spends`
  (624 docs, ~$45-50). enrich_state=75 COMPLETED (63 reuse-prod + 12 smoke). User go/no-go pending.

### Pass-2 bounded concurrency (2026-06-22) — built, QA-hardened, awaiting go
- Added `--workers N` (default 1 = unchanged sequential) to `run_pass2_enrich.py` to cut the ~5hr
  sequential run (612 docs @ 31s/doc) to ~40-60min at 8 workers. Sonnet 4.5 quota = **5M TPM / 10k RPM**
  (verified via service-quotas) → 8 workers (~150K TPM) is <3%, ample headroom. ThreadPoolExecutor with
  cost-RESERVE-before-submit (N workers can't collectively overshoot --max-cost), per-doc quarantine
  isolation, idempotent resume preserved.
- **QA discipline caught a real BLOCKER the dev test missed:** qa-gate FAILED first round — the
  `enrich_state[key]=` writes in enrich_one run on worker threads but were UNGUARDED, racing the collector's
  `json.dump` → `RuntimeError: dictionary changed size during iteration`, ~deterministic at 612-doc scale
  (gate reproduced 15/15 at 150/8; the 12-doc dev test was too small to hit the iteration window). Also a
  degenerate ceiling test (admitted 0, proved nothing). **FIXED:** `with _STATE_LOCK:` around both writers;
  ceiling test rewritten to admit-exactly-5; added a 150-doc/8-worker race regression test. **re-QA PASS**
  (gate proved the lock load-bearing: crash 7/10 with it neutralized, 0/8 with it). 64 tests pass.
- LESSON (→ aws-dev / data-engineering): a threaded batch writing a shared dict + serializing it must lock
  BOTH the writers AND the serializer — locking only the reader gives no protection; and concurrency tests
  must run at SCALE (≥150 items) or the race window is missed. Also: long-gen Bedrock invoke_model needs
  read_timeout > max gen time (60s default + retries = silent multi-spend hang).
- **READY (awaiting final user go):** `python src/extract/run_pass2_enrich.py --all --workers 8 --max-cost 60
  --i-understand-this-spends` — 612 pending, ~$45, ~40-60min, idempotent/resumable.

### New-FG E2E test on the DEPLOYED AWS pipeline (5594650, 2026-06-22)
- Goal: prove the deployed `flk-plm-etl-poc` Step Functions pipeline runs a brand-new FG E2E "without
  stops". **Result: Stages 1-4 ran CLEAN end-to-end on AWS, zero stops** — preflight+G0+manifest (21 rows:
  20 BDA PDFs + 1 declared-skip .docx) → Stage2/3 BDA Map **20/20 outputs** → Stage4 enrich+classifier →
  **silver=20 (6 drawings + 14 component_specs)**. ~$7 BDA+enrich, under $12 ceiling, 0 quarantine.
- Stopped at **Stage5_Neo4jLoad** — EXPECTED: deployed Stage5/6 run on **Fargate which cannot reach the
  local Docker twin** (localhost), and the secret=prod + isolation guard protect prod. This is the silver
  audit checkpoint, NOT a bug. "Final part" = run Stage5/6 LOCALLY (the proven path) → gold. PARKED awaiting go.
- **Staging+trigger mechanism (learned, reusable):** new run prefix `date=<Y/M/D>/runs/<run_id>/`; stage
  `BOM_to_file.xlsx`→`source/manifest_input/` + docs→`source/docs/<filename>` (the `|`-split filenames the
  manifest Lambda resolves) — ALL uploads need SSE-KMS (`--sse aws:kms --sse-kms-key-id <WorkingCmk>`, L6,
  CMK-deny bucket). **Preflight G_preflight REQUIRES a `source/_START` attestation** = `{run_id,
  expected_doc_count, docs:[{name,sha256,size}]}` — it verifies each staged doc's size+sha + ≥1 BDA row;
  build `_START` FROM the staged S3 objects so sizes/shas match by construction. Trigger = manual
  `start-execution` with input `{run_id, run_prefix, cfg{fgs, cost_ceiling, ...all lambda/taskdef ARNs}}`
  (clone a prior run's input as template). No auto-trigger fires on upload. **stop-at-silver is a
  BUILD-TIME ASL variant (embed_asl.stop_after_silver), NOT a runtime flag** — the deployed SM is full
  silver→gold, so it naturally fail-stops at Stage5 for a local-twin FG (= the silver checkpoint).

### Pass-2 full run IN PROGRESS (2026-06-22)
- `--all --workers 8 --max-cost 60` launched (detached). Progressing ~82/612 net-new docs, ~$30, 8 workers
  healthy, no stalls. On pace for ~$45 total. Idempotent/resumable; ledger
  `costs/executions/pass2_enrich_ledger.ndjson`. User reviewing results when it completes before Phase 4.

### Pass-2 COST-CEILING bug fixed + full run (2026-06-22)
- **BUG (real overspend):** `--max-cost` metered a RESERVATION from the stale token ESTIMATE (~$0.07/doc,
  fixed 4000-output-token assumption); ACTUAL averaged ~$0.35/doc (5x, max $3.01). A `--max-cost 60` run
  reached **$64.74 and would not have stopped until ~850 docs (~$300)** — the ceiling was effectively inert.
  Stopped it manually at $64.74 / 182 docs enriched (idempotent, no loss).
- **FIX:** ceiling now meters ACTUAL cumulative `spent` + a realistic forward reservation
  `max(stale_est, running_actual_avg, PER_DOC_COST_FLOOR=0.35)`, in BOTH sequential and concurrency paths;
  overshoot bounded to ≤ workers × per-doc. qa-gate: FAIL→fix→re-QA PASS; +1 discriminating regression test
  (`test_workers_ceiling_bounds_actual_spend_when_estimate_runs_low`), 65 tests pass. LESSON (aws-dev/
  data-engineering): a cost ceiling MUST meter actual spend, never a pre-run estimate that can run low.
- **Resumed `--max-cost 220`** (idempotent): net ~361/612 enriched, ~$140 actual, 8 workers, on pace.
  True full-run cost ~$190-210 (NOT the original ~$45 dry-run estimate, which under-modeled output tokens 5x).
  Total enrich_state COMPLETED ~440 (63 reuse-prod + 12 smoke + ~365 this run+prior). Idempotent/resumable.

### Pass-2 COMPLETE + Stage-5 PROD-WRITE INCIDENT #2 (2026-06-22)
- **Pass-2 DONE:** resume `--max-cost 220` finished 430/430; **624 unique docs COMPLETED, 0 fail, 100% schema_valid**;
  enrich_state COMPLETED total 687; final-run spend $209.50/$220 (under ceiling); cumulative all-runs ~$275.
- **ETL Gold run-2538815a-retry15 FAILED at Stage 5** but proved the **Stage-4 rearch** (silver=122 ≫ old stall of 4,
  bda=118, gold/_COMPLETE present — per-sha Distributed Map + drawing/spec classifier working).
- **INCIDENT #2 (prod-write recurrence):** Stage-5 ECS taskdef + ALL pipeline IaC defaulted `Neo4jSecretArn` to the
  **PROD Aura secret `plm/neo4j/creds-43Ev6N` (neo4j+s://e23c24ac.databases.neo4j.io)** — NOT the twin. The run
  MERGEd into PRODUCTION and was only stopped by prod's legacy `drawing_number IS UNIQUE` constraint colliding on a
  pre-existing node (`5603404…DECAL_THUNDER`). The twin-isolation guard FAILED to catch it because it only refused
  `Drawing WHERE grain_key IS NULL` — prod Drawings carry grain_key, so foreign=0, guard passed. Contamination from the
  separate new-FG run `20260622-5594650a`: **8 nodes (4 Drawing validated=false + 4 Component) + 4 HAS_DRAWING edges**
  (prod 20,355 vs baseline 20,347). retry15 itself left 0 (constraint blocked before commit).
- **RESTORED:** surgical snapshot (`restore_snapshot_prod_20260622-5594650a_20260622.json`) then DETACH DELETE of exactly
  the run-tagged 8 nodes — prod back to 20,347, **1,142 legit USES edges preserved** (NOT archive-replay; the 20260611
  archive is a different 72k-node graph). **3-LEG TEST on live prod: 15/15 PASS all legs** — Leg1 deterministic (1142 USES,
  0 qty mismatch), Leg2 live GPT-5.5 agent, Leg3 compare = **AGREE 15/15 (CSV==graph==agent)**. Prod confirmed healthy.
- **FIXED (data-eng + 3-persona ×3 rounds to clean + terminal qa-gate PASS, 355 tests):** (1) replaced content-probe guard
  with fail-closed **URI-identity allow-list** `assert_twin_target` (only 127.0.0.1/localhost; runs BEFORE any driver opens;
  in Stage5 AND Stage6); (2) hard **deny-list** `_FORBIDDEN_HOSTS`+`.databases.neo4j.io` suffix so `TWIN_NEO4J_HOSTS` env can't
  re-add prod; `_uri_host` canonicalizes `strip().rstrip(".").lower()` (closes trailing-dot FQDN evasion); (3) idempotent
  **twin-schema bootstrap** (`grain_key IS UNIQUE`+`component_id IS UNIQUE`, DROP legacy `drawing_number` unique, twin-only,
  before first MERGE); (4) all 5 IaC templates + build/dist artifacts default to non-resolving sentinel
  `…000000000000:secret:REPLACE_WITH_TWIN_SECRET_ARN`; (5) partition_by_class fail-closed on unknown doc_class; (6) USES
  scoped to drawing-producing comps; (7) deterministic multi-PDF suffix. **LESSON: twin isolation must assert TARGET IDENTITY
  (URI allow-list + deny-list), never probe graph CONTENTS — a schema-sharing prod graph defeats a content probe.**
- **OPEN (operator preconditions before any Fargate Stage-5 re-run):** (a) provision a real twin endpoint + supply its secret
  ARN at deploy (sentinel default is intentionally non-resolving = fail-safe); (b) live local-Docker-twin smoke of run
  20260620-2538815a (`run_stage5_local_twin.py`/`run_stage6_local_twin.py`, bolt://127.0.0.1) to prove MERGE-level no-dup.
- Verdict + finding trail: `etl-pipeline/docs/reviews/qa_gate_stage5_neo4j_scoped.md` + `BATCH_FIX_SUMMARY.md`.

### Phase 8 doc suite BUILT + monitor paused (2026-06-23)
- **Plan status map:** Phases 0–3 DONE (BDA Pass-1 624/~$186, Pass-2 624/$275/100% schema-valid, manifest 1180 rows, silver 624 drawing+63 component_spec, 391 quarantined-by-design). **Phase 4 (twin load) is the next frontier — BLOCKED on standing up the local Docker twin Neo4j.** Phases 5/6/9 follow.
- **Phase 8 documentation suite COMPLETE** (`AWS/docs/reports/`, DOCX+PDF each): `AWS_Twin_Architecture`, `AWS_Twin_Deployment_Summary`, `AWS_Twin_HowTo_Setup`, `AWS_Twin_User_Guide`, `AWS_Twin_Infographic` (3-pg A4, 6 abstract GPT-Image-2 panels) + `AWS/PROJECT_MEMORY.md`. Builders + `twin_facts.json` (canonical numbers) + `twin_panels/` in `deliverables-scripts/`.
- **Integrity rule enforced:** real Phase 0–3 numbers tagged MEASURED; twin graph stats + twin-vs-prod comparison tagged **PROJECTED/pending Phase 4** (no fabricated graph counts). Every doc stamped `load_event_id PENDING-PHASE-4 · blueprint_version live-2026-06-19`. Secret/PII scan CLEAN on all 6 (placeholders for acct/ARN/creds, generic roles). G0 stated honestly as BYPASSED_POC.
- **Plan deviation (user-approved):** infographic uses Azure GPT-Image-2 (authorized cross-cloud fallback), NOT AWS-native Nova Canvas — Nova Canvas enablement deferred to Phase 9 repo/resource stand-up. Abstract prompts only (no drawing content) per G0.
- **ETL retry15 monitor cron CANCELLED** (was `4eb046a7`, :09/:29/:49 hourly) — paused until the new Neo4j twin is stood up + retry launched. Recreate pointed at the twin run when ready.

### Twin Neo4j created + Option B guard carve-out (2026-06-23)
- **User created a dedicated twin Aura instance** `2467c721.databases.neo4j.io` ("Instance02", created 2026-06-23)
  — creds in OneDrive `AI/Technical Validation/AWS/Neo4j/` (`Credentials for Instance02.txt`,
  `Neo4j-2467c721-Created-2026-06-23.txt`, + `AWS Twin.txt`). **PLAINTEXT — must rotate + move to Secrets
  Manager + delete the OneDrive files** (EA-P0, same exposure pattern as prod Aura creds).
- **Option B implemented** (data-engineering skill + 3-persona + qa-gate PASS): carved the twin Aura host
  out of the guard's blanket `*.databases.neo4j.io` deny so Stage-5/6 can load to it WITHOUT weakening the
  prod block. `etl-pipeline/src/lambdas/neo4j_load.py`: new `_ALLOWED_AURA_TWIN_HOSTS` (CODE-level, not env
  — env still can't enable any Aura host); `_is_forbidden_host` precedence = exact-prod FIRST/absolute →
  approved carve-out → generic Aura suffix; import-time disjoint assert. **3-persona fuzzed 1620+12 prod
  decorations, 0 bypasses.** Secondary fixes: idempotent `_uri_host` strip (DE-P2), `database` passthrough
  (Stage5 handler+provision_twin+Stage6 via `_DbScopedDriver`), `loaded_to_host`/`target_host` provenance
  (EA-P1-2), NEW deploy-time `src/iac/verify_twin_secret.py` reusing the SAME guard (EA-P1-1), stale-doc
  fixes (local-runner docstring, `Neo4jSecretArn` desc in all 5 IaC templates, VPC README prod-host ref),
  NEW `AWS/.gitignore` (Neo4j/ + cred patterns). **444 tests green (379 etl + 65 AWS), qa-gate PASS.**
- **Secret-ARN deploy path:** create a Secrets Manager secret `plm/neo4j/twin-creds` holding the twin Aura
  `uri/username/password/database`, pass its ARN as the `Neo4jSecretArn` CFN param (default is non-resolving
  sentinel). Pre-deploy gate: `python src/iac/verify_twin_secret.py --secret-arn <arn>`.
- **Twin secret created (POC, no rotation per user):** `plm/neo4j/twin-creds-gmYzkV` (us-east-2) holds the
  Instance02 uri/user/pw/database. AWS-managed KMS (no CMK grant needed).
- **CUTOVER DEPLOYED (2026-06-23):** built+pushed Option-B images **tag `optb-twin-1`** (stage5 digest
  `…468213b1`, stage6 `…89e4e20d`) via CodeBuild `flk-plm-etl-poc-images` (source zip re-uploaded SSE-KMS
  key `42e68e15`). Redeployed ALL THREE stacks (`-foundation`, `-taskdefs`, `-pipeline`) with
  `Neo4jSecretArn`→twin; taskdefs now **rev :5** → `optb-twin-1`. Deleted stale `:latest` ECR tags (footgun).
- **THE RUNTIME-READ GOTCHA (key lesson):** the app reads creds at RUNTIME via `neo4j_load.handler` →
  `get_secret_json($.cfg.neo4jSecretArn)` using the ECS **TASK role `flk-plm-etl-poc-exec`** (defined in
  **phase0_foundation**, NOT phase5_taskdefs). The taskdef `secrets:` block uses the **execution role
  `flk-plm-etl-poc-task-exec`**. Redeploying taskdefs alone left the task role still GetSecretValue-scoped to
  PROD → IAM-simulator caught `twin=implicitDeny, prod=allowed`. **Fix: redeploy phase0_foundation too.** Now
  BOTH roles: twin=allowed, prod=implicitDeny. LESSON: when an app reads a secret itself (not via the ECS
  secrets-injection block), the TASK role governs it — and that grant may live in the foundation stack.
- **`$.cfg.neo4jSecretArn` comes from the START-EXECUTION INPUT, not the stack** — the ASL injects
  NEO4J_SECRET_ARN from it. So the launch input is the deciding value; cloning a prior retry verbatim
  re-introduces prod. Corrected launch input saved: `etl-pipeline/docs/restore_points/twin_launch_input_2026-06-23.json`
  (cfg.neo4jSecretArn=twin, taskdefs :5; full-scan 0 prod/stale tokens).
- **prod now blocked at 4 layers:** launch input + IAM (both roles deny prod) + runtime carve-out guard +
  deploy-time `verify_twin_secret.py`. Restore point: `etl-pipeline/docs/restore_points/RESTORE_POINT_2026-06-23_twin-cutover.md`.
- **run-2538815a-twin-1 FAILED at the FINAL gold write** (Stage 6) — but proved the cutover: all data gates
  passed (37 Drawing + 85 Component loaded into the twin, validated=false; G4/G5/reconcile PASS), only the
  S3 gold write failed `AccessDenied: PutObject .../gold/run_report.json — explicit deny in resource policy`.
  Red herring in the event blob: a `403 CannotPullContainerError` on the **GuardDuty sidecar** (non-essential
  AWS-injected container) — NOT our image; `validate` pulled fine and exited 1 on the S3 deny.
- **ROOT CAUSE (scoped QA, single fix, no whack-a-mole):** the Stage-5/6 **Fargate taskdefs never injected
  `WORKING_CMK_ARN`**, so `aws_io._sse_args()` returned `{}` and `put_json/put_bytes` sent NO SSE-KMS header.
  The working-bucket policy force-encrypts `gold/*` (NOT in the bronze/silver `NotResource` carve-outs) →
  deny. All 8 gold writes route through that one helper, so ONE fix covered all. KMS grants were already in
  place (task role `flk-plm-etl-poc-exec` allowed kms:GenerateDataKey/Decrypt on CMK `42e68e15`). Lambdas get
  `WORKING_CMK_ARN` via phase12; the Fargate taskdefs were the gap (Stage 5 didn't matter — it writes only
  Neo4j, not S3). See [[feedback-fargate-working-cmk-env]].
- **FIX (no image rebuild — aws_io already reads the env):** added `WorkingCmkArn` param + `WORKING_CMK_ARN`
  env to BOTH containers in `phase5_taskdefs.yaml` (+ regression test `test_both_taskdefs_inject_working_cmk_arn`,
  380 tests green). Redeployed taskdefs → **rev :6**; updated launch input taskdef ARNs :5→:6.
- **run-2538815a-twin-2 ✅ SUCCEEDED (2026-06-23) — TWIN CUTOVER PROVEN E2E.** gold/_COMPLETE + 37 extraction
  + 50 component_specs + graph/nodes.csv + run_report + reconciliation_report all landed. **Twin graph: 37
  Drawings validated=TRUE (0 false), 85 Components, 122 nodes, all stamped loaded_to_host=2467c721.** Re-run
  was idempotent (37 nodes re-MERGEd, no dupes, flipped to validated). NO BDA/silver re-spend.
- **NEXT:** recreate the ETL monitor cron on twin runs; then the original Twin Phase 4 (624-doc silver from the
  `flk-plm-drawings-ai-techval` bucket). Operator cred hygiene (delete plaintext OneDrive `Neo4j/*.txt`) deferred (POC).

### ORIGINAL TWIN PHASE 4 COMPLETE — 687-doc corpus loaded prod-parity (2026-06-24)
- **Decision:** load the 15-FG / 687-doc original corpus (624 BDA→Claude drawings + 63 reuse-prod specs = true twin
  scope) via the **PROD loader `build_fresh_graph.py`** (one-off), NOT the ETL — to get Drawing grain byte-parity
  with prod by construction (the ETL "fixed" prod's multi-PDF suffix → 74-128 key divergence). User chose: match
  prod exactly · evaluate build_fresh_graph · PII=RETAIN (POC). Grain source = `data/silver/*.json` (LOCAL, not S3).
- **Built** `AWS/src/load/load_twin_via_build_fresh.py` (+ 18 TDD tests `AWS/tests/test_load_twin_via_build_fresh.py`):
  a wrapper that (1) HARD-asserts the twin host EXACTLY == `2467c721.databases.neo4j.io` before importing the loader
  (defuses build_fresh_graph's PROD-WRITE LANDMINE — if any NEO4J_* env unset it imports query_graph.py hardcoding
  prod; that fallback now also raises on missing pwd post-DLP), (2) adapts silver→loader shape (`_pdf_filename :=
  _source_pdf_filename` ALWAYS = single grain source of truth + collision field-consistency fix), (3) routes through
  the loader's OWN `_resolve_drawing_number(use_pdf_stem=True)` + `__{pdf_stem[-30:]}` suffix for prod-identical grain.
- **3-persona review** (NO-GO→fixes) caught: P0 silent 687→685 collapse (collision compared 2 different fields) → FIXED
  (687 distinct keys, 0 collapses); "byte-identical to prod" reframed to "prod grain FUNCTION on twin's own source set"
  (the twin's silver is a genuinely different/smaller doc set than prod → ~27 doc-count deltas, EXPECTED, = what the
  comparison measures); guard hardened to exact-host; PII attestation corrected (0 Person nodes created — no record has
  a `personnel` key). **qa-gate: FAIL (2 majors: collapse-abort was plan-only; az-token gap could half-wipe) → fixed →
  re-gate PASS** (+ live-count==687 post-load hardening).
- **RAN staged** (wipe→load→verify→USES): wiped the 143 ETL nodes (clean prod-parity rebuild) → `--load` 53 min:
  **687/687 drawings, 0 failed, 687 embeddings OK**, post-load assert live==687 PASS → `--verify`: 827/827 components,
  15/15 parents PASS, 0 orphans, 0 missing embeddings (27 doc-count mismatches = the EXPECTED source-corpus delta, graph
  == silver exactly). Then `load_uses_edges.py --execute`: **1142 USES edges, all gates PASS** (qty+assembly_id on all,
  0 dup, 0 negative, 15 FGs). **FINAL TWIN: 15724 nodes — 15 Product + 827 BOMComponent + 687 Drawing + 1185 Part,
  1142 USES + 1749 HAS_DRAWING, 687 embeddings, 0 orphans.** Twin is comparison-ready (vs prod, scoped to 15 common FGs).
- LESSON [[feedback-prod-loader-twin-reuse]]: reusing a prod loader for a twin needs a host-exact guard wrapper (prod
  fallback landmine) + a silver→loader adapter; grain parity comes from the loader's OWN function, but the twin's key
  SET legitimately differs by source-corpus differences — don't assert set-equality, assert "no silent drop + grain fn parity".

### Phase 6 twin-vs-prod comparison COMPLETE (2026-06-24)
- `AWS/src/compare/twin_vs_prod_diff.py` — read-only dual-DB diff (hard write-guard on BOTH graphs so prod
  e23c24ac is never mutated; 7 tests). 3 traversals + field-richness, scoped to the 15 common FGs. Output:
  `docs/reports/AWS_Twin_vs_Prod_Comparison_20260624_final.{md,json}`.
- **KEY FINDING — raw set-diff was misleading:** raw 440 twin-only / 638 prod-only, but **731 are NAMING
  ARTIFACTS** (same source doc keyed `{cid}_{stem}` in twin vs bare `{stem}` in prod — prod's supplemental/
  phase5/heather loaders didn't cid-prefix; twin used use_pdf_stem=True everywhere). **Normalized TRUE delta:
  twin-only 75 / prod-only 272.** Prod genuinely has ~272 more docs (vendor spec sub-sheets + non-PDF) the
  BDA→Claude twin lacks; bulk MATCH. Components 1269/1269 + USES 1142/1142 IDENTICAL. Field-richness: prod
  vision pipeline persists far more notes/bom text/drawing (expected; reported not scored).
- LESSON: comparing two graphs built by the SAME loader from DIFFERENT source pipelines — ALWAYS normalize
  the join key before set-diffing; a loader-path naming difference inflated the apparent delta 3-6×.

### Phases 8 + 9 COMPLETE → PLAN DONE (2026-06-24)
- **Phase 8 doc-refresh:** `deliverables-scripts/twin_facts.json` flipped to all-MEASURED (no PROJECTED);
  6 builders re-run → DOCX+PDF in `AWS/docs/reports/` with real twin stats + measured comparison section.
  Infographic PDF written as `_NEW.pdf` (old one locked by open Acrobat — rename after closing).
- **Phase 9 local repo:** `PLM-AI-Drawing-tool-AWS-Twin` (sibling of AWS/), 119 files, main+dev, commit
  `5ecc60d`. Built an AWS-twin-aware `sanitize_for_repo.py` (extends the PLM-AI-Drawing-tool one with
  AWS account 161643475055 / twin 2467c721 / prod e23c24ac / ARNs); scrubbed all committed text to
  placeholders (creds via env), post-scan + independent grep CLEAN, secret-scanner hook PASSED. The
  sanitizer itself is gitignored (holds real scrub patterns). Data/secrets/creds/docx/pdf/approval all
  gitignored. **Local-only — remote push is a separate authorized step (DLP discipline).**
- **secret-scanner gotcha:** the hook's placeholder-exemption only fires on a FULL comment line (starts
  with # or //), NOT a trailing comment; and it matches `PASSWORD='<8+ chars>'`. Fix for example creds in
  docs = use `$PW` env-var refs (no quoted 8+ char literal) rather than `<TWIN_NEO4J_PASSWORD>` placeholders.
- **STATUS: AWS_TWIN_EXECUTION_PLAN v3.6 — ALL PHASES 0–9 DONE.** Twin built+validated+compared+documented
  +repo'd. Housekeeping only: cred hygiene (plaintext OneDrive creds), optional remote push, G0 formalize.

### Head-to-head comparison deliverable + quality-fix plan (2026-06-24)
- **5-FG head-to-head** (`docs/reports/AWS_Twin_vs_Prod_HeadToHead_5FG.docx`+`.pdf`+`.xlsx`): tightest-overlap
  FGs 5594650/5594661 (100% doc match) + 5073403/5073415 + 4840537. Weighted scorecard (richness 30/correctness
  25/completeness 15/speed 10/cost 20): **Prod 80.0 vs Twin 65.5** — prod richer notes/bom + ~25% cheaper; twin
  faster + more dimensions (1305 vs 518). Both a weighted scorecard AND neutral side-by-side. Builders:
  `deliverables-scripts/{h2h_analysis,build_h2h_docx,build_h2h_xlsx}.py`. Cost: twin MEASURED ($0.739/doc =
  $0.298 BDA + $0.441 Claude), prod ESTIMATE (~$0.55/doc, no prod ledger).
- **ROOT-CAUSED two twin quality gaps (plan `docs/plans/TWIN_NOTES_REVISION_FIX_PLAN.md`, plan-only, 5-FG scope):**
  - **notes=0 is a FIELD-NAME MISMATCH, not missing extraction:** the twin Pass-2 prompt emits `manufacturing_notes`
    (populated!) but prod's schema + the loader use `general_notes` → notes silently dropped at load. Fix A
    (zero-spend): map manufacturing_notes→general_notes in the loader adapter + re-load 5 FGs. Fix B (optional,
    ~$3-5): align the Pass-2 prompt to emit general_notes + re-extract 5 FGs.
  - **revision agreement 41% is mostly NORMALIZATION, not error:** on 5594650, 17/20 actually agree; "mismatches"
    are format (twin `'2'` vs prod `'Rev. 2, 3/2025'`; twin often cleaner). The 41% metric was too strict
    (exact string). Fix C: normalized revision comparator in twin_vs_prod_diff.py.
  - Recommended sequence C+A first (zero-spend, recovers the bulk) → re-measure → B only if needed. TDD + tests
    specified in the plan. Expected: twin notes 0→comparable, rev-agree 41%→75-90% normalized, twin total rises.

### Related
- [[project_plm_drawing_extraction]] / [[project_plm_drawing_agent_app]] — production project being twinned
- [[aws-bda-config]] — BDA blueprints/project/inference profiles
- [[data-dev-planning-skill]] — reusable planning skill built from this engagement's method
- [[reference-gpt-image-not-on-bedrock]] — Nova Canvas is the AWS-native text-to-image model
