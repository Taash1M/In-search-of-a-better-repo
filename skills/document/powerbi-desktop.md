---
name: powerbi-desktop
description: "Programmatically create and modify Power BI Desktop (.pbix/.pbip) files — inject DAX measures, build report pages with visuals, manage semantic models, connect to Analysis Services, handle SecurityBindings/DPAPI. CRITICAL: .pbix modification is IMPOSSIBLE in PBI 2.153+ — must use .pbip format. Use when creating .pbix/.pbip files from scratch, injecting measures into existing reports, building visual layouts programmatically, or automating Power BI Desktop workflows. Trigger on: 'pbix', 'pbip', 'Power BI', 'DAX measure', 'report page', 'Power BI Desktop', 'semantic model', '.pbix file', '.pbip file'."
---

# Power BI Desktop Automation Skill

## Overview
This skill covers programmatic creation and modification of Power BI Desktop (.pbix) files, including injecting DAX measures, building report pages with visuals, and connecting to the local Analysis Services instance.

## .pbix File Format

### Structure
- A .pbix file is a **ZIP archive** using the **OPC (Open Packaging Convention)** format — the same format used by .docx, .xlsx, .pptx
- PBI Desktop uses .NET's `System.IO.Packaging` to create these files
- Key internal files for a **live connection** report:
  - `Version` — version string in UTF-16-LE (e.g., `1.28`)
  - `[Content_Types].xml` — OPC content type declarations (UTF-8 with BOM `\xef\xbb\xbf`)
  - `Connections` — JSON defining the remote dataset connection (UTF-8)
  - `Report/Layout` — JSON containing pages, visuals, config, and **report-level measures** (UTF-16-LE, NO BOM)
  - `Settings` — JSON report settings (UTF-16-LE)
  - `Metadata` — JSON metadata (UTF-16-LE)
  - `DiagramLayout` — JSON model diagram positions (UTF-16-LE, NO BOM). Only present after PBI Desktop opens and saves.
  - `SecurityBindings` — **DPAPI-encrypted content hash** (see critical section below)
  - `Report/StaticResources/SharedResources/BaseThemes/*.json` — theme file

### Critical: Import Mode vs Live Connection
- For **import mode** .pbix files, report-level measures go in `DataModelSchema`
- For **live connection** .pbix files, there is NO `DataModelSchema` file
- Report-level measures are stored in `Report/Layout` -> `config` -> `modelExtensions`
- Injecting a DataModelSchema into a live connection .pbix will be silently ignored

### SecurityBindings — CRITICAL DISCOVERY

**`SecurityBindings` contains a DPAPI-encrypted hash of the report content.** When you modify the `Report/Layout` content, the hash no longer matches, and PBI Desktop rejects the file as **"corrupted or was created by an unrecognized version."**

**Symptoms of SecurityBindings mismatch:**
- File opens fine if you write the EXACT same bytes back (hash unchanged)
- File rejected as "corrupted" if you write ANY different content (even 1 byte)
- The error is generic — PBI Desktop does not say "SecurityBindings mismatch"
- OPC package structure is valid, JSON is valid, ZIP metadata is correct — but PBI still rejects it

**Solution: Remove SecurityBindings when modifying layout content.** PBI Desktop recreates it when the user saves the file. For live connection reports without RLS, this is safe.

**How the discovery was made:** Writing identical bytes back via OPC worked, but writing different content failed. Even a straight copy of a previously-working backup failed after PBI Desktop received an update that made the check stricter. Removing SecurityBindings (and its `[Content_Types].xml` entry) resolved the issue completely.

### ZIP Metadata Requirements
PBI Desktop creates ZIP entries with specific metadata in the **central directory**:

| Property | Required Value | Notes |
|----------|---------------|-------|
| `create_version` | `45` (ZIP 4.5) | In central directory, not local header |
| `external_attr` | `0` | Python zipfile sets `25165824` — must be 0 |
| `compress_type` | `8` (DEFLATED) | Standard |
| `create_system` | `0` (MS-DOS) | Standard |

Each local file header also contains a 28-byte OPC extra field: `20a2180028a014000000000000000000000000000000000000000000`

### Recommended Approach: Binary ZIP Rebuild

**Do NOT use .NET's System.IO.Packaging or Python's zipfile for WRITING.** Both produce files that PBI Desktop may reject. Instead, use **raw binary ZIP manipulation**:

1. Read the original .pbix as raw bytes
2. Parse the ZIP structure (local file headers + central directory)
3. Rebuild the ZIP byte-by-byte, replacing only `Report/Layout` content
4. Skip `SecurityBindings` entry entirely
5. Update CRC, compressed size, uncompressed size in both local header and central directory
6. Recalculate central directory offsets

This preserves ALL original metadata (timestamps, extra fields, compression, flags) exactly.

```python
"""
Binary ZIP rebuild for .pbix files.
Replaces Report/Layout and removes SecurityBindings.
"""
import struct, zlib, os, zipfile, json

def read_u16(data, offset): return struct.unpack_from('<H', data, offset)[0]
def read_u32(data, offset): return struct.unpack_from('<I', data, offset)[0]
def write_u16(data, offset, value): struct.pack_into('<H', data, offset, value)
def write_u32(data, offset, value): struct.pack_into('<I', data, offset, value)

def deflate(data):
    c = zlib.compressobj(zlib.Z_DEFAULT_COMPRESSION, zlib.DEFLATED, -15)
    return c.compress(data) + c.flush()

def crc32(data):
    return zlib.crc32(data) & 0xFFFFFFFF

def rebuild_pbix(original_bytes, new_layout_bytes):
    """
    Rebuild a .pbix, replacing Report/Layout and removing SecurityBindings.
    Preserves all other entries byte-for-byte.
    """
    eocd_offset = original_bytes.rfind(b'PK\x05\x06')
    cd_offset = read_u32(original_bytes, eocd_offset + 16)
    cd_count = read_u16(original_bytes, eocd_offset + 10)

    # Parse central directory
    entries = []
    pos = cd_offset
    for _ in range(cd_count):
        fname_len = read_u16(original_bytes, pos + 28)
        extra_len = read_u16(original_bytes, pos + 30)
        comment_len = read_u16(original_bytes, pos + 32)
        filename = original_bytes[pos + 46:pos + 46 + fname_len].decode('utf-8')
        cd_entry_size = 46 + fname_len + extra_len + comment_len
        entries.append({
            'filename': filename,
            'cd_raw': bytearray(original_bytes[pos:pos + cd_entry_size]),
            'local_offset': read_u32(original_bytes, pos + 42),
        })
        pos += cd_entry_size

    # Rebuild
    output = bytearray()
    new_offsets = {}
    kept = 0

    for entry in entries:
        # Skip SecurityBindings
        if entry['filename'] == 'SecurityBindings':
            continue

        lo = entry['local_offset']
        l_fname_len = read_u16(original_bytes, lo + 26)
        l_extra_len = read_u16(original_bytes, lo + 28)
        l_header_size = 30 + l_fname_len + l_extra_len
        l_comp_size = read_u32(original_bytes, lo + 18)
        local_header = bytearray(original_bytes[lo:lo + l_header_size])
        comp_data = original_bytes[lo + l_header_size:lo + l_header_size + l_comp_size]

        if entry['filename'] == 'Report/Layout':
            new_crc = crc32(new_layout_bytes)
            new_comp = deflate(new_layout_bytes)
            write_u32(local_header, 14, new_crc)
            write_u32(local_header, 18, len(new_comp))
            write_u32(local_header, 22, len(new_layout_bytes))
            write_u32(entry['cd_raw'], 16, new_crc)
            write_u32(entry['cd_raw'], 20, len(new_comp))
            write_u32(entry['cd_raw'], 24, len(new_layout_bytes))
            comp_data = new_comp

        new_offsets[entry['filename']] = len(output)
        output.extend(local_header)
        output.extend(comp_data)
        kept += 1

    # Central directory
    cd_start = len(output)
    for entry in entries:
        if entry['filename'] == 'SecurityBindings':
            continue
        write_u32(entry['cd_raw'], 42, new_offsets[entry['filename']])
        output.extend(entry['cd_raw'])
    cd_end = len(output)

    # EOCD
    eocd = bytearray(original_bytes[eocd_offset:eocd_offset + 22])
    write_u16(eocd, 8, kept)
    write_u16(eocd, 10, kept)
    write_u32(eocd, 12, cd_end - cd_start)
    write_u32(eocd, 16, cd_start)
    output.extend(eocd)

    return bytes(output)

# Usage:
# base_bytes = open('fresh_base.pbix', 'rb').read()
# layout_bytes = open('modified_layout.bin', 'rb').read()  # UTF-16-LE encoded JSON
# result = rebuild_pbix(base_bytes, layout_bytes)
# open('output.pbix', 'wb').write(result)
```

### Fresh Base File Strategy

Always keep a **fresh base .pbix** created by PBI Desktop:
1. Open PBI Desktop
2. Connect to the target dataset (Get Data > Power BI datasets)
3. Save immediately without changes
4. Keep this file as `fresh_base.pbix` — never modify it directly

Use this as the template for all programmatic rebuilds. It guarantees:
- Correct Version string for the current PBI Desktop version
- Valid Connections file with proper dataset reference
- Correct `[Content_Types].xml` entries
- Proper ZIP metadata and OPC extra fields

### Reading .pbix Files
Python's `zipfile` module is fine for **reading** .pbix files:
```python
import zipfile, json

with zipfile.ZipFile('report.pbix', 'r') as z:
    layout_raw = z.read('Report/Layout')
    layout_text = layout_raw.decode('utf-16-le')
    layout = json.loads(layout_text)
    config = json.loads(layout['config'])
```

## Report-Level Measures in Live Connection Reports

### Storage Location
Measures are stored in: `Report/Layout` -> JSON -> `config` (string) -> parsed JSON -> `modelExtensions`

### modelExtensions Structure
```json
{
  "modelExtensions": [{
    "name": "extension",
    "entities": [
      {
        "name": "TableName",
        "extends": "TableName",
        "measures": [
          {
            "name": "Measure Name",
            "dataType": 6,
            "expression": "VAR _today = TODAY()\nRETURN\nCALCULATE(...)",
            "errorMessage": null,
            "hidden": false,
            "formulaOverride": null,
            "formatInformation": {
              "formatString": "G",
              "format": "General",
              "thousandSeparator": false,
              "currencyFormat": null,
              "dateTimeCustomFormat": null
            },
            "displayFolder": "Price History"
          }
        ]
      }
    ]
  }]
}
```

### Measure Definition Fields
| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Measure name (must be unique within the entity) |
| `dataType` | int | Use `6` for measures to be visible. PBI Desktop's UI creates with `3` but `6` works for programmatic injection |
| `expression` | string | DAX expression as a single string. Multi-line uses `\n` |
| `errorMessage` | null/string | Set to `null` for new measures |
| `hidden` | bool | Whether the measure is hidden in the Fields pane |
| `formulaOverride` | null/string | Set to `null` |
| `formatInformation` | object | Display formatting (see below) |
| `displayFolder` | string | Folder name for grouping in Fields pane. Include this — it helps with visibility |

### dataType Values
- `dataType: 3` — PBI Desktop's default when creating via UI. **Use this for DirectQuery/Composite models** (reports with a `DataModel` file, e.g., Fabric Lakehouse, SQL Server). In these models, PBI interprets `dataType` as the SSAS data type enum, and `6` maps to a Date/DateTime type — causing chart axes to show "h:mm:ssfff tt" instead of numeric values.
- `dataType: 6` — Use for **live connection** reports only (reports with a `Connections` file, no `DataModel`). With `3`, programmatic measures may be invisible in the Fields pane in live connection mode.
- **How to tell which to use:** Check the base .pbix ZIP contents. If it has `DataModel` → use `3`. If it has `Connections` → use `6`.
- Always pair with `displayFolder` for best results
- In query Extension blocks, always use `DataType: 7` regardless of modelExtensions dataType

### Format Information Options
```json
// General (default)
{"formatString": "G", "format": "General", "thousandSeparator": false, "currencyFormat": null, "dateTimeCustomFormat": null}

// Currency (format and currencyFormat MUST be null in v2.152+ — they are enums, not strings)
{"formatString": "$#,##0.00", "thousandSeparator": true, "currencyFormat": null, "dateTimeCustomFormat": null}

// Percentage
{"formatString": "0.0 %;-0.0 %;0.0 %", "thousandSeparator": false, "currencyFormat": null, "dateTimeCustomFormat": null}

// Whole Number
{"formatString": "#,##0", "thousandSeparator": true, "currencyFormat": null, "dateTimeCustomFormat": null}

// Currency — max 3 decimal places (no trailing zeros)
{"formatString": "$#,##0.###", "thousandSeparator": true, "currencyFormat": null, "dateTimeCustomFormat": null}

// Date (short)
{"formatString": "dd\\-MMM\\-yy", "thousandSeparator": false, "currencyFormat": null, "dateTimeCustomFormat": "dd\\-MMM\\-yy"}
```

### Number Format Strings (dataTransforms)

In `dataTransforms.selects[].format` and `dataTransforms.queryMetadata.Select[].Format`, use standard .NET format strings:

| Pattern | Example Output | Use Case |
|---------|---------------|----------|
| `$#,##0.00` | $1,234.56 | Currency with exactly 2 decimals |
| `$#,##0.###` | $1,234.5 or $1,234.567 | Currency with up to 3 decimals (no trailing zeros) |
| `$#,##0.000` | $1,234.560 | Currency with exactly 3 decimals (with trailing zeros) |
| `#,##0.###` | 1,234.567 | Number with up to 3 decimals |
| `0` | 1235 | Integer (no decimals) |
| `0.0 %;-0.0 %;0.0 %` | 45.2 % | Percentage with 1 decimal |
| `dd\-MMM\-yy` | 15-Jan-26 | Short date |
| `G` | (varies) | General (PBI default) |

**Key:** `0` = required digit (shows 0 if no value), `#` = optional digit (shows nothing if no value). Use `#` after the decimal point for "max N decimals" behavior.

### Entity Mapping
Each entity in `modelExtensions` maps to a table in the remote semantic model:
- `name`: The table name (must match exactly, case-sensitive)
- `extends`: Same as `name` — indicates this entity extends the remote table
- `measures`: Array of measure definitions

Measures that reference a specific table's columns should be placed on that table's entity.

## Report/Layout JSON Structure

### Encoding
- **UTF-16-LE** (Little Endian), **NO BOM** (no `\xff\xfe` prefix)
- First bytes should be `7b 00 22 00` (which is `{"` in UTF-16-LE)
- Python round-trip (`json.loads` then `json.dumps` with `separators=(",",":")` and `ensure_ascii=False`) produces byte-identical output to PBI Desktop's serialization

### Top-Level Structure
```json
{
  "id": 0,
  "resourcePackages": [...],
  "sections": [...],
  "config": "<JSON string>",
  "layoutOptimization": 0
}
```

Note: `config` is a **JSON string inside JSON** — must be serialized as a string, not a nested object.

### Section (Page) Structure
```json
{
  "id": 0,
  "name": "unique_hex_id_20chars",
  "displayName": "Page Name",
  "filters": "[]",
  "ordinal": 0,
  "visualContainers": [],
  "config": "{}",
  "displayOption": 1,
  "width": 1280,
  "height": 720
}
```

### Config Structure (parsed from the config string)
```json
{
  "version": "5.69",
  "themeCollection": {
    "baseTheme": {
      "name": "CY25SU12",
      "type": 2,
      "version": {"visual": "2.5.0", "report": "3.1.0", "page": "2.3.0"}
    }
  },
  "activeSectionIndex": 0,
  "modelExtensions": [...],
  "defaultDrillFilterOtherVisuals": true,
  "linguisticSchemaSyncVersion": 0,
  "settings": {
    "useNewFilterPaneExperience": true,
    "allowChangeFilterTypes": true,
    "useStylableVisualContainerHeader": true,
    "queryLimitOption": 6,
    "useEnhancedTooltips": true,
    "exportDataMode": 1,
    "useDefaultAggregateDisplayName": true
  }
}
```

**IMPORTANT:** When modifying config, preserve ALL existing keys. Only modify the `modelExtensions` key.

**CRITICAL:** `modelExtensions` must be placed inside this config object (which is a JSON string at `layout["config"]`), NOT as a top-level key on the layout itself. Writing `layout["modelExtensions"] = [...]` is a silent no-op — PBI ignores it and visuals show `Missing_References` errors. The correct pattern:
```python
config = json.loads(layout["config"])
config["modelExtensions"] = [...]  # Add/modify measures here
layout["config"] = json.dumps(config, separators=(",",":"), ensure_ascii=False)
```

## Visual Container Patterns

Every non-textbox visual requires THREE fields: `config`, `query`, and `dataTransforms`. Missing any of these causes visuals to show errors or blank content.

### Visual Container Skeleton
```json
{
  "x": 20, "y": 100, "z": 1000,
  "width": 300, "height": 200,
  "config": "<JSON string>",
  "query": "<JSON string>",
  "dataTransforms": "<JSON string>",
  "filters": "[]"
}
```

All of `config`, `query`, `dataTransforms`, and `filters` are **JSON strings** (serialized with `json.dumps`).

**CRITICAL — Dual Position Storage:** The visual's position/size is stored in TWO places that MUST be kept in sync:
1. Top-level: `vc.x`, `vc.y`, `vc.width`, `vc.height`, `vc.z`
2. Inside config: `config.layouts[0].position.x/y/width/height/z` (this is the **authoritative** source PBI reads)

When creating or resizing visuals, the `config` JSON string must include a `layouts` array:
```json
{
  "name": "unique_20char_hex_id",
  "layouts": [{"id": 0, "position": {"x": 20, "y": 100, "z": 1000, "width": 300, "height": 200, "tabOrder": 1000}}],
  "singleVisual": { ... }
}
```
If you only set the top-level fields without updating `config.layouts[0].position`, PBI Desktop will ignore your changes. See Gotcha #18.

### Pattern 1: Textbox (no query/dataTransforms needed)

Textboxes only need `config`. They do NOT need `query` or `dataTransforms`.

```json
// config.singleVisual
{
  "visualType": "textbox",
  "objects": {
    "general": [{
      "properties": {
        "paragraphs": [{
          "textRuns": [{
            "value": "Title Text",
            "textStyle": {
              "fontFamily": "Segoe UI",
              "fontSize": "16.00pt",
              "fontColor": "#1A3A5C",
              "fontWeight": "bold"
            }
          }]
        }]
      }
    }]
  }
}
```

### Pattern 2: Card with Report-Level Measure

Cards referencing report-level measures require `Schema: "extension"` in the From clause and an Extension block with the DAX expression in the query.

**config.singleVisual.prototypeQuery:**
```json
{
  "Version": 2,
  "From": [{"Name": "p", "Entity": "TableName", "Schema": "extension", "Type": 0}],
  "Select": [{
    "Measure": {"Expression": {"SourceRef": {"Source": "p"}}, "Property": "MeasureName"},
    "Name": "TableName.MeasureName",
    "NativeReferenceName": "MeasureName"
  }]
}
```

**query (SemanticQueryDataShapeCommand):**
```json
{
  "Query": {
    "Version": 2,
    "From": [{"Name": "p", "Entity": "TableName", "Schema": "extension", "Type": 0}],
    "Select": [{
      "Measure": {"Expression": {"SourceRef": {"Source": "p"}}, "Property": "MeasureName"},
      "Name": "TableName.MeasureName",
      "NativeReferenceName": "MeasureName"
    }]
  },
  "Binding": {
    "Primary": {"Groupings": [{"Projections": [0]}]},
    "DataReduction": {"DataVolume": 3, "Primary": {"Top": {}}},
    "Version": 1
  },
  "ExecutionMetricsKind": 1,
  "Extension": {
    "Version": 0,
    "Name": "extension",
    "Entities": [{
      "Extends": "TableName",
      "Name": "TableName",
      "Measures": [{
        "Name": "MeasureName",
        "Expression": "DAX expression here",
        "DataType": 7
      }]
    }]
  }
}
```

**dataTransforms selects:**
```json
{
  "displayName": "MeasureName",
  "format": "G",
  "queryName": "TableName.MeasureName",
  "roles": {"Values": true},
  "type": {"category": null, "underlyingType": 261},
  "expr": {
    "Measure": {
      "Expression": {"SourceRef": {"Schema": "extension", "Entity": "TableName"}},
      "Property": "MeasureName"
    }
  }
}
```

**Key points for measures in visuals:**
- `"Schema": "extension"` in From clause — required for report-level measures
- `"NativeReferenceName"` in Select — required
- Extension block contains actual DAX expression with `DataType: 7` (maps from modelExtensions `dataType: 6`)
- dataTransforms expr uses `SourceRef` with both `Schema` and `Entity`
- `underlyingType: 261` for numeric measures (Double = category 1 + type 5)

### Pattern 3: Slicer (Dropdown)

```json
// query Binding
{
  "Primary": {"Groupings": [{"Projections": [0]}]},
  "DataReduction": {"DataVolume": 4, "Primary": {"Window": {}}},
  "IncludeEmptyGroups": true,
  "Version": 1
}
```

### Pattern 4: Slicer (Between/Date Range)

Query has 3 Selects: the column + Min aggregation + Max aggregation. Binding Projections uses `[1, 2]`.

```json
// Select entries
[
  {"Column": {"Expression": {"SourceRef": {"Source": "s"}}, "Property": "StartDate"}, "Name": "..."},
  {"Aggregation": {"Expression": {"Column": {"Expression": {"SourceRef": {"Source": "s"}}, "Property": "StartDate"}}, "Function": 3}, "Name": "Min(...)"},
  {"Aggregation": {"Expression": {"Column": {"Expression": {"SourceRef": {"Source": "s"}}, "Property": "StartDate"}}, "Function": 4}, "Name": "Max(...)"}
]
```

### Pattern 5: Area/Line Chart

```json
// query Binding
{
  "Primary": {"Groupings": [{"Projections": [0, 1]}]},
  "DataReduction": {"DataVolume": 4, "Primary": {"BinnedLineSample": {}}},
  "Version": 1
}
```

- Use `BinnedLineSample` data reduction (not `Top` or `Window`)
- Projections: `[0]` = Category (X-axis), `[1]` = Y value
- For line charts, add `lineStyles` with `showMarker: true` in vcObjects

### Pattern 6: Table with Columns AND Measures

Tables that show both regular columns and report-level measures need **two From entries**: one regular and one with `Schema: "extension"`.

```json
// query From
[
  {"Name": "t", "Entity": "TableName", "Type": 0},
  {"Name": "t1", "Entity": "TableName", "Schema": "extension", "Type": 0}
]

// query Binding
{
  "Primary": {"Groupings": [{"Projections": [0, 1, 2, 3, 4]}]},
  "DataReduction": {"DataVolume": 3, "Primary": {"Window": {"Count": 500}}},
  "Subtotal": 1,
  "Version": 1
}
```

- Column selects use the `"t"` source (regular)
- Measure selects use the `"t1"` source (extension)
- Extension block must include ALL measures with their DAX expressions
- Order dependencies first in the Extension.Entities.Measures array

### Pattern 6b: Flat Table with Pivoted Period Measures (Live Connection)

When you need a matrix-like layout where each row = one Item + Price List and columns spread across time periods, **do NOT use `pivotTable` visual type with live connections** — PBI Desktop cannot bind fields to Rows/Columns/Values wells via JSON manipulation. Instead, use a flat `tableEx` with numbered Extension measures (P1 Start, P1 End, P1 Diff, ..., PN Start, PN End, PN Diff, Net Change, # Changes).

**Why this works:** Each "period" is a separate Extension measure using `TOPN(N, dates, StartDate, ASC)` to get the Nth chronological date. PBI treats them as regular table columns.

**Critical requirements (all 3 must be met):**
1. Measures must be defined in `layout.config.modelExtensions` (report-level) — PBI validates prototypeQuery references against this
2. Measures must also be in the query's `Extension` block — Analysis Services executes DAX from here
3. All four visual binding fields must be synchronized: `prototypeQuery`, `projections`, `query`, `dataTransforms`

**DAX pattern for Nth Start Date:**
```dax
// Gets the Nth earliest StartDate for each Item + PriceList combination
VAR _dates = CALCULATETABLE(
    VALUES('Table'[StartDate]),
    ALLEXCEPT('Table', 'Table'[MSIB1Item], 'Table'[PriceListName])
)
RETURN
    IF(
        N <= COUNTROWS(_dates),
        MAXX(
            TOPN(N, _dates, 'Table'[StartDate], ASC),
            'Table'[StartDate]
        )
    )
```

**DAX pattern for Nth Price Diff:**
```dax
// Gets price difference at the Nth period (new price minus previous price)
VAR _dates = CALCULATETABLE(
    VALUES('Table'[StartDate]),
    ALLEXCEPT('Table', 'Table'[MSIB1Item], 'Table'[PriceListName])
)
VAR _nthStart =
    IF(N <= COUNTROWS(_dates),
        MAXX(TOPN(N, _dates, 'Table'[StartDate], ASC), 'Table'[StartDate]))
VAR _nthPrice =
    CALCULATE(MAX('Table'[ItemPrice]),
        ALLEXCEPT('Table', 'Table'[MSIB1Item], 'Table'[PriceListName]),
        'Table'[StartDate] = _nthStart)
VAR _prevEnd =
    CALCULATE(MAX('Table'[EndDate]),
        ALLEXCEPT('Table', 'Table'[MSIB1Item], 'Table'[PriceListName]),
        'Table'[EndDate] < _nthStart)
VAR _prevPrice =
    CALCULATE(MAX('Table'[ItemPrice]),
        ALLEXCEPT('Table', 'Table'[MSIB1Item], 'Table'[PriceListName]),
        'Table'[EndDate] = _prevEnd)
RETURN
    IF(ISBLANK(_prevPrice) || ISBLANK(_nthStart), BLANK(), _nthPrice - _prevPrice)
```

**DAX pattern for Net Change (cumulative):**
```dax
VAR _dates = CALCULATETABLE(
    VALUES('Table'[StartDate]),
    ALLEXCEPT('Table', 'Table'[MSIB1Item], 'Table'[PriceListName])
)
VAR _latestStart = MAXX(_dates, 'Table'[StartDate])
VAR _firstStart = MINX(_dates, 'Table'[StartDate])
VAR _latestPrice =
    CALCULATE(MAX('Table'[ItemPrice]),
        ALLEXCEPT('Table', 'Table'[MSIB1Item], 'Table'[PriceListName]),
        'Table'[StartDate] = _latestStart)
VAR _firstPrice =
    CALCULATE(MAX('Table'[ItemPrice]),
        ALLEXCEPT('Table', 'Table'[MSIB1Item], 'Table'[PriceListName]),
        'Table'[StartDate] = _firstStart)
RETURN
    IF(ISBLANK(_latestPrice) || ISBLANK(_firstPrice) || _latestStart = _firstStart,
        BLANK(), _latestPrice - _firstPrice)
```

**Visual binding — all four fields must be updated:**

```python
# 1. prototypeQuery — PBI validates field refs against modelExtensions
sv['prototypeQuery'] = {
    "Version": 2,
    "From": [
        {"Name": "t", "Entity": entity, "Type": 0},
        {"Name": "t1", "Entity": entity, "Schema": "extension", "Type": 0}
    ],
    "Select": [
        # Columns
        {"Column": {"Expression": {"SourceRef": {"Source": "t"}}, "Property": "MSIB1Item"},
         "Name": f"{entity}.MSIB1Item"},
        {"Column": {"Expression": {"SourceRef": {"Source": "t"}}, "Property": "PriceListName"},
         "Name": f"{entity}.PriceListName"},
        # Extension measures (one per period column)
        {"Measure": {"Expression": {"SourceRef": {"Source": "t1"}}, "Property": "P1 Start"},
         "Name": f"{entity}.P1 Start", "NativeReferenceName": "P1 Start"},
        # ... repeat for all period measures
    ]
}

# 2. projections — maps fields to visual wells
sv['projections'] = {
    "Values": [{"queryRef": name, "active": True} for name in all_field_names]
}

# 3. query — actual DAX execution (includes Extension block)
# Same as Pattern 6, but with full Extension.Entities.Measures list

# 4. dataTransforms — display names, formats, ordering
# Same as Pattern 6, with format strings for dates/currencies
```

**Registering measures in modelExtensions:**
```python
# Add period measures to the appropriate entity in modelExtensions
config = json.loads(layout['config'])
for entity_def in config['modelExtensions'][0]['entities']:
    if entity_def['name'] == entity_name:
        entity_def['measures'].append({
            "name": "P1 Start Americas",
            "dataType": 4,    # 4 for dates
            "expression": "<DAX expression>"
        })
        entity_def['measures'].append({
            "name": "P1 Diff Americas",
            "dataType": 7,    # 7 for currency/decimal
            "expression": "<DAX expression>"
        })
layout['config'] = json.dumps(config, ensure_ascii=False, separators=(',', ':'))
```

**Result:** A flat table showing `Item | Price List | Start 1 | End 1 | Diff 1 | ... | Start N | End N | Diff N | Net Change | # Changes` — one row per Item + Price List combination.

### Pattern 7: Bar Chart with Aggregation

```json
// query Binding
{
  "Primary": {"Groupings": [{"Projections": [0]}]},
  "Secondary": {"Groupings": [{"Projections": [1]}]},
  "DataReduction": {"DataVolume": 4, "Primary": {"Sample": {}}, "Secondary": {"Top": {}}},
  "Version": 1
}
```

### Pattern 8: Bar Chart with Measure

Same as Pattern 7 but with `Schema: "extension"` in From and an Extension block (similar to card pattern).

### Visual Name and Z-Order Conventions
- Visual names: 20-character hex strings from `uuid.uuid4().hex[:20]`
- Z-order: increment by 1000 per visual, reset per page
- Section names: also 20-character hex strings
- Section IDs: sequential integers starting from 0

## Complete Workflow: Build Report with Visuals

### End-to-End Pipeline

```
1. Create fresh_base.pbix in PBI Desktop (connect to dataset, save, close)
2. Read fresh_base layout via Python zipfile (READ only)
3. Build new layout JSON with:
   a. Measures in config.modelExtensions
   b. Sections with visualContainers (each having config + query + dataTransforms)
4. Encode layout as UTF-16-LE (no BOM)
5. Rebuild .pbix using binary ZIP, replacing Report/Layout and removing SecurityBindings
6. Open in PBI Desktop to verify
```

### Python Layout Preparation
```python
import json, zipfile

# Read base layout
with zipfile.ZipFile('fresh_base.pbix', 'r') as z:
    layout = json.loads(z.read('Report/Layout').decode('utf-16-le'))

# Modify layout (add measures, pages, visuals)
config = json.loads(layout['config'])
config['modelExtensions'] = [...]  # Add measures
layout['config'] = json.dumps(config, ensure_ascii=False, separators=(',', ':'))
layout['sections'] = [...]  # Add pages with visuals

# Encode
output = json.dumps(layout, ensure_ascii=False, separators=(',', ':')).encode('utf-16-le')
open('layout_modified.bin', 'wb').write(output)
```

### Binary Injection
```python
base_bytes = open('fresh_base.pbix', 'rb').read()
layout_bytes = open('layout_modified.bin', 'rb').read()
result = rebuild_pbix(base_bytes, layout_bytes)  # Function defined above
open('output.pbix', 'wb').write(result)
```

## Key Gotchas (Ranked by Pain Level)

1. **SecurityBindings MUST be removed** when changing Report/Layout content. It contains a DPAPI content hash. PBI Desktop rejects the file as "corrupted" if the hash doesn't match. Remove the entry entirely from the ZIP.
2. **Use binary ZIP rebuild** — not OPC, not Python zipfile writer. Copy original bytes, replace only Report/Layout compressed data, skip SecurityBindings.
3. **Every non-textbox visual needs `config` + `query` + `dataTransforms`** — missing any one causes blank/error visuals.
4. **Report-level measures need `Schema: "extension"`** in query From clauses and `NativeReferenceName` in Select.
5. **Extension blocks in queries must contain the actual DAX** — the Expression field must have the full DAX text, not just a reference.
6. **`dataType: 6`** in modelExtensions maps to **`DataType: 7`** in query Extension blocks.
7. **config, query, dataTransforms, filters** are all **JSON-in-JSON** — serialize with `json.dumps`, not as nested objects.
8. **Report/Layout encoding** is UTF-16-LE without BOM.
9. **Keep a fresh_base.pbix** — create it by connecting to the dataset in PBI Desktop and saving immediately. Use as the base for all rebuilds.
10. **PBI Desktop must be closed** before modifying the .pbix file.
11. **Python zipfile is fine for READING** .pbix but NOT for writing.
12. **Write PowerShell to .ps1 files** — don't pass inline via bash (variable mangling with `$`).
13. **NEVER use inter-measure bracket references** — see "Critical: No Inter-Measure References" below. ALL measures in both `modelExtensions` AND Extension blocks must be self-contained DAX (no `[OtherMeasure]` refs).
14. **Preserve all existing config keys** when modifying layout — only change what you need.
15. **prototypeQuery + projections MUST be synchronized with query + dataTransforms** when changing visual field bindings. PBI Desktop uses `config.singleVisual.prototypeQuery` and `config.singleVisual.projections` as the AUTHORITATIVE source for visual field definitions. Updating only `vc.query` and `vc.dataTransforms` is INSUFFICIENT — PBI ignores the query/dataTransforms and falls back to old columns from prototypeQuery. All four fields must be updated together.
16. **Extension measures MUST exist in `modelExtensions`** (report-level) for table/matrix visuals with live connections. PBI validates prototypeQuery field references against `layout.config.modelExtensions`. If a measure is defined only in a query-level Extension block but NOT in modelExtensions, PBI shows "Fields that need to be fixed" and lists all unresolvable measures. The query Extension block provides the DAX for execution; modelExtensions provides the registry for validation. Both must contain the measure.
17. **`pivotTable` (matrix) visual type does NOT work via JSON manipulation with live connections.** PBI Desktop cannot bind fields to the matrix Rows/Columns/Values wells from programmatic layout changes. The field wells show "Add data fields here" (empty). Use the flat `tableEx` approach with numbered period Extension measures instead (see Pattern 6b).
18. **Visual position/size must be set in BOTH locations.** Each visual container stores position in TWO places: the top-level `vc.x/y/width/height/z` AND inside `config.layouts[0].position.x/y/width/height/z`. **PBI Desktop uses `config.layouts[0].position` as the AUTHORITATIVE source.** Updating only the top-level fields has NO visible effect — PBI ignores them and reads from config. Always update both simultaneously:
    ```python
    def set_vc_pos(vc, x=None, y=None, width=None, height=None, z=None):
        if x is not None: vc['x'] = x
        if y is not None: vc['y'] = y
        if width is not None: vc['width'] = width
        if height is not None: vc['height'] = height
        if z is not None: vc['z'] = z
        cfg = json.loads(vc['config'])
        pos = cfg['layouts'][0]['position']
        if x is not None: pos['x'] = x
        if y is not None: pos['y'] = y
        if width is not None: pos['width'] = width
        if height is not None: pos['height'] = height
        if z is not None: pos['z'] = z
        vc['config'] = json.dumps(cfg, ensure_ascii=False, separators=(",",":"))
    ```
19. **`formatInformation` fields `format` and `currencyFormat` are strict enums** in PBI v2.152+. String values like `"Currency"` or `"$#,##0.00"` cause `ModelAuthoringHostService.UpdateModelExtensions` "wrong arg" errors. Set both to `null`. Only `formatString` (e.g., `"$#,##0.00"`) is needed for display. Safe pattern: `{"formatString": "$#,##0.00", "thousandSeparator": true, "currencyFormat": null, "dateTimeCustomFormat": null}`.
20. **Measure `underlyingType` must be 261 (Double), NOT 518 (DateTime).** PBI encodes types as `(category << 8) | valueType`. Category 1 = Numbers, Type 5 = Double → 261. Category 2 = Temporal, Type 6 = DateTime → 518. Using 518 causes chart Y-axes to display as "h:mm:ssfff tt" (time format) instead of numeric values. Cards may appear correct because they format single values using the format string, but chart axes derive their scale/labels from underlyingType.
21. **The `format` field in `formatInformation` is an enum.** PBI March 2026+ (v2.152+) rejects values like `"Currency"`, `"Percentage"`, `"WholeNumber"` with `Error converting value "Currency" to type 'Microsoft.PowerBI.Modeling.Contracts.Format'`. Omit the `format` field entirely — `formatString` alone (e.g. `"$#,##0.00"`) is sufficient for display.
22. **`dataType` in modelExtensions depends on model type.** For DirectQuery/Composite models (with `DataModel` file — Fabric Lakehouse, SQL Server), use `dataType: 3` (Decimal). For live connection reports (with `Connections` file), use `dataType: 6`. Using `6` in DirectQuery models causes PBI to interpret measures as DateTime, making chart axes show "h:mm:ssfff tt" instead of numeric values. Cards appear correct because they format single values, but chart axes derive type from `dataType`.
23. **Layout sizing: always run a visual sanity check.** After building the layout, iterate every visual container and verify: (a) no visual overflows the page (`x+w <= PAGE_W`, `y+h <= PAGE_H`), (b) adjacent visuals have at least 4px gap (no overlap), (c) card/label text fits within card width (keep measure names under 16 chars for 200px cards). Use a grid-based layout system with documented Y-band allocations (see example below). After generating, open in PBI Desktop and visually confirm — text truncation, chart title overlap, and table column clipping are invisible to code checks.
    ```python
    # Layout sanity check — add after building layout, before serialize
    for s in layout["sections"]:
        for i, vc in enumerate(s.get("visualContainers", [])):
            c = json.loads(vc.get("config", "{}"))
            pos = c.get("layouts", [{}])[0].get("position", {})
            x, y, w, h = pos.get("x", 0), pos.get("y", 0), pos.get("width", 0), pos.get("height", 0)
            if x + w > PAGE_W + 5:
                print(f"WARNING: visual {i} overflows right: x={x} w={w}")
            if y + h > PAGE_H + 5:
                print(f"WARNING: visual {i} overflows bottom: y={y} h={h}")
    ```
    **Layout grid pattern** — document Y-bands in a docstring at the top of each `build_page_*()` function:
    ```python
    def build_page_health():
        """Layout grid (1280x720):
            y=0-47:    Title banner
            y=50-104:  Slicer panel
            y=108-131: Explainer bar
            y=136-207: KPI cards (6 x 200px, 8px gap)
            y=214-393: Charts (2 side-by-side, 15px gap)
            y=398-399: Separator
            y=404-423: Section header
            y=428-715: Detail table
        """
    ```
24. **Pages are `sections`, NOT `pages`.** The layout JSON stores pages under `layout["sections"]`, not `layout["pages"]`. There is no `pages` key. Each section has `displayName`, `ordinal`, `visualContainers`, `config`, `width`, `height`. When adding a new page, append to `layout["sections"]` and set `ordinal` to the next sequential number.
25. **`modelExtensions` lives inside `layout["config"]` (a JSON string), NOT at the layout top level.** When modifying an existing .pbix, you must: (1) parse the config string: `config = json.loads(layout["config"])`, (2) modify `config["modelExtensions"]`, (3) serialize back: `layout["config"] = json.dumps(config, separators=(",",":"), ensure_ascii=False)`. Writing to `layout["modelExtensions"]` (top level) is silently ignored by PBI Desktop — measures won't resolve and visuals show `Missing_References` errors with "Fix this" badges on every card/chart.
26. **PyArrow `date32` causes empty PBI DirectLake slicers.** When writing dimension tables to Delta Lake, Python `datetime.date` objects infer as PyArrow `date32` type. Fabric Lakehouse imports `date32` as a Date type, but DirectLake slicers may show empty if the report column expects a string. Fix: convert dates to strings with `.strftime("%Y-%m-%d")` before writing, and use explicit `pa.schema([..., pa.field("full_date", pa.string())])` with `schema_mode="overwrite"` to force the Delta schema update.
27. **PBI Desktop overrides `underlyingType` from Fabric semantic model.** Even if you set `underlyingType: 1` (text) in a slicer's dataTransforms, PBI Desktop will override it to match the semantic model column type (e.g., 519 for DateTime) when connecting. **Strategy:** Set `underlying` to match what PBI will impose (519), and use `formatString` / `columnProperties` to control the display format (e.g., `"MMM-dd-yyyy"`). This prevents silent format conflicts.
28. **Slicer display format via `columnProperties`.** To override slicer item formatting, add `columnProperties` to the singleVisual config: `"columnProperties": {"table.column": {"displayName": "Label", "formatString": "MMM-dd-yyyy"}}`. Also pass the same format to the `_dt_select_column` `fmt` parameter in dataTransforms. Both are needed — `columnProperties` for the visual, `dataTransforms.selects.format` for data binding.
29. **Capture user's manual PBI Desktop positions.** When a user adjusts visual positions/sizes in PBI Desktop, extract positions from the saved .pbix (parse ZIP -> Report/Layout -> sections -> visualContainers -> config -> layouts[0].position). Update the generation script with exact `{x, y, width, height, z}` values. This prevents regeneration from overwriting the user's preferred layout. Always document the Y-band grid in a docstring.
30. **PBIX ZIP modification is IMPOSSIBLE in PBI 2.153+ (April 2026).** PBI Desktop validates Report/Layout content against an internal integrity check — any byte change (even 1 byte) causes `MashupValidationError: This file is corrupted`. This was proven exhaustively: raw byte surgery, Python zipfile, PowerShell .NET ZipFile, direct byte replacement — ALL fail. SecurityBindings removal does NOT help. **Fix: Use .pbip format.** Save As → Power BI Project from PBI Desktop. This decomposes Report/Layout into plain JSON files (pages/, visuals/, reportExtensions.json) that are freely editable. Workflow: (1) open .pbix in Desktop, (2) File → Save As → Power BI Project (.pbip), (3) edit JSON files directly, (4) reopen .pbip in Desktop, (5) publish or Save As .pbix. **ALWAYS try .pbip first for any programmatic report modification.**
31. **TREATAS with island tables (no relationships).** When a table has no relationships to any other table (island table), you cannot use `VALUES('Table'[column])` in TREATAS if the column doesn't exist. Instead, derive the join key from an existing column using SELECTCOLUMNS: `TREATAS(SELECTCOLUMNS(FILTER('island_table', ...), "dk", INT(SUBSTITUTE(LEFT('island_table'[timestamp_col], 10), "-", ""))), 'target_table'[date_key])`. This converts ISO timestamp strings like "2026-04-13T12:34:56" to YYYYMMDD integers (20260413) that match date_key columns. VAR blocks work in report-level measures (unlike bracket refs), so use them to keep complex TREATAS expressions readable.
32. **Slicer must match the table used by page visuals.** If ALL visuals on a page reference only one table (an island table with no relationships), the slicer MUST use a column from THAT table. A `dim_date.full_date` slicer won't filter island-table visuals because there's no relationship to propagate the filter. Use the island table's own timestamp/date column instead. On mixed pages (visuals from related AND unrelated tables), the slicer should use the dimension table — TREATAS measures will handle the cross-table bridge.
33. **Always verify column names against the TMDL.** Before writing measures or visual references, read the `.tmdl` file in the semantic model definition to get exact column names. Column names in design documents or ETL scripts often differ from the actual Fabric Lakehouse column names (e.g., `deployments_found` vs `deployments_total`, `rbac_users_found` vs `rbac_user_count`). A wrong column name produces `QueryExtensionMeasureError: Column 'X' in table 'Y' cannot be found`.
34. **Report-level measures in .pbip use `dataType: "Double"` (string), not `dataType: 3` (int).** The `reportExtensions.json` format differs from the legacy `modelExtensions` in `layout["config"]`. Also: no `formatInformation` wrapper needed — just `formatString` directly. And `displayOption: "FitToPage"` is a string, not int 1. See the PBIP File Type Deep Reference section for full schema differences.

## PBI Desktop Local Analysis Services Instance

### Finding the Port
PBI Desktop Store version stores the port file at:
```
C:\Users\<username>\Microsoft\Power BI Desktop Store App\AnalysisServicesWorkspaces\AnalysisServicesWorkspace_<guid>\Data\msmdsrv.port.txt
```

Non-Store version:
```
C:\Users\<username>\AppData\Local\Microsoft\Power BI Desktop\AnalysisServicesWorkspaces\...
```

The port file contains the port number with spaces between digits (e.g., `6 3 8 1 7` = port 63817).

### Connecting via TOM (Tabular Object Model)
Required NuGet packages (.NET Framework net45 versions, NOT .NET Core):
- `Microsoft.AnalysisServices.retail.amd64` — contains `Microsoft.AnalysisServices.Tabular.dll`
- `Microsoft.AnalysisServices.AdomdClient.retail.amd64` — ADOMD client

```python
import clr, sys, os

dll_dir = r'path\to\net45\dlls'
sys.path.insert(0, dll_dir)
clr.AddReference(os.path.join(dll_dir, 'Microsoft.AnalysisServices.Tabular.dll'))
clr.AddReference(os.path.join(dll_dir, 'Microsoft.AnalysisServices.Core.dll'))

from Microsoft.AnalysisServices.Tabular import Server

server = Server()
server.Connect(f'Data Source=localhost:{port}')
# For live connection reports: server.Databases.Count will be 0
# Measures cannot be added via TOM for live connections
server.Disconnect()
```

**Important:** For live connection reports, the local AS instance will have **0 databases**. Measures cannot be added via TOM for live connections — they must be injected into the .pbix file's Report/Layout.

## Live Connection Configuration

### Connections File Format
```json
{
  "Version": 2,
  "Connections": [{
    "Name": "EntityDataSource",
    "ConnectionString": "Data Source=pbiazure://api.powerbi.com;Initial Catalog=<dataset-id>;Identity Provider=\"https://login.microsoftonline.com/common, https://analysis.windows.net/powerbi/api, 7f67af8a-fedc-4b08-8b4e-37c4d127b6cf\";Integrated Security=ClaimsToken",
    "ConnectionType": "pbiServiceLive",
    "PbiServiceModelId": 12345678,
    "PbiModelVirtualServerName": "sobe_wowvirtualserver",
    "PbiModelDatabaseName": "<dataset-guid>"
  }]
}
```

## Power BI REST API Reference

### Clone a Report
```
POST https://api.powerbi.com/v1.0/myorg/groups/{sourceWorkspaceId}/reports/{reportId}/Clone
{
    "name": "New Report Name",
    "targetWorkspaceId": "{targetWorkspaceId}",
    "targetModelId": "{datasetId}"
}
```

### Execute DAX Queries (for validation)
```
POST https://api.powerbi.com/v1.0/myorg/groups/{workspaceId}/datasets/{datasetId}/executeQueries
{
    "queries": [{"query": "EVALUATE ROW(\"Result\", 1+1)"}],
    "serializerSettings": {"includeNulls": true}
}
```

### Export .pbix (Import mode only)
```
GET https://api.powerbi.com/v1.0/myorg/groups/{workspaceId}/reports/{reportId}/Export
```
**Note:** This ONLY works for import mode reports. Live connection reports return error `ExportPBIX_ModelessWorkbookNotFound`.

## Environment Notes (Fluke UBI)

### Power BI Workspaces
| Environment | Workspace ID |
|-------------|-------------|
| Dev (FLK-BI-DEV) | `6fec84af-8245-4738-b317-f29326432ae3` |
| QA (FLK-BI-QA) | `7f77ddaf-78e7-471c-b104-9000eb5fd761` |
| Prod (FLK-BI-PROD) | `a59d3713-6f5a-470e-833e-15bbf60e8c97` |
| Prod2 (FLK-BI-PROD2) | `77022434-8325-4d68-9b96-02ea76d7319d` |

### Auth Token for Power BI API
```bash
az account get-access-token --resource https://analysis.windows.net/powerbi/api --query accessToken -o tsv
```

### PBI Desktop Store Location
```
<USER_HOME>/AppData\Local\Microsoft\WindowsApps\PBIDesktopStore.exe
```
Process name when running: `PBIDesktop.exe` (NOT `PBIDesktopStore.exe`)

## Column Metadata Reference

When building visual queries, columns need specific type metadata:

| Column Type | qmType | underlyingType | Example Columns |
|-------------|--------|----------------|-----------------|
| Text/String | 2048 | 1 | MSIB1Item, PriceListName |
| Date | 4 | 519 | StartDate, EndDate |
| Numeric | 1 | 259 | ItemPrice |
| Measure (numeric) | — | 261 | All report-level measures returning numbers |

Aggregation function codes for query Select:
- `3` = MIN
- `4` = MAX
- `5` = COUNT_NONNULL

## .pbip Report Modification Workflow (RECOMMENDED for PBI 2.153+)

**As of PBI Desktop April 2026 (v2.153.910.0), .pbip is the ONLY viable path for programmatic report modification.** The .pbix format has an unbypassable content hash check.

### Step-by-Step Workflow

1. **Convert .pbix → .pbip**: Open the .pbix in PBI Desktop → File → Save As → Power BI Project (.pbip)
2. **Understand the file structure**:
   ```
   MyReport.pbip                          # Entry point (JSON, points to .Report/ and .SemanticModel/)
   MyReport.Report/
     definition/
       report.json                        # Report-level settings
       pages/
         pages.json                       # Page order array (pageOrder + activePageName)
         {pageId}/
           page.json                      # Page metadata (displayName, dimensions)
           visuals/
             {visualId}/
               visual.json                # Visual definition (type, query, objects, position)
       reportExtensions.json              # Report-level measures (replaces modelExtensions)
   MyReport.SemanticModel/
     definition/
       tables/{tablename}.tmdl           # Table columns, types, partitions
       relationships.tmdl                 # All model relationships
       model.tmdl                         # Model-level settings
   ```
3. **Read the TMDL first**: Before writing ANY measure or visual reference, read the `.tmdl` files to get exact column names and verify relationships. Column names in design docs often differ from actual names.
4. **Edit JSON files directly**: All JSON files can be edited with any text editor or programmatically. No ZIP manipulation needed.
5. **Key format differences from .pbix**:
   - `reportExtensions.json`: measures use `dataType: "Double"` (string), not `dataType: 3` (int)
   - `reportExtensions.json`: `formatString` is a direct field, no `formatInformation` wrapper
   - `page.json`: `displayOption: "FitToPage"` (string, not int 1)
   - `visual.json`: position includes `tabOrder` alongside x/y/z/width/height
   - `visual.json`: report-level measures use `"Schema": "extension"` in SourceRef
   - `pages.json`: uses `pageOrder` array, not `sections` — page IDs are folder names
6. **Validate**: Reopen the .pbip in PBI Desktop. PBI validates on open and shows clear error messages if something is wrong.
7. **Publish**: From PBI Desktop → Publish to workspace, or Save As .pbix for distribution.

### Adding a New Page

1. Create a new folder under `pages/` with a unique hex ID (e.g., `a1b2c3d4e5f6789012ab`)
2. Add `page.json` with schema, name, displayName, displayOption, height, width
3. Create `visuals/` subfolder with a subfolder per visual, each containing `visual.json`
4. Add the page ID to the `pageOrder` array in `pages/pages.json`
5. If adding measures, add them to `reportExtensions.json` under the correct entity

### Adding Report-Level Measures

Edit `reportExtensions.json`. Each entity has a `measures` array:
```json
{
  "name": "My Measure",
  "dataType": "Double",
  "expression": "SUM('TableName'[Column])",
  "formatString": "$#,##0.00",
  "displayFolder": "FolderName"
}
```

**Rules:**
- ALL DAX must be fully inlined — NO bracket refs to other measures (`[OtherMeasure]` fails)
- VAR/RETURN blocks work and are recommended for complex measures
- Fabric Lakehouse tables need single quotes: `'schemaName tableName'[column]`
- Column names must exactly match the TMDL definition

### Cross-Table Measures for Island Tables

When a table has no relationships (island table), use TREATAS with SELECTCOLUMNS to derive join keys:

```dax
// Count rows in related_table for dates matching island_table timestamps
CALCULATE(
    COUNTROWS('related_table'),
    TREATAS(
        SELECTCOLUMNS(
            FILTER('island_table', 'island_table'[verdict] = "GOOD"),
            "dk",
            INT(SUBSTITUTE(LEFT('island_table'[timestamp_col], 10), "-", ""))
        ),
        'related_table'[date_key]
    )
)
```

This converts ISO timestamp "2026-04-13T12:34:56" → date_key 20260413 and pushes it as a virtual filter.

## Troubleshooting

### "MashupValidationError: This file is corrupted" (PBI 2.153+, April 2026+)
**This is a DIFFERENT error from the SecurityBindings issue below.** PBI 2.153+ validates Report/Layout against an internal content hash. NO programmatic .pbix modification works — not raw bytes, not zipfile, not OPC, not .NET ZipFile. **The ONLY fix is to use .pbip format.** See Gotcha #30 for the complete workflow. If you see this error, stop trying to fix the .pbix and convert to .pbip immediately.

### "This file is corrupted or was created by an unrecognized version" (PBI ≤2.152)
1. **Most likely cause:** SecurityBindings hash mismatch. Remove SecurityBindings from the ZIP.
2. **Second cause:** Wrong ZIP metadata (create_version, external_attr). Use binary rebuild instead of Python zipfile.
3. **Third cause:** Layout JSON encoding wrong. Must be UTF-16-LE without BOM.
4. **Diagnosis:** If writing the same bytes back works but different bytes fail, it's SecurityBindings.

### Visuals show blank or "Can't display"
1. Missing `query` and/or `dataTransforms` fields on the visual container.
2. Missing `Schema: "extension"` in query From clause for report-level measures.
3. Missing `NativeReferenceName` in query Select for measures.
4. Missing `Extension` block in SemanticQueryDataShapeCommand.
5. Wrong `underlyingType` in dataTransforms (measures need 261 for numeric, NOT 518 which is DateTime — see Gotcha #20).

### Measures invisible in Fields pane
1. Use `dataType: 6` instead of `3` in modelExtensions.
2. Include `displayFolder` in measure definition.

### "Fields that need to be fixed" error on table/matrix visuals
1. **Most likely cause:** Extension measures are NOT registered in `layout.config.modelExtensions`. PBI validates `prototypeQuery` field references against modelExtensions. If a measure exists only in the query's Extension block, PBI flags it as unresolvable. Fix: add all Extension measures to `modelExtensions` under the correct entity.
2. **Second cause:** `prototypeQuery` references a measure name that doesn't match the name in modelExtensions (case-sensitive).
3. **Third cause:** The measure's `dataType` in modelExtensions doesn't match what PBI expects. Use `4` for dates, `6` for numbers, `7` for currency/decimal.

### Visual shows old columns despite updated query/dataTransforms
1. **Root cause:** `config.singleVisual.prototypeQuery` and `config.singleVisual.projections` were NOT updated. PBI uses these as the authoritative field definitions, ignoring `vc.query` and `vc.dataTransforms`.
2. Fix: update ALL FOUR fields: `prototypeQuery`, `projections`, `query`, `dataTransforms`.
3. Verify: After rebuild, extract and check that `prototypeQuery.Select` contains the new field names.

### Matrix (`pivotTable`) field wells empty with live connection
1. **Root cause:** PBI Desktop cannot bind matrix Rows/Columns/Values wells from JSON manipulation with live connections.
2. Fix: Switch to flat `tableEx` with numbered period Extension measures (see Pattern 6b).

### Visual position/size changes have no visible effect
1. **Root cause:** Only the top-level `vc.x/y/width/height` was updated, but PBI Desktop reads position from `config.layouts[0].position` inside the config JSON string. The config position is the **authoritative** source.
2. Fix: Update BOTH locations simultaneously. Use the `set_vc_pos()` helper from Gotcha #18.
3. Verify: After rebuild, extract a visual's config and check that `layouts[0].position` matches the top-level values.

### "Cannot perform interop call to: ModelAuthoringHostService.UpdateModelExtensions"
1. **Root cause:** `formatInformation` contains enum fields with string values. Both `format` and `currencyFormat` are strict enums in PBI v2.152+. Strings like `"Currency"`, `"$#,##0.00"` cause deserialization errors.
2. Fix: Set `format` and `currencyFormat` to `null`. Keep `formatString` for display. Safe pattern: `{"formatString": "$#,##0.00", "thousandSeparator": true, "currencyFormat": null, "dateTimeCustomFormat": null}`.
3. If error mentions `CurrencyFormat`, the `currencyFormat` field has a string value — set to `null`.
4. If error mentions `Format`, the `format` field has a string value — remove it or set to `null`.

### `Missing_References` error — cards/charts show "Fix this" but table visuals work
1. **Most likely cause:** `modelExtensions` was written to `layout["modelExtensions"]` (top level) instead of inside `layout["config"]` (JSON string → parsed → `modelExtensions`). Table visuals work because they reference columns directly; cards/charts fail because they reference report-level measures that PBI can't find at the wrong location.
2. Fix: Parse `layout["config"]` as JSON, add measures to `config["modelExtensions"]`, serialize back to string, remove any top-level `layout["modelExtensions"]` key. See Gotcha #25.
3. Verify: After rebuild, extract layout and confirm `json.loads(layout["config"]).get("modelExtensions")` contains your measures, and `layout.get("modelExtensions")` is `None`.

### DirectLake slicer shows empty despite data existing
1. **Most likely cause:** The Delta Lake column was written as PyArrow `date32` type (from Python `datetime.date` objects), but the PBI DirectLake slicer expects a string. Fabric imports `date32` as Date type, and the slicer filter binding doesn't match.
2. Fix: Convert dates to strings with `.strftime("%Y-%m-%d")` before writing to Delta. Use explicit PyArrow schema with `pa.field("column_name", pa.string())` and pass `schema_mode="overwrite"` to `write_deltalake()` to force schema update.
3. Verify: Read the Delta table back and confirm `df["column_name"].dtype` is `object` (string), not `datetime64` or `date32`.

### Measure evaluation errors
1. Verify ALL measures are self-contained (no bracket refs to other report-level measures) — see Critical section below.
2. Verify table names match exactly (case-sensitive) between modelExtensions and the semantic model.
3. Verify `dataType: 6` in modelExtensions maps to `DataType: 7` in Extension blocks.

## Critical: No Inter-Measure References in Report-Level Measures

### The Rule

**NEVER write a report-level measure that references another report-level measure using bracket notation.** Both `modelExtensions` definitions AND query Extension blocks must contain fully self-contained DAX expressions. No `[OtherMeasure]` references.

### Why This Fails

When PBI Desktop evaluates report-level measures (defined in `modelExtensions`), it cannot resolve bracket references like `[Current Price]` to other report-level measures in the same entity. Analysis Services treats these as column references, not measure references, and throws:

```
Calculation error in measure 'Table'[Measure]: The value for 'OtherMeasure'
cannot be determined. Either the column doesn't exist, or there is no current
row for this column.
```

This affects **both** locations where measure DAX is stored:
1. **`config.modelExtensions`** — PBI Desktop validates these definitions and errors before query execution
2. **Query Extension blocks** — Analysis Services evaluates these for each visual

### What NOT To Do

```dax
// BAD — references other report-level measures
Price Change $ = [Current Price] - [Previous Price]
Price Change % = DIVIDE([Price Change $], [Previous Price], BLANK())
```

### What To Do Instead — Inline All Logic

Every measure must compute its full result using only table columns, DAX functions, and VAR statements:

```dax
// GOOD — fully self-contained, no measure references
Price Change $ Americas =
VAR _today = TODAY()
VAR _currentPrice =
    CALCULATE(
        MAX('Price List Americas'[ItemPrice]),
        'Price List Americas'[StartDate] <= _today,
        'Price List Americas'[EndDate] >= _today
    )
VAR _currentStart =
    CALCULATE(
        MAX('Price List Americas'[StartDate]),
        'Price List Americas'[StartDate] <= _today,
        'Price List Americas'[EndDate] >= _today
    )
VAR _prevEnd =
    CALCULATE(
        MAX('Price List Americas'[EndDate]),
        ALLEXCEPT('Price List Americas', 'Price List Americas'[MSIB1Item], 'Price List Americas'[PriceListName]),
        'Price List Americas'[EndDate] < _currentStart
    )
VAR _prevPrice =
    CALCULATE(
        MAX('Price List Americas'[ItemPrice]),
        ALLEXCEPT('Price List Americas', 'Price List Americas'[MSIB1Item], 'Price List Americas'[PriceListName]),
        'Price List Americas'[EndDate] = _prevEnd
    )
RETURN
    IF(ISBLANK(_currentPrice) || ISBLANK(_prevPrice), BLANK(), _currentPrice - _prevPrice)
```

### Validation Check

After generating measures, scan for violations:
```python
import re

def find_measure_refs(dax_expr, known_measures):
    """Find [MeasureName] references in DAX, excluding column references like 'Table'[Column]."""
    deps = set()
    for match in re.finditer(r'\[([^\]]+)\]', dax_expr):
        name = match.group(1)
        start = match.start()
        if start > 0 and dax_expr[start - 1] == "'":
            continue  # Column reference, not measure
        if name in known_measures:
            deps.add(name)
    return deps

# Check modelExtensions
for entity in model_extensions[0]['entities']:
    known = {m['name'] for m in entity['measures']}
    for m in entity['measures']:
        refs = find_measure_refs(m['expression'], known)
        if refs:
            raise ValueError(
                f"VIOLATION: [{entity['name']}] {m['name']} references "
                f"other report-level measures: {refs}. "
                f"Inline the logic instead."
            )

# Check Extension blocks in all visuals
for section in layout['sections']:
    for vc in section['visualContainers']:
        if 'query' not in vc:
            continue
        query = json.loads(vc['query'])
        for cmd in query.get('Commands', []):
            ext = cmd.get('SemanticQueryDataShapeCommand', {}).get('Extension', {})
            for entity in ext.get('Entities', []):
                for m in entity.get('Measures', []):
                    refs = find_measure_refs(m['Expression'], known)
                    if refs:
                        raise ValueError(
                            f"VIOLATION: Extension [{m['Name']}] references: {refs}"
                        )
```

### If You Inherit Existing Measures With Bracket References

Use this inlining approach to fix them:

1. Build a map of all report-level measures: `{name: expression}`
2. For each measure with bracket refs, recursively resolve the referenced expressions
3. Rewrite as a single self-contained VAR/RETURN expression
4. Update BOTH `modelExtensions` AND all Extension blocks that contain the measure

```python
# Pattern for inlining common derived measures
def inline_price_change_dollar(table):
    """Generate self-contained Price Change $ DAX for a given table."""
    return (
        f"VAR _today = TODAY()\n"
        f"VAR _currentPrice = CALCULATE(MAX('{table}'[ItemPrice]), "
        f"'{table}'[StartDate] <= _today, '{table}'[EndDate] >= _today)\n"
        f"VAR _currentStart = CALCULATE(MAX('{table}'[StartDate]), "
        f"'{table}'[StartDate] <= _today, '{table}'[EndDate] >= _today)\n"
        f"VAR _prevEnd = CALCULATE(MAX('{table}'[EndDate]), "
        f"ALLEXCEPT('{table}', '{table}'[MSIB1Item], '{table}'[PriceListName]), "
        f"'{table}'[EndDate] < _currentStart)\n"
        f"VAR _prevPrice = CALCULATE(MAX('{table}'[ItemPrice]), "
        f"ALLEXCEPT('{table}', '{table}'[MSIB1Item], '{table}'[PriceListName]), "
        f"'{table}'[EndDate] = _prevEnd)\n"
        f"RETURN IF(ISBLANK(_currentPrice) || ISBLANK(_prevPrice), BLANK(), "
        f"_currentPrice - _prevPrice)"
    )
```

## Compelling Visual Design

This section covers everything needed to create executive-grade Power BI visuals programmatically: theme JSON, typography, color palettes, per-visual formatting, conditional formatting, and design principles.

### Executive Dashboard Design Principles

**Layout and Information Architecture:**
- F-pattern scanning: Place the most important KPIs top-left; navigation and filters along the top or left edge
- Maximum 6-8 visuals per page — fewer visuals with higher information density beats many small visuals
- Maximum 3 slicers per page — too many filters overwhelm users
- Group related visuals together with consistent spacing (8-16px gaps)
- Page dimensions: `1280 x 720` (16:9) is the standard; `1920 x 1080` for large displays
- Z-order: 0-based, increment by 1000 per visual for easy insertion later

**Visual Hierarchy:**
- KPI cards at the top (callout numbers catch attention first)
- Trend charts in the middle (line/area/bar)
- Detail tables at the bottom (drill-down data)
- Slicers on the left sidebar or top row

**Minimize Chart Junk (IBCS Principles):**
- No 3D effects, no gradients on chart areas, no decorative elements
- Remove unnecessary gridlines — show horizontal gridlines only, dashed, light gray
- Remove chart borders unless grouping visuals
- Hide visual headers (the hover icons) by default — they add clutter
- Prefer data labels over axis labels where space permits
- Use abbreviated number formats: `12.3M` instead of `12,345,678`

### Theme JSON Structure

A theme JSON file controls global formatting for all visuals in a report. It can be applied via PBI Desktop (View > Themes > Browse) or injected into the `.pbix` at `Report/StaticResources/SharedResources/BaseThemes/`.

#### Top-Level Properties
```json
{
  "$schema": "https://raw.githubusercontent.com/microsoft/powerbi-desktop-samples/main/Report%20Theme%20JSON%20Schema/reportThemeSchema-2.149.json",
  "name": "Executive Dashboard",

  "dataColors": [
    "#005EB8", "#24477F", "#4169E1", "#8AD4EB",
    "#F3C13A", "#A2AAAD", "#595959", "#C85200"
  ],

  "background": "#F5F5F5",
  "foreground": "#252423",
  "tableAccent": "#005EB8",

  "good": "#178E0B",
  "neutral": "#E5AC12",
  "bad": "#AB1A1A",

  "maximum": "#D63554",
  "center": "#D9B300",
  "minimum": "#1AAB40",

  "textClasses": { },
  "visualStyles": { }
}
```

| Property | Purpose |
|----------|---------|
| `dataColors` | Array of hex codes for data series. Rotates after exhausted. |
| `background` | Report page background color |
| `foreground` | Default text color |
| `tableAccent` | Accent color for table/matrix visuals |
| `good` / `neutral` / `bad` | Sentiment colors for KPI and waterfall visuals |
| `maximum` / `center` / `minimum` | Divergent gradient colors for conditional formatting |

### Typography (`textClasses`)

**IMPORTANT:** The property name in `textClasses` is `fontFace`, NOT `fontFamily`. The `fontFamily` property is used inside `visualStyles` instead.

#### The Four Primary Text Classes
```json
"textClasses": {
  "callout": {
    "fontSize": 28,
    "fontFace": "Segoe UI Semibold",
    "color": "#252423"
  },
  "title": {
    "fontSize": 12,
    "fontFace": "Segoe UI Semibold",
    "color": "#333333"
  },
  "header": {
    "fontSize": 11,
    "fontFace": "Segoe UI Semibold",
    "color": "#333333"
  },
  "label": {
    "fontSize": 9,
    "fontFace": "Segoe UI",
    "color": "#666666"
  }
}
```

| Text Class | Used By |
|-----------|---------|
| `callout` | Card data labels, KPI indicators, gauge callouts |
| `title` | Axis titles, chart titles |
| `header` | Tab headers, key influencer headers |
| `label` | Table/matrix values, axis labels, legend text |

#### Secondary (Inherited) Classes
```json
"largeTitle": { "fontSize": 14, "fontFace": "Segoe UI", "color": "#0c62fb" },
"lightLabel": { "color": "#3e3e3e" },
"largeLightLabel": { "color": "#3e3e3e" },
"smallLightLabel": { "color": "#666666" },
"boldLabel": { "fontFace": "Segoe UI Bold" },
"semiboldLabel": { "fontFace": "Segoe UI Semibold" }
```

#### Recommended Executive Typography Stack
- **KPI numbers (callout)**: Segoe UI Semibold or DIN, 28-45pt
- **Chart titles (title)**: Segoe UI Semibold, 11-14pt
- **Axis labels (label)**: Segoe UI, 8-10pt
- **Data labels**: Segoe UI, 8-9pt

### Professional Color Palettes

#### McKinsey-Inspired Corporate Palette
```json
"dataColors": ["#005EB8", "#24477F", "#4169E1", "#8AD4EB", "#F3C13A", "#A2AAAD"]
```
| Hex | Role |
|-----|------|
| `#005EB8` | Primary data series (Corporate Blue) |
| `#24477F` | Secondary data (Dark Blue) |
| `#4169E1` | Tertiary (Royal Blue) |
| `#8AD4EB` | Supporting (Light Blue) |
| `#F3C13A` | Highlights/KPI accent (Gold) |
| `#A2AAAD` | Neutral/reference (Silver Gray) |

#### Dark Theme Executive Palette
```json
{
  "background": "#0A1628",
  "foreground": "#C8D0D8",
  "tableAccent": "#005EB8",
  "dataColors": ["#4169E1", "#8AD4EB", "#F3C13A", "#1AAB40", "#FF6B6B", "#A2AAAD"]
}
```
| Element | Hex |
|---------|-----|
| Page Background | `#0A1628` (very dark navy) |
| Visual Background | `#041C32` (dark navy) |
| Text Headers | `#FFFFFF` (white) |
| Text Body | `#C8D0D8` (light bluish gray) |

#### IBCS-Standard Monochrome Palette
```json
"dataColors": ["#333333", "#666666", "#999999", "#BBBBBB", "#DDDDDD"]
```
IBCS recommends grayscale for clarity. Color reserved only for variance indicators.

#### Power BI Default (for reference)
```json
"dataColors": ["#01B8AA", "#374649", "#FD625E", "#F2C80F", "#5F6B6D", "#8AD4EB", "#FE9666", "#A66999"]
```

### `visualStyles` — Global and Per-Visual Formatting

#### Structure and Precedence
```
visualStyles
  └─ "*" (all visuals)         ← lowest priority
  └─ "lineChart" (specific)    ← overrides "*"
  └─ singleVisual.objects      ← per-instance, overrides theme (stored in layout JSON)
  └─ vcObjects                 ← container-level, overrides theme (stored in layout JSON)
```

#### Global Formatting (All Visuals)
```json
"visualStyles": {
  "*": {
    "*": {
      "*": [{
        "fontSize": 9,
        "fontFamily": "Segoe UI",
        "wordWrap": true
      }],
      "general": [{ "responsive": true }],
      "title": [{
        "show": true,
        "fontColor": {"solid": {"color": "#333333"}},
        "fontSize": 11,
        "fontFamily": "Segoe UI Semibold",
        "alignment": "Left"
      }],
      "subTitle": [{
        "show": false,
        "fontColor": {"solid": {"color": "#A6A6A6"}},
        "fontSize": 10,
        "fontFamily": "Segoe UI"
      }],
      "divider": [{
        "show": false,
        "color": {"solid": {"color": "#E6E6E6"}},
        "style": "solid",
        "width": 1
      }],
      "background": [{
        "show": true,
        "color": {"solid": {"color": "#FFFFFF"}},
        "transparency": 0
      }],
      "border": [{
        "show": false,
        "color": {"solid": {"color": "#E6E6E6"}},
        "radius": 0
      }],
      "dropShadow": [{
        "show": false,
        "color": {"solid": {"color": "#333333"}},
        "position": "outer",
        "preset": "bottomRight",
        "transparency": 60
      }],
      "visualHeader": [{
        "show": false,
        "background": {"solid": {"color": "#FFFFFF"}},
        "border": {"solid": {"color": "#E6E6E6"}},
        "transparency": 100,
        "foreground": {"solid": {"color": "#A6A6A6"}}
      }],
      "visualHeaderTooltip": [{"show": false}],
      "padding": [{"top": 0, "bottom": 0, "left": 0, "right": 0}]
    }
  }
}
```

### Line Chart Formatting

```json
"lineChart": {
  "*": {
    "lineStyles": [{
      "lineStyle": "lineOnly",
      "showMarker": false,
      "markerShape": "circle",
      "markerSize": 5,
      "markerColor": {"solid": {"color": "#005EB8"}},
      "stepped": false,
      "strokeWidth": 2,
      "showSeries": false
    }],
    "categoryAxis": [{
      "show": true,
      "axisType": "Categorical",
      "color": {"solid": {"color": "#949494"}},
      "fontSize": 8,
      "fontFamily": "Segoe UI",
      "preferredCategoryWidth": 20,
      "maxMarginFactor": 30,
      "concatenateLabels": true,
      "showAxisTitle": false,
      "axisStyle": "showTitleOnly",
      "gridLineShow": false,
      "gridLineColor": {"solid": {"color": "#E6E6E6"}},
      "gridLineThickness": 1,
      "gridlineStyle": "Solid"
    }],
    "valueAxis": [{
      "show": true,
      "position": "Left",
      "axisScale": "Linear",
      "labelColor": {"solid": {"color": "#949494"}},
      "fontSize": 8,
      "fontFamily": "Segoe UI",
      "labelDisplayUnits": 0,
      "labelPrecision": 0,
      "showAxisTitle": false,
      "gridlineShow": true,
      "gridlineColor": {"solid": {"color": "#E6E6E6"}},
      "gridlineThickness": 1,
      "gridlineStyle": "dashed"
    }],
    "legend": [{
      "show": true,
      "position": "Top",
      "showTitle": false,
      "labelColor": {"solid": {"color": "#666666"}},
      "fontFamily": "Segoe UI",
      "fontSize": 8
    }],
    "labels": [{
      "show": false,
      "fontSize": 8,
      "fontFamily": "Segoe UI",
      "color": {"solid": {"color": "#333333"}}
    }],
    "plotArea": [{
      "transparency": 0
    }]
  }
}
```

**Stepped Line Property:** Set `"stepped": true` in `lineStyles` for CamelCamelCamel-style price charts where values change at discrete moments, not continuously.

**Gridline Best Practice (IBCS):** Show horizontal gridlines only (`valueAxis.gridlineShow: true`, `categoryAxis.gridLineShow: false`), in dashed light gray. This reduces clutter while maintaining readability.

Valid `gridlineStyle` values: `"Solid"`, `"dashed"`, `"dotted"`

### Bar/Column Chart Formatting

```json
"clusteredBarChart": {
  "*": {
    "legend": [{
      "show": true,
      "position": "Top",
      "showTitle": false,
      "labelColor": {"solid": {"color": "#666666"}},
      "fontFamily": "Segoe UI",
      "fontSize": 8
    }],
    "categoryAxis": [{
      "show": true,
      "fontSize": 9,
      "fontFamily": "Segoe UI",
      "labelColor": {"solid": {"color": "#666666"}},
      "preferredCategoryWidth": 20,
      "maxMarginFactor": 30,
      "innerPadding": 20,
      "concatenateLabels": true,
      "showAxisTitle": false,
      "gridLineShow": false
    }],
    "valueAxis": [{
      "show": true,
      "fontSize": 8,
      "fontFamily": "Segoe UI",
      "labelColor": {"solid": {"color": "#949494"}},
      "showAxisTitle": false,
      "gridlineShow": true,
      "gridlineColor": {"solid": {"color": "#E6E6E6"}},
      "gridlineThickness": 1,
      "gridlineStyle": "dashed",
      "labelDisplayUnits": 0,
      "labelPrecision": 0
    }],
    "labels": [{
      "show": true,
      "fontSize": 8,
      "fontFamily": "Segoe UI",
      "color": {"solid": {"color": "#333333"}},
      "labelDisplayUnits": 1000000,
      "labelPrecision": 1
    }]
  }
}
```

**Number Abbreviation (IBCS):** Use `"labelDisplayUnits": 1000000` and `"labelPrecision": 1` to display `12.3` instead of `12,345,678`.

### Card Visual Formatting

#### Classic Card (`"card"`)
```json
"card": {
  "*": {
    "calloutValue": [{
      "fontSize": 27,
      "fontFamily": "DIN",
      "color": {"solid": {"color": "#333333"}},
      "labelDisplayUnits": 0,
      "labelPrecision": 2
    }],
    "categoryLabels": [{
      "show": true,
      "color": {"solid": {"color": "#A6A6A6"}},
      "fontSize": 12,
      "fontFamily": "Segoe UI"
    }],
    "labels": [{
      "fontSize": 12,
      "fontFamily": "Segoe UI",
      "color": {"solid": {"color": "#333333"}},
      "labelDisplayUnits": 0,
      "labelPrecision": 2
    }],
    "wordWrap": [{"show": true}]
  }
}
```

#### New Card Visual (`"cardVisual"`) — with Sparkline Support
**IMPORTANT:** The `"$id": "default"` property is required for new card visual properties to work. Without it, properties silently fail.

```json
"cardVisual": {
  "*": {
    "value": [{
      "$id": "default",
      "fontSize": 28,
      "fontFamily": "DIN",
      "fontColor": {"solid": {"color": "#333333"}},
      "horizontalAlignment": "center",
      "textWrap": true,
      "labelDisplayUnits": 0,
      "showBlankAs": "--"
    }],
    "label": [{
      "$id": "default",
      "show": true,
      "fontSize": 12,
      "fontFamily": "Segoe UI",
      "fontColor": {"solid": {"color": "#A6A6A6"}}
    }],
    "referenceLabel": [{
      "$id": "default",
      "show": false
    }],
    "cards": [{
      "$id": "default",
      "paddingUniform": 8,
      "background": {"solid": {"color": "#FFFFFF"}},
      "backgroundTransparency": 0,
      "borderShow": false,
      "borderColor": {"solid": {"color": "#000000"}},
      "borderWidth": 1,
      "borderRadius": 0
    }],
    "layout": [{
      "$id": "default",
      "alignment": "center",
      "orientation": 0
    }],
    "image": [{
      "$id": "default",
      "imageType": "Default",
      "imageURL": ""
    }]
  }
}
```

#### SVG Sparklines in Card Visuals
To add sparklines to the new card visual without custom visuals:
1. Create a DAX measure that generates SVG markup
2. Set the card's Image data role to the SVG measure
3. Set `image.imageType` to `"ImageURL"`

Example DAX sparkline measure:
```dax
Sparkline =
VAR MaxVal = MAXX(ALL('Date'[Month]), [Sales])
VAR SparkData =
    CONCATENATEX(
        SUMMARIZE(ALL('Date'[Month]), 'Date'[MonthNum], "Val", [Sales]),
        FORMAT([MonthNum] * 100 / 12, "0") & "," &
        FORMAT(100 - [Val] * 100 / MaxVal, "0"),
        " ", [MonthNum]
    )
RETURN
"data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><polyline points='" & SparkData & "' fill='none' stroke='%234472C4' stroke-width='2'/></svg>"
```

### Table/Matrix Formatting

```json
"tableEx": {
  "*": {
    "grid": [{
      "gridVertical": true,
      "gridVerticalColor": {"solid": {"color": "#E6E6E6"}},
      "gridVerticalWeight": 1,
      "gridHorizontal": true,
      "gridHorizontalColor": {"solid": {"color": "#E6E6E6"}},
      "gridHorizontalWeight": 1,
      "rowPadding": 3,
      "outlineColor": {"solid": {"color": "#E6E6E6"}},
      "outlineWeight": 1,
      "textSize": 9
    }],
    "columnHeaders": [{
      "fontColor": {"solid": {"color": "#FFFFFF"}},
      "backColor": {"solid": {"color": "#005EB8"}},
      "outline": "BottomOnly",
      "autoSizeColumnWidth": true,
      "fontFamily": "Segoe UI Semibold",
      "fontSize": 9,
      "alignment": "Left",
      "wordWrap": true
    }],
    "values": [{
      "fontColorPrimary": {"solid": {"color": "#333333"}},
      "backColorPrimary": {"solid": {"color": "#FFFFFF"}},
      "fontColorSecondary": {"solid": {"color": "#333333"}},
      "backColorSecondary": {"solid": {"color": "#F5F5F5"}},
      "outline": "None",
      "wordWrap": true,
      "fontFamily": "Segoe UI",
      "fontSize": 9
    }],
    "total": [{
      "totals": true,
      "fontColor": {"solid": {"color": "#FFFFFF"}},
      "backColor": {"solid": {"color": "#24477F"}},
      "outline": "TopOnly",
      "fontFamily": "Segoe UI Semibold",
      "fontSize": 9
    }]
  }
}
```

**Alternating row colors:** Use `backColorPrimary` (white) and `backColorSecondary` (light gray `#F5F5F5`) in the `values` object.

### Slicer Formatting

```json
"slicer": {
  "*": {
    "general": [{
      "outlineColor": {"solid": {"color": "#E6E6E6"}},
      "outlineWeight": 1,
      "orientation": 0,
      "responsive": true
    }],
    "data": [{"mode": "Dropdown"}],
    "selection": [{
      "selectAllCheckboxEnabled": true,
      "singleSelect": false
    }],
    "header": [{
      "show": true,
      "fontColor": {"solid": {"color": "#333333"}},
      "background": {"solid": {"color": "#FFFFFF"}},
      "outline": "BottomOnly",
      "textSize": 10,
      "fontFamily": "Segoe UI Semibold"
    }],
    "items": [{
      "fontColor": {"solid": {"color": "#666666"}},
      "background": {"solid": {"color": "#FFFFFF"}},
      "outline": "None",
      "textSize": 9,
      "fontFamily": "Segoe UI"
    }]
  }
}
```

Slicer `data.mode` values: `"Dropdown"`, `"Basic"` (list), `"Between"` (range)

### Visual Container Formatting (`vcObjects`)

These control the visual container itself (title bar, background, border, shadow), NOT the chart data. Set via `singleVisual.vcObjects` in the layout JSON.

```json
"vcObjects": {
  "title": [{
    "properties": {
      "show": {"expr": {"Literal": {"Value": "true"}}},
      "text": {"expr": {"Literal": {"Value": "'Revenue Trend'"}}},
      "fontColor": {"solid": {"color": "#333333"}},
      "fontSize": {"expr": {"Literal": {"Value": "11D"}}},
      "fontFamily": {"expr": {"Literal": {"Value": "'Segoe UI Semibold'"}}},
      "alignment": {"expr": {"Literal": {"Value": "'left'"}}}
    }
  }],
  "background": [{
    "properties": {
      "show": {"expr": {"Literal": {"Value": "true"}}},
      "color": {"solid": {"color": "#FFFFFF"}},
      "transparency": {"expr": {"Literal": {"Value": "0D"}}}
    }
  }],
  "border": [{
    "properties": {
      "show": {"expr": {"Literal": {"Value": "true"}}},
      "color": {"solid": {"color": "#E1DFDD"}},
      "width": {"expr": {"Literal": {"Value": "1L"}}},
      "radius": {"expr": {"Literal": {"Value": "0L"}}}
    }
  }],
  "dropShadow": [{
    "properties": {
      "show": {"expr": {"Literal": {"Value": "true"}}},
      "color": {"solid": {"color": "#333333"}},
      "position": {"expr": {"Literal": {"Value": "'outer'"}}},
      "preset": {"expr": {"Literal": {"Value": "'bottomRight'"}}},
      "transparency": {"expr": {"Literal": {"Value": "60D"}}},
      "shadowBlur": {"expr": {"Literal": {"Value": "5D"}}},
      "shadowDistance": {"expr": {"Literal": {"Value": "3D"}}},
      "shadowSpread": {"expr": {"Literal": {"Value": "0D"}}}
    }
  }],
  "visualHeader": [{
    "properties": {
      "show": {"expr": {"Literal": {"Value": "false"}}}
    }
  }],
  "padding": [{
    "properties": {
      "top": {"expr": {"Literal": {"Value": "0L"}}},
      "bottom": {"expr": {"Literal": {"Value": "0L"}}},
      "left": {"expr": {"Literal": {"Value": "0L"}}},
      "right": {"expr": {"Literal": {"Value": "0L"}}}
    }
  }]
}
```

**Literal value suffixes in layout JSON:**
- `"12D"` — double (decimal)
- `"100L"` — long (integer)
- `"true"` / `"false"` — boolean as strings
- `"'text'"` — string values wrapped in single quotes

**Theme color references in layout JSON:**
```json
"fontColor": {"solid": {"color": {"expr": {"ThemeDataColor": {"ColorId": 1, "Percent": 0}}}}}
```

### Conditional Formatting in Layout JSON

Conditional formatting is stored in `singleVisual.objects` using expression syntax.

#### Rules-Based Background Color
```json
"objects": {
  "values": [{
    "properties": {
      "backColor": {
        "solid": {"color": {"expr": {"Conditional": {
          "Cases": [
            {
              "Condition": {"Comparison": {
                "ComparisonKind": 1,
                "Left": {"Aggregation": {"Expression": {"Column": {"Expression": {"SourceRef": {"Entity": "Sales"}}, "Property": "Amount"}}, "Function": 0}},
                "Right": {"Literal": {"Value": "1000L"}}
              }},
              "Value": {"Literal": {"Value": "'#FF0000'"}}
            }
          ],
          "DefaultValue": {"Literal": {"Value": "'#00FF00'"}}
        }}}}
      }
    },
    "selector": {"data": [{"dataViewWildcard": {"matchingOption": 1}}]}
  }]
}
```

`ComparisonKind` values: `0` = Equal, `1` = GreaterThan, `2` = GreaterThanOrEqual, `3` = LessThan, `4` = LessThanOrEqual

`Aggregation.Function` values: `0` = Sum, `1` = Avg, `2` = Count, `3` = Min, `4` = Max

#### Gradient / Color Scale (`fillRule`)
```json
"backColor": {
  "solid": {"color": {"expr": {"FillRule": {
    "Input": {"Aggregation": {"Expression": {"Column": {"Expression": {"SourceRef": {"Entity": "Table1"}}, "Property": "Value"}}, "Function": 0}},
    "FillRule": {
      "linearGradient3": {
        "min": {"color": {"Literal": {"Value": "'#FF0000'"}}},
        "mid": {"color": {"Literal": {"Value": "'#FFFF00'"}}},
        "max": {"color": {"Literal": {"Value": "'#00FF00'"}}}
      }
    }
  }}}}
}
```
Use `linearGradient2` for 2-stop (min/max) or `linearGradient3` for 3-stop (min/mid/max).

#### Data Bars (Table/Matrix columns)
```json
"dataBar": {
  "positiveColor": {"solid": {"color": "#4472C4"}},
  "negativeColor": {"solid": {"color": "#FF0000"}},
  "axisColor": {"solid": {"color": "#CCCCCC"}},
  "reverseDirection": false,
  "hideText": false
}
```

#### DAX-Driven Conditional Formatting (Recommended)
Create a DAX measure that returns theme color names, then apply via the FX button:
```dax
BackgroundColor =
SWITCH(
    TRUE(),
    [Variance%] >= 0.05, "good",
    [Variance%] >= -0.05, "neutral",
    "bad"
)
```
In the layout JSON, a measure-based format is stored as:
```json
"backColor": {
  "solid": {"color": {"expr": {
    "Measure": {
      "Expression": {"SourceRef": {"Entity": "Formatting"}},
      "Property": "BackgroundColorMeasure"
    }
  }}}
}
```

### Reference Lines and Analytics

These are per-visual formatting stored in `singleVisual.objects`.

#### Constant Line (Y-Axis)
```json
"y1AxisReferenceLine": [{
  "show": true,
  "value": "75",
  "lineColor": {"solid": {"color": "#FF0000"}},
  "transparency": 0,
  "style": "dashed",
  "position": "front",
  "dataLabelShow": true,
  "dataLabelColor": {"solid": {"color": "#FF0000"}},
  "dataLabelDecimalPoints": 0,
  "dataLabelHorizontalPosition": "left",
  "dataLabelVerticalPosition": "above",
  "dataLabelDisplayUnits": 0,
  "dataLabelText": "ValueAndName"
}]
```
Also available: `y2AxisReferenceLine` (secondary Y), `xAxisReferenceLine` (X axis)

Valid `dataLabelText` values: `"Value"`, `"Name"`, `"ValueAndName"`

#### Trend Line
```json
"trend": [{
  "show": true,
  "lineColor": {"solid": {"color": "#000000"}},
  "transparency": 30,
  "style": "dashed",
  "combineSeries": true,
  "useHighlightValues": true
}]
```

#### Average / Min / Max / Median / Percentile Lines
Same property structure as reference lines, using object names: `"averageLine"`, `"minLine"`, `"maxLine"`, `"medianLine"`, `"percentileLine"` (with additional `percentile` numeric property)

### Sparklines in Tables/Matrices

- Add via field dropdown in PBI Desktop or programmatically
- Maximum **5 sparklines** per visual
- Displays up to **52 data points** per sparkline
- Formatting: chart type (line/column), data color, markers (highest, lowest, first, last), marker size/color/shape
- **Limitation:** No conditional formatting on sparklines

### Filter JSON Structure

Filters are stored as a string-encoded JSON array in each visual container's `filters` field.

#### Basic Filter
```json
{
  "$schema": "https://powerbi.com/product/schema#basic",
  "target": {"table": "Sales", "column": "Region"},
  "filterType": 1,
  "operator": "In",
  "values": ["East", "West"],
  "requireSingleSelection": false
}
```

#### Advanced Filter
```json
{
  "$schema": "https://powerbi.com/product/schema#advanced",
  "target": {"table": "Sales", "column": "Amount"},
  "filterType": 0,
  "logicalOperator": "And",
  "conditions": [
    {"operator": "GreaterThan", "value": 1000},
    {"operator": "LessThan", "value": 5000}
  ]
}
```

#### Top N Filter
```json
{
  "$schema": "https://powerbi.com/product/schema#topN",
  "target": {"table": "Products", "column": "Name"},
  "filterType": 5,
  "operator": "Top",
  "itemCount": 10,
  "orderBy": {"table": "Sales", "measure": "Total Revenue"}
}
```

#### Relative Date Filter
```json
{
  "$schema": "https://powerbi.com/product/schema#relativeDate",
  "target": {"table": "Date", "column": "Date"},
  "filterType": 6,
  "operator": "InLast",
  "timeUnitsCount": 3,
  "timeUnitType": "Months",
  "includeToday": true
}
```

Condition operators: `"None"`, `"LessThan"`, `"LessThanOrEqual"`, `"GreaterThan"`, `"GreaterThanOrEqual"`, `"Contains"`, `"DoesNotContain"`, `"StartsWith"`, `"DoesNotStartWith"`, `"Is"`, `"IsNot"`, `"IsBlank"`, `"IsNotBlank"`

### Visual Type Registry

Complete mapping of PBI visual types to `visualStyles` keys:

| Visual | Key |
|--------|-----|
| Line Chart | `"lineChart"` |
| Area Chart | `"areaChart"` |
| Stacked Area | `"stackedAreaChart"` |
| Bar Chart (Stacked) | `"barChart"` |
| Clustered Bar | `"clusteredBarChart"` |
| Column Chart (Stacked) | `"columnChart"` |
| Clustered Column | `"clusteredColumnChart"` |
| 100% Stacked Bar | `"hundredPercentStackedBarChart"` |
| 100% Stacked Column | `"hundredPercentStackedColumnChart"` |
| Line & Clustered Column | `"lineClusteredColumnComboChart"` |
| Line & Stacked Column | `"lineStackedColumnComboChart"` |
| Ribbon Chart | `"ribbonChart"` |
| Waterfall | `"waterfallChart"` |
| Pie Chart | `"pieChart"` |
| Donut Chart | `"donutChart"` |
| Treemap | `"treemap"` |
| Scatter Chart | `"scatterChart"` |
| Funnel | `"funnel"` |
| Gauge | `"gauge"` |
| Card (Classic) | `"card"` |
| Card (New) | `"cardVisual"` |
| Multi Row Card | `"multiRowCard"` |
| KPI | `"kpi"` |
| Table | `"tableEx"` |
| Matrix | `"pivotTable"` |
| Slicer | `"slicer"` |
| Map (Bing) | `"map"` |
| Filled Map | `"filledMap"` |
| Shape Map | `"shapeMap"` |
| Decomposition Tree | `"decompositionTreeVisual"` |
| Key Influencers | `"keyDriversVisual"` |
| Action Button | `"actionButton"` |
| Shape | `"shape"` |
| Text Box | `"textbox"` |
| Image | `"image"` |

### CamelCamelCamel-Style Line Chart Pattern

For price history charts with multiple items as separate lines:

**Key differences from standard line chart:**
1. Add `MSIB1Item` (or equivalent) as **Series** role — one line per item
2. Query Binding uses **Primary** (Category + Y) and **Secondary** (Series) groupings
3. DataReduction: `Primary: BinnedLineSample`, `Secondary: Top { Count: 60 }`

```python
# Config projections
"projections": {
    "Category": [{"queryRef": f"{table}.StartDate", "active": True}],
    "Y": [{"queryRef": f"Max({table}.ItemPrice)", "active": True}],
    "Series": [{"queryRef": f"{table}.MSIB1Item", "active": True}],
}

# Query Binding
"Binding": {
    "Primary": {"Groupings": [{"Projections": [0, 1]}]},
    "Secondary": {"Groupings": [{"Projections": [2]}]},
    "DataReduction": {
        "DataVolume": 4,
        "Primary": {"BinnedLineSample": {}},
        "Secondary": {"Top": {"Count": 60}},
    },
    "Version": 1,
}

# dataTransforms — include Series in all mapping structures
"projectionOrdering": {"Category": [0], "Y": [1], "Series": [2]},
"visualElements": [{"DataRoles": [
    {"Name": "Category", "Projection": 0, "isActive": True},
    {"Name": "Y", "Projection": 1, "isActive": True},
    {"Name": "Series", "Projection": 2, "isActive": True},
]}]
```

### Complete Executive Theme Template

Production-ready theme combining all best practices:

```json
{
  "$schema": "https://raw.githubusercontent.com/microsoft/powerbi-desktop-samples/main/Report%20Theme%20JSON%20Schema/reportThemeSchema-2.149.json",
  "name": "Executive Dashboard",

  "dataColors": [
    "#005EB8", "#24477F", "#4169E1", "#8AD4EB",
    "#F3C13A", "#A2AAAD", "#595959", "#C85200"
  ],

  "background": "#F5F5F5",
  "foreground": "#252423",
  "tableAccent": "#005EB8",

  "good": "#178E0B",
  "neutral": "#E5AC12",
  "bad": "#AB1A1A",
  "maximum": "#D63554",
  "center": "#D9B300",
  "minimum": "#1AAB40",

  "textClasses": {
    "callout": {"fontSize": 28, "fontFace": "Segoe UI Semibold", "color": "#252423"},
    "title": {"fontSize": 12, "fontFace": "Segoe UI Semibold", "color": "#333333"},
    "header": {"fontSize": 11, "fontFace": "Segoe UI Semibold", "color": "#333333"},
    "label": {"fontSize": 9, "fontFace": "Segoe UI", "color": "#666666"}
  },

  "visualStyles": {
    "*": {
      "*": {
        "*": [{"fontSize": 9, "fontFamily": "Segoe UI", "wordWrap": true}],
        "title": [{"show": true, "fontColor": {"solid": {"color": "#333333"}}, "fontSize": 11, "fontFamily": "Segoe UI Semibold", "alignment": "Left"}],
        "background": [{"show": true, "color": {"solid": {"color": "#FFFFFF"}}, "transparency": 0}],
        "border": [{"show": false}],
        "dropShadow": [{"show": false}],
        "visualHeader": [{"show": false}]
      }
    },
    "lineChart": {
      "*": {
        "lineStyles": [{"lineStyle": "lineOnly", "showMarker": false, "stepped": false, "strokeWidth": 2}],
        "categoryAxis": [{"show": true, "fontSize": 8, "fontFamily": "Segoe UI", "color": {"solid": {"color": "#949494"}}, "showAxisTitle": false, "gridLineShow": false}],
        "valueAxis": [{"show": true, "fontSize": 8, "fontFamily": "Segoe UI", "labelColor": {"solid": {"color": "#949494"}}, "showAxisTitle": false, "gridlineShow": true, "gridlineColor": {"solid": {"color": "#E6E6E6"}}, "gridlineThickness": 1, "gridlineStyle": "dashed", "labelDisplayUnits": 0}],
        "legend": [{"show": true, "position": "Top", "showTitle": false, "fontSize": 8}],
        "labels": [{"show": false}]
      }
    },
    "clusteredBarChart": {
      "*": {
        "categoryAxis": [{"show": true, "fontSize": 9, "fontFamily": "Segoe UI", "showAxisTitle": false, "gridLineShow": false}],
        "valueAxis": [{"show": true, "fontSize": 8, "showAxisTitle": false, "gridlineShow": true, "gridlineColor": {"solid": {"color": "#E6E6E6"}}, "gridlineStyle": "dashed"}],
        "labels": [{"show": true, "fontSize": 8, "labelDisplayUnits": 1000000, "labelPrecision": 1}]
      }
    },
    "cardVisual": {
      "*": {
        "*": [{"$id": "default", "paddingUniform": 8}]
      }
    }
  }
}
```

### IBCS (International Business Communication Standards) Quick Reference

| Principle | Application |
|-----------|-------------|
| **Simplify** | Remove chart junk: no 3D, no gradients, no unnecessary gridlines |
| **Condense** | High information density — data labels preferred over axis labels |
| **Unify** | Consistent notation across all charts and reports |
| **Structure** | Logical reading order, clear visual hierarchy |
| **Express** | Variance analysis as primary focus (AC vs PL, AC vs PY) |
| **Standardize** | AC = solid fill, PL = outlined, FC = hatched, PY = lighter shade |

### Reference Links

**Official Microsoft:**
- [Report Themes Documentation](https://learn.microsoft.com/en-us/power-bi/create-reports/desktop-report-themes)
- [Theme JSON Schema (GitHub)](https://github.com/microsoft/powerbi-desktop-samples/blob/main/Report%20Theme%20JSON%20Schema/README.md)
- [Card Visual Format Settings](https://learn.microsoft.com/en-us/power-bi/visuals/power-bi-visualization-card-visual-new-format-settings)
- [Sparklines in Tables](https://learn.microsoft.com/en-us/power-bi/create-reports/power-bi-sparklines-tables)
- [Objects and Properties (Developer)](https://learn.microsoft.com/en-us/power-bi/developer/visuals/objects-properties)
- [PBIR Report Format](https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-report)

**GitHub Repositories:**
- [deldersveld/PowerBI-ThemeTemplates](https://github.com/deldersveld/PowerBI-ThemeTemplates) — Per-visual JSON templates
- [MattRudy/PowerBI-ThemeTemplates](https://github.com/MattRudy/PowerBI-ThemeTemplates) — Theme snippets
- [Apress/pro-power-bi-theme-creation](https://github.com/Apress/pro-power-bi-theme-creation) — Full attribute files per visual
- [NatVanG/PBI-Inspector](https://github.com/NatVanG/PBI-Inspector) — Layout JSON inspection tool

**Community:**
- [SQLBI — Re-using Visual Formatting](https://www.sqlbi.com/articles/re-using-visual-formatting-in-and-across-power-bi-reports/)
- [Data Goblins — Programmatic Report Modification](https://data-goblins.com/power-bi/programmatically-modify-reports)
- [Kerry Kolosko — Sparklines in Card Visual](https://kerrykolosko.com/adding-sparklines-to-new-card-visual/)
- [Antares Analytics — Layout File Guide](https://www.antaresanalytics.net/post/a-beginner-s-guide-to-automating-power-bi-with-the-layout-file-part-2)
- [IBCS Standards](https://www.ibcs.com/)
- [Zebra BI — IBCS for Power BI](https://zebrabi.com/ibcs/)

## Report Beautification System

This section defines 10 beautification techniques that can be individually toggled on or off for any report. When the user asks to beautify a report, use the interview flow below to determine which techniques to apply.

### Beautification Interview Flow

**When the user requests report beautification (e.g., "make it look better", "beautify", "enhance visuals"), follow this process:**

1. Ask the user using `AskUserQuestion` with the following question:

   **Question:** "How would you like to beautify this report?"
   **Options:**
   - **Auto (Recommended)** — "I'll pick the 3 most impactful techniques based on the report's content and visual types"
   - **Choose manually** — "Select specific techniques from the full list of 10"
   - **All 10** — "Apply every beautification technique for maximum visual impact"

2. **If "Auto":** Analyze the report's visual types and apply the 3 most appropriate techniques using these priority rules:
   - **Always include B1 (Shadows + Rounded Corners)** — universal impact, works on every visual type
   - **If report has tables/matrices:** Include B5 (Conditional Formatting) — heat maps and data bars transform plain tables
   - **If report has cards/KPIs:** Include B4 (SVG Measures) — dynamic arrows and indicators make cards compelling
   - **If report has charts:** Include B3 (Color Theme JSON) — consistent palette makes charts cohesive
   - **If report has many pages:** Include B3 (Color Theme JSON) — theme ensures cross-page consistency
   - **Fallback top 3:** B1 + B3 + B5 (covers the widest range of visual types)

3. **If "Choose manually":** Present the 10 techniques using `AskUserQuestion` with `multiSelect: true`:

   **Question:** "Which beautification techniques do you want to apply?"
   **Options (multi-select):**
   - B1: Shadows + Rounded Corners
   - B2: Background Images
   - B3: Color Theme JSON
   - B4: SVG Measures (dynamic icons)

   Then a second question with the remaining:
   - B5: Conditional Formatting
   - B6: Deneb Custom Visuals
   - B7: Sparklines + KPI Indicators
   - B8: Glassmorphism Effects

   Then if needed:
   - B9: Play Axis Animation
   - B10: Grid Layout System

4. **If "All 10":** Apply every technique in order B1 through B10.

### Technique Reference

#### B1: Shadows + Rounded Corners + Modern Card Styling

**What:** Add subtle drop shadows, rounded borders (8-12px), and accent bars to all visuals. Hides visual headers for a clean look.

**Applies to:** Every visual type (cards, charts, tables, slicers)

**Programmatic:** YES — fully automatable via layout JSON `vcObjects`

**Implementation (layout JSON per visual):**
```json
"vcObjects": {
  "border": [{
    "properties": {
      "show": {"expr": {"Literal": {"Value": "true"}}},
      "color": {"solid": {"color": "#E1DFDD"}},
      "width": {"expr": {"Literal": {"Value": "1L"}}},
      "radius": {"expr": {"Literal": {"Value": "10L"}}}
    }
  }],
  "dropShadow": [{
    "properties": {
      "show": {"expr": {"Literal": {"Value": "true"}}},
      "color": {"solid": {"color": "#000000"}},
      "position": {"expr": {"Literal": {"Value": "'outer'"}}},
      "preset": {"expr": {"Literal": {"Value": "'bottomRight'"}}},
      "transparency": {"expr": {"Literal": {"Value": "85D"}}},
      "shadowBlur": {"expr": {"Literal": {"Value": "6D"}}},
      "shadowDistance": {"expr": {"Literal": {"Value": "3D"}}},
      "shadowSpread": {"expr": {"Literal": {"Value": "0D"}}}
    }
  }],
  "background": [{
    "properties": {
      "show": {"expr": {"Literal": {"Value": "true"}}},
      "color": {"solid": {"color": "#FFFFFF"}},
      "transparency": {"expr": {"Literal": {"Value": "0D"}}}
    }
  }],
  "visualHeader": [{
    "properties": {
      "show": {"expr": {"Literal": {"Value": "false"}}}
    }
  }]
}
```

**Key settings:**
- `radius: 10L` — modern feel without being too rounded (8-12px range)
- `transparency: 85D` — subtle shadow (default is too harsh at 60)
- `shadowBlur: 6D`, `shadowDistance: 3D` — gentle lift effect
- `visualHeader.show: false` — hides the three-dot menu for cleaner look
- White background on gray page creates the "floating card" effect
- **Consistency rule:** Use identical radius, shadow, and padding across ALL visuals on a page

**Accent bars (new card visual only):**
Add a thick colored left-border on cards for visual hierarchy. Set via the card's `cards.borderShow` and custom border properties.

#### B2: Designed Background Images

**What:** Design the entire dashboard layout externally in PowerPoint, Figma, or Canva — with colored panels, sections, dividers, branding — then import as a canvas background image. Set visual backgrounds to transparent.

**Applies to:** Page-level (affects entire page appearance)

**Programmatic:** PARTIAL — page wallpaper can be set via section config, but the image must be designed externally

**Implementation approach:**
1. Create a 1280x720 (or 1920x1080) background image externally
2. Include visual "containers" as colored rectangles, header bars, navigation panels, brand logos
3. Export as PNG
4. Set as page wallpaper in the section config:

```json
// In section.config (parsed)
{
  "objects": {
    "wallpaper": [{
      "properties": {
        "image": {
          "image": {
            "url": {"expr": {"ResourcePackageItem": {"PackageName": "SharedResources", "ItemName": "bg_image.png"}}},
            "scaling": {"expr": {"Literal": {"Value": "'Fit'"}}}
          }
        },
        "transparency": {"expr": {"Literal": {"Value": "0D"}}}
      }
    }]
  }
}
```

5. Set all visual backgrounds to transparent so they sit on the designed canvas
6. Dark backgrounds + white text look striking but NOTE: PDF export does not include wallpaper

**Alternative — solid page background (simpler, fully programmatic):**
```json
// In section.config (parsed)
{
  "objects": {
    "background": [{
      "properties": {
        "color": {"solid": {"color": {"expr": {"Literal": {"Value": "'#F4F4F4'"}}}}},
        "transparency": {"expr": {"Literal": {"Value": "0D"}}}
      }
    }]
  }
}
```

**Resources:**
- [Power BI Backgrounds GitHub Tool](https://github.com/Zerg00s/Power-BI-Backgrounds) — Open-source SVG background generator
- [Figma Power BI UI Kit](https://www.figma.com/community/file/1108563240558755576/power-bi-backgrounds)
- PowerPoint: Set slide to 1280x720, design placeholders, export as PNG

#### B3: Color Theme JSON

**What:** Generate a branded theme JSON file with `dataColors`, `visualStyles`, `textClasses`, and semantic colors. Apply report-wide for instant consistency across every visual.

**Applies to:** All visuals globally

**Programmatic:** YES — fully automatable

**Implementation:** Generate and inject a theme JSON file. See the "Theme JSON Structure" and "Complete Executive Theme Template" sections above for full structure.

**Theme generation tools (for user reference):**
| Tool | URL |
|------|-----|
| PowerBI.tips Theme Generator | https://tools.powerbi.tips/themes/palette |
| Coolors to PBI Extension | https://www.vahiddm.com/post/coolors-to-powerbi-theme |
| BIBB Theme Generator | https://bibb.pro/post/power-bi-json-report-theme-generator-by-bibb/ |
| PowerBI Theme Templates (GitHub) | https://github.com/MattRudy/PowerBI-ThemeTemplates |

**Programmatic theme injection via binary rebuild:**
1. Generate the theme JSON in Python
2. Base64-encode or add as a resource in `Report/StaticResources/SharedResources/BaseThemes/`
3. Reference in layout config `themeCollection`

**Or apply via layout objects:** Set `visualStyles` properties directly in each visual's `singleVisual.objects` and `vcObjects` (the approach used in our enhance_visuals.py scripts).

#### B4: SVG Measures in DAX (Dynamic Icons & Sparklines)

**What:** Write SVG markup as a DAX measure, set data category to "Image URL", and PBI renders vector graphics inline. Creates dynamic arrows, traffic lights, progress bars, and sparklines without custom visuals.

**Applies to:** Cards, tables, matrices, slicers

**Programmatic:** YES — generate DAX measures and inject into modelExtensions

**Implementation — inject as report-level measures in modelExtensions:**

```python
# Arrow indicator measure
arrow_svg_dax = '''
VAR _Value = [YoY Growth]
VAR _Color = IF(_Value >= 0, "#28a745", "#dc3545")
VAR _Rotation = IF(_Value >= 0, "0", "180")
RETURN
"data:image/svg+xml;utf8," &
"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' width='24' height='24'>" &
"<polygon points='12,2 22,18 2,18' fill='" & _Color & "' transform='rotate(" & _Rotation & ",12,12)'/>" &
"</svg>"
'''

# Progress bar measure
progress_bar_dax = '''
VAR _Pct = [Completion Pct]
VAR _Width = ROUND(_Pct * 200, 0)
VAR _Color = SWITCH(TRUE(),
    _Pct >= 0.9, "#28a745",
    _Pct >= 0.6, "#ffc107",
    "#dc3545"
)
RETURN
"data:image/svg+xml;utf8," &
"<svg xmlns='http://www.w3.org/2000/svg' width='200' height='20'>" &
"<rect x='0' y='0' width='200' height='20' rx='10' fill='#e9ecef'/>" &
"<rect x='0' y='0' width='" & _Width & "' height='20' rx='10' fill='" & _Color & "'/>" &
"</svg>"
'''

# KPI dot measure
kpi_dot_dax = '''
VAR _Margin = [Profit Margin]
VAR _Color = SWITCH(TRUE(),
    _Margin > 0.25, "#28a745",
    _Margin > 0.10, "#ffc107",
    "#dc3545"
)
RETURN
"data:image/svg+xml;utf8," &
"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'>" &
"<circle cx='50' cy='50' r='40' fill='" & _Color & "'/>" &
"</svg>"
'''
```

**Measure definition in modelExtensions:**
```json
{
  "name": "Arrow SVG",
  "dataType": 6,
  "expression": "<DAX from above>",
  "hidden": false,
  "formatInformation": {"formatString": "G", "format": "General"},
  "displayFolder": "Indicators"
}
```

**Key rules:**
- Data category must be "Image URL" — set in PBI Desktop after opening the modified file
- `"data:image/svg+xml;utf8,"` prefix is required
- URL-encode special characters: `%23` for `#` in color codes (within the SVG attributes)
- Max ~32K characters per measure value
- Turn off totals row in tables (would show raw SVG text)
- Simpler alternative: `UNICHAR(9650)` / `UNICHAR(9660)` for up/down arrows with conditional font color

#### B5: Conditional Formatting (Gradient / Rules / DAX Color)

**What:** Dynamic formatting driven by data values — gradient color scales on table cells, rules-based color bands (red/yellow/green), and DAX measures that return hex colors.

**Applies to:** Tables, matrices, cards, charts (data point colors)

**Programmatic:** YES — stored in `singleVisual.objects` in layout JSON

**Implementation — three approaches:**

**1. Gradient (color scale) — via `fillRule` in objects:**
```json
"backColor": {
  "solid": {"color": {"expr": {"FillRule": {
    "Input": {"Aggregation": {
      "Expression": {"Column": {"Expression": {"SourceRef": {"Entity": "Sales"}}, "Property": "Revenue"}},
      "Function": 0
    }},
    "FillRule": {
      "linearGradient3": {
        "min": {"color": {"Literal": {"Value": "'#FFFFFF'"}}},
        "mid": {"color": {"Literal": {"Value": "'#B3D4FF'"}}},
        "max": {"color": {"Literal": {"Value": "'#005EB8'"}}}
      }
    }
  }}}}
}
```

**2. Rules-based — via `Conditional.Cases`:**
See the "Conditional Formatting in Layout JSON" section above for full JSON structure.

**3. DAX color measure (recommended for reusability):**
```dax
StatusColor =
SWITCH(TRUE(),
    [Variance%] >= 0.05, "#107C10",
    [Variance%] >= -0.05, "#797775",
    "#D13438"
)
```
Apply via:
```json
"fontColor": {
  "solid": {"color": {"expr": {
    "Measure": {
      "Expression": {"SourceRef": {"Entity": "TableName"}},
      "Property": "StatusColor"
    }
  }}}
}
```

**Dynamic divergent gradient (advanced DAX):**
```dax
HeatmapColor =
VAR _Value = [Metric]
VAR _Min = [Min Metric]
VAR _Max = [Max Metric]
VAR _Pct = DIVIDE(_Value - _Min, _Max - _Min, 0.5)
VAR _R = INT(255 * IF(_Pct < 0.5, 1, 2 * (1 - _Pct)))
VAR _G = INT(255 * IF(_Pct > 0.5, 1, 2 * _Pct))
VAR _B = 0
RETURN FORMAT(_R * 65536 + _G * 256 + _B, "\#000000")
```

#### B6: Deneb Custom Visuals (Vega/Vega-Lite)

**What:** Deneb is a Microsoft-certified, free marketplace visual that renders Vega or Vega-Lite JSON specifications. Unlocks chart types PBI doesn't have natively: beeswarm plots, bump charts, radial charts, Sankey diagrams, waffle charts, heatmaps.

**Applies to:** Any visual slot (replaces a native chart)

**Programmatic:** YES — Vega-Lite specs are JSON, can be generated in Python

**Implementation — requires the Deneb visual to be installed in the workspace:**

The Deneb visual must be added from AppSource first. Once present, visuals using it are stored in the layout JSON with `visualType` referencing the Deneb custom visual GUID. The Vega/Vega-Lite spec is stored in the visual's properties.

**Example Vega-Lite heatmap spec:**
```json
{
  "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
  "data": {"name": "dataset"},
  "mark": "rect",
  "encoding": {
    "x": {"field": "Month", "type": "ordinal"},
    "y": {"field": "Region", "type": "nominal"},
    "color": {
      "field": "Revenue", "type": "quantitative",
      "scale": {"scheme": "blues"}
    },
    "tooltip": [
      {"field": "Month"}, {"field": "Region"},
      {"field": "Revenue", "format": "$,.0f"}
    ]
  }
}
```

**Key facts:**
- Certified by Microsoft: exports to PDF, email, mobile, Report Server
- No external data leaves the report
- Integrates with PBI interactivity (tooltips, cross-filtering)
- Community templates: [PBI-David/Deneb-Showcase](https://github.com/PBI-David/Deneb-Showcase), [Vega-Lite Gallery](https://vega.github.io/vega-lite/examples/)

**Limitation for binary rebuild:** The Deneb custom visual package must already be registered in the report's `resourcePackages`. Adding a new custom visual programmatically to a .pbix requires modifying the resourcePackages array, which is complex but possible.

#### B7: Sparklines + KPI Indicators + Bullet Charts

**What:** Compact, information-dense micro-visualizations: native sparklines in table cells, KPI status indicators, and bullet charts showing actual vs. target with qualitative bands.

**Applies to:** Tables, matrices, KPI cards

**Programmatic:** PARTIAL — native sparklines configurable via layout JSON; marketplace KPI visuals need their packages registered

**Native sparklines (tables/matrices):**
- Add via column field dropdown > "Add a sparkline"
- Maximum 52 data points on X-axis
- Maximum 5 sparklines per visual
- Line or bar type
- Stored in the visual's `dataTransforms` and `query` configuration

**Marketplace visuals for enhanced KPIs:**
| Visual | What It Does |
|--------|-------------|
| KPI by Powerviz | 100+ templates, 16 layers, 40+ chart variations |
| Power KPI Matrix | Numerical values + status indicators + trend sparklines |
| SMART KPI List | Sparkline with bandwidth overlay + bullet graph |
| OKVIZ Bullet Chart | Actual bar + target marker + qualitative color bands |

**Design rule:** A well-designed KPI shows 3 things: actual, target, trend. If a stakeholder can't understand it in 5 seconds, simplify.

#### B8: Glassmorphism / Neumorphism Effects

**What:** Modern UI design trends. Glassmorphism = frosted-glass translucent panels with blur and depth. Neumorphism = soft shadows creating extruded "plastic" look. Both create premium visual depth.

**Applies to:** Page-level (background images with glass/soft-shadow panels)

**Programmatic:** PARTIAL — background images can be generated; HTML visual measures can be injected as DAX

**Glassmorphism implementation:**
1. Design background images with vibrant gradients externally
2. Create frosted-glass panel overlays (semi-transparent white rectangles with blur)
3. Import as page wallpaper
4. Set visual backgrounds to semi-transparent white

**Or via HTML custom visual + DAX measure:**
```dax
GlassPanel =
"<div style='
  background: rgba(255,255,255,0.15);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid rgba(255,255,255,0.25);
  border-radius: 12px;
  padding: 20px;
  color: white;
'>
  <h2>" & FORMAT([Revenue], "$#,##0") & "</h2>
  <p>Total Revenue</p>
</div>"
```

**Neumorphism implementation:**
- Generate component images using CSS (tools like neumorphism.io generate shadow values)
- Dual box-shadows: light (top-left highlight) + dark (bottom-right shadow) on matching background
- Export as PNG/SVG, use as background images

**Resources:**
- [BIBB Glassmorphism Tool](https://bibb.pro/post/modern-design-business-intelligence-glassmorphism-power-bi/)
- [Neumorphism in PBI (DataStud)](https://datastud.dev/posts/power-bi-neumorphism/)
- [Metricalist Glassmorphism Templates](https://metricalist.com/powerbi-solutions/category/power-bi-designs/glassmorphism/)

**Best for:** Executive dashboards where visual impression matters most. Not suitable for reports that need to be simple and scannable.

#### B9: Play Axis / Animated Data Storytelling

**What:** The Play Axis marketplace visual acts as an animated slicer — auto-cycles through time periods, animating all connected visuals. Bookmark-driven transitions create guided storytelling.

**Applies to:** Time-based data, sequential categories, presentations

**Programmatic:** PARTIAL — bookmarks stored as JSON in layout; Play Axis visual needs its package registered

**Bookmark-based storytelling (fully programmatic):**
1. Create bookmarks capturing different visual states (filter selections, visibility)
2. Add navigation buttons that switch between bookmarks
3. Configure transitions and spotlight effects

**Bookmark JSON structure in layout:**
```json
{
  "config": {
    "bookmarks": [{
      "name": "bk_overview",
      "displayName": "Overview",
      "explorationState": {
        "version": "1.2",
        "activeSection": "section_id",
        "filters": { "byExpr": [...] }
      },
      "options": {
        "targetVisualNames": [],
        "allVisuals": true,
        "displayOption": 0
      }
    }]
  }
}
```

**Play Axis (marketplace visual):**
- Install from AppSource (by mprozil)
- Drag a time-based field into the Play Axis area
- Controls: play, pause, stop, previous, next
- Customize: transition speed, display label, stop button

**Best for:** Presentations, wall displays, time-series exploration. Not recommended for self-service reports where users prefer manual navigation.

#### B10: Grid Layout System + Precise Spacing

**What:** Apply systematic grid-based layout with consistent spacing (8-point grid), proper padding (12-20px), and exact X/Y coordinate alignment for pixel-perfect visual placement.

**Applies to:** All visuals (position and size)

**Programmatic:** YES — visual positions (x, y, width, height) are in the layout JSON. **IMPORTANT:** Positions must be set in BOTH the top-level `vc.x/y/width/height` AND `config.layouts[0].position` — see Gotcha #18 and the Visual Container Skeleton section.

**8-Point Grid System:**
| Element | Value |
|---------|-------|
| Base unit | 8px |
| Tight spacing (related items) | 16px |
| Medium spacing (visual groups) | 24px |
| Section separation / page margins | 32px |
| Card padding | 24px |
| Canvas size | 1280x720 or 1664x936 |
| Max visuals per page | 6-8 |

**Implementation — calculate positions programmatically:**
```python
def grid_layout(canvas_w=1280, canvas_h=720, margin=32, gap=16, cols=3, rows=3):
    """Calculate visual positions on an 8px grid."""
    usable_w = canvas_w - 2 * margin - (cols - 1) * gap
    usable_h = canvas_h - 2 * margin - (rows - 1) * gap
    cell_w = int(usable_w / cols / 8) * 8  # Snap to 8px grid
    cell_h = int(usable_h / rows / 8) * 8

    positions = []
    for row in range(rows):
        for col in range(cols):
            x = margin + col * (cell_w + gap)
            y = margin + row * (cell_h + gap)
            positions.append({"x": x, "y": y, "width": cell_w, "height": cell_h})
    return positions

# Example: 3-column layout for KPI cards across the top
card_positions = grid_layout(cols=4, rows=1, margin=32, gap=16)
# Returns: [{"x": 32, "y": 32, "width": 288, "height": 648}, ...]
```

**Spacing calculator for fine-tuning:**
```python
def calculate_spacing(canvas_w, margin, gap, num_visuals, visual_widths):
    """Verify total width fits within canvas."""
    total = 2 * margin + sum(visual_widths) + (num_visuals - 1) * gap
    assert total <= canvas_w, f"Overflow: {total} > {canvas_w}"
    return total
```

**Visual hierarchy Z-order:**
- Background shapes: z=0-999
- Content visuals: z=1000+ (increment by 1000)
- Overlay elements (navigation, tooltips): z=10000+

### Beautification Technique Summary

| ID | Technique | Impact | Programmatic | When to Use |
|----|-----------|--------|:------------:|-------------|
| B1 | Shadows + Rounded Corners | Very High | Full | Always — universal improvement |
| B2 | Background Images | Very High | Partial | Executive dashboards, branded reports |
| B3 | Color Theme JSON | High | Full | Always — ensures consistency |
| B4 | SVG Measures (icons) | High | Full | Reports with KPIs, status indicators |
| B5 | Conditional Formatting | High | Full | Reports with tables, matrices, comparisons |
| B6 | Deneb (Vega/Vega-Lite) | Very High | Full (JSON) | When native charts are insufficient |
| B7 | Sparklines + KPI | High | Partial | Dense KPI dashboards, scorecards |
| B8 | Glassmorphism | Medium-High | Partial | Premium executive presentations |
| B9 | Play Axis / Animation | Medium | Partial | Time-series storytelling, presentations |
| B10 | Grid Layout System | Medium | Full | Every report — foundational good design |

### Default Auto-Selection Logic

When the user selects "Auto" mode, analyze the report and pick the top 3:

```python
def select_beautification_techniques(layout):
    """Analyze report and return the 3 most impactful techniques."""
    selected = ["B1"]  # Always include shadows + rounded corners

    visual_types = set()
    for section in layout.get('sections', []):
        for vc in section.get('visualContainers', []):
            if 'config' in vc:
                cfg = json.loads(vc['config'])
                vtype = cfg.get('singleVisual', {}).get('visualType', '')
                visual_types.add(vtype)

    has_tables = bool(visual_types & {'tableEx', 'pivotTable'})
    has_cards = bool(visual_types & {'card', 'cardVisual', 'multiRowCard', 'kpi'})
    has_charts = bool(visual_types & {
        'lineChart', 'areaChart', 'barChart', 'clusteredBarChart',
        'columnChart', 'clusteredColumnChart', 'pieChart', 'donutChart',
        'scatterChart', 'waterfallChart', 'funnel', 'gauge'
    })
    num_pages = len(layout.get('sections', []))

    # Pick 2nd technique
    if has_tables:
        selected.append("B5")  # Conditional formatting transforms tables
    elif has_cards:
        selected.append("B4")  # SVG icons make cards compelling
    else:
        selected.append("B3")  # Theme ensures consistency

    # Pick 3rd technique
    if "B3" not in selected and (has_charts or num_pages > 2):
        selected.append("B3")  # Theme for multi-page/chart consistency
    elif "B5" not in selected and has_tables:
        selected.append("B5")  # Conditional formatting
    elif "B4" not in selected and has_cards:
        selected.append("B4")  # SVG indicators
    else:
        selected.append("B10")  # Grid layout as universal fallback

    return selected[:3]
```

### Applying Beautification to Existing Reports

When beautifying an existing report (not building from scratch):

1. **Extract** the current layout from the .pbix
2. **Analyze** visual types to determine applicable techniques
3. **Interview** the user (or use auto-selection)
4. **Apply** selected techniques by modifying `objects`, `vcObjects`, and `config` in the layout JSON
5. **Preserve** all existing queries, dataTransforms, filters, and measures — beautification is formatting-only
6. **Rebuild** using the binary ZIP approach
7. **Verify** the output opens correctly in PBI Desktop

**Safety rules:**
- NEVER modify `query`, `dataTransforms`, or `filters` during beautification
- ONLY modify `objects`, `vcObjects`, and section `config` (page backgrounds)
- Back up the .pbix before applying changes
- Test with PBI Desktop after every rebuild

## PBIR — Power BI Enhanced Report Format

PBIR is the next-generation report format where each page, visual, and bookmark is stored as a separate JSON file in a folder structure. This replaces the monolithic `Report/Layout` JSON blob. PBIR is currently in preview but **will become the only supported format at GA**.

### Why PBIR Matters
- Each visual is a separate `visual.json` file — no more parsing a 500KB monolithic layout
- Proper JSON schemas with VS Code autocomplete and validation
- Git-friendly diffs — changes to one visual don't affect other files
- Copy/paste visuals between reports by copying folders
- Batch operations via scripts across all visuals
- No binary ZIP manipulation needed — just plain files on disk

### PBIR Folder Structure
```
MyReport.Report/
  definition/
    report.json                    # Report-level settings, theme, filters
    reportExtensions.json          # Report-level measures (replaces modelExtensions)
    version.json                   # PBIR version metadata
    pages/
      pages.json                   # Page order and active page
      SalesOverview/
        page.json                  # Page size, background, page-level filters
        visuals/
          revenue_card/
            visual.json            # Visual type, position, query, formatting
          sales_chart/
            visual.json
      PriceHistory/
        page.json
        visuals/
          ...
    bookmarks/
      bookmarks.json               # Bookmark order and groups
      [bookmarkName].bookmark.json # Individual bookmark state
  definition.pbir                  # Semantic model reference
  StaticResources/
    RegisteredResources/           # Themes, images, custom visuals
  .platform                        # Fabric Git integration metadata
```

### Key PBIR Files

**`definition.pbir`** — Semantic model reference:
```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definitionProperties/2.0.0/schema.json",
  "version": "4.0",
  "datasetReference": {
    "byPath": { "path": "../Sales.Dataset" }
  }
}
```

For live connection to a remote model:
```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definitionProperties/2.0.0/schema.json",
  "version": "4.0",
  "datasetReference": {
    "byConnection": {
      "connectionString": "Data Source=\"powerbi://api.powerbi.com/v1.0/myorg/[WorkspaceName]\";initial catalog=[SemanticModelName];access mode=readonly;integrated security=ClaimsToken;semanticmodelid=[SemanticModelId]"
    }
  }
}
```

**`report.json`** — Report settings and theme:
```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/report/1.0.0/schema.json",
  "themeCollection": {
    "baseTheme": {
      "name": "CY24SU06",
      "reportVersionAtImport": "5.55",
      "type": "SharedResources"
    }
  },
  "annotations": [
    { "name": "defaultPage", "value": "c2d9b4b1487b2eb30e98" }
  ]
}
```

**`reportExtensions.json`** — Report-level measures (equivalent to `modelExtensions` in the legacy format):
Schema: [https://github.com/microsoft/json-schemas/tree/main/fabric/item/report/definition/reportExtension](https://github.com/microsoft/json-schemas/tree/main/fabric/item/report/definition/reportExtension)

**`page.json`** — Page definition:
Schema: [https://github.com/microsoft/json-schemas/tree/main/fabric/item/report/definition/page](https://github.com/microsoft/json-schemas/tree/main/fabric/item/report/definition/page)

**`visual.json`** — Individual visual (position, type, query, formatting):
Schema: [https://github.com/microsoft/json-schemas/tree/main/fabric/item/report/definition/visualContainer](https://github.com/microsoft/json-schemas/tree/main/fabric/item/report/definition/visualContainer)

### Enabling PBIR

**For PBIP files:**
1. File > Options and settings > Options > Preview features
2. Check "Store reports using enhanced metadata format (PBIR)"

**For PBIX files:**
1. File > Options and settings > Options > Preview features
2. Check "Store PBIR reports using enhanced metadata format (PBIR)"

### PBIR Naming Convention
By default, pages, visuals, and bookmarks use 20-character unique identifiers (e.g., `90c2e07d8e84e7d5c026`). These can be renamed to descriptive names — the name must consist of word characters, digits, underscores, or hyphens.

### PBIR Annotations
Pages, visuals, and reports support `annotations` — name-value pairs that Power BI Desktop ignores but external scripts can use:
```json
"annotations": [
  { "name": "category", "value": "executive-dashboard" },
  { "name": "owner", "value": "analytics-team" }
]
```

### PBIR Limitations (Preview)
- Large reports with 500+ files may have authoring performance issues
- 1,000 max pages, 1,000 max visuals per page
- 300 MB max for all report files
- Once converted from legacy, cannot revert via UI (backup is created)

### PBIR vs Binary ZIP (.pbix) Approach
| Aspect | PBIR (Folder) | .pbix (Binary ZIP) |
|--------|---------------|-------------------|
| Format | Plain JSON files on disk | ZIP archive with UTF-16-LE encoded monolithic layout |
| Git-friendly | Each visual is a separate file | Entire layout changes on any edit |
| Tooling | VS Code with schema validation | Custom Python scripts |
| SecurityBindings | Not needed | Must be removed when modifying |
| Current Status | Preview (will become mandatory at GA) | Current production format |
| Use When | New projects, PBIP workflows, Fabric Git integration | Existing .pbix files, legacy workflows |

**Recommendation:** For new projects, consider using PBIR format if your team uses PBIP/Fabric Git integration. For modifying existing .pbix files, continue using the binary ZIP rebuild approach documented above.

## TMDL — Tabular Model Definition Language

TMDL is a human-readable, text-based format for defining Power BI semantic models. It uses YAML-like indentation syntax and is much easier to read/write than TMSL (JSON). TMDL maps 1:1 to the Tabular Object Model (TOM).

### TMDL Folder Structure
```
MyModel.SemanticModel/
  definition/
    database.tmdl              # Database config
    model.tmdl                 # Model config, culture, ref tables
    relationships.tmdl         # All relationships
    expressions.tmdl           # Parameters, shared queries
    tables/
      Sales.tmdl               # Table with columns, measures, partitions
      Product.tmdl
      Calendar.tmdl
    roles/
      role1.tmdl
    cultures/
      en-US.tmdl
```

### TMDL Syntax Examples

**Table with measures and columns:**
```tmdl
table Sales

    partition 'Sales-Partition' = m
        mode: import
        source =
            let
                Source = Sql.Database(Server, Database)
            in
                finalStep

    measure 'Sales Amount' = SUMX('Sales', 'Sales'[Quantity] * 'Sales'[Net Price])
        formatString: $ #,##0

    measure 'Sales YTD' =
            var result = TOTALYTD([Sales Amount], 'Calendar'[Date])
            return result
        formatString: $ #,##0

    column 'Product Key'
        dataType: int64
        isHidden
        sourceColumn: ProductKey
        summarizeBy: None

    column Quantity
        dataType: int64
        sourceColumn: Quantity
```

**Relationships:**
```tmdl
relationship cdb6e6a9-c9d1-42b9-b9e0-484a1bc7e123
    fromColumn: Sales.'Product Key'
    toColumn: Product.'Product Key'
```

**Expressions (parameters):**
```tmdl
expression Server = "localhost" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]
expression Database = "Contoso" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]
```

### TMDL Key Rules
- Indentation is strict (single tab per level)
- Object names with special characters must be enclosed in single quotes (`'My Measure'`)
- Default properties (like measure expressions) use `=` delimiter
- Non-expression properties use `:` delimiter
- Multi-line expressions must be indented one level deeper than parent properties
- Boolean properties can use shortcut syntax: `isHidden` implies `isHidden: true`
- Descriptions use triple-slash: `/// This is a description`

## MCP Servers for Power BI

Two MCP servers are available for AI-assisted Power BI development:

### Microsoft Power BI Modeling MCP Server
- **Repo:** [microsoft/powerbi-modeling-mcp](https://github.com/microsoft/powerbi-modeling-mcp)
- **Purpose:** Semantic model operations — tables, columns, measures, relationships, DAX queries
- **26 tools** covering: connection to local PBI Desktop AS instance or Fabric workspace, DAX query generation/execution/analysis, TMDL loading, bulk operations (rename, refactor, translate)
- **Scope:** Metadata and DAX only — does NOT modify report pages or visuals
- **Safety:** Requires user approval before first modification/query via MCP Elicitation protocol
- **Install:** VS Code extension (recommended) or manual MCP client config
- **Best for:** Writing DAX measures, building semantic models, querying data, applying modeling best practices

### SARA Power BI MCP Server (Community)
- **Repo:** [mateuscbrito/powerbi-server](https://github.com/mateuscbrito/powerbi-server)
- **Purpose:** Programmatic control over PBIR reports, semantic models, AND visual management
- **Capabilities:** Report refactoring, visual creation/management, auditing, DAX operations
- **Requires:** Windows, Power BI Desktop, Python 3.10+, PBIP save format enabled
- **Best for:** Full report automation including visual layout (covers both model and report layers)

### Other Tools

| Tool | Purpose | Link |
|------|---------|------|
| **pbi-tools** | CLI to compile PBIR back to .pbit (openable in PBI Desktop) | [pbi.tools](https://pbi.tools/cli/) |
| **pbir_tools** (Python) | Python library for PBIR report creation | [david-iwdb/pbir_tools](https://github.com/david-iwdb/pbir_tools) |
| **PBI Inspector** | Layout JSON inspection and testing | [NatVanG/PBI-Inspector](https://github.com/NatVanG/PBI-Inspector) |

### PBIR JSON Schemas (for validation)
All schemas published at: [https://github.com/microsoft/json-schemas/tree/main/fabric/item/report/definition](https://github.com/microsoft/json-schemas/tree/main/fabric/item/report/definition)

Individual schemas:
- Visual: `visualContainer` schema
- Page: `page` schema
- Report: `report` schema
- Bookmarks: `bookmark` and `bookmarksMetadata` schemas
- Report extensions: `reportExtension` schema

---

## Best Practice Analyzer (BPA) Rule Authoring

BPA rules are the primary mechanism for enforcing data model quality standards in Power BI semantic models. Rules are defined as JSON and evaluated by Tabular Editor using Dynamic LINQ expressions against the Tabular Object Model (TOM).

### BPA Rule JSON Structure

Each rule is a JSON object within an array:

```json
[
  {
    "ID": "RULE_ID_UPPERCASE",
    "Name": "Human-readable rule name",
    "Category": "Performance",
    "Severity": 3,
    "Scope": "Measure",
    "Expression": "DynamicLINQ expression returning true for violations",
    "Description": "Why this rule matters and how to fix violations.",
    "CompatibilityLevel": 1200
  }
]
```

### Rule Fields

| Field | Type | Description |
|-------|------|-------------|
| `ID` | string | Unique identifier, UPPER_SNAKE_CASE (e.g., `UNUSED_HIDDEN_COLUMNS`) |
| `Name` | string | Display name shown in BPA results |
| `Category` | string | Grouping: `Performance`, `DAX Expressions`, `Naming Conventions`, `Formatting`, `Maintenance`, `Error Prevention`, `Metadata` |
| `Severity` | int | `1` = Info, `2` = Warning, `3` = Error |
| `Scope` | string | TOM object type to evaluate: `Model`, `Table`, `Column`, `Measure`, `Hierarchy`, `Level`, `Relationship`, `Perspective`, `Culture`, `Partition`, `DataSource`, `Role`, `CalculationGroup`, `CalculationItem`, `KPI` |
| `Expression` | string | Dynamic LINQ expression. Returns `true` for objects that VIOLATE the rule. |
| `Description` | string | Explanation shown to the user when a violation is found |
| `CompatibilityLevel` | int | Minimum compatibility level (1200 for most, 1400+ for some features) |
| `FixExpression` | string | (Optional) Dynamic LINQ expression that auto-fixes the violation |

### Dynamic LINQ Expression Syntax

BPA expressions are evaluated against each object matching the `Scope`. The object is the implicit context (`this`).

**Common properties by scope:**

| Scope | Properties |
|-------|-----------|
| `Column` | `Name`, `DataType`, `IsHidden`, `DisplayFolder`, `Description`, `Table.Name`, `IsKey`, `SortByColumn`, `SourceColumn`, `Type` (Calculated, Data, RowNumber) |
| `Measure` | `Name`, `Expression`, `DisplayFolder`, `Description`, `IsHidden`, `FormatString`, `KPI`, `Table.Name` |
| `Table` | `Name`, `Description`, `IsHidden`, `Columns`, `Measures`, `Partitions`, `CalculationGroup` |
| `Relationship` | `FromTable.Name`, `FromColumn.Name`, `ToTable.Name`, `ToColumn.Name`, `IsActive`, `CrossFilteringBehavior` |
| `Partition` | `Name`, `SourceType`, `Expression`, `Table.Name`, `Mode` |

**String methods:** `.Contains("x")`, `.StartsWith("x")`, `.EndsWith("x")`, `.ToUpper()`, `.ToLower()`, `.Length`, `.Trim()`

**Collection methods:** `.Any(expr)`, `.All(expr)`, `.Count()`, `.Count(expr)`

**Logical operators:** `and`, `or`, `not`, `==`, `!=`, `<`, `>`, `<=`, `>=`

**Special methods:**
- `RegEx.IsMatch(property, "pattern")` — regex matching
- `DependsOn.Any(Key.ObjectType == ObjectType.Column)` — dependency analysis
- `ReferencedBy.Count == 0` — find unused objects
- `Model.Tables.Any(...)` — access the full model from any object
- `Tokenize()` — splits DAX expressions into tokens for analysis

### Production-Ready BPA Rules

#### Performance Rules

```json
{
  "ID": "REMOVE_UNUSED_HIDDEN_COLUMNS",
  "Name": "Remove unused hidden columns",
  "Category": "Performance",
  "Severity": 2,
  "Scope": "Column",
  "Expression": "IsHidden and ReferencedBy.Count == 0 and not UsedInSortBy.Any() and not UsedInGroupBy.Any() and not UsedInHierarchies.Any() and not Table.Columns.Any(SortByColumn == outerIt) and Type.ToString() != \"RowNumber\"",
  "Description": "Hidden columns that are not referenced by any measure, relationship, sort-by, group-by, or hierarchy consume memory without providing value. Remove them to reduce model size."
}
```

```json
{
  "ID": "AVOID_BIDIRECTIONAL_RELATIONSHIPS",
  "Name": "Avoid bi-directional relationships",
  "Category": "Performance",
  "Severity": 2,
  "Scope": "Relationship",
  "Expression": "CrossFilteringBehavior == CrossFilteringBehavior.BothDirections",
  "Description": "Bi-directional cross-filtering can cause ambiguous filter paths and performance degradation. Use single-direction filtering and explicit CROSSFILTER() in DAX where needed."
}
```

```json
{
  "ID": "AVOID_CALCULATED_COLUMNS",
  "Name": "Prefer measures over calculated columns",
  "Category": "Performance",
  "Severity": 1,
  "Scope": "Column",
  "Expression": "Type == ColumnType.Calculated and not IsHidden",
  "Description": "Visible calculated columns are computed during refresh and stored in memory. Consider replacing with measures (computed at query time) to reduce model size, unless the column is needed for sorting, filtering, or relationships."
}
```

```json
{
  "ID": "REDUCE_COLUMNS_WITH_HIGH_CARDINALITY",
  "Name": "Review high-cardinality text columns",
  "Category": "Performance",
  "Severity": 1,
  "Scope": "Column",
  "Expression": "not IsHidden and DataType == DataType.String and Statistics.DistinctValueCount > 1000000",
  "Description": "Text columns with over 1M distinct values significantly increase model size. Consider hashing, grouping, or removing if not needed for end-user filtering."
}
```

#### DAX Expression Rules

```json
{
  "ID": "NO_CALCULATE_WITHOUT_FILTER",
  "Name": "CALCULATE should have at least one filter argument",
  "Category": "DAX Expressions",
  "Severity": 2,
  "Scope": "Measure",
  "Expression": "RegEx.IsMatch(Expression, \"(?i)CALCULATE\\s*\\(\\s*[^,)]+\\s*\\)\")",
  "Description": "CALCULATE() without filter arguments performs an implicit context transition. While sometimes intentional, it is often a mistake. Add explicit filter arguments or remove the CALCULATE wrapper."
}
```

```json
{
  "ID": "AVOID_IFERROR_ISERROR",
  "Name": "Avoid IFERROR and ISERROR",
  "Category": "DAX Expressions",
  "Severity": 2,
  "Scope": "Measure",
  "Expression": "RegEx.IsMatch(Expression, \"(?i)(IFERROR|ISERROR)\\s*\\(\")",
  "Description": "IFERROR/ISERROR evaluate the expression twice — once to check for error and once for the result. Use DIVIDE() for division-by-zero scenarios, or IF+ISBLANK for null checks."
}
```

```json
{
  "ID": "USE_DIVIDE_FUNCTION",
  "Name": "Use DIVIDE instead of / operator",
  "Category": "DAX Expressions",
  "Severity": 1,
  "Scope": "Measure",
  "Expression": "RegEx.IsMatch(Expression, \"[^/]/[^/\\*]\")",
  "Description": "The / operator throws an error on division by zero. DIVIDE() handles it gracefully with an optional alternate result. Replace x/y with DIVIDE(x, y)."
}
```

#### Naming Convention Rules

```json
{
  "ID": "NO_TECHNICAL_PREFIXES_ON_MEASURES",
  "Name": "Measures should not have technical prefixes",
  "Category": "Naming Conventions",
  "Severity": 2,
  "Scope": "Measure",
  "Expression": "RegEx.IsMatch(Name, \"^(m_|msr_|measure_|calc_|dax_)\")",
  "Description": "Measure names appear directly in reports. Use human-readable names without technical prefixes. Example: 'Total Revenue' instead of 'm_TotalRevenue'."
}
```

```json
{
  "ID": "NO_SPECIAL_CHARS_IN_MEASURE_NAMES",
  "Name": "Measure names should not contain special characters",
  "Category": "Naming Conventions",
  "Severity": 2,
  "Scope": "Measure",
  "Expression": "RegEx.IsMatch(Name, \"[^a-zA-Z0-9 %$#()_-]\")",
  "Description": "Special characters in measure names can cause issues with DAX references and report URLs. Use only alphanumeric characters, spaces, and common symbols (%, $, #, parentheses)."
}
```

#### Metadata Rules

```json
{
  "ID": "MEASURES_SHOULD_HAVE_DESCRIPTIONS",
  "Name": "Provide descriptions for visible measures",
  "Category": "Metadata",
  "Severity": 1,
  "Scope": "Measure",
  "Expression": "not IsHidden and string.IsNullOrWhiteSpace(Description)",
  "Description": "Visible measures should have descriptions to help report authors understand what they calculate. Add a Description property explaining the business logic."
}
```

```json
{
  "ID": "MEASURES_SHOULD_HAVE_FORMAT_STRINGS",
  "Name": "Measures should have format strings",
  "Category": "Formatting",
  "Severity": 2,
  "Scope": "Measure",
  "Expression": "not IsHidden and string.IsNullOrWhiteSpace(FormatString)",
  "Description": "Measures without format strings display raw numbers. Add a FormatString (e.g., '$#,##0.00', '0.0%', '#,##0') for proper display in reports."
}
```

### Rule Source Locations

BPA rules can be loaded from multiple sources (evaluated in this priority order):

| Source | Location | Scope |
|--------|----------|-------|
| Model-embedded | `Model.Database.GetAnnotation("TabularEditor_BestPracticeRules")` | Per-model |
| User-level | `%LocalAppData%\TabularEditor3\BPARules.json` | Per-user |
| Machine-level | `C:\Program Files\Tabular Editor 3\BPARules.json` | All users |
| URL (TE3 Preferences) | Configured in Preferences.json under `BpaRulesUrls` | Remote |
| Built-in | Packaged with Tabular Editor | Default |

### Applying BPA Rules

**In Tabular Editor 3 UI:**
1. Model menu > Manage BPA Rules
2. Add rules from file, URL, or create new
3. Run: Model > Best Practice Analyzer (Ctrl+B)

**Via CLI (for CI/CD):**
```bash
TabularEditor.exe Model.bim -A BPARules.json -O SarifOutput.sarif
```

**Via C# Script:**
```csharp
var rules = RuleDefinition.FromJson(File.ReadAllText("BPARules.json"));
var analyzer = new Analyzer(Model, rules);
var results = analyzer.Analyze();
foreach (var result in results) {
    Info($"{result.Rule.Severity}: {result.ObjectName} - {result.Rule.Name}");
}
```

### TE3 Compatibility Notes

- Use `\r\n` (CRLF) line endings in rule JSON files on Windows
- Regex in Dynamic LINQ uses .NET regex syntax, not JavaScript
- Valid `Scope` values are exact TOM type names (case-sensitive)
- `FixExpression` executes as a Dynamic LINQ statement (not expression) — use `Name = "new_name"` syntax
- Rules with `Severity: 3` cause non-zero exit code in CLI mode (useful for CI/CD build gates)

---

## PBIP Cascading Rename Operations

When renaming tables, columns, or measures in a PBIP project, changes must cascade across multiple file types. Missing any location causes broken references.

### 12-Step Rename Cascade

Follow this checklist whenever renaming a table, column, or measure:

#### Step 1: TMDL Declaration
Update the object declaration in `tables/<TableName>.tmdl`:
```tmdl
// Renaming a column:
column 'New Column Name'        // was 'Old Column Name'
    sourceColumn: NewColumnName  // update if source also changed

// Renaming a table: rename the file itself
// tables/OldTableName.tmdl → tables/NewTableName.tmdl
```

#### Step 2: model.tmdl References
Update any `ref` entries in `definition/model.tmdl`:
```tmdl
ref table 'New Table Name'    // was 'Old Table Name'
```

#### Step 3: relationships.tmdl
Update relationship endpoints in `definition/relationships.tmdl`:
```tmdl
relationship <guid>
    fromColumn: 'New Table Name'.'New Column Name'
    toColumn: OtherTable.ForeignKey
```

#### Step 4: DAX Expressions in SemanticModel
Search ALL `.tmdl` files for DAX references:
- `'Old Table Name'[Old Column Name]` → `'New Table Name'[New Column Name]`
- `[Old Measure Name]` → `[New Measure Name]`
- Check: measure expressions, calculated column expressions, calculated table expressions, KPI expressions

#### Step 5: DAX Expressions in Report
Search `definition/pages/*/visuals/*/visual.json` for DAX in:
- Query expressions
- Conditional formatting expressions
- Tooltip measure references
- Extension block measure definitions

#### Step 6: visual.json — Entity References
In each `visual.json`, update the `Entity` property in data role mappings:
```json
{"Entity": "New Table Name", "Property": "New Column Name"}
```

#### Step 7: visual.json — queryRef References
Update `queryRef` strings that reference the old name:
```json
"queryRef": "New Table Name.New Column Name"
```
Also check `nativeQueryRef` properties.

#### Step 8: visual.json — SparklineData Metadata Selectors
SparklineData uses a non-obvious metadata format:
```json
"metadata": {
  "columns": {
    "New Table Name.New Column Name": {"roles": {"Category": true}}
  }
}
```
This is the most commonly missed location during renames.

#### Step 9: page.json Filters
Update page-level filter definitions in `pages/<PageName>/page.json`:
```json
{"target": {"table": "New Table Name", "column": "New Column Name"}}
```

#### Step 10: reportExtensions.json
Update report-level measure definitions:
```json
{
  "entities": [{
    "name": "New Table Name",
    "extends": "New Table Name",
    "measures": [...]
  }]
}
```

#### Step 11: semanticModelDiagramLayout.json
Update table/column positions in the diagram layout file. Not critical for functionality but avoids confusion in the diagram view.

#### Step 12: Culture Files (Linguistic Metadata)
Update `cultures/<locale>.tmdl` if linguistic metadata references the old name. This affects Q&A natural language queries.

### Rename Search Script

Use this to find all references before renaming:

```python
import os, re, json

def find_all_references(project_root, old_name):
    """Find all files in a PBIP project that reference a given name."""
    hits = []
    for root, dirs, files in os.walk(project_root):
        dirs[:] = [d for d in dirs if d not in {'.git', '.pbi', 'node_modules'}]
        for f in files:
            if f.endswith(('.tmdl', '.json', '.tmd')):
                path = os.path.join(root, f)
                with open(path, 'r', encoding='utf-8') as fh:
                    content = fh.read()
                    if old_name in content:
                        lines = [i+1 for i, line in enumerate(content.split('\n')) if old_name in line]
                        hits.append((path, lines))
    return hits

# Usage:
# refs = find_all_references("MyProject.Report", "Old Column Name")
# for path, lines in refs:
#     print(f"  {path}: lines {lines}")
```

### DAX Query File Locations (Dual Location)

DAX query files can exist in TWO locations within a PBIP project:
1. `<Report>.Report/definition/` — report-level queries
2. `<SemanticModel>.SemanticModel/definition/` — model-level queries

**Both must be checked during renames.** This dual location is a common gotcha.

---

## Tabular Editor CLI for CI/CD

Tabular Editor (TE2 open-source, TE3 commercial) provides a CLI for automated deployment, BPA analysis, and format conversion in CI/CD pipelines.

### CLI Command Reference

```bash
# Basic syntax
TabularEditor.exe <input> [<output>] [options]
```

#### Input Formats
| Flag | Format | Example |
|------|--------|---------|
| (positional) | .bim file | `Model.bim` |
| (positional) | TMDL folder | `./definition/` |
| (positional) | .pbit file | `Template.pbit` |
| `-S "provider=..."` | Live AS connection | `"provider=MSOLAP;Data Source=localhost:54321"` |

#### Deployment Flags

| Flag | Description |
|------|-------------|
| `-D <server> <database>` | Deploy to Analysis Services / Fabric |
| `-O` | Overwrite existing model (required for updates) |
| `-C` | Deploy connections (data sources) |
| `-R` | Deploy role members |
| `-M` | Deploy model-level security |
| `-E` | Deploy effective permissions |
| `-P` | Deploy partitions (use with caution — can trigger full refresh) |

**Deploy to Fabric workspace:**
```bash
TabularEditor.exe ./definition/ -D "powerbi://api.powerbi.com/v1.0/myorg/WorkspaceName" "DatasetName" -O -C -R
```

**Deploy with service principal:**
```bash
TabularEditor.exe ./definition/ ^
  -D "powerbi://api.powerbi.com/v1.0/myorg/WorkspaceName" "DatasetName" ^
  -O -C ^
  -A "AppId=<client-id>;TenantId=<tenant-id>;AppSecret=<client-secret>"
```

#### Script Execution

```bash
# Run a C# script against a model
TabularEditor.exe Model.bim -S script.csx

# Run script and save result
TabularEditor.exe Model.bim -S script.csx -B OutputModel.bim
```

#### BPA Analysis

```bash
# Run BPA and output as SARIF (for Azure DevOps / GitHub code scanning)
TabularEditor.exe Model.bim -A BPARules.json -O Results.sarif

# Run BPA with exit code on errors (Severity 3 = non-zero exit)
TabularEditor.exe Model.bim -A BPARules.json
echo Exit code: %ERRORLEVEL%
```

SARIF output integrates with:
- Azure DevOps SARIF SAST Scans Tab extension
- GitHub Code Scanning (upload via `github/codeql-action/upload-sarif`)

#### Format Conversion

```bash
# BIM to TMDL
TabularEditor.exe Model.bim -T ./tmdl_output/

# TMDL to BIM
TabularEditor.exe ./definition/ -B Model.bim

# BIM to PBIP
TabularEditor.exe Model.bim -PBIP ./project_output/

# Schema comparison (diff two models)
TabularEditor.exe Model_v1.bim -DIFF Model_v2.bim
```

### Authentication Methods

| Method | Flag | Use Case |
|--------|------|----------|
| Windows Integrated | (default) | Local development |
| Service Principal | `-A "AppId=...;TenantId=...;AppSecret=..."` | CI/CD pipelines |
| Interactive (Azure AD) | `-A "Interactive"` | Manual one-time operations |
| Access Token | `-A "AccessToken=<token>"` | When token is pre-acquired |

### Azure DevOps Pipeline YAML

```yaml
trigger:
  branches:
    include: [main]
  paths:
    include: ['SemanticModel/**']

pool:
  vmImage: 'windows-latest'

variables:
  - group: 'PBI-ServicePrincipal'  # Contains CLIENT_ID, CLIENT_SECRET, TENANT_ID

steps:
  - task: PowerShell@2
    displayName: 'Install Tabular Editor CLI'
    inputs:
      targetType: inline
      script: |
        dotnet tool install TabularEditor.TOMWrapper.NetCore --global
        # Or download TE2 portable:
        # Invoke-WebRequest -Uri "https://github.com/TabularEditor/TabularEditor/releases/latest/download/TabularEditor.Portable.zip" -OutFile TE.zip
        # Expand-Archive TE.zip -DestinationPath .\TE

  - task: PowerShell@2
    displayName: 'Run BPA Analysis'
    inputs:
      targetType: inline
      script: |
        TabularEditor.exe ./SemanticModel/definition/ `
          -A ./BPARules.json `
          -O $(Build.ArtifactStagingDirectory)/bpa-results.sarif
        if ($LASTEXITCODE -ne 0) {
          Write-Error "BPA analysis found errors (Severity 3 violations)"
          exit 1
        }

  - task: PublishBuildArtifacts@1
    displayName: 'Publish SARIF Results'
    inputs:
      PathtoPublish: '$(Build.ArtifactStagingDirectory)/bpa-results.sarif'
      ArtifactName: 'BPA-Results'

  - task: PowerShell@2
    displayName: 'Deploy to Fabric'
    condition: and(succeeded(), eq(variables['Build.SourceBranch'], 'refs/heads/main'))
    inputs:
      targetType: inline
      script: |
        TabularEditor.exe ./SemanticModel/definition/ `
          -D "powerbi://api.powerbi.com/v1.0/myorg/$(WORKSPACE_NAME)" "$(DATASET_NAME)" `
          -O -C -R `
          -A "AppId=$(CLIENT_ID);TenantId=$(TENANT_ID);AppSecret=$(CLIENT_SECRET)"
```

### GitHub Actions Workflow

```yaml
name: PBI Model CI/CD
on:
  push:
    branches: [main]
    paths: ['SemanticModel/**']

jobs:
  validate-and-deploy:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install Tabular Editor
        run: dotnet tool install TabularEditor.TOMWrapper.NetCore --global

      - name: Run BPA
        run: |
          TabularEditor.exe ./SemanticModel/definition/ -A ./BPARules.json -O bpa.sarif
          if ($LASTEXITCODE -ne 0) { exit 1 }

      - name: Upload SARIF
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: bpa.sarif

      - name: Deploy
        if: github.ref == 'refs/heads/main'
        run: |
          TabularEditor.exe ./SemanticModel/definition/ `
            -D "powerbi://api.powerbi.com/v1.0/myorg/${{ vars.WORKSPACE }}" "${{ vars.DATASET }}" `
            -O -C -R `
            -A "AppId=${{ secrets.CLIENT_ID }};TenantId=${{ secrets.TENANT_ID }};AppSecret=${{ secrets.CLIENT_SECRET }}"
```

---

## Enhanced TOM Patterns (PowerShell)

### DAX Queries via ADOMD.NET

ADOMD.NET allows executing DAX queries against the local AS instance or remote endpoints.

```powershell
# Load ADOMD.NET assembly
Add-Type -Path "$env:LOCALAPPDATA\TabularEditor3\Plugins\Microsoft.AnalysisServices.AdomdClient.dll"

# Connect
$conn = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdConnection
$conn.ConnectionString = "Data Source=localhost:$port"
$conn.Open()

# Execute DAX query
$cmd = $conn.CreateCommand()
$cmd.CommandText = "EVALUATE ROW(""Result"", COUNTROWS('Sales'))"
$reader = $cmd.ExecuteReader()

while ($reader.Read()) {
    for ($i = 0; $i -lt $reader.FieldCount; $i++) {
        Write-Host "$($reader.GetName($i)): $($reader.GetValue($i))"
    }
}
$reader.Close()
$conn.Close()
```

**Critical gotcha — fully qualified column names:** ADOMD.NET returns column names WITH brackets: `row["[Column]"]`, not `row["Column"]`. Always use bracket-wrapped names when accessing result columns.

**DAX query format requirements:**
- `EVALUATE` keyword required (not `SELECT`)
- Table expressions only (no scalar expressions without `ROW()` wrapper)
- Use `EVALUATE ROW("label", <scalar_expression>)` for single values
- Use `EVALUATE TOPN(10, 'Table')` for table samples
- Column references in DAX: `'Table Name'[Column Name]` (single quotes for table, brackets for column)

### DMV Queries for Model Metadata

Discovery Management Views (DMVs) return metadata about the loaded model:

```powershell
# List all tables
$cmd.CommandText = "SELECT [TABLE_NAME], [TABLE_TYPE] FROM `$SYSTEM.TMSCHEMA_TABLES"

# List all measures
$cmd.CommandText = "SELECT [TABLE_NAME], [MEASURE_NAME], [EXPRESSION] FROM `$SYSTEM.TMSCHEMA_MEASURES"

# List all columns with types
$cmd.CommandText = "SELECT [TABLE_NAME], [COLUMN_NAME], [DATA_TYPE], [IS_HIDDEN] FROM `$SYSTEM.TMSCHEMA_COLUMNS WHERE [TYPE] <> 3"
# TYPE 3 = RowNumber (internal, always exclude)

# List all relationships
$cmd.CommandText = "SELECT * FROM `$SYSTEM.TMSCHEMA_RELATIONSHIPS"

# Model memory usage
$cmd.CommandText = "SELECT [TABLE_NAME], [COLUMN_NAME], [DICTIONARY_SIZE], [COLUMN_ENCODING] FROM `$SYSTEM.DISCOVER_STORAGE_TABLE_COLUMN_SEGMENTS"
```

**Key DMV gotcha:** The `$` in `$SYSTEM` must be escaped in PowerShell (`` `$SYSTEM ``).

### Enum Discovery via Reflection

Discover all valid enum values for TOM properties at runtime:

```powershell
# Load TOM assembly
$tomDll = Get-ChildItem "$env:LOCALAPPDATA\TabularEditor3\Plugins" -Filter "Microsoft.AnalysisServices.Tabular.dll" -Recurse | Select-Object -First 1
Add-Type -Path $tomDll.FullName

# Discover all enum types in TOM
$tomAssembly = [System.Reflection.Assembly]::LoadFrom($tomDll.FullName)
$enums = $tomAssembly.GetTypes() | Where-Object { $_.IsEnum }
$enums | ForEach-Object {
    Write-Host "`n--- $($_.Name) ---"
    [Enum]::GetValues($_) | ForEach-Object { Write-Host "  $_ = $([int]$_)" }
}

# Common enums you'll need:
# DataType: String=2, Int64=6, Double=8, DateTime=9, Decimal=10, Boolean=11
# ColumnType: Data=1, Calculated=2, RowNumber=3
# ModeType: Import=1, DirectQuery=2, Default=0, Dual=3
# CrossFilteringBehavior: OneDirection=1, BothDirections=2, Automatic=3
# RelationshipEndCardinality: Many=1, One=2, None=0
```

### TMSL Refresh with Error Handling

Tabular Model Scripting Language (TMSL) commands control model refresh:

```powershell
# Full refresh
$tmsl = @"
{
  "refresh": {
    "type": "full",
    "objects": [
      {"database": "$databaseName"}
    ]
  }
}
"@

# Table-level refresh
$tmsl = @"
{
  "refresh": {
    "type": "full",
    "objects": [
      {"database": "$databaseName", "table": "Sales"}
    ]
  }
}
"@

# Execute TMSL
$server.Execute($tmsl)

# Check results (CRITICAL — Execute() does NOT throw on data errors)
$results = $server.Execute($tmsl)
foreach ($result in $results) {
    foreach ($msg in $result.Messages) {
        if ($msg.GetType().Name -eq "XmlaError") {
            Write-Error "Refresh failed: $($msg.Description)"
        } elseif ($msg.GetType().Name -eq "XmlaWarning") {
            Write-Warning "Refresh warning: $($msg.Description)"
        }
    }
}
```

**Critical: `Server.Execute()` returns silently even on errors.** Always iterate the result messages to detect failures. Check for `XmlaError` type messages.

### SaveChanges Batching Pattern

When creating new tables AND relationships in the same session, order matters:

```powershell
$server = New-Object Microsoft.AnalysisServices.Tabular.Server
$server.Connect("Data Source=localhost:$port")
$db = $server.Databases[0]
$model = $db.Model

# Step 1: Create new table with columns
$newTable = New-Object Microsoft.AnalysisServices.Tabular.Table
$newTable.Name = "NewDimension"
# ... add columns, partitions ...
$model.Tables.Add($newTable)

# MUST SaveChanges before adding relationships TO the new table
$model.SaveChanges()

# Step 2: Now create relationship
$rel = New-Object Microsoft.AnalysisServices.Tabular.SingleColumnRelationship
$rel.FromColumn = $model.Tables["FactSales"].Columns["DimKey"]
$rel.ToColumn = $model.Tables["NewDimension"].Columns["Key"]
$model.Relationships.Add($rel)

# Save again
$model.SaveChanges()
```

**Why two saves?** Analysis Services validates relationships during `SaveChanges()`. If the target table doesn't exist in the model yet (because it was added in the same batch but not committed), the validation fails. Always: create table → save → create relationship → save.

### Explicit Column Creation for New Tables

When adding a new table via TOM, you must explicitly add ALL columns:

```powershell
$table = New-Object Microsoft.AnalysisServices.Tabular.Table
$table.Name = "Calendar"

# Partition (M query or calculated)
$partition = New-Object Microsoft.AnalysisServices.Tabular.Partition
$partition.Name = "Calendar-Partition"
$partition.Source = New-Object Microsoft.AnalysisServices.Tabular.MPartitionSource
$partition.Source.Expression = "let Source = #date(2020,1,1) ... in FinalStep"
$table.Partitions.Add($partition)

# MUST add columns explicitly — TOM does NOT auto-detect from partition source
$col1 = New-Object Microsoft.AnalysisServices.Tabular.DataColumn
$col1.Name = "Date"
$col1.DataType = [Microsoft.AnalysisServices.Tabular.DataType]::DateTime
$col1.SourceColumn = "Date"
$table.Columns.Add($col1)

$col2 = New-Object Microsoft.AnalysisServices.Tabular.DataColumn
$col2.Name = "Year"
$col2.DataType = [Microsoft.AnalysisServices.Tabular.DataType]::Int64
$col2.SourceColumn = "Year"
$table.Columns.Add($col2)

$model.Tables.Add($table)
$model.SaveChanges()
```

**Without explicit columns, the table appears empty in the model** even though the partition query returns data. The columns define the schema; the partition provides the data.

---

## SVG Measure Pattern Library

SVG measures generate inline vector graphics in DAX, rendered in table/matrix visuals and cards. Each measure returns a `data:image/svg+xml` URL.

### SVG Measure Prerequisites

1. Set data category to "Image URL" on the measure (in PBI Desktop: Measure Tools > Data Category > Image URL)
2. In tables: turn off totals row (totals show raw SVG text)
3. Max ~32K characters per measure value
4. URL-encode `#` as `%23` inside SVG attribute values

### Pattern 1: Adjacent Bar Chart with Variance

Two horizontal bars (actual vs. target) with a variance indicator:

```dax
SVG Adjacent Bars =
VAR _Actual = [Sales Amount]
VAR _Target = [Sales Target]
VAR _MaxVal = MAX(_Actual, _Target) * 1.1
VAR _ActualWidth = DIVIDE(_Actual, _MaxVal) * 180
VAR _TargetWidth = DIVIDE(_Target, _MaxVal) * 180
VAR _Color = IF(_Actual >= _Target, "%2328a745", "%23dc3545")
RETURN
"data:image/svg+xml;utf8," &
"<svg xmlns='http://www.w3.org/2000/svg' width='200' height='30'>" &
"<rect x='10' y='2' width='" & _ActualWidth & "' height='12' rx='2' fill='" & _Color & "'/>" &
"<rect x='10' y='16' width='" & _TargetWidth & "' height='12' rx='2' fill='%23CCCCCC'/>" &
"</svg>"
```

### Pattern 2: Bullet Chart (Actual vs Target with Qualitative Ranges)

```dax
SVG Bullet =
VAR _Actual = [Sales Amount]
VAR _Target = [Sales Target]
VAR _Max = _Target * 1.5
VAR _Poor = _Target * 0.5
VAR _OK = _Target * 0.75
VAR _Good = _Target
VAR _Scale = DIVIDE(200, _Max)
RETURN
"data:image/svg+xml;utf8," &
"<svg xmlns='http://www.w3.org/2000/svg' width='220' height='24'>" &
"<rect x='10' width='" & FORMAT(_Max * _Scale, "0") & "' height='24' fill='%23E0E0E0'/>" &
"<rect x='10' width='" & FORMAT(_Good * _Scale, "0") & "' height='24' fill='%23BDBDBD'/>" &
"<rect x='10' width='" & FORMAT(_OK * _Scale, "0") & "' height='24' fill='%239E9E9E'/>" &
"<rect x='10' width='" & FORMAT(_Poor * _Scale, "0") & "' height='24' fill='%23757575'/>" &
"<rect x='10' y='6' width='" & FORMAT(MIN(_Actual, _Max) * _Scale, "0") & "' height='12' fill='%23333333'/>" &
"<line x1='" & FORMAT(_Target * _Scale + 10, "0") & "' y1='2' x2='" & FORMAT(_Target * _Scale + 10, "0") & "' y2='22' stroke='%23FF0000' stroke-width='2'/>" &
"</svg>"
```

### Pattern 3: Lollipop Chart

```dax
SVG Lollipop =
VAR _Value = [Completion Pct]
VAR _X = ROUND(_Value * 180, 0) + 15
VAR _Color = SWITCH(TRUE(),
    _Value >= 0.9, "%2328a745",
    _Value >= 0.6, "%23ffc107",
    "%23dc3545"
)
RETURN
"data:image/svg+xml;utf8," &
"<svg xmlns='http://www.w3.org/2000/svg' width='210' height='20'>" &
"<line x1='15' y1='10' x2='" & _X & "' y2='10' stroke='" & _Color & "' stroke-width='2'/>" &
"<circle cx='" & _X & "' cy='10' r='6' fill='" & _Color & "'/>" &
"<text x='" & (_X + 10) & "' y='14' font-size='10' fill='%23333333'>" & FORMAT(_Value, "0%") & "</text>" &
"</svg>"
```

### Pattern 4: Status Pill

```dax
SVG Status Pill =
VAR _Status = [Order Status]
VAR _Color = SWITCH(_Status,
    "Completed", "%2328a745",
    "In Progress", "%23ffc107",
    "Delayed", "%23dc3545",
    "Cancelled", "%23999999",
    "%23CCCCCC"
)
VAR _TextColor = IF(_Status IN {"In Progress"}, "%23333333", "%23FFFFFF")
RETURN
"data:image/svg+xml;utf8," &
"<svg xmlns='http://www.w3.org/2000/svg' width='100' height='22'>" &
"<rect x='2' y='2' width='96' height='18' rx='9' fill='" & _Color & "'/>" &
"<text x='50' y='15' text-anchor='middle' font-size='10' font-family='Segoe UI' fill='" & _TextColor & "'>" & _Status & "</text>" &
"</svg>"
```

### Pattern 5: Diverging Bar Chart

```dax
SVG Diverging Bar =
VAR _Variance = [Variance Pct]
VAR _BarWidth = ROUND(ABS(_Variance) * 80, 0)
VAR _Color = IF(_Variance >= 0, "%2328a745", "%23dc3545")
VAR _X = IF(_Variance >= 0, 100, 100 - _BarWidth)
RETURN
"data:image/svg+xml;utf8," &
"<svg xmlns='http://www.w3.org/2000/svg' width='200' height='20'>" &
"<line x1='100' y1='0' x2='100' y2='20' stroke='%23999999' stroke-width='1'/>" &
"<rect x='" & _X & "' y='3' width='" & _BarWidth & "' height='14' rx='2' fill='" & _Color & "'/>" &
"<text x='" & IF(_Variance >= 0, _X + _BarWidth + 4, _X - 4) & "' y='14' text-anchor='" & IF(_Variance >= 0, "start", "end") & "' font-size='9' fill='%23333333'>" & FORMAT(_Variance, "+0.0%;-0.0%") & "</text>" &
"</svg>"
```

### Pattern 6: Sparkline (Mini Line Chart)

```dax
SVG Sparkline =
VAR _Data = SUMMARIZE(ALL('Date'[MonthNum]), 'Date'[MonthNum], "Val", [Sales Amount])
VAR _MaxVal = MAXX(_Data, [Val])
VAR _MinVal = MINX(_Data, [Val])
VAR _Range = _MaxVal - _MinVal
VAR _Points =
    CONCATENATEX(
        _Data,
        FORMAT([MonthNum] * 16, "0") & "," &
        FORMAT(40 - DIVIDE([Val] - _MinVal, _Range) * 36, "0.0"),
        " ",
        [MonthNum]
    )
RETURN
"data:image/svg+xml;utf8," &
"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 200 44' width='200' height='44'>" &
"<polyline points='" & _Points & "' fill='none' stroke='%234472C4' stroke-width='1.5'/>" &
"</svg>"
```

### Pattern 7: Waterfall Step

```dax
SVG Waterfall Step =
VAR _StartVal = [Previous Balance]
VAR _EndVal = [Current Balance]
VAR _Change = _EndVal - _StartVal
VAR _MaxVal = MAX(ABS(_StartVal), ABS(_EndVal)) * 1.2
VAR _Scale = DIVIDE(100, _MaxVal)
VAR _Color = IF(_Change >= 0, "%2328a745", "%23dc3545")
VAR _Y1 = 100 - (_StartVal * _Scale)
VAR _Y2 = 100 - (_EndVal * _Scale)
RETURN
"data:image/svg+xml;utf8," &
"<svg xmlns='http://www.w3.org/2000/svg' width='60' height='100'>" &
"<line x1='0' y1='" & _Y1 & "' x2='60' y2='" & _Y1 & "' stroke='%23CCCCCC' stroke-width='1' stroke-dasharray='2'/>" &
"<rect x='15' y='" & MIN(_Y1, _Y2) & "' width='30' height='" & ABS(_Y2 - _Y1) & "' fill='" & _Color & "'/>" &
"</svg>"
```

### Pattern 8: Dumbbell Plot (Before/After)

```dax
SVG Dumbbell =
VAR _Before = [Prior Year Amount]
VAR _After = [Current Year Amount]
VAR _Max = MAX(_Before, _After) * 1.1
VAR _Scale = DIVIDE(180, _Max)
VAR _X1 = _Before * _Scale + 10
VAR _X2 = _After * _Scale + 10
VAR _Color = IF(_After >= _Before, "%2328a745", "%23dc3545")
RETURN
"data:image/svg+xml;utf8," &
"<svg xmlns='http://www.w3.org/2000/svg' width='200' height='20'>" &
"<line x1='" & MIN(_X1, _X2) & "' y1='10' x2='" & MAX(_X1, _X2) & "' y2='10' stroke='" & _Color & "' stroke-width='2'/>" &
"<circle cx='" & _X1 & "' cy='10' r='4' fill='%23999999'/>" &
"<circle cx='" & _X2 & "' cy='10' r='4' fill='" & _Color & "'/>" &
"</svg>"
```

### SVG Color Encoding Reference

In SVG within DAX measures, `#` must be URL-encoded as `%23`:

| Color | Encoded | Meaning |
|-------|---------|---------|
| `#28a745` | `%2328a745` | Green (positive/good) |
| `#dc3545` | `%23dc3545` | Red (negative/bad) |
| `#ffc107` | `%23ffc107` | Yellow/amber (warning) |
| `#4472C4` | `%234472C4` | Blue (neutral/primary) |
| `#333333` | `%23333333` | Dark gray (text) |
| `#999999` | `%23999999` | Medium gray (secondary) |
| `#CCCCCC` | `%23CCCCCC` | Light gray (background) |
| `#FFFFFF` | `%23FFFFFF` | White |

### Unicode Character Alternatives

For simpler indicators without full SVG, use UNICHAR:

| Character | UNICHAR Code | Use Case |
|-----------|-------------|----------|
| ▲ (up triangle) | `UNICHAR(9650)` | Positive trend |
| ▼ (down triangle) | `UNICHAR(9660)` | Negative trend |
| ● (filled circle) | `UNICHAR(9679)` | Status dot |
| ○ (empty circle) | `UNICHAR(9675)` | Inactive status |
| ★ (star) | `UNICHAR(9733)` | Rating |
| ☆ (empty star) | `UNICHAR(9734)` | Empty rating |
| ✓ (check mark) | `UNICHAR(10003)` | Complete |
| ✗ (cross) | `UNICHAR(10007)` | Failed |
| ■ (square) | `UNICHAR(9632)` | Progress block |
| □ (empty square) | `UNICHAR(9633)` | Remaining block |

---

## Naming Convention Standardization

### Measure Name Construction Order

Follow this standard ordering for measure names:

```
[Aggregation] [Base Name] [Period] ([Unit])
```

| Component | Position | Examples |
|-----------|----------|----------|
| Aggregation | Prefix | Sum, Count, Avg, Min, Max, Distinct Count |
| Base Name | Core | Revenue, Orders, Customers, Margin, Days to Ship |
| Period | Suffix | YTD, QTD, MTD, PY, PQ, PM, R12M, nYP (n years prior) |
| Unit | Parenthetical | ($), (%), (Days), (Units) |

**Examples:**
- `Sum Revenue YTD ($)` — Sum aggregation, Revenue base, Year-to-Date period, dollar unit
- `Avg Days to Ship R12M` — Average aggregation, Days to Ship base, Rolling 12 Months period
- `Count Orders PY` — Count aggregation, Orders base, Prior Year period
- `Distinct Count Customers MTD` — Distinct Count aggregation, Customers base, Month-to-Date

### Period Convention (SQLBI Standard)

| Abbreviation | Meaning | DAX Function |
|--------------|---------|-------------|
| YTD | Year-to-Date | `TOTALYTD()` |
| QTD | Quarter-to-Date | `TOTALQTD()` |
| MTD | Month-to-Date | `TOTALMTD()` |
| PY | Prior Year | `SAMEPERIODLASTYEAR()` |
| PQ | Prior Quarter | `DATEADD('Date'[Date], -1, QUARTER)` |
| PM | Prior Month | `DATEADD('Date'[Date], -1, MONTH)` |
| R12M | Rolling 12 Months | `DATESINPERIOD('Date'[Date], MAX('Date'[Date]), -12, MONTH)` |
| nYP | n Years Prior | `DATEADD('Date'[Date], -n, YEAR)` |
| MAT | Moving Annual Total | Same as R12M (used interchangeably) |
| YoY | Year-over-Year (%) | `DIVIDE([Current] - [PY], [PY])` |

### 10 Naming Convention Rules

#### Rule 1: Human-Readable Names
- **Do:** `Total Revenue`, `Customer Count`, `Average Order Value`
- **Don't:** `TotalRev`, `CustCnt`, `AvgOrdVal`

#### Rule 2: No Technical Prefixes
- **Do:** `Total Revenue`
- **Don't:** `m_TotalRevenue`, `msr_Revenue`, `_Revenue`

#### Rule 3: No Hungarian Notation
- **Do:** `Revenue`, `Order Date`
- **Don't:** `intRevenue`, `dtOrderDate`, `strCustomerName`

#### Rule 4: Consistent Aggregation Prefixes
Pick ONE style and use it everywhere:
- Style A (verb): `Sum Revenue`, `Count Orders`, `Avg Margin`
- Style B (noun): `Total Revenue`, `Number of Orders`, `Average Margin`

#### Rule 5: Tables — Singular Nouns, No Prefixes
- **Do:** `Customer`, `Product`, `Calendar`, `Sales`
- **Don't:** `DimCustomer`, `FactSales`, `tblProduct`, `dim_Customer`
- **Exception:** When consuming an existing Gold layer with Dim/Fact naming (like UBI), keep the existing convention for consistency

#### Rule 6: Columns — Descriptive, CamelCase or Spaces
- **Do:** `Customer Name`, `Order Date`, `Product Category`
- **Don't:** `CUSTOMER_NAME`, `ord_dt`, `ProdCat`

#### Rule 7: Boolean Columns — "Is" or "Has" Prefix
- **Do:** `Is Active`, `Has Warranty`, `Is Returned`
- **Don't:** `Active`, `Warranty`, `Returned`, `ActiveFlag`, `Y/N Active`

#### Rule 8: Display Folders for Organization
Group related measures in display folders:
```
📁 Revenue
    Sum Revenue
    Sum Revenue YTD
    Sum Revenue PY
    Revenue YoY (%)
📁 Orders
    Count Orders
    Count Orders MTD
    Avg Order Value
📁 Customers
    Distinct Count Customers
    Count New Customers
```

#### Rule 9: No Abbreviations (Except Standard Periods)
- **Do:** `Revenue`, `Quantity`, `Manufacturing`
- **Don't:** `Rev`, `Qty`, `Mfg`
- **Exception:** Standard period abbreviations (YTD, PY, R12M) are acceptable

#### Rule 10: Consistent Unit Indicators
If a measure needs a unit clarification, use parentheses at the end:
- `Average Lead Time (Days)`
- `Total Weight (kg)`
- `Conversion Rate (%)`

### Naming Convention Audit Workflow

**Phase 1: Discovery** — Export all object names from the model
```powershell
# Via TOM
$model.Tables | ForEach-Object {
    $tableName = $_.Name
    $_.Measures | ForEach-Object { [PSCustomObject]@{Type="Measure"; Table=$tableName; Name=$_.Name; Folder=$_.DisplayFolder} }
    $_.Columns | ForEach-Object { [PSCustomObject]@{Type="Column"; Table=$tableName; Name=$_.Name; Hidden=$_.IsHidden} }
} | Export-Csv "model_names_audit.csv" -NoTypeInformation
```

**Phase 2: Detection** — Flag violations against the 10 rules

**Phase 3: Proposal** — Generate rename proposals with old → new mapping

**Phase 4: Review** — Present to stakeholders for approval

**Phase 5: Execution** — Apply renames using the PBIP Cascading Rename checklist

---

## Tabular Editor C# Scripting Patterns

C# scripts (`.csx` files) run inside Tabular Editor and have full access to the TOM via the `Model` global variable. They provide a more concise and powerful way to manipulate semantic models than PowerShell + TOM.

### Script Execution Context

```csharp
// Global variables available in every script:
// Model — the TOM Model object
// Selected — currently selected objects in TE UI
// Output() — write to TE output pane
// Info(), Warning(), Error() — logging
// ScriptHelper — utility methods
// EvaluateDax("query") — execute DAX against the model

// Access model objects:
var tables = Model.Tables;
var measures = Model.AllMeasures;
var columns = Model.AllColumns;
var relationships = Model.Relationships;
```

### Pattern: Bulk Measure Generation

Generate time intelligence measures for all base measures:

```csharp
// For each visible measure, create YTD and PY variants
foreach (var m in Model.AllMeasures.Where(m => !m.IsHidden && !m.Name.Contains("YTD") && !m.Name.Contains("PY")))
{
    var table = m.Table;
    var baseName = m.Name;

    // YTD measure
    var ytdName = baseName + " YTD";
    if (!table.Measures.Contains(ytdName))
    {
        var ytd = table.AddMeasure(ytdName, $"TOTALYTD({m.DaxObjectFullName}, 'Date'[Date])");
        ytd.FormatString = m.FormatString;
        ytd.DisplayFolder = m.DisplayFolder;
        ytd.Description = $"Year-to-date calculation of {baseName}";
    }

    // PY measure
    var pyName = baseName + " PY";
    if (!table.Measures.Contains(pyName))
    {
        var py = table.AddMeasure(pyName, $"CALCULATE({m.DaxObjectFullName}, SAMEPERIODLASTYEAR('Date'[Date]))");
        py.FormatString = m.FormatString;
        py.DisplayFolder = m.DisplayFolder;
        py.Description = $"Prior year calculation of {baseName}";
    }
}
```

### Pattern: Create SUM Measures from Selected Columns

```csharp
foreach (var c in Selected.Columns.Where(c => c.DataType == DataType.Decimal || c.DataType == DataType.Double || c.DataType == DataType.Int64))
{
    var measureName = "Sum " + c.Name;
    if (!c.Table.Measures.Contains(measureName))
    {
        var m = c.Table.AddMeasure(measureName, $"SUM({c.DaxObjectFullName})");
        m.FormatString = c.DataType == DataType.Int64 ? "#,##0" : "#,##0.00";
        m.DisplayFolder = "Auto-Generated";
    }
}
```

### Pattern: Format String Cleanup

```csharp
// Apply standard format strings based on measure name patterns
foreach (var m in Model.AllMeasures.Where(m => string.IsNullOrEmpty(m.FormatString) || m.FormatString == "0"))
{
    var name = m.Name.ToLower();
    if (name.Contains("revenue") || name.Contains("amount") || name.Contains("price") || name.Contains("cost"))
        m.FormatString = "$#,##0.00";
    else if (name.Contains("count") || name.Contains("quantity") || name.Contains("number"))
        m.FormatString = "#,##0";
    else if (name.Contains("pct") || name.Contains("percent") || name.Contains("ratio") || name.Contains("margin"))
        m.FormatString = "0.0%";
    else if (name.Contains("date"))
        m.FormatString = "dd-MMM-yyyy";
}
```

### Pattern: Display Folder Organization

```csharp
// Auto-organize measures into display folders based on naming patterns
var folderMap = new Dictionary<string, string> {
    {"revenue", "Revenue"}, {"sales", "Revenue"},
    {"cost", "Costs"}, {"expense", "Costs"},
    {"margin", "Profitability"}, {"profit", "Profitability"},
    {"count", "Counts"}, {"number", "Counts"},
    {"avg", "Averages"}, {"average", "Averages"},
    {"ytd", "Time Intelligence"}, {"py", "Time Intelligence"}, {"mtd", "Time Intelligence"},
};

foreach (var m in Model.AllMeasures.Where(m => string.IsNullOrEmpty(m.DisplayFolder)))
{
    var name = m.Name.ToLower();
    foreach (var kvp in folderMap)
    {
        if (name.Contains(kvp.Key)) { m.DisplayFolder = kvp.Value; break; }
    }
}
```

### Pattern: DAX Execution and Results

```csharp
// Execute DAX and process results
var result = EvaluateDax("EVALUATE ROW(\"Total\", COUNTROWS('Sales'))");
// result is a DataTable

foreach (System.Data.DataRow row in result.Rows)
{
    Output($"Result: {row[0]}");
}

// WARNING: Boolean columns require FORMAT wrapper
// BAD:  MAXX('Table', 'Table'[BoolCol])  — returns True/False string
// GOOD: MAXX('Table', FORMAT('Table'[BoolCol], "0"))  — returns 1/0
```

### Pattern: WinForms Dialog for User Input

```csharp
// Show a dialog to let the user select options
using System.Windows.Forms;

var form = new Form() { Text = "Select Tables", Width = 300, Height = 400 };
var checklist = new CheckedListBox() { Dock = DockStyle.Fill };
foreach (var t in Model.Tables.OrderBy(t => t.Name))
    checklist.Items.Add(t.Name);
var btnOK = new Button() { Text = "OK", Dock = DockStyle.Bottom, DialogResult = DialogResult.OK };
form.Controls.Add(checklist);
form.Controls.Add(btnOK);

if (form.ShowDialog() == DialogResult.OK)
{
    foreach (var item in checklist.CheckedItems)
    {
        var tableName = item.ToString();
        // Process selected tables...
        Output($"Processing: {tableName}");
    }
}
```

### Pattern: DAX Formatting

```csharp
// Format all measure expressions using DAX Formatter service
foreach (var m in Model.AllMeasures)
{
    m.FormatDax();  // Built-in TE3 method — calls daxformatter.com
}
```

### Key C# Scripting Gotchas

1. **`Selected` is empty in CLI mode** — only populated when run from TE3 UI. Guard with `if (Selected.Measures.Count() == 0) return;`
2. **DAX results return column names with brackets** — `row["[ColumnName]"]` not `row["ColumnName"]`
3. **Separate `EvaluateDax()` calls outperform batched UNION queries** — counter-intuitive but confirmed in TE3
4. **Boolean columns need `FORMAT()` wrapper** for `MINX`/`MAXX` — otherwise returns string `True`/`False`
5. **LINQ is available** — `Model.AllMeasures.Where(m => ...)`, `OrderBy`, `Select`, `Any`, `All`
6. **Changes are auto-tracked** — no explicit save needed in TE3 UI; use `Model.SaveChanges()` only in external scripts

---

## Tabular Editor Macro System

Macros in Tabular Editor 3 are saved C# scripts that appear in the right-click context menu, enabling one-click model operations.

### MacroActions.json Structure

Macros are stored in `MacroActions.json`:

```json
[
  {
    "Name": "Create SUM Measures",
    "Tooltip": "Creates SUM measures for selected numeric columns",
    "Enabled": "Selected.Columns.Any(c => c.DataType == DataType.Decimal || c.DataType == DataType.Int64)",
    "Execute": "foreach(var c in Selected.Columns.Where(c => c.DataType == DataType.Decimal || c.DataType == DataType.Int64)) { c.Table.AddMeasure(\"Sum \" + c.Name, \"SUM(\" + c.DaxObjectFullName + \")\").FormatString = \"#,##0.00\"; }",
    "ValidContexts": "Column"
  }
]
```

### Macro Fields

| Field | Description |
|-------|-------------|
| `Name` | Display name in the context menu |
| `Tooltip` | Hover text description |
| `Enabled` | Dynamic LINQ expression — macro appears grayed out when this returns false |
| `Execute` | C# code to run (single-line; use `\n` for multi-line) |
| `ValidContexts` | Comma-separated TOM types: `Table`, `Column`, `Measure`, `Hierarchy`, `Partition`, `Model`, `Relationship` |

### File Locations

| OS | Path |
|----|------|
| Windows | `%LocalAppData%\TabularEditor3\MacroActions.json` |
| macOS (Parallels) | `~/Library/Application Support/TabularEditor3/MacroActions.json` |
| WSL | `/mnt/c/Users/<user>/AppData/Local/TabularEditor3/MacroActions.json` |

### Example Macros

**Hide all foreign key columns:**
```json
{
  "Name": "Hide Foreign Key Columns",
  "Tooltip": "Hides all columns ending with 'Key' or 'ID' in selected tables",
  "Enabled": "Selected.Tables.Any()",
  "Execute": "foreach(var t in Selected.Tables) foreach(var c in t.Columns.Where(c => c.Name.EndsWith(\"Key\") || c.Name.EndsWith(\"ID\"))) { c.IsHidden = true; }",
  "ValidContexts": "Table"
}
```

**Add description from column name:**
```json
{
  "Name": "Auto-Describe Columns",
  "Tooltip": "Generates descriptions from column names using word splitting",
  "Enabled": "Selected.Columns.Any(c => string.IsNullOrEmpty(c.Description))",
  "Execute": "foreach(var c in Selected.Columns.Where(c => string.IsNullOrEmpty(c.Description))) { c.Description = System.Text.RegularExpressions.Regex.Replace(c.Name, \"([a-z])([A-Z])\", \"$1 $2\"); }",
  "ValidContexts": "Column"
}
```

**Mark as date table:**
```json
{
  "Name": "Mark as Date Table",
  "Tooltip": "Sets the selected table as a date table using the Date column",
  "Enabled": "Selected.Table != null && Selected.Table.Columns.Any(c => c.Name == \"Date\" && c.DataType == DataType.DateTime)",
  "Execute": "Selected.Table.DataCategory = \"Time\"; Selected.Table.Columns[\"Date\"].IsKey = true;",
  "ValidContexts": "Table"
}
```

### Performance Insight

When executing DAX from macros, **separate `EvaluateDax()` calls outperform batched UNION queries**:

```csharp
// FASTER: Separate calls
foreach (var t in Model.Tables) {
    var result = EvaluateDax($"EVALUATE ROW(\"Count\", COUNTROWS('{t.Name}'))");
    // process result
}

// SLOWER: Batched UNION
var unionQuery = string.Join(" UNION ", Model.Tables.Select(t => $"ROW(\"Table\", \"{t.Name}\", \"Count\", COUNTROWS('{t.Name}'))"));
var result = EvaluateDax($"EVALUATE {unionQuery}");
```

---

## Tabular Editor 3 Configuration Management

### Configuration File Hierarchy

| File | Purpose | Scope |
|------|---------|-------|
| `Preferences.json` | Application settings, BPA URLs, compiler config | User-level |
| `.tmuo` (Tabular Model User Options) | Model-specific settings: workspace DB, deployment target, data source overrides | Per-model |
| `Layouts.json` | Window layout and panel positions | User-level |
| `UiPreferences.json` | UI-specific preferences | User-level |
| `MacroActions.json` | Saved C# macro scripts | User-level |

### Preferences.json Key Settings

Location: `%LocalAppData%\TabularEditor3\Preferences.json`

```json
{
  "BpaRulesUrls": [
    "https://raw.githubusercontent.com/TabularEditor/BestPracticeRules/master/BPARules-standard.json"
  ],
  "ProxyUseSystemSettings": true,
  "Updates_CheckForUpdates": true,
  "Features_AllowUnsupportedPBIFeatures": false,
  "Dax_DefaultSeparatorStyle": "US",
  "Dax_FormatDaxEnabled": true,
  "Editor_AutoComplete": true,
  "Deployment_DeployConnections": true,
  "Deployment_DeployRoles": true,
  "Deployment_DeployPartitions": false,
  "Schema_CompareOptions": "Default"
}
```

### .tmuo (Tabular Model User Options)

The `.tmuo` file stores per-model developer settings. **Never commit to version control** — it contains user-specific workspace database connections and may contain encrypted credentials.

Location: Same directory as the `.bim` or `.tmdl` model files, named `<ModelName>.tmuo`

```json
{
  "WorkspaceDatabase": {
    "Server": "localhost:54321",
    "Database": "my_workspace_db_guid"
  },
  "DeploymentTarget": {
    "Server": "powerbi://api.powerbi.com/v1.0/myorg/MyWorkspace",
    "Database": "MyDataset"
  },
  "DataSourceOverrides": {
    "SQL Server": {
      "ConnectionString": "Data Source=dev-server;Initial Catalog=DevDB;Integrated Security=true"
    }
  },
  "CredentialStore": {
    "type": "WindowsUserKey",
    "encrypted_credentials": "..."
  }
}
```

### Team Development Workflow

Each developer maintains their own `.tmuo` pointing to their personal workspace:

1. **Add `.tmuo` to `.gitignore`** — never commit
2. Each developer creates their own `.tmuo` with their workspace DB connection
3. Shared model files (`.bim`, `.tmdl`, `BPARules.json`) are version-controlled
4. When a developer opens the model, TE3 connects to their workspace DB for real-time validation
5. Deployment targets can differ per developer (dev vs. test environments)

### Cross-Platform Access

| Platform | Config Path |
|----------|------------|
| Windows | `%LocalAppData%\TabularEditor3\` |
| macOS (Parallels) | `~/Library/Application Support/TabularEditor3/` |
| WSL | `/mnt/c/Users/<user>/AppData/Local/TabularEditor3/` |

---

## PBIP File Type Deep Reference

### visual.json Structure

Each visual in a PBIR project has its own `visual.json` with this structure:

```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/1.5.0/schema.json",
  "name": "unique_visual_id",
  "position": {
    "x": 100, "y": 200, "z": 1000,
    "width": 400, "height": 300,
    "tabOrder": 1000
  },
  "visual": {
    "visualType": "lineChart",
    "query": { ... },
    "objects": { ... },
    "vcObjects": { ... },
    "prototypeQuery": { ... },
    "projections": { ... },
    "dataTransforms": { ... }
  },
  "filters": [ ... ]
}
```

### Entity/Property Pattern in visual.json

Data field references use this structure throughout visual.json:

```json
{
  "Column": {
    "Expression": {
      "SourceRef": {"Entity": "TableName"}
    },
    "Property": "ColumnName"
  }
}
```

For measures:
```json
{
  "Measure": {
    "Expression": {
      "SourceRef": {"Entity": "TableName"}
    },
    "Property": "MeasureName"
  }
}
```

### queryRef Format

`queryRef` is a string identifier used in projections, dataTransforms, and metadata:

| Object Type | queryRef Format | Example |
|-------------|----------------|---------|
| Column | `TableName.ColumnName` | `Sales.OrderDate` |
| Measure | `TableName.MeasureName` | `Sales.Total Revenue` |
| Aggregation | `Agg(TableName.ColumnName)` | `Sum(Sales.Amount)` |
| Extension measure | `TableName.MeasureName` | Same as regular measure |

### nativeQueryRef

`nativeQueryRef` maps to the display name shown in the visual's field wells:

```json
{
  "queryRef": "Sales.Total Revenue",
  "nativeQueryRef": "Total Revenue"
}
```

### page.json Structure

```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/1.3.0/schema.json",
  "name": "SalesOverview",
  "displayName": "Sales Overview",
  "displayOption": 1,
  "height": 720,
  "width": 1280,
  "objects": {
    "background": [{ ... }],
    "wallpaper": [{ ... }],
    "outspace": [{ ... }],
    "outspaceFill": [{ ... }]
  },
  "filters": [ ... ],
  "annotations": [ ... ]
}
```

### reportExtensions.json Structure

Replaces `modelExtensions` from the legacy layout format:

```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/reportExtension/1.0.0/schema.json",
  "name": "extension",
  "entities": [
    {
      "name": "Sales",
      "extends": "Sales",
      "measures": [
        {
          "name": "Total Revenue YTD",
          "expression": "TOTALYTD(SUM('Sales'[Revenue]), 'Date'[Date])",
          "dataType": "double",
          "formatString": "$#,##0.00",
          "hidden": false,
          "displayFolder": "Revenue"
        }
      ]
    }
  ]
}
```

### Filter Configuration in visual.json

```json
{
  "type": "categorical",
  "expression": {
    "Column": {
      "Expression": {"SourceRef": {"Entity": "Sales"}},
      "Property": "Region"
    }
  },
  "filter": {
    "whereItems": [{
      "condition": {
        "In": {
          "Expressions": [{"Column": {"Expression": {"SourceRef": {"Entity": "Sales"}}, "Property": "Region"}}],
          "Values": [[{"Literal": {"Value": "'East'"}}], [{"Literal": {"Value": "'West'"}}]]
        }
      }
    }]
  }
}
```

### Conditional Formatting Expression Nesting

Conditional formatting in PBIR uses deeply nested expression trees:

```json
{
  "properties": {
    "backColor": {
      "solid": {
        "color": {
          "expr": {
            "Conditional": {
              "Cases": [{
                "Condition": {
                  "Comparison": {
                    "ComparisonKind": 1,
                    "Left": { "Measure": { ... } },
                    "Right": { "Literal": { "Value": "1000L" } }
                  }
                },
                "Value": { "Literal": { "Value": "'#FF0000'" } }
              }],
              "DefaultValue": { "Literal": { "Value": "'#00FF00'" } }
            }
          }
        }
      }
    }
  }
}
```

### Sort Definition Blocks

Sort-by configuration in visual.json:

```json
{
  "sort": [{
    "direction": 1,
    "field": {
      "Column": {
        "Expression": {"SourceRef": {"Entity": "Date"}},
        "Property": "MonthNumber"
      }
    }
  }]
}
```

Direction values: `1` = Ascending, `2` = Descending

### SparklineData Metadata Format

The most non-obvious format in PBIP files. SparklineData uses a specialized metadata selector:

```json
{
  "SparklineData": {
    "metadata": {
      "columns": {
        "Sales.Revenue": {
          "roles": {"Y": true},
          "type": {"category": null, "underlyingType": 259}
        },
        "Date.Month": {
          "roles": {"Category": true},
          "type": {"category": null, "underlyingType": 519}
        }
      }
    },
    "data": "dynamic"
  }
}
```

The keys in `metadata.columns` use the `Table.Column` format (same as `queryRef`). This is distinct from the `Entity`/`Property` format used elsewhere and is commonly missed during renames.

---

## Sanity Checkpoint — Existing Capability Verification

After enhancing this skill, verify all original sections are intact by checking for these section headers:

### Pre-Enhancement Section Registry (2962 lines, 150+ sections)

**Core Sections (must exist):**
- `## Overview`
- `## .pbix File Format`
- `### SecurityBindings — CRITICAL DISCOVERY`
- `### Recommended Approach: Binary ZIP Rebuild`
- `## Report-Level Measures in Live Connection Reports`
- `## Report/Layout JSON Structure`
- `## Visual Container Patterns` (Patterns 1-8)
- `## Complete Workflow: Build Report with Visuals`
- `## Key Gotchas (Ranked by Pain Level)` (34 gotchas)
- `## .pbip Report Modification Workflow (RECOMMENDED for PBI 2.153+)`
- `## PBI Desktop Local Analysis Services Instance`
- `## Live Connection Configuration`
- `## Power BI REST API Reference`
- `## Column Metadata Reference`
- `## Troubleshooting` (8 scenarios)
- `## Critical: No Inter-Measure References in Report-Level Measures`
- `## Compelling Visual Design`
- `### Theme JSON Structure`
- `### Typography (textClasses)`
- `### Professional Color Palettes`
- `### visualStyles — Global and Per-Visual Formatting`
- `### Conditional Formatting in Layout JSON`
- `### Filter JSON Structure`
- `### Visual Type Registry`
- `## Report Beautification System` (B1-B10)
- `## PBIR — Power BI Enhanced Report Format`
- `## TMDL — Tabular Model Definition Language`
- `## MCP Servers for Power BI`

**Enhancement Sections (added):**
- `## Best Practice Analyzer (BPA) Rule Authoring`
- `## PBIP Cascading Rename Operations`
- `## Tabular Editor CLI for CI/CD`
- `## Enhanced TOM Patterns (PowerShell)`
- `## SVG Measure Pattern Library`
- `## Naming Convention Standardization`
- `## Tabular Editor C# Scripting Patterns`
- `## Tabular Editor Macro System`
- `## Tabular Editor 3 Configuration Management`
- `## PBIP File Type Deep Reference`

### Verification Script

```python
import re

def verify_skill_integrity(skill_path):
    """Verify all expected sections exist in the enhanced skill file."""
    with open(skill_path, 'r', encoding='utf-8') as f:
        content = f.read()

    required_sections = [
        "## Overview",
        "## .pbix File Format",
        "### SecurityBindings",
        "### Recommended Approach: Binary ZIP Rebuild",
        "## Report-Level Measures",
        "## Report/Layout JSON Structure",
        "## Visual Container Patterns",
        "## Complete Workflow",
        "## Key Gotchas",
        "## PBI Desktop Local Analysis Services Instance",
        "## Live Connection Configuration",
        "## Power BI REST API Reference",
        "## Column Metadata Reference",
        "## Troubleshooting",
        "## Critical: No Inter-Measure References",
        "## Compelling Visual Design",
        "## Report Beautification System",
        "## PBIR",
        "## TMDL",
        "## MCP Servers",
        "## Best Practice Analyzer",
        "## PBIP Cascading Rename",
        "## Tabular Editor CLI",
        "## Enhanced TOM Patterns",
        "## SVG Measure Pattern Library",
        "## Naming Convention Standardization",
        "## Tabular Editor C# Scripting",
        "## Tabular Editor Macro System",
        "## Tabular Editor 3 Configuration",
        "## PBIP File Type Deep Reference",
    ]

    results = []
    for section in required_sections:
        found = section.lower() in content.lower()
        results.append((section, found))
        print(f"{'PASS' if found else 'FAIL'}: {section}")

    passed = sum(1 for _, f in results if f)
    print(f"\n{passed}/{len(results)} sections verified")
    return all(f for _, f in results)
```
