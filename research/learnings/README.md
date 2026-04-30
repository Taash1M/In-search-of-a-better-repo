# Research: Distilled Learnings

Patterns, anti-patterns, and gotchas extracted from 3+ months of Claude Code usage across UBI platform engineering, AI tooling, document generation, and team enablement work.

---

## 1. Azure AI Foundry

**Foundry project prerequisite.** An Azure AI Foundry *project* must exist before any model deployments can be made. Creating the hub resource alone is not sufficient — the project is the scope for deployments, keys, and quotas.

**api-version requirement.** The Foundry endpoint requires an explicit `api-version` query parameter on every request. Omitting it returns a 400 with a misleading error. Use the version that matches the SDK you are on; mismatches cause silent degradation.

**x-api-key header.** When calling Foundry endpoints directly (not via SDK), the auth header is `x-api-key`, not `Authorization: Bearer`. The SDK handles this transparently, but raw HTTP callers must set it explicitly.

**RBAC via REST API.** `az role assignment create` fails silently on the Fluke AI ML Technology subscription — it returns success but the assignment does not persist. Always use the Azure REST API PUT endpoint (`/providers/Microsoft.Authorization/roleAssignments/{guid}`) with a fresh UUID for the assignment name. Verify with `az role assignment list` after.

---

## 2. Claude Code Skills

**200-600 line sweet spot.** Skills below 200 lines tend to lack enough context for complex tasks. Skills above 600 lines blow out the context budget on smaller models (especially haiku). Target 300-500 lines for skills that need to work across model tiers.

**Frontmatter `when` field behavior.** The `when` field in skill frontmatter is a trigger hint, not a hard filter. Claude Code reads all available skill names on every turn and pattern-matches against the user's message. Skills with vague `when` descriptions get missed; be specific and include example phrasings.

**Context budget on haiku.** Haiku has a significantly smaller effective context window for skill execution. Skills that load multiple reference files (templates, catalogs, schemas) in a single turn can hit budget before producing output. For haiku, split multi-phase skills into separate invocations or defer loading reference files until the phase that needs them.

**Research-first before upgrading.** Before adopting a new open-source library or upgrading a dependency, run `repo-eval` to check production readiness, maintenance activity, and security posture. Two instances of adopting a library without this step led to mid-project pivots when API stability issues were discovered.

---

## 3. Document Generation

**python-docx: always set Normal style first.** If the `Normal` paragraph style is not explicitly set before writing body content, python-docx inherits Word's default theme font, which varies by system and produces inconsistent output across machines. Set `doc.styles['Normal'].font.name` and `doc.styles['Normal'].font.size` at document creation time.

**OXML for features not exposed natively.** python-docx does not expose all Word formatting features through its Python API. Table borders, paragraph shading, custom list styles, and certain run-level properties require direct OXML manipulation via `lxml`. The pattern is: get the element (`._element`), build the XML node, append or merge. Always test OXML additions against a round-trip open in Word — some constructs are valid XML but cause Word repair prompts.

**cairosvg needs MSYS2 DLLs on Windows.** cairosvg requires native Cairo libraries. On Windows, the Python wheel does not bundle them. Install MSYS2 (64-bit), then copy the required DLLs to a location on `PATH`. Required DLLs: `libcairo-2.dll`, `libgdk_pixbuf-2.0-0.dll`, `libglib-2.0-0.dll`, `libgobject-2.0-0.dll`, plus their transitive dependencies. DLL location: `<USER_HOME>/tools\cairo-dlls\`. See `research/memory/reference_cairosvg_windows.md` for the full list.

**D2 path gotchas.** The D2 CLI (`d2.exe`) requires forward-slash paths even on Windows — backslashes cause silent parse failures. The `$` character in diagram source triggers shell variable substitution when passed via subprocess; wrap in single quotes or escape. `|md|` literal blocks break if the content contains `<` — use `|` plain blocks or escape the angle brackets.

---

## 4. Data Engineering (UBI)

**Always use all-purpose clusters for interactive work.** Job clusters on Databricks terminate immediately on job completion and cannot be attached to notebooks for inspection. All interactive development and debugging must use all-purpose clusters. Job clusters are for scheduled production runs only.

**Oracle VARCHAR2 lands as STRING in Bronze.** All Oracle source columns with `VARCHAR2` type are ingested as `STRING` in the Bronze layer regardless of their semantic content (dates, numbers, flags). Do not assume numeric or date types in Bronze; always cast explicitly in Silver.

**Silver does type casting and JOINs.** The Silver layer is where raw strings become typed columns (CAST to DECIMAL, DATE, TIMESTAMP) and where the ~25 dimension table JOINs occur (customer, product, org, currency). Business logic — return sign flipping, SalesCreditPct splits, relative amount calculations — also lives in Silver. Bronze-to-Silver is the most complex transformation stage.

**Gold creates views with backtick-quoted aliases.** Gold layer objects are Spark SQL views, not physical tables. Column aliases use backticks (not double-quotes) because Spark SQL uses backticks for identifier quoting. Business-friendly names with spaces (e.g., `` `Sales Order Number` ``) are standard. Direct Delta (ADLS publish) mirrors Gold views in Delta format for Power BI DirectQuery.

**Delta Lake maintenance: OPTIMIZE then VACUUM.** `OPTIMIZE` compacts small files into larger ones and optionally clusters by a column (Z-ORDER). `VACUUM` removes old file versions beyond the retention threshold (default 7 days). Always run OPTIMIZE before VACUUM — VACUUM on un-optimized tables removes files that are still needed for compaction. Never set retention below 7 days unless time-travel is explicitly disabled.

**Data skew detection and salting.** When a Spark job shows one task taking 10x longer than others, check for partition skew with `spark.sql("SELECT _partition_id, count(*) FROM ...")`. Skew on high-cardinality keys (e.g., customer ID in large fact tables) is addressed by salting: add a random integer suffix (0-N) to the join key, explode the dimension side, join on the salted key, then drop the salt. N=10 resolves most skew cases without excessive memory overhead.

---

## 5. Diagram Quality

**Always visually inspect before embedding.** Diagram generation tools (cairosvg, matplotlib, D2) can produce syntactically valid output that is visually broken — missing icons, overlapping labels, distorted aspect ratios, or clipped text. Never embed a diagram in a document without opening the PNG/SVG and inspecting it. Automated checks (file size > 0, no exception thrown) are necessary but not sufficient.

**Fix+regenerate loop.** When a diagram has visual defects, the correction cycle is: identify the defect in the rendered output, trace it to the source (icon registry, layout coordinates, label length, bounding box), fix the source, regenerate, and re-inspect. Do not embed partially fixed diagrams — complete the loop first.

**Missing icons fail silently in cairosvg.** If an Azure icon path is wrong or the SVG file is missing, cairosvg renders a blank space with no error. Always validate icon registry entries against the actual files in `Azure_Public_Service_Icons_V23/` before running generation. A pre-flight check that lists all referenced icon paths and confirms they exist on disk prevents this class of defect.

---

## 6. Git and Repo Patterns

**Safe directory for cross-user ownership.** When running git commands on a repo owned by a different Windows user (e.g., running as `<ADMIN_USER>` on a repo owned by `<USER>`), git refuses to operate with a "dubious ownership" error. Fix with `git config --global --add safe.directory <path>`. This is required on any shared machine or when using elevated shells.

**Never use `-uall` on large repos.** `git status -uall` recursively lists every untracked file in every subdirectory. On repos with large `node_modules/`, build outputs, or data directories, this can take minutes and produce megabytes of output. Use `git status` (no flags) or `git status -u` (default, one level deep) instead.
