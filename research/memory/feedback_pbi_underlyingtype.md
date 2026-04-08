---
name: PBI type encoding and formatInformation rules
description: dataType 3 vs 6 (model-dependent), underlyingType 261=Double, format/currencyFormat must be null, Fabric table naming
type: feedback
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

## Other rules
- Never use bracket refs `[OtherMeasure]` in report-level measures — inline full DAX.
- Fabric Lakehouse tables named as `"<schema> <table>"` (space-separated). DAX needs single quotes: `SUM('llmUsage llm_usage'[col])`.
- In query Extension blocks, always use `DataType: 7` regardless of modelExtensions dataType.
