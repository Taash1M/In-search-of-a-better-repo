---
name: PBI type encoding, modelExtensions placement, formatInformation, .pbip workflow, island table patterns, Fabric DirectQuery M query folding
description: PBIX impossible in 2.153+ (use .pbip), TREATAS island tables, Fabric DirectQuery M queries must be simple table refs (no Table.AddColumn/SelectColumns), Fabric shortcuts don't auto-sync Delta schema changes, ambiguous relationship paths from bidirectional cross-filter, schema_mode="overwrite" for Delta column additions, blob upload auth-mode key not login
type: feedback
originSessionId: f4d03941-dd0b-44f2-bb99-51b65b072972
---
## dataType in modelExtensions — depends on model type
- **DirectQuery/Composite models** (has `DataModel` file — Fabric Lakehouse, SQL Server): use `dataType: 3` (Decimal Number). Value `6` maps to Date/DateTime in the SSAS enum, causing chart axes to show "h:mm:ssfff tt".
- **Live connection reports** (has `Connections` file, no `DataModel`): use `dataType: 6` for visibility. Value `3` may make measures invisible in Fields pane.
- **How to check:** Inspect ZIP contents of base .pbix. `DataModel` present → use 3. `Connections` present → use 6.

**Why:** PBI interprets `dataType` differently by model type. In DirectQuery, it's the actual SSAS DataType enum. In live connection, it controls Fields pane visibility. Cards show correct values with either value, but chart axes derive their type from `dataType`.

## underlyingType in dataTransforms
Use `underlyingType: 261` (Double) for numeric measures, NOT 518 (DateTime). PBI encodes as `(category << 8) | valueType`. 261 = Numbers+Double, 518 = Temporal+DateTime.

## formatInformation — strict enums in v2.152+
Both `format` and `currencyFormat` are enum fields. String values like `"Currency"`, `"$#,##0.00"` cause `ModelAuthoringHostService.UpdateModelExtensions` "wrong arg" errors. Set both to `null` — `formatString` alone is sufficient.

## modelExtensions placement — CRITICAL
`modelExtensions` must live inside `layout["config"]` (a JSON string), NOT as a top-level key on the layout object. Writing `layout["modelExtensions"] = [...]` is silently ignored by PBI Desktop — measures won't resolve and visuals show `Missing_References` errors. Correct pattern: parse `json.loads(layout["config"])`, modify `config["modelExtensions"]`, serialize back.

**Why:** Learned the hard way (2026-04-13) — cards/charts showed "Fix this" errors while table visuals (which reference columns directly) worked fine. The modelExtensions were at the wrong nesting level.

**How to apply:** When modifying an existing .pbix, always parse the config string first. When generating from scratch, set `modelExtensions` on the config dict before serializing it as the layout config string.

## Pages are `sections`, not `pages`
The layout JSON stores pages under `layout["sections"]`. There is no `pages` key. Using `layout["pages"]` raises `KeyError`.

**Why:** PBI internal terminology uses "sections" in the JSON but "pages" in the UI. Easy to mix up when writing modification scripts.

## PyArrow date32 causes empty DirectLake slicers
Python `datetime.date` objects infer as PyArrow `date32` → Fabric imports as Date type → DirectLake slicers show empty. Fix: convert to strings with `.strftime("%Y-%m-%d")` and use explicit `pa.schema([pa.field("col", pa.string())])` with `schema_mode="overwrite"`.

**Why:** Discovered on DimDate `full_date` field (2026-04-13). PyArrow type inference is invisible — the ETL runs fine but PBI slicer breaks silently.

## Slicer mode conversion when data type changes
When a Delta column changes from date to string (e.g., `date32` → `pa.string()`), "Between" date-range slicers break silently (show empty or error). You must rebuild the slicer as a Dropdown list slicer. The "Between" slicer has 3 selects (column, Earliest, Latest) — the dropdown replacement has only 1 select (the column).

**Important:** PBI Desktop overrides `underlyingType` to match the Fabric semantic model column type. If the model sees the column as DateTime, PBI forces `underlyingType: 519` regardless of what you set. Strategy: set `underlying=519` in the slicer and control display via `formatString` (e.g., `"MMM-dd-yyyy"` for "Apr-13-2026"). Add format via both `columnProperties` on the singleVisual config AND `fmt` in `_dt_select_column`.

**Why:** Discovered on full_date slicer (2026-04-13). Backend type changed but report slicers still referenced the old type. PBI doesn't show a clear error — the slicer just renders empty. Setting underlyingType=1 was then overridden by PBI Desktop to 519.

## Visual layout sanity check — MANDATORY for PBI page generation
After building any PBI page layout, run a bounds check: verify no visual overflows the page (`x+w <= PAGE_W`, `y+h <= PAGE_H`). Document Y-band allocations in a docstring at the top of each `build_page_*()` function. Keep card measure names under 16 chars for 200px-wide cards to avoid label truncation. Remove redundant section headers above charts — use the chart's built-in `title` object instead.

**Why:** First health check page build (2026-04-13) had overlapping visuals, truncated card labels ("Latest Deployments Healthy" in 195px card), and duplicate headers competing with chart auto-titles. Required full layout redesign.

**How to apply:** Use grid-based Y-band planning. Add automated `for vc in vcs: check x+w, y+h` sanity loop before serializing. Open in PBI Desktop for visual confirmation — text truncation and chart title overlap are invisible to code checks.

## Capture user's manual PBI Desktop adjustments
When user adjusts visuals in PBI Desktop, extract positions from the saved .pbix (parse ZIP -> Report/Layout -> sections -> visualContainers -> config -> layouts[0].position) and update the generation script with exact `{x, y, width, height, z}` values. Document the Y-band grid in a docstring. This prevents regeneration from overwriting preferred layout.

**Why:** User's manual formatting adjustments (2026-04-13) reduced 20 visuals to 18, removed subtitle/slicer bg shape, adjusted all positions. These were format-level changes that must survive script re-runs.

**How to apply:** After user says "I fixed it manually", extract positions before regenerating. Use high z-values (4000-19000) for proper layering.

## README textbox search — skip contents_idx
When `update_readme_page` rewrites the Contents textbox (Step 1), it adds text like "Page 5  Usage & Health Insights". If later steps search for "Usage & Health Insights" or "Infrastructure Health" in `cfg_str`, they match the *contents* textbox and overwrite the page list. Fix: always skip `contents_idx` in Steps 3-4 search loops.

**Why:** Discovered 2026-04-13 when insight docs search clobbered the 5-page contents list. The contents textbox is a superset of all page names.

## Combo chart (lineClusteredColumnComboChart) — multi-entity Extension
PBI combo charts use projections `Category`, `Column y`, `Line y`. The Extension block supports multiple entities when measures come from different tables (e.g., bars from llm_usage + line from health_checks). Each entity declares its own `Extends`/`Name`/`Measures`. If both measures share the same table, combine into one entity. The From clause needs separate aliases (`m1`, `m2`) for each measure-bearing table.

**How to apply:** Add `lineClusteredColumnComboChart` to the slicer fixer's chart-type list so `full_date` underlyingType fixes apply to combo charts too.

## ZIP DataModel compression — CRITICAL
The DataModel entry in .pbix ZIP files uses **method=0 (stored/uncompressed)**. Never deflate it. When replacing ZIP entries, check the local header's compression method at offset 8: if method=0, write raw bytes (compressed_size == uncompressed_size). If method=8, deflate. Deflating a stored entry corrupts the CRC and PBI won't open the file.

**Why:** Discovered 2026-04-13 when DataModel injection from base file caused `BadZipFile: Bad CRC-32 for file 'DataModel'`. The `_replace_entry` helper always deflated, but the header still said method=0.

## NEVER inject DataModel across .pbix files — CRITICAL
Do NOT replace the DataModel entry in a DirectLake .pbix (has `Connections` file) with a DataModel from a different .pbix (e.g., an import-mode base file). PBI Desktop tolerates the mismatch, but **PBI Service rejects it during publish** (UnknownError). The DataModel has internal state (versions, column mappings, dataset references) tied to its original connection mode.

Additionally, injecting a DataModel that contains extra relationships (e.g., dim_date → health_checks) can create **cyclic filter paths** with TREATAS DAX: TREATAS pushes health_checks → dim_date, and the injected relationship pushes dim_date → health_checks = cycle. Without the relationship, TREATAS works as a one-way virtual filter with no cycle and no need for CROSSFILTER.

**Why:** Discovered 2026-04-13. Injecting base file DataModel (51323 bytes, import-mode) into DirectLake v2 caused: (1) cyclic reference during evaluation on llm_usage table, (2) publish to PBI Service failed with UnknownError even after adding CROSSFILTER to break cycles. Removing both the injection and CROSSFILTER fixed both issues locally. **BUG: Publish still fails (2026-04-13) — needs investigation.** May require rebuilding the report natively in PBI Desktop rather than programmatic ZIP manipulation.

**How to apply:** Only modify `Report/Layout` in the ZIP. Never touch `DataModel`. If relationships are needed, add them in PBI Desktop on the target file directly or in the Fabric semantic model.

## modelExtensions measures — always replace, never skip
When adding report-level measures to modelExtensions, use replace-or-add logic (overwrite existing measures by name). Do NOT skip measures that already exist — they may have stale DAX from a prior run. This is especially important for TREATAS-based cross-table measures that replaced direct CALCULATE filters.

**Why:** Discovered 2026-04-13 when "Requests (Healthy)" measures kept old non-TREATAS DAX because the skip-if-exists logic preserved them from a prior build.

## Bar chart measures must exist in modelExtensions
When a visual references a measure by name (via `Measure` in prototypeQuery Select), that measure MUST exist in modelExtensions. Inline DAX in the visual definition alone is not enough — PBI resolves the `Property` name against the model, and missing measures produce `Missing_References` errors.

**Why:** Discovered 2026-04-13 when "Requests by Verdict" bar chart showed Missing_References. The visual was built correctly but the measure was never added to INSIGHT_MEASURES.

## Preserve user's manual PBI Desktop position tweaks
When updating README or other textbox content programmatically, only modify the `paragraphs` content — do NOT replace the entire visual or override `position`. Users adjust fractional positions in PBI Desktop (e.g., y=96.51, x=12.79) that must survive script re-runs. For new visuals (not yet in the file), use hardcoded positions; for existing visuals, update text only.

**Why:** Discovered 2026-04-13 when regeneration kept resetting user's README layout adjustments (Contents header, page list, Architecture header all repositioned manually).

## PBIX ZIP manipulation is IMPOSSIBLE in PBI 2.153+ — CRITICAL
PBI Desktop April 2026 (2.153.910.0) validates Report/Layout content against an internal integrity check. **Any modification to Report/Layout bytes — even 1 byte — causes "MashupValidationError: This file is corrupted"**. This was proven exhaustively:
- Raw byte surgery (preserving all ZIP metadata): fails
- Python zipfile module (clean rewrite): fails
- Direct byte replacement (no JSON parsing): fails
- Zero-change round-trip: works (proves ZIP structure is fine; content hash is the blocker)

**Fix: Use .pbip format instead.** Save As → Power BI Project (.pbip) from PBI Desktop. This decomposes Report/Layout into plain JSON files (pages/, visuals/, reportExtensions.json) that can be edited freely. PBI Desktop validates on open, not via embedded hash.

**Why:** Discovered 2026-04-22 after 8+ failed attempts with different ZIP approaches. SecurityBindings (DPAPI blob) is NOT the hash — removing it doesn't help. The hash/checksum location is unknown but validated by PBI Desktop on file open.

**How to apply:** Never modify .pbix files programmatically. Always use .pbip format for report modifications. Workflow: (1) open .pbix in Desktop, (2) Save As .pbip, (3) edit JSON files, (4) reopen .pbip in Desktop, (5) publish or Save As .pbix.

## .pbip format conventions
- Page schema: `https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.1.0/schema.json`
- Visual schema: `https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.8.0/schema.json`
- `reportExtensions.json` replaces `modelExtensions` in config — measures use `dataType: "Double"` (string, not int 3)
- No `formatInformation` wrapper — just `formatString` directly
- `displayOption: "FitToPage"` (string, not int 1)
- Each visual is a separate file: `pages/{pageId}/visuals/{visualId}/visual.json`
- Position uses `tabOrder` field alongside x/y/z/width/height

## TREATAS with island tables (no relationships)
When a table has no relationships to any other table (island table), TREATAS can bridge it via a computed column. If the island table has a timestamp string but no date_key, derive it: `INT(SUBSTITUTE(LEFT('Table'[timestamp_col], 10), "-", ""))` converts "2026-04-13T..." → 20260413.

Pattern: `TREATAS(SELECTCOLUMNS(FILTER('island_table', ...), "dk", INT(SUBSTITUTE(LEFT('island_table'[timestamp], 10), "-", ""))), 'target_table'[date_key])`

**Critical for page-level consistency:** If ALL visuals on a page reference only the island table, the slicer MUST use a column from that table (not from an unrelated dim table). A `dim_date.full_date` slicer won't filter island-table visuals. Use the timestamp column instead.

**Why:** Discovered 2026-04-22 when health_checks (no date_key, no dim_date relationship) was used with dim_date slicers and bar chart categories — slicer did nothing, bar chart showed wrong data.

## Fabric DirectQuery — M query folding is STRICT (CRITICAL)
In Fabric DirectQuery (Lakehouse SQL endpoint), ALL M query steps must fold to native SQL. `Table.AddColumn`, `Table.SelectColumns`, `Table.TransformColumns`, and any computed/derived columns in M will fail with: **"Unable to convert an M query in table 'X' into a native source query."**

**Only safe M pattern for Fabric DirectQuery:**
```m
let
    Source = Sql.Database("server", "database"),
    Table = Source{[Schema="schema",Item="table"]}[Data]
in
    Table
```

**Why:** Discovered 2026-04-29 when adding `year_month` via `Table.AddColumn` and selecting columns via `Table.SelectColumns` both failed. Fabric SQL endpoint requires complete query folding — no client-side computation.

**How to apply:** If you need a derived column (e.g., `year_month` from `month` + `year`), add it in the ETL pipeline (Python/DuckDB) and write it to the Delta table. Then wait for Fabric Lakehouse to detect the schema change before referencing it in TMDL. Never compute it in M.

## Fabric Lakehouse shortcuts don't auto-detect Delta schema changes
When you add new columns to an existing Delta table via `write_deltalake(schema_mode="overwrite")`, the Fabric Lakehouse shortcut does NOT immediately detect the new columns. The SQL endpoint still reports the old schema (e.g., `Invalid column name 'year_month'`).

**Fix:** User must go to Fabric portal → Lakehouse → manually refresh the table schema. Alternatively, delete and recreate the shortcut.

**Why:** Discovered 2026-04-29 when `year_month` existed in the Delta table metadata but Fabric returned "Invalid column name". The Delta table was correct (verified via DuckDB on VM), but Fabric's schema cache was stale.

**How to apply:** After any Delta schema change, don't reference the new column in TMDL until Fabric has synced. Plan for a manual Fabric portal step after ETL deploys schema changes.

## Delta table schema changes need `schema_mode="overwrite"`
When adding new columns to an existing Delta table, `write_deltalake()` requires `schema_mode="overwrite"` (deltalake 1.5.0+). Without it, the write fails with a schema mismatch error (e.g., 38 columns vs 37 expected).

**Why:** Default `write_deltalake` enforces schema match. Adding `year_month` to dim_date (12 cols vs 11) and `date_key` to user_activity (38 vs 37) both failed until `schema_mode="overwrite"` was added.

## Ambiguous relationship paths from bidirectional cross-filter
Adding a new relationship can create an ambiguous path if an indirect path already exists through bidirectional cross-filter relationships. PBI errors with `PFE_XL_USERELATIONSHIP_AMBIGUOUS_PATH`.

**Example:** Adding `user_activity→dim_date` created a second path: `user_activity→job_runs↔health_checks→dim_date` (the `↔` is bidirectional `crossFilteringBehavior: bothDirections`). Fix: set one of the indirect relationships to `isActive: false`.

**How to apply:** Before adding a new relationship, trace ALL existing paths between the two tables (including through bidirectional relationships). If a second path exists, deactivate one of the intermediate relationships.

## Blob upload auth mode
`az storage blob upload --auth-mode login` can fail with permission errors on some storage accounts. Use `--auth-mode key` instead.

**Why:** Discovered 2026-04-29 when deploying scripts to `flkaienablement` blob. Login auth returned authorization error despite having RBAC access.

## Blank bars in PBI charts from orphan dimension keys
When PBI bar/donut charts show a blank bar, it means fact table records have a foreign key value with no matching dimension entry. The dimension lookup returns NULL for the display name. Common causes:
- **Model keys**: `_get_model_key()` fallback returns raw deployment name (e.g., `"claude-code"`) which isn't in DIM_MODELS. Fix: add catch-all entries to the dimension table.
- **Node keys**: Old fact records (Delta merge preserves history) may have keys from before the dimension was expanded. Fix: add catch-all entries + validate keys in Silver processing.

**How to apply:** When adding new LiteLLM gateway deployments or model configurations, always check that DIM_MODELS and DIM_NODES have matching entries. Add catch-all rows for any potential orphans.

## Other rules
- Never use bracket refs `[OtherMeasure]` in report-level measures — inline full DAX.
- Fabric Lakehouse tables named as `"<schema> <table>"` (space-separated). DAX needs single quotes: `SUM('llmUsage llm_usage'[col])`.
- In query Extension blocks, always use `DataType: 7` regardless of modelExtensions dataType.
