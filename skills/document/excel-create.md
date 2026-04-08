---
name: excel-create
description: "Use this skill any time an .xlsx or .xls file is involved — creating Excel workbooks, spreadsheets, reports, or dashboards; reading, parsing, or extracting data from Excel files; editing, modifying, or formatting existing workbooks; data analysis, ETL, pivot tables, charts, conditional formatting, or data validation. Trigger whenever the user mentions 'Excel', 'spreadsheet', 'workbook', '.xlsx', '.xls', '.csv to Excel', 'data table', or references an Excel filename."
---

# Excel Creation, Beautification & Data Engineering Skill

## Quick Reference

| Task | Tool | Guide |
|------|------|-------|
| Read/analyze content | `pandas.read_excel()` or `openpyxl.load_workbook()` | [Reading Data](#reading-data) |
| Create new workbook | openpyxl (primary) or xlsxwriter (rich formatting) | [Creation Engines](#creation-engines) |
| Modify existing workbook | openpyxl (only library that can read+write) | [openpyxl](#openpyxl-primary) |
| Data analysis + export | pandas + openpyxl/xlsxwriter engine | [Pandas Integration](#pandas-integration) |
| Large file streaming | openpyxl read_only/write_only mode | [Performance](#performance-optimization) |
| Charts | openpyxl or xlsxwriter | [Charts](#charts) |
| Conditional formatting | openpyxl or xlsxwriter | [Conditional Formatting](#conditional-formatting) |
| VBA macros | xlsxwriter (`add_vba_project`) | [VBA Macros](#vba-macros) |
| Dashboard | xlsxwriter (sparklines + data bars) | [Dashboard Design](#dashboard-design) |

---

## Library Selection Guide

| Feature | openpyxl | xlsxwriter | pandas |
|---------|----------|------------|--------|
| Read Excel files | Yes | **No** | Yes |
| Write Excel files | Yes | Yes | Yes (via engine) |
| Modify existing files | Yes | **No** | **No** |
| Advanced formatting | Yes | **Yes+** | No |
| Charts | Yes | Yes | No |
| Conditional formatting | Yes | Yes | No |
| Data bars / icon sets | Yes | Yes | No |
| Sparklines | **No** | Yes | No |
| VBA macros (.xlsm) | **No** | Yes | No |
| Tables (Ctrl+T) | Yes | Yes | No |
| Data validation | Yes | Yes | No |
| Images | Yes | Yes | No |
| Comments/notes | Yes | Yes | No |
| Large file performance | Moderate | **Fast** | Moderate |
| Rich text in cells | **No** | Yes | No |
| Streaming read | Yes (read_only) | N/A | No |
| Streaming write | Yes (write_only) | Yes (row-by-row) | No |
| Header/footer images | **No** | Yes | No |
| Outline/grouping | Yes | Yes | No |
| Autofilter | Yes | Yes | No |
| Freeze panes | Yes | Yes | No |
| Page setup/print | Yes | Yes | No |

**Decision matrix:**
- **Need to read OR modify existing files** → openpyxl (only option)
- **Creating new files with rich formatting** → xlsxwriter (faster, more features)
- **Quick data export with minimal formatting** → pandas with openpyxl or xlsxwriter engine
- **Data analysis pipeline** → pandas for transforms, then openpyxl/xlsxwriter for formatting
- **Need VBA macros or sparklines** → xlsxwriter (only option)
- **Large files (100K+ rows)** → openpyxl read_only/write_only or xlsxwriter

---

## Creation Engines

### openpyxl (Primary)

Python library for reading, writing, and modifying .xlsx files. The only library that can modify existing workbooks.

#### Setup

```python
pip install openpyxl
```

```python
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, PatternFill, Border, Side, Alignment, NamedStyle
from openpyxl.utils import get_column_letter
from openpyxl.chart import BarChart, LineChart, PieChart, Reference
from openpyxl.formatting.rule import (
    ColorScaleRule, DataBarRule, IconSetRule, CellIsRule, FormulaRule
)
from openpyxl.worksheet.table import Table, TableStyleInfo
from openpyxl.worksheet.datavalidation import DataValidation

# Create new workbook
wb = Workbook()
ws = wb.active
ws.title = "Data"

# Write data
ws['A1'] = "Header"
ws['A1'].font = Font(bold=True, size=12)
ws.append(["Col1", "Col2", "Col3"])  # Append row

wb.save("output.xlsx")
```

#### Reading Existing Files

```python
# Standard read
wb = load_workbook("existing.xlsx")
ws = wb.active

# Read with data_only (cached formula values instead of formulas)
wb = load_workbook("existing.xlsx", data_only=True)

# Read-only mode (streaming, low memory)
wb = load_workbook("large_file.xlsx", read_only=True)
ws = wb['Sheet1']
for row in ws.iter_rows(min_row=2, values_only=True):
    print(row)
wb.close()  # MUST close read-only workbooks

# Access cell values
value = ws['A1'].value
value = ws.cell(row=1, column=1).value
```

#### Writing Data

```python
# Cell by cell
ws['A1'] = "Text"
ws['B1'] = 42
ws['C1'] = datetime.datetime(2026, 2, 18)
ws['D1'] = "=SUM(B1:B10)"

# Append rows (fast for bulk data)
data = [
    ["Name", "Revenue", "Growth"],
    ["APAC", 12500000, 0.18],
    ["EMEA", 9800000, 0.12],
    ["Americas", 15200000, 0.22],
]
for row in data:
    ws.append(row)

# Write from list of dicts
headers = list(data_dicts[0].keys())
ws.append(headers)
for record in data_dicts:
    ws.append(list(record.values()))
```

#### Cell Styling

```python
from openpyxl.styles import Font, PatternFill, Border, Side, Alignment

# Font
cell.font = Font(
    name='Calibri', size=11, bold=True, italic=False,
    color='FFFFFF', underline='single'  # or 'double', 'none'
)

# Fill (background color)
cell.fill = PatternFill(
    start_color='4472C4', end_color='4472C4', fill_type='solid'
)

# Alignment
cell.alignment = Alignment(
    horizontal='center',  # 'left', 'center', 'right', 'justify'
    vertical='center',    # 'top', 'center', 'bottom'
    wrap_text=True,
    indent=1,             # 0-15, indentation level
    text_rotation=0       # 0-180 degrees
)

# Borders
thin_side = Side(style='thin', color='D9D9D9')
cell.border = Border(
    left=thin_side, right=thin_side,
    top=thin_side, bottom=thin_side
)

# Number format
cell.number_format = '$#,##0.00'
cell.number_format = '0.0%'
cell.number_format = 'yyyy-mm-dd'
```

**Border styles:** `'thin'`, `'medium'`, `'thick'`, `'double'`, `'dotted'`, `'dashed'`, `'dashDot'`, `'dashDotDot'`, `'hair'`, `'mediumDashed'`, `'mediumDashDot'`, `'mediumDashDotDot'`, `'slantDashDot'`

#### Named Styles (Reusable)

```python
from openpyxl.styles import NamedStyle

# Define once
header_style = NamedStyle(name='header')
header_style.font = Font(name='Calibri', bold=True, color='FFFFFF', size=11)
header_style.fill = PatternFill(start_color='44546A', end_color='44546A', fill_type='solid')
header_style.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
header_style.border = Border(
    bottom=Side(style='medium', color='000000')
)
wb.add_named_style(header_style)

# Apply to any cell
ws['A1'].style = 'header'
ws['B1'].style = 'header'
```

#### Column and Row Dimensions

```python
# Set column width (in characters, approximately)
ws.column_dimensions['A'].width = 25
ws.column_dimensions['B'].width = 15

# Set row height (in points)
ws.row_dimensions[1].height = 35

# Auto-fit column width (manual calculation — openpyxl has no built-in auto-fit)
def auto_fit_columns(ws, min_width=8, max_width=50, padding=2):
    """Calculate and set column widths based on content."""
    for column_cells in ws.columns:
        col_letter = get_column_letter(column_cells[0].column)
        max_length = 0
        for cell in column_cells:
            if cell.value is not None:
                cell_len = len(str(cell.value))
                if cell_len > max_length:
                    max_length = cell_len
        adjusted = min(max(max_length + padding, min_width), max_width)
        ws.column_dimensions[col_letter].width = adjusted * 1.15  # Font scaling factor

auto_fit_columns(ws)

# Hide column
ws.column_dimensions['C'].hidden = True

# Hide row
ws.row_dimensions[5].hidden = True

# Group/outline rows (collapsible)
ws.row_dimensions.group(start=5, end=10, outline_level=1, hidden=True)

# Group/outline columns
ws.column_dimensions.group('D', 'F', outline_level=1, hidden=True)
```

#### Merge Cells

```python
# Merge
ws.merge_cells('A1:E1')
ws['A1'] = "Merged Header"
ws['A1'].alignment = Alignment(horizontal='center')

# Unmerge
ws.unmerge_cells('A1:E1')

# CAUTION: Merged cells break sorting, filtering, and accessibility.
# Prefer "Center Across Selection" when possible (not directly supported
# in openpyxl — use alignment with fill on each cell instead).
```

#### Images

```python
from openpyxl.drawing.image import Image

img = Image('logo.png')
img.width = 150  # pixels
img.height = 50
ws.add_image(img, 'A1')  # Anchor to cell A1
```

#### Freeze Panes

```python
# Freeze rows above and columns to the left of the specified cell
ws.freeze_panes = 'A2'   # Freeze header row
ws.freeze_panes = 'B2'   # Freeze header row + column A
ws.freeze_panes = 'C3'   # Freeze rows 1-2 and columns A-B
ws.freeze_panes = None    # Unfreeze
```

#### Autofilter

```python
ws.auto_filter.ref = 'A1:E100'

# Add filter criteria (informational — Excel applies on open)
ws.auto_filter.add_filter_column(0, ['APAC', 'EMEA'])
ws.auto_filter.add_sort_condition('B2:B100')
```

#### Sheet Protection

```python
# Protect sheet with password
ws.protection.sheet = True
ws.protection.password = 'mypassword'
ws.protection.enable()

# Granular protection (True = protected/locked)
ws.protection.formatCells = False      # Allow formatting
ws.protection.formatRows = False       # Allow row formatting
ws.protection.insertRows = False       # Allow inserting rows
ws.protection.sort = False             # Allow sorting
ws.protection.autoFilter = False       # Allow filtering
ws.protection.selectLockedCells = False
ws.protection.selectUnlockedCells = False

# Workbook protection
wb.security.workbookPassword = 'bookpassword'
wb.security.lockStructure = True
```

#### Page Setup / Print

```python
# Orientation
ws.page_setup.orientation = ws.ORIENTATION_LANDSCAPE  # or ORIENTATION_PORTRAIT

# Paper size
ws.page_setup.paperSize = ws.PAPERSIZE_LETTER  # or PAPERSIZE_A4

# Fit to page
ws.page_setup.fitToWidth = 1
ws.page_setup.fitToHeight = 0  # 0 = as many pages as needed vertically

# Margins (in inches)
ws.page_margins.left = 0.5
ws.page_margins.right = 0.5
ws.page_margins.top = 0.5
ws.page_margins.bottom = 0.5
ws.page_margins.header = 0.3
ws.page_margins.footer = 0.3

# Print titles (repeat rows/columns)
ws.print_title_rows = '1:2'      # Repeat rows 1-2 on every page
ws.print_title_cols = 'A:B'      # Repeat columns A-B on every page

# Print area
ws.print_area = 'A1:G50'

# Header and footer
ws.oddHeader.center.text = "Monthly Report"
ws.oddFooter.left.text = "Confidential"
ws.oddFooter.center.text = "Page &[Page] of &[Pages]"
ws.oddFooter.right.text = "&[Date]"

# Gridlines
ws.sheet_properties.pageSetUpPr.fitToPage = True
ws.print_options.gridLines = False  # Don't print gridlines
```

---

### xlsxwriter (Rich Formatting)

Write-only library optimized for creating new, richly formatted .xlsx files. Faster than openpyxl for large files. Supports sparklines and VBA macros.

#### Setup

```python
pip install xlsxwriter
```

```python
import xlsxwriter

workbook = xlsxwriter.Workbook('output.xlsx')
worksheet = workbook.add_worksheet('Data')

# Write data
worksheet.write('A1', 'Header')
worksheet.write(0, 1, 42)           # row, col (0-indexed)
worksheet.write_row('A2', [1, 2, 3])
worksheet.write_column('D1', [10, 20, 30])

workbook.close()  # MUST close to write the file
```

#### Format Objects

```python
# Create format objects (immutable after creation)
header_fmt = workbook.add_format({
    'bold': True,
    'font_name': 'Calibri',
    'font_size': 11,
    'font_color': '#FFFFFF',
    'bg_color': '#44546A',
    'border': 1,
    'border_color': '#44546A',
    'align': 'center',
    'valign': 'vcenter',
    'text_wrap': True,
    'num_format': '0.00',
})

# Apply to cells
worksheet.write('A1', 'Revenue', header_fmt)

# Currency format
currency_fmt = workbook.add_format({
    'num_format': '$#,##0.00',
    'font_name': 'Calibri',
    'font_size': 10,
})

# Percentage format
pct_fmt = workbook.add_format({
    'num_format': '0.0%',
    'font_name': 'Calibri',
})

# Date format
date_fmt = workbook.add_format({
    'num_format': 'yyyy-mm-dd',
    'font_name': 'Calibri',
})

# Red negative numbers in parentheses
acct_fmt = workbook.add_format({
    'num_format': '#,##0.00_);[Red](#,##0.00)',
})
```

**xlsxwriter format properties:**

| Property | Type | Example |
|----------|------|---------|
| `bold` | bool | `True` |
| `italic` | bool | `True` |
| `underline` | int | `1` (single), `2` (double) |
| `font_name` | str | `'Calibri'` |
| `font_size` | int | `11` |
| `font_color` | str | `'#FFFFFF'` or `'white'` |
| `bg_color` | str | `'#4472C4'` |
| `border` | int | `1` (thin), `2` (medium), `5` (thick) |
| `border_color` | str | `'#D9D9D9'` |
| `align` | str | `'center'`, `'left'`, `'right'`, `'justify'` |
| `valign` | str | `'vcenter'`, `'top'`, `'bottom'` |
| `text_wrap` | bool | `True` |
| `indent` | int | `1` |
| `rotation` | int | `0`-`360` |
| `num_format` | str | `'$#,##0.00'` |
| `locked` | bool | `True` (for protection) |
| `hidden` | bool | `True` (hide formula) |

#### Column and Row Sizing

```python
# Set column width (in character units)
worksheet.set_column('A:A', 25)          # Column A = 25 chars
worksheet.set_column('B:D', 15)          # Columns B-D = 15 chars
worksheet.set_column('E:E', 12, currency_fmt)  # Width + default format

# Set row height (in points)
worksheet.set_row(0, 35, header_fmt)     # Row 0 = 35pt with format
worksheet.set_row(1, 20)                 # Row 1 = 20pt

# Hide column
worksheet.set_column('F:F', None, None, {'hidden': True})

# Hide row
worksheet.set_row(5, None, None, {'hidden': True})
```

#### Merge Cells

```python
merge_fmt = workbook.add_format({
    'bold': True, 'align': 'center', 'valign': 'vcenter',
    'font_size': 14, 'bg_color': '#44546A', 'font_color': '#FFFFFF'
})
worksheet.merge_range('A1:E1', 'Report Title', merge_fmt)
```

#### Images

```python
worksheet.insert_image('A1', 'logo.png', {
    'x_offset': 10, 'y_offset': 5,
    'x_scale': 0.5, 'y_scale': 0.5,
    'positioning': 1  # 1=move with cells, 2=don't move/size, 3=move and size
})

# From bytes/buffer
worksheet.insert_image('A1', 'logo.png', {'image_data': io.BytesIO(img_bytes)})
```

#### Freeze Panes

```python
worksheet.freeze_panes(1, 0)    # Freeze row 0 (header)
worksheet.freeze_panes(1, 1)    # Freeze row 0 + column 0
worksheet.freeze_panes(2, 2)    # Freeze rows 0-1 + columns 0-1
```

#### Autofilter

```python
worksheet.autofilter(0, 0, last_row, last_col)
# or
worksheet.autofilter('A1:E100')
```

#### Page Setup / Print

```python
worksheet.set_landscape()        # or set_portrait()
worksheet.set_paper(1)           # 1=Letter, 9=A4
worksheet.set_margins(left=0.5, right=0.5, top=0.5, bottom=0.5)
worksheet.set_header('&L&"Calibri,Bold"Company Name&C&"Calibri"Monthly Report&R&D')
worksheet.set_footer('&LConfidential&CPage &P of &N&R&F')
worksheet.repeat_rows(0, 1)      # Repeat rows 0-1 on every page
worksheet.repeat_columns(0, 0)   # Repeat column A on every page
worksheet.print_area('A1:G50')
worksheet.fit_to_pages(1, 0)     # Fit to 1 page wide, unlimited tall
worksheet.hide_gridlines(1)      # 0=screen+print, 1=print only, 2=screen+print
worksheet.set_print_scale(75)    # 75% scale
```

#### Header/Footer Format Codes

| Code | Meaning |
|------|---------|
| `&L` | Left section |
| `&C` | Center section |
| `&R` | Right section |
| `&P` | Page number |
| `&N` | Total pages |
| `&D` | Date |
| `&T` | Time |
| `&F` | Filename |
| `&A` | Sheet name |
| `&Z&F` | Full file path |
| `&"Font,Style"` | Font name and style |
| `&B` | Bold |
| `&I` | Italic |
| `&nn` | Font size (e.g., `&12`) |

#### Sheet Protection

```python
worksheet.protect('password', {
    'format_cells': True,      # Allow formatting
    'insert_rows': True,       # Allow inserting rows
    'sort': True,              # Allow sorting
    'autofilter': True,        # Allow filtering
    'select_locked_cells': True,
    'select_unlocked_cells': True,
})
```

#### Outline / Grouping

```python
# Group rows (collapsible)
worksheet.set_row(4, None, None, {'level': 1})
worksheet.set_row(5, None, None, {'level': 1})
worksheet.set_row(6, None, None, {'level': 1, 'collapsed': True})

# Group columns
worksheet.set_column('D:F', 12, None, {'level': 1, 'collapsed': True})
```

#### Sparklines

```python
# Line sparkline
worksheet.add_sparkline('G2', {
    'range': 'B2:F2',
    'type': 'line',
    'high_point': True,
    'low_point': True,
    'markers': True,
    'style': 36,           # Built-in style 1-36
    'series_color': '#4472C4',
    'negative_color': '#FF0000',
})

# Column sparkline
worksheet.add_sparkline('G3', {
    'range': 'B3:F3',
    'type': 'column',
    'style': 36,
})

# Win/Loss sparkline
worksheet.add_sparkline('G4', {
    'range': 'B4:F4',
    'type': 'win_loss',
})
```

#### VBA Macros

```python
# Step 1: Extract vbaProject.bin from an existing .xlsm file
# Run: vba_extract.py source_macro_file.xlsm

# Step 2: Create macro-enabled workbook
workbook = xlsxwriter.Workbook('output.xlsm')  # Note: .xlsm extension
worksheet = workbook.add_worksheet()

# Add the VBA binary
workbook.add_vba_project('./vbaProject.bin')

# Optional: Set VBA codenames if macros reference them
workbook.set_vba_name('ThisWorkbook')
worksheet.set_vba_name('Sheet1')

# Add a button linked to a macro
worksheet.insert_button('B3', {
    'macro': 'say_hello',
    'caption': 'Run Macro',
    'width': 100,
    'height': 30
})

workbook.close()
```

#### Rich Text in Cells

```python
# xlsxwriter can format parts of a cell differently (openpyxl cannot)
red = workbook.add_format({'color': 'red'})
blue = workbook.add_format({'color': 'blue'})
bold = workbook.add_format({'bold': True})

worksheet.write_rich_string('A1',
    'This is ', bold, 'bold', ' and ', red, 'red', ' and ', blue, 'blue', '.'
)
```

---

### Pandas Integration

Use pandas for data manipulation, then openpyxl or xlsxwriter for formatting.

#### Basic Export

```python
import pandas as pd

df = pd.DataFrame({
    'Name': ['APAC', 'EMEA', 'Americas'],
    'Revenue': [12500000, 9800000, 15200000],
    'Growth': [0.18, 0.12, 0.22]
})

# Simple export (openpyxl engine — default)
df.to_excel('output.xlsx', index=False, sheet_name='Revenue')

# With xlsxwriter engine
df.to_excel('output.xlsx', index=False, engine='xlsxwriter')
```

#### Multiple Sheets

```python
with pd.ExcelWriter('report.xlsx', engine='openpyxl') as writer:
    df_summary.to_excel(writer, sheet_name='Summary', index=False)
    df_detail.to_excel(writer, sheet_name='Detail', index=False)
    df_appendix.to_excel(writer, sheet_name='Appendix', index=False)
```

#### Pandas + xlsxwriter Formatting

```python
with pd.ExcelWriter('report.xlsx', engine='xlsxwriter') as writer:
    df.to_excel(writer, sheet_name='Data', index=False, startrow=1)

    workbook = writer.book
    worksheet = writer.sheets['Data']

    # Define formats
    header_fmt = workbook.add_format({
        'bold': True, 'bg_color': '#44546A', 'font_color': '#FFFFFF',
        'border': 1, 'align': 'center', 'valign': 'vcenter',
        'font_name': 'Calibri', 'font_size': 11
    })
    currency_fmt = workbook.add_format({'num_format': '$#,##0.00'})
    pct_fmt = workbook.add_format({'num_format': '0.0%'})

    # Write formatted headers
    for col_num, header in enumerate(df.columns):
        worksheet.write(1, col_num, header, header_fmt)

    # Title row
    title_fmt = workbook.add_format({
        'bold': True, 'font_size': 16, 'font_color': '#1E2761'
    })
    worksheet.merge_range('A1:C1', 'Revenue Report', title_fmt)

    # Column formats
    worksheet.set_column('B:B', 15, currency_fmt)
    worksheet.set_column('C:C', 12, pct_fmt)

    # Conditional formatting
    worksheet.conditional_format('C3:C100', {
        'type': 'cell', 'criteria': '>=', 'value': 0.15,
        'format': workbook.add_format({'bg_color': '#C6EFCE', 'font_color': '#006100'})
    })
```

#### Pandas + openpyxl Formatting

```python
with pd.ExcelWriter('report.xlsx', engine='openpyxl') as writer:
    df.to_excel(writer, sheet_name='Data', index=False)

    wb = writer.book
    ws = writer.sheets['Data']

    # Style headers
    header_font = Font(bold=True, color='FFFFFF', size=11)
    header_fill = PatternFill(start_color='44546A', end_color='44546A', fill_type='solid')

    for cell in ws[1]:  # Row 1
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal='center', vertical='center')

    # Auto-fit columns
    auto_fit_columns(ws)

    # Number formats
    for row in ws.iter_rows(min_row=2, min_col=2, max_col=2):
        for cell in row:
            cell.number_format = '$#,##0.00'
```

#### Append to Existing File

```python
# openpyxl is the only engine that can append to existing files
with pd.ExcelWriter('existing.xlsx', engine='openpyxl', mode='a',
                     if_sheet_exists='overlay') as writer:
    df_new.to_excel(writer, sheet_name='NewSheet', index=False)
```

**`if_sheet_exists` options:** `'error'` (default), `'new'` (create with suffix), `'replace'` (delete and recreate), `'overlay'` (write on top of existing)

#### Reading Excel Files

```python
# Basic read
df = pd.read_excel('file.xlsx')

# Specific sheet
df = pd.read_excel('file.xlsx', sheet_name='Data')

# Multiple sheets (returns dict of DataFrames)
dfs = pd.read_excel('file.xlsx', sheet_name=None)

# With options
df = pd.read_excel('file.xlsx',
    sheet_name='Data',
    header=0,              # Row index for headers (0-based)
    skiprows=2,            # Skip first 2 rows
    usecols='A:E',         # Only read columns A-E
    dtype={'ID': str},     # Force column types
    na_values=['N/A', '-'],
    engine='openpyxl'      # Explicit engine
)
```

---

## Design System

### Color Palettes

**The 60-30-10 Rule:** 60% dominant (background, large fills), 30% secondary (headers, cards), 10% accent (highlights, KPIs).

#### Corporate Palettes

| Theme | Header | Alt Row | Accent | Text | Best For |
|-------|--------|---------|--------|------|----------|
| **Classic Blue** | `#4472C4` | `#D6DCE4` | `#4472C4` | `#000000` | General corporate |
| **Dark Navy** | `#44546A` | `#E7E9ED` | `#2F5496` | `#000000` | Executive reports |
| **Forest Green** | `#548235` | `#E2EFDA` | `#70AD47` | `#000000` | Sustainability, growth |
| **Warm Orange** | `#C55A11` | `#FBE5D6` | `#ED7D31` | `#000000` | Marketing, creative |
| **Berry** | `#7030A0` | `#E8D5F5` | `#9B59B6` | `#000000` | Innovation, premium |
| **Teal** | `#2E75B6` | `#DAEEF3` | `#00B0F0` | `#000000` | Technology, data |
| **Charcoal Minimal** | `#333333` | `#F2F2F2` | `#333333` | `#000000` | Minimal, modern |
| **Fortive Corporate** | `#005EB8` | `#E6F0FA` | `#00A3E0` | `#000000` | Fortive brand |

#### Financial Model Color Coding (Investment Banking Standard)

| Font Color | Hex | Meaning |
|------------|-----|---------|
| Blue | `#0070C0` | Hard-coded inputs / assumptions |
| Black | `#000000` | Formulas / calculations (same sheet) |
| Green | `#00B050` | Links to other worksheets |
| Red | `#FF0000` | Links to external files / errors |

#### Excel's Built-in Conditional Format Colors

| Category | Background | Font Color | Usage |
|----------|-----------|------------|-------|
| Good | `#C6EFCE` | `#006100` | Positive values, pass |
| Bad | `#FFC7CE` | `#9C0006` | Negative values, fail |
| Neutral | `#FFEB9C` | `#9C6500` | Warning, amber |

### Typography

| Context | Font | Size | Weight |
|---------|------|------|--------|
| Data cells | Calibri, Arial | 10-11pt | Regular |
| Column headers | Calibri, Arial | 11-12pt | Bold |
| Report title | Calibri Light, Segoe UI | 14-18pt | Regular or Bold |
| Financial models | Calibri, Arial Narrow | 10pt | Regular |
| Monospace (IDs, codes) | Consolas, Courier New | 10pt | Regular |

**Rules:**
- Maximum 2 font families per workbook
- Left-align text, right-align numbers, center headers
- Minimum 10pt for readability
- Use weight contrast (bold vs. regular) for hierarchy

### Border Hierarchy

| Type | Style | Color | Usage |
|------|-------|-------|-------|
| None | — | — | Most internal cells (use fill instead) |
| Thin | `thin` | `#D9D9D9` | Subtle separators |
| Medium | `medium` | `#000000` | Section breaks, table outline |
| Thick/Double | `thick`/`double` | `#000000` | Grand totals, financial statement bottom |
| Top-only medium | medium top | `#000000` | Subtotal separator |

**Best practice:** Avoid "all borders on every cell." Use fill colors for visual grouping and reserve borders for structural emphasis.

### Alignment Rules

| Data Type | Horizontal | Vertical |
|-----------|-----------|----------|
| Text/labels | Left | Center |
| Numbers | Right | Center |
| Currency | Right | Center |
| Headers | Center | Bottom or Center |
| Dates | Center or Right | Center |
| Percentages | Right | Center |

---

## Number Format Strings

Excel number format codes are their own mini-language. Format strings can have up to 4 sections: `positive;negative;zero;text`.

### Common Formats

| Category | Format String | Example Output |
|----------|--------------|----------------|
| General | `General` | (default) |
| Integer | `#,##0` | 1,234 |
| 2 decimals | `#,##0.00` | 1,234.56 |
| Currency | `"$"#,##0.00` | $1,234.56 |
| Accounting | `_("$"* #,##0.00_);_("$"* (#,##0.00);_("$"* "-"??_);_(@_)` | (aligned with dashes for zero) |
| Percentage | `0.0%` | 12.3% |
| Date (ISO) | `yyyy-mm-dd` | 2026-02-18 |
| Date (US) | `mm/dd/yyyy` | 02/18/2026 |
| Date (short) | `d-mmm-yy` | 18-Feb-26 |
| Date (long) | `dddd, mmmm d, yyyy` | Wednesday, February 18, 2026 |
| Time | `hh:mm:ss` | 14:30:00 |
| Integer with sign | `+#,##0;-#,##0;0` | +1,234 / -1,234 / 0 |
| Red negatives | `#,##0.00;[Red](#,##0.00)` | 1,234.56 / (1,234.56) in red |

### Scale Reduction (Thousands / Millions / Billions)

| Format String | Input | Output |
|--------------|-------|--------|
| `#,##0,` | 1234567 | 1,235 |
| `#,##0,"K"` | 1234567 | 1,235K |
| `#,##0,,` | 1234567890 | 1,235 |
| `$#,##0.0,,"M"` | 1234567890 | $1,234.6M |
| `$#,##0.0,,,"B"` | 1234567890000 | $1,234.6B |

### Format Code Characters

| Character | Meaning |
|-----------|---------|
| `0` | Required digit (displays 0 if no digit) |
| `#` | Optional digit (displays nothing if no digit) |
| `,` | Thousands separator (or scale divider if trailing) |
| `.` | Decimal point |
| `%` | Multiply by 100 and display percent sign |
| `"text"` | Literal text |
| `_` | Space equal to the width of the next character |
| `*` | Repeat the next character to fill the column |
| `[Red]` | Color: `[Black]`, `[Blue]`, `[Cyan]`, `[Green]`, `[Magenta]`, `[Red]`, `[White]`, `[Yellow]` |
| `[condition]` | Conditional: `[>100]`, `[<=0]` |
| `@` | Text placeholder |

### Conditional Number Formats

```
[>=1000000]$#,##0.0,,"M";[>=1000]$#,##0.0,"K";$#,##0
```
This auto-scales: values ≥1M show as "$1.2M", ≥1K as "$1.2K", else "$1,234".

---

## Conditional Formatting

### openpyxl

```python
from openpyxl.formatting.rule import (
    ColorScaleRule, DataBarRule, IconSetRule, CellIsRule, FormulaRule
)
from openpyxl.styles import PatternFill, Font
from openpyxl.styles.differential import DifferentialStyle

# Cell value rules
red_fill = PatternFill(start_color='FFC7CE', end_color='FFC7CE', fill_type='solid')
red_font = Font(color='9C0006')
green_fill = PatternFill(start_color='C6EFCE', end_color='C6EFCE', fill_type='solid')
green_font = Font(color='006100')

ws.conditional_formatting.add('C2:C100',
    CellIsRule(operator='greaterThan', formula=['0'],
              fill=green_fill, font=green_font))
ws.conditional_formatting.add('C2:C100',
    CellIsRule(operator='lessThan', formula=['0'],
              fill=red_fill, font=red_font))

# Formula-based rule (highlight entire row)
ws.conditional_formatting.add('A2:E100',
    FormulaRule(formula=['$D2="Overdue"'],
               fill=PatternFill(start_color='FFC7CE', end_color='FFC7CE', fill_type='solid')))

# 3-color scale (green-yellow-red)
ws.conditional_formatting.add('B2:B100',
    ColorScaleRule(
        start_type='min', start_color='F8696B',
        mid_type='percentile', mid_value=50, mid_color='FFEB84',
        end_type='max', end_color='63BE7B'
    ))

# 2-color scale (white to blue)
ws.conditional_formatting.add('B2:B100',
    ColorScaleRule(
        start_type='min', start_color='FFFFFF',
        end_type='max', end_color='4472C4'
    ))

# Data bars
ws.conditional_formatting.add('D2:D100',
    DataBarRule(
        start_type='min', end_type='max',
        color='4472C4', showValue=True
    ))

# Icon sets
ws.conditional_formatting.add('E2:E100',
    IconSetRule(
        icon_style='3TrafficLights1',
        type='percent',
        values=[0, 33, 67]
    ))
```

**Available icon styles:** `'3Arrows'`, `'3ArrowsGray'`, `'3Flags'`, `'3TrafficLights1'`, `'3TrafficLights2'`, `'3Signs'`, `'3Symbols'`, `'3Symbols2'`, `'4Arrows'`, `'4ArrowsGray'`, `'4RedToBlack'`, `'4Rating'`, `'4TrafficLights'`, `'5Arrows'`, `'5ArrowsGray'`, `'5Rating'`, `'5Quarters'`

### xlsxwriter

```python
# Cell value conditional format
good_fmt = workbook.add_format({'bg_color': '#C6EFCE', 'font_color': '#006100'})
bad_fmt = workbook.add_format({'bg_color': '#FFC7CE', 'font_color': '#9C0006'})

worksheet.conditional_format('C2:C100', {
    'type': 'cell', 'criteria': '>=', 'value': 0,
    'format': good_fmt
})
worksheet.conditional_format('C2:C100', {
    'type': 'cell', 'criteria': '<', 'value': 0,
    'format': bad_fmt
})

# 3-color scale
worksheet.conditional_format('B2:B100', {
    'type': '3_color_scale',
    'min_color': '#F8696B',
    'mid_color': '#FFEB84',
    'max_color': '#63BE7B'
})

# Data bars (solid fill)
worksheet.conditional_format('D2:D100', {
    'type': 'data_bar',
    'bar_color': '#4472C4',
    'bar_solid': True
})

# Icon sets with custom thresholds
worksheet.conditional_format('E2:E100', {
    'type': 'icon_set',
    'icon_style': '3_traffic_lights',
    'icons': [
        {'criteria': '>=', 'type': 'number', 'value': 90},
        {'criteria': '>=', 'type': 'number', 'value': 70},
        {'criteria': '<',  'type': 'number', 'value': 70}
    ]
})

# Formula-based (highlight entire row where column D = "Overdue")
worksheet.conditional_format('A2:E100', {
    'type': 'formula',
    'criteria': '=$D2="Overdue"',
    'format': bad_fmt
})

# Top/Bottom N
worksheet.conditional_format('B2:B100', {
    'type': 'top', 'value': 10, 'criteria': '%',  # Top 10%
    'format': good_fmt
})

# Duplicate values
worksheet.conditional_format('A2:A100', {
    'type': 'duplicate',
    'format': workbook.add_format({'bg_color': '#FFEB9C', 'font_color': '#9C6500'})
})
```

### Common Formula-Based Rules

| Purpose | Formula |
|---------|---------|
| Highlight entire row | `=$B2="Overdue"` |
| Alternating row color | `=MOD(ROW(),2)=0` |
| Highlight duplicates | `=COUNTIF($A:$A,$A2)>1` |
| Dates in past | `=A2<TODAY()` |
| Top N values | `=A2>=LARGE($A$2:$A$100,10)` |
| Above average | `=A2>AVERAGE($A$2:$A$100)` |
| Variance > threshold | `=ABS(B2-C2)/C2>0.1` |
| Weekend dates | `=OR(WEEKDAY(A2)=1,WEEKDAY(A2)=7)` |

---

## Charts

### openpyxl Charts

```python
from openpyxl.chart import BarChart, LineChart, PieChart, Reference
from openpyxl.chart.series import DataPoint
from openpyxl.chart.label import DataLabelList

# Bar/Column chart
chart = BarChart()
chart.type = "col"             # "col" for column, "bar" for horizontal
chart.title = "Revenue by Region"
chart.y_axis.title = "Revenue ($M)"
chart.x_axis.title = "Region"
chart.style = 10               # Built-in style 1-48

data = Reference(ws, min_col=2, min_row=1, max_row=5, max_col=2)
cats = Reference(ws, min_col=1, min_row=2, max_row=5)
chart.add_data(data, titles_from_data=True)
chart.set_categories(cats)
chart.shape = 4                # Rounded corners

ws.add_chart(chart, "D2")     # Anchor position

# Line chart
line = LineChart()
line.title = "Monthly Trend"
line.style = 10
data = Reference(ws, min_col=2, min_row=1, max_row=13, max_col=2)
cats = Reference(ws, min_col=1, min_row=2, max_row=13)
line.add_data(data, titles_from_data=True)
line.set_categories(cats)
line.series[0].smooth = True   # Smooth line

ws.add_chart(line, "D15")

# Pie chart
pie = PieChart()
pie.title = "Market Share"
data = Reference(ws, min_col=2, min_row=1, max_row=5)
cats = Reference(ws, min_col=1, min_row=2, max_row=5)
pie.add_data(data, titles_from_data=True)
pie.set_categories(cats)

ws.add_chart(pie, "D28")

# Chart sizing
chart.width = 18    # in cm (default ~15)
chart.height = 10   # in cm (default ~7.5)
```

### xlsxwriter Charts

```python
chart = workbook.add_chart({'type': 'column'})

chart.add_series({
    'name':       '=Data!$B$1',
    'categories': '=Data!$A$2:$A$5',
    'values':     '=Data!$B$2:$B$5',
    'fill':       {'color': '#4472C4'},
    'gap':        150,
})

chart.set_title({'name': 'Revenue by Region'})
chart.set_x_axis({
    'name': 'Region',
    'label_position': 'low',
    'major_gridlines': {'visible': False},
})
chart.set_y_axis({
    'name': 'Revenue ($M)',
    'major_gridlines': {'visible': True, 'line': {'color': '#E2E8F0', 'width': 0.5}},
})
chart.set_legend({'position': 'bottom'})
chart.set_size({'width': 720, 'height': 400})  # in pixels
chart.set_plotarea({'border': {'none': True}, 'fill': {'none': True}})

worksheet.insert_chart('D2', chart)

# Line chart
line = workbook.add_chart({'type': 'line'})
line.add_series({
    'name': 'Trend',
    'categories': '=Data!$A$2:$A$13',
    'values': '=Data!$B$2:$B$13',
    'line': {'color': '#4472C4', 'width': 2.5},
    'smooth': True,
    'marker': {'type': 'circle', 'size': 5, 'fill': {'color': '#4472C4'}},
})

# Combination chart (column + line)
combo = workbook.add_chart({'type': 'column'})
combo.add_series({
    'name': 'Revenue',
    'categories': '=Data!$A$2:$A$5',
    'values': '=Data!$B$2:$B$5',
    'fill': {'color': '#4472C4'},
})
line_overlay = workbook.add_chart({'type': 'line'})
line_overlay.add_series({
    'name': 'Growth %',
    'categories': '=Data!$A$2:$A$5',
    'values': '=Data!$C$2:$C$5',
    'y2_axis': True,
    'line': {'color': '#ED7D31', 'width': 2},
})
combo.combine(line_overlay)
combo.set_y2_axis({'name': 'Growth %', 'num_format': '0%'})

# Pie / Doughnut
pie = workbook.add_chart({'type': 'doughnut'})
pie.add_series({
    'name': 'Share',
    'categories': '=Data!$A$2:$A$5',
    'values': '=Data!$B$2:$B$5',
    'points': [
        {'fill': {'color': '#4472C4'}},
        {'fill': {'color': '#ED7D31'}},
        {'fill': {'color': '#A5A5A5'}},
        {'fill': {'color': '#FFC000'}},
    ],
    'data_labels': {'percentage': True, 'position': 'outside_end'},
})
```

**xlsxwriter chart types:** `'area'`, `'bar'`, `'column'`, `'doughnut'`, `'line'`, `'pie'`, `'radar'`, `'scatter'`, `'stock'`

**Subtypes (append to type):** `'stacked'`, `'percent_stacked'` — e.g., `{'type': 'column', 'subtype': 'stacked'}`

---

## Tables

### openpyxl Tables

```python
from openpyxl.worksheet.table import Table, TableStyleInfo

# Create table (data must already be in the cells)
tab = Table(displayName="SalesData", ref="A1:E20")
style = TableStyleInfo(
    name="TableStyleMedium9",  # Built-in style name
    showFirstColumn=False,
    showLastColumn=False,
    showRowStripes=True,
    showColumnStripes=False
)
tab.tableStyleInfo = style
ws.add_table(tab)
```

**Recommended table styles:**
- `TableStyleMedium2` — Blue headers, blue-gray banding (classic corporate)
- `TableStyleMedium9` — Blue headers, lighter banding
- `TableStyleMedium15` — Green headers (finance)
- `TableStyleLight1` — Minimal, thin borders only
- `TableStyleDark1` — Dark headers, high contrast

### xlsxwriter Tables

```python
# Write data first, then add table
data = [
    ['Region', 'Revenue', 'Growth', 'Status'],
    ['APAC', 12500000, 0.18, 'On Track'],
    ['EMEA', 9800000, 0.12, 'Behind'],
    ['Americas', 15200000, 0.22, 'Ahead'],
]
for row_num, row_data in enumerate(data):
    worksheet.write_row(row_num, 0, row_data)

worksheet.add_table(0, 0, len(data)-1, len(data[0])-1, {
    'name': 'SalesData',
    'style': 'Table Style Medium 9',
    'autofilter': True,
    'columns': [
        {'header': 'Region'},
        {'header': 'Revenue', 'format': currency_fmt},
        {'header': 'Growth', 'format': pct_fmt},
        {'header': 'Status'},
    ],
    'total_row': True,
    'total_string': 'Total',          # Label in first column
    'total_function': 'sum',           # For numeric columns
})
```

---

## Data Validation

### openpyxl

```python
from openpyxl.worksheet.datavalidation import DataValidation

# Dropdown list
dv = DataValidation(
    type="list",
    formula1='"Option A,Option B,Option C"',
    allow_blank=True
)
dv.error = "Invalid selection"
dv.errorTitle = "Error"
dv.prompt = "Select an option"
dv.promptTitle = "Choose"
ws.add_data_validation(dv)
dv.add('D2:D100')

# Whole number range
dv_num = DataValidation(
    type="whole",
    operator="between",
    formula1=1,
    formula2=100
)
ws.add_data_validation(dv_num)
dv_num.add('E2:E100')

# Date range
dv_date = DataValidation(
    type="date",
    operator="greaterThan",
    formula1="2025-01-01"
)
ws.add_data_validation(dv_date)
dv_date.add('F2:F100')

# Custom formula
dv_custom = DataValidation(
    type="custom",
    formula1='=LEN(A2)<=50'
)
ws.add_data_validation(dv_custom)
dv_custom.add('A2:A100')
```

### xlsxwriter

```python
# Dropdown list
worksheet.data_validation('D2:D100', {
    'validate': 'list',
    'source': ['Option A', 'Option B', 'Option C'],
    'input_title': 'Choose',
    'input_message': 'Select an option',
    'error_title': 'Error',
    'error_message': 'Invalid selection',
})

# Integer range
worksheet.data_validation('E2:E100', {
    'validate': 'integer',
    'criteria': 'between',
    'minimum': 1,
    'maximum': 100,
})

# Text length
worksheet.data_validation('A2:A100', {
    'validate': 'length',
    'criteria': '<=',
    'value': 50,
})

# List from cell range
worksheet.data_validation('G2:G100', {
    'validate': 'list',
    'source': '=Lookups!$A$1:$A$20',
})
```

---

## Dashboard Design

### KPI Scorecard Pattern (xlsxwriter)

```python
import xlsxwriter

wb = xlsxwriter.Workbook('dashboard.xlsx')
ws = wb.add_worksheet('Dashboard')

# Hide gridlines for dashboard look
ws.hide_gridlines(2)

# Define formats
title_fmt = wb.add_format({
    'bold': True, 'font_size': 18, 'font_color': '#1E2761',
    'bottom': 2, 'bottom_color': '#4472C4'
})
kpi_value_fmt = wb.add_format({
    'bold': True, 'font_size': 28, 'font_color': '#1E2761',
    'align': 'center', 'valign': 'vcenter'
})
kpi_label_fmt = wb.add_format({
    'font_size': 10, 'font_color': '#605E5C',
    'align': 'center', 'valign': 'top'
})
kpi_trend_good = wb.add_format({
    'bold': True, 'font_size': 10, 'font_color': '#107C10',
    'align': 'center'
})
kpi_trend_bad = wb.add_format({
    'bold': True, 'font_size': 10, 'font_color': '#D13438',
    'align': 'center'
})
kpi_bg = wb.add_format({'bg_color': '#F4F4F4', 'border': 0})

# Title
ws.merge_range('A1:H1', 'Monthly Performance Dashboard — February 2026', title_fmt)
ws.set_row(0, 40)

# KPI cards (row 3-5)
kpis = [
    {'value': '$12.4M', 'label': 'Revenue', 'trend': '+18% YoY', 'up': True},
    {'value': '1,247', 'label': 'Orders', 'trend': '+8% MoM', 'up': True},
    {'value': '94.2%', 'label': 'CSAT', 'trend': '+2.1pts', 'up': True},
    {'value': '$420', 'label': 'Avg Order', 'trend': '-3% MoM', 'up': False},
]

for i, kpi in enumerate(kpis):
    col = i * 2
    # Background fill
    for r in range(2, 6):
        ws.write_blank(r, col, None, kpi_bg)
        ws.write_blank(r, col + 1, None, kpi_bg)
    ws.merge_range(2, col, 3, col + 1, kpi['value'], kpi_value_fmt)
    ws.merge_range(4, col, 4, col + 1, kpi['label'], kpi_label_fmt)
    trend_fmt = kpi_trend_good if kpi['up'] else kpi_trend_bad
    ws.merge_range(5, col, 5, col + 1, kpi['trend'], trend_fmt)

# Sparklines in row 7 (next to each KPI)
ws.set_row(2, 35)  # KPI value row height
ws.set_row(5, 20)  # Trend row height

# Column widths
for i in range(8):
    ws.set_column(i, i, 12)

wb.close()
```

### Traffic Light Implementation

**Method 1: Icon Set Conditional Formatting**
```python
# openpyxl
ws.conditional_formatting.add('F2:F100',
    IconSetRule('3TrafficLights1', 'num', [0, 70, 90]))

# xlsxwriter
worksheet.conditional_format('F2:F100', {
    'type': 'icon_set',
    'icon_style': '3_traffic_lights',
    'icons': [
        {'criteria': '>=', 'type': 'number', 'value': 90},
        {'criteria': '>=', 'type': 'number', 'value': 70},
        {'criteria': '<',  'type': 'number', 'value': 70}
    ],
    'icons_only': True  # Hide values, show only icons
})
```

**Method 2: Conditional Cell Color**
```python
# xlsxwriter
green = wb.add_format({'bg_color': '#C6EFCE', 'font_color': '#006100', 'align': 'center'})
amber = wb.add_format({'bg_color': '#FFEB9C', 'font_color': '#9C6500', 'align': 'center'})
red = wb.add_format({'bg_color': '#FFC7CE', 'font_color': '#9C0006', 'align': 'center'})

worksheet.conditional_format('F2:F100', {'type': 'cell', 'criteria': '>=', 'value': 90, 'format': green})
worksheet.conditional_format('F2:F100', {'type': 'cell', 'criteria': 'between', 'minimum': 70, 'maximum': 89, 'format': amber})
worksheet.conditional_format('F2:F100', {'type': 'cell', 'criteria': '<', 'value': 70, 'format': red})
```

### Dashboard Design Rules

1. **Turn off gridlines** — `ws.hide_gridlines(2)` (xlsxwriter) or `ws.sheet_view.showGridLines = False` (openpyxl)
2. **Freeze panes** so headers remain visible
3. **Limit to 6-10 KPIs** maximum on one screen
4. **Group related metrics** with background fills
5. **Consistent number formatting** throughout
6. **Use data bars** for visual progress indicators
7. **Add sparklines** (xlsxwriter only) for trend context
8. **Minimize scrolling** — key metrics visible without scrolling
9. **Use a dark header bar** for title/navigation area
10. **Add slicers** connected to Tables or PivotTables for interactivity (manual in Excel)

---

## Data Engineering Patterns

### ETL Pipeline: Read → Transform → Write

```python
import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

# EXTRACT
df = pd.read_excel('raw_data.xlsx', sheet_name='Export')

# TRANSFORM
df['Revenue'] = pd.to_numeric(df['Revenue'], errors='coerce')
df['Date'] = pd.to_datetime(df['Date'])
df = df.dropna(subset=['Revenue'])
df['Quarter'] = df['Date'].dt.to_period('Q').astype(str)
df_summary = df.groupby(['Region', 'Quarter']).agg(
    Total_Revenue=('Revenue', 'sum'),
    Avg_Revenue=('Revenue', 'mean'),
    Order_Count=('Revenue', 'count')
).reset_index()

# LOAD with formatting
with pd.ExcelWriter('report.xlsx', engine='openpyxl') as writer:
    df_summary.to_excel(writer, sheet_name='Summary', index=False)
    df.to_excel(writer, sheet_name='Raw Data', index=False)

    # Format Summary sheet
    ws = writer.sheets['Summary']
    # (apply styling as shown in previous sections)
```

### Large File Streaming (Read)

```python
from openpyxl import load_workbook

# Streaming read — processes one row at a time, low memory
wb = load_workbook('huge_file.xlsx', read_only=True)
ws = wb['Data']

row_count = 0
for row in ws.iter_rows(min_row=2, values_only=True):
    # Process each row without loading entire file
    name, value, date = row[0], row[1], row[2]
    row_count += 1

print(f"Processed {row_count} rows")
wb.close()  # MUST close read-only workbooks
```

### Large File Streaming (Write)

```python
from openpyxl import Workbook

# Write-only mode — rows written to disk immediately, low memory
wb = Workbook(write_only=True)
ws = wb.create_sheet('Data')

# Write headers
ws.append(['ID', 'Name', 'Revenue', 'Date'])

# Write 1M rows without holding them in memory
for i in range(1_000_000):
    ws.append([i, f'Item_{i}', i * 10.5, '2026-02-18'])

wb.save('large_output.xlsx')
```

### Streaming Copy/Transform

```python
from openpyxl import load_workbook, Workbook

# Read one file, transform, write to another — fully streaming
src = load_workbook('input.xlsx', read_only=True)
out = Workbook(write_only=True)

for name in src.sheetnames:
    ws_in = src[name]
    ws_out = out.create_sheet(title=name)
    for row in ws_in.iter_rows(values_only=False):
        # Transform: multiply column 3 by 1.1
        values = []
        for i, cell in enumerate(row):
            v = cell.value
            if i == 2 and isinstance(v, (int, float)):
                v = v * 1.1
            values.append(v)
        ws_out.append(values)

out.save('transformed.xlsx')
src.close()
```

### Multi-Source Consolidation

```python
import pandas as pd
import glob

# Consolidate multiple Excel files into one
files = glob.glob('data/*.xlsx')
frames = []

for f in files:
    df = pd.read_excel(f, sheet_name='Data')
    df['Source_File'] = os.path.basename(f)
    frames.append(df)

consolidated = pd.concat(frames, ignore_index=True)

# Export with formatting
with pd.ExcelWriter('consolidated.xlsx', engine='xlsxwriter') as writer:
    consolidated.to_excel(writer, sheet_name='All Data', index=False)
    # Add summary pivot
    summary = consolidated.pivot_table(
        index='Region', columns='Quarter',
        values='Revenue', aggfunc='sum', fill_value=0
    )
    summary.to_excel(writer, sheet_name='Summary')
```

### CSV to Formatted Excel

```python
import pandas as pd

df = pd.read_csv('data.csv')

with pd.ExcelWriter('formatted.xlsx', engine='xlsxwriter') as writer:
    df.to_excel(writer, sheet_name='Data', index=False, startrow=1)

    wb = writer.book
    ws = writer.sheets['Data']

    # Title
    title_fmt = wb.add_format({'bold': True, 'font_size': 16, 'font_color': '#1E2761'})
    ws.merge_range('A1:E1', 'Data Export', title_fmt)

    # Format headers
    header_fmt = wb.add_format({
        'bold': True, 'bg_color': '#44546A', 'font_color': '#FFFFFF',
        'border': 1, 'align': 'center', 'text_wrap': True
    })
    for col, header in enumerate(df.columns):
        ws.write(1, col, header, header_fmt)

    # Auto-fit columns
    for i, col in enumerate(df.columns):
        max_len = max(df[col].astype(str).map(len).max(), len(col)) + 2
        ws.set_column(i, i, min(max_len * 1.1, 50))

    # Freeze header
    ws.freeze_panes(2, 0)

    # Add table
    ws.add_table(1, 0, len(df) + 1, len(df.columns) - 1, {
        'name': 'DataTable',
        'style': 'Table Style Medium 9',
        'columns': [{'header': col} for col in df.columns]
    })
```

---

## Professional Report Template

Complete pattern for building a consultant-grade Excel report.

```python
import xlsxwriter
import datetime

def create_professional_report(filename, data, title, author=""):
    """Create a formatted multi-sheet Excel report."""
    wb = xlsxwriter.Workbook(filename)

    # ── Define formats ──────────────────────────────────────
    fmts = {}

    # Title / cover
    fmts['title'] = wb.add_format({
        'bold': True, 'font_size': 24, 'font_color': '#1E2761',
        'font_name': 'Calibri Light', 'bottom': 3, 'bottom_color': '#4472C4'
    })
    fmts['subtitle'] = wb.add_format({
        'font_size': 14, 'font_color': '#605E5C', 'font_name': 'Calibri'
    })
    fmts['meta'] = wb.add_format({
        'font_size': 10, 'font_color': '#A5A5A5', 'italic': True
    })

    # Section header
    fmts['section'] = wb.add_format({
        'bold': True, 'font_size': 14, 'font_color': '#1E2761',
        'bottom': 2, 'bottom_color': '#4472C4'
    })

    # Table header
    fmts['header'] = wb.add_format({
        'bold': True, 'font_name': 'Calibri', 'font_size': 11,
        'font_color': '#FFFFFF', 'bg_color': '#44546A',
        'border': 1, 'border_color': '#44546A',
        'align': 'center', 'valign': 'vcenter', 'text_wrap': True
    })

    # Data cells
    fmts['text'] = wb.add_format({
        'font_name': 'Calibri', 'font_size': 10,
        'border': 1, 'border_color': '#E2E8F0'
    })
    fmts['number'] = wb.add_format({
        'font_name': 'Calibri', 'font_size': 10,
        'num_format': '#,##0', 'align': 'right',
        'border': 1, 'border_color': '#E2E8F0'
    })
    fmts['currency'] = wb.add_format({
        'font_name': 'Calibri', 'font_size': 10,
        'num_format': '$#,##0.00', 'align': 'right',
        'border': 1, 'border_color': '#E2E8F0'
    })
    fmts['pct'] = wb.add_format({
        'font_name': 'Calibri', 'font_size': 10,
        'num_format': '0.0%', 'align': 'right',
        'border': 1, 'border_color': '#E2E8F0'
    })
    fmts['date'] = wb.add_format({
        'font_name': 'Calibri', 'font_size': 10,
        'num_format': 'yyyy-mm-dd', 'align': 'center',
        'border': 1, 'border_color': '#E2E8F0'
    })

    # Alternating row
    fmts['alt_text'] = wb.add_format({
        'font_name': 'Calibri', 'font_size': 10,
        'bg_color': '#F2F2F2',
        'border': 1, 'border_color': '#E2E8F0'
    })
    fmts['alt_number'] = wb.add_format({
        'font_name': 'Calibri', 'font_size': 10,
        'num_format': '#,##0', 'align': 'right',
        'bg_color': '#F2F2F2',
        'border': 1, 'border_color': '#E2E8F0'
    })
    fmts['alt_currency'] = wb.add_format({
        'font_name': 'Calibri', 'font_size': 10,
        'num_format': '$#,##0.00', 'align': 'right',
        'bg_color': '#F2F2F2',
        'border': 1, 'border_color': '#E2E8F0'
    })
    fmts['alt_pct'] = wb.add_format({
        'font_name': 'Calibri', 'font_size': 10,
        'num_format': '0.0%', 'align': 'right',
        'bg_color': '#F2F2F2',
        'border': 1, 'border_color': '#E2E8F0'
    })

    # Total row
    fmts['total_label'] = wb.add_format({
        'bold': True, 'font_name': 'Calibri', 'font_size': 10,
        'top': 5, 'bottom': 6, 'top_color': '#000000', 'bottom_color': '#000000'
    })
    fmts['total_number'] = wb.add_format({
        'bold': True, 'font_name': 'Calibri', 'font_size': 10,
        'num_format': '#,##0', 'align': 'right',
        'top': 5, 'bottom': 6, 'top_color': '#000000', 'bottom_color': '#000000'
    })
    fmts['total_currency'] = wb.add_format({
        'bold': True, 'font_name': 'Calibri', 'font_size': 10,
        'num_format': '$#,##0.00', 'align': 'right',
        'top': 5, 'bottom': 6, 'top_color': '#000000', 'bottom_color': '#000000'
    })

    # Conditional format styles
    fmts['good'] = wb.add_format({'bg_color': '#C6EFCE', 'font_color': '#006100'})
    fmts['bad'] = wb.add_format({'bg_color': '#FFC7CE', 'font_color': '#9C0006'})
    fmts['neutral'] = wb.add_format({'bg_color': '#FFEB9C', 'font_color': '#9C6500'})

    # ── Cover sheet ─────────────────────────────────────────
    cover = wb.add_worksheet('Cover')
    cover.hide_gridlines(2)
    cover.set_column('A:A', 5)
    cover.set_column('B:B', 80)

    cover.write('B3', title, fmts['title'])
    cover.write('B5', f'Prepared by: {author}', fmts['subtitle'])
    cover.write('B6', f'Date: {datetime.date.today().strftime("%B %d, %Y")}', fmts['subtitle'])
    cover.write('B8', 'CONFIDENTIAL', fmts['meta'])

    # ── Data sheets (add your data here) ────────────────────
    # ... use fmts dict to style each sheet consistently ...

    wb.close()
    return filename
```

---

## Performance Optimization

### openpyxl Performance Tips

| Technique | Impact | When |
|-----------|--------|------|
| `read_only=True` | 90% memory reduction | Reading large files |
| `write_only=True` | 90% memory reduction | Writing large files |
| `data_only=True` | Faster read | When you need values, not formulas |
| Avoid per-cell styling in loops | 10-50x faster | Styling large ranges |
| Use `ws.append()` instead of cell-by-cell | 3-5x faster | Writing bulk data |
| Use `NamedStyle` instead of inline styles | 2-3x faster | Repeated styles |
| Close workbooks after use | Prevents memory leaks | Always |

### xlsxwriter Performance Tips

| Technique | Impact | When |
|-----------|--------|------|
| `constant_memory=True` | Fixed memory usage | Writing very large files |
| Avoid per-row formatting | Faster | Use `set_column()` for column-level formats |
| Write data in order (top to bottom) | Required in constant_memory mode | Always preferred |

```python
# Constant memory mode for huge files
wb = xlsxwriter.Workbook('huge.xlsx', {'constant_memory': True})
ws = wb.add_worksheet()

for row in range(1_000_000):
    ws.write_row(row, 0, [row, f'Item_{row}', row * 10.5])

wb.close()
```

### pandas Performance Tips

```python
# Faster Excel reading with specific columns and dtypes
df = pd.read_excel('large.xlsx',
    usecols=['A', 'B', 'C'],       # Only read needed columns
    dtype={'ID': 'int32', 'Name': 'category'},  # Efficient types
    engine='openpyxl'
)

# For very large files, consider converting to CSV first
# CSV reads are 5-10x faster than Excel reads
```

### File Size Optimization

- Avoid styling empty cells (each styled cell adds to file size)
- Use `NamedStyle` in openpyxl — shared styles reference once, reducing file size
- Compress images before inserting (150 DPI for screen, 300 DPI for print)
- Remove unused sheets
- Limit conditional formatting ranges to actual data ranges

---

## Accessibility

### WCAG Color Contrast

| Background | Text | Ratio | Level |
|------------|------|-------|-------|
| `#FFFFFF` (white) | `#000000` (black) | 21:1 | AAA |
| `#4472C4` (blue) | `#FFFFFF` (white) | 4.6:1 | AA |
| `#44546A` (dark gray) | `#FFFFFF` (white) | 7.2:1 | AAA |
| `#D6DCE4` (light gray) | `#000000` (black) | 12.1:1 | AAA |
| `#C6EFCE` (light green) | `#006100` (dark green) | 5.8:1 | AA |
| `#FFC7CE` (light red) | `#9C0006` (dark red) | 5.3:1 | AA |
| `#FFEB9C` (light yellow) | `#9C6500` (dark gold) | 4.5:1 | AA |

### Colorblind-Safe Palettes

Instead of red/green (affects ~8% of males):
- **Blue/Orange:** `#4472C4` / `#ED7D31`
- **Blue/Red:** `#4472C4` / `#C00000`
- **Purple/Orange:** `#7030A0` / `#ED7D31`
- For icon sets, prefer **arrows** (direction conveys meaning) over circle colors

### Best Practices

1. **Always use Format as Table** (Ctrl+T) — creates semantic structure for screen readers
2. **Name tables descriptively** — `SalesData` not `Table1`
3. **Name worksheets descriptively** — `Q1 Revenue` not `Sheet1`
4. **Add alt text** to charts and images
5. **Avoid merged cells** — breaks screen reader navigation
6. **Don't use color alone** for meaning — add text/icons alongside
7. **Logical reading order** — data flows left-to-right, top-to-bottom
8. **Remove blank sheets** from the workbook
9. **Use cell styles** (Heading 1, Input, Calculation, Total) for semantics
10. **Run accessibility checker** — Review > Check Accessibility

---

## Common Design Mistakes

| Mistake | Fix |
|---------|-----|
| Gridlines visible on reports | Turn off: View > uncheck Gridlines |
| Merged cells everywhere | Use "Center Across Selection" or avoid |
| All borders on every cell | Use fill colors + strategic borders only |
| Comic Sans or decorative fonts | Use Calibri, Arial, or Segoe UI |
| More than 4 colors | Stick to 60-30-10 palette |
| Inconsistent number formats | Standardize per column |
| Blank rows/columns as spacers | Use cell padding, borders, or fills |
| Using color alone for meaning | Add text labels or icons alongside |
| Hard-coded numbers in formulas | Put inputs in labeled cells, reference them |
| Default chart formatting | Customize title, colors, labels, remove chart junk |
| Overuse of conditional formatting | Apply sparingly to highlight exceptions |
| Not using Excel Tables | Ctrl+T for auto-expansion, banding, structured refs |
| Minus signs for negative values (financial) | Use parentheses: `#,##0_);(#,##0)` |
| No source/date on reports | Add source line + date in footer |

---

## Dependencies

```bash
pip install openpyxl           # Read/write/modify .xlsx
pip install xlsxwriter         # Write-only, rich formatting
pip install pandas             # Data analysis + Excel I/O
pip install "markitdown[xlsx]" # Text extraction from Excel (optional)
```

---

## Gotchas & Troubleshooting

### 1. openpyxl Cannot Do Rich Text in Cells

openpyxl cannot apply different formatting to different parts of text within a single cell (e.g., bold + red on part of the value). Use xlsxwriter's `write_rich_string()` instead.

### 2. xlsxwriter Cannot Read or Modify Files

xlsxwriter is write-only. To modify an existing file, use openpyxl. There is no workaround.

### 3. openpyxl Auto-Fit Column Width Doesn't Exist

openpyxl has no built-in auto-fit. The `auto_size=True` / `bestFit=True` property does not work reliably (sometimes hides columns). Use the manual calculation pattern:

```python
for column_cells in ws.columns:
    max_length = 0
    col_letter = get_column_letter(column_cells[0].column)
    for cell in column_cells:
        if cell.value:
            max_length = max(max_length, len(str(cell.value)))
    ws.column_dimensions[col_letter].width = (max_length + 2) * 1.15
```

### 4. openpyxl Header/Footer Images Not Supported

openpyxl cannot insert images into headers/footers. xlsxwriter can:
```python
worksheet.set_header('&L&[Picture]', None, {'image_left': 'logo.png'})
```

### 5. Number Stored as Text (Green Triangle)

Excel shows a green triangle when a number is stored as text. In openpyxl, ensure you write actual numbers, not strings:

```python
# WRONG — stores as text
ws['A1'] = '1234'

# CORRECT — stores as number
ws['A1'] = 1234
ws['A1'] = float('1234.56')
```

### 6. Datetime Timezone Issues

openpyxl strips timezone info from datetime objects. Always use timezone-naive datetimes:

```python
import datetime
# WRONG — may cause issues
ws['A1'] = datetime.datetime.now(datetime.timezone.utc)

# CORRECT
ws['A1'] = datetime.datetime.now()
```

### 7. xlsxwriter Object Reuse Across Workbooks

Don't reuse `Workbook` objects. Create a fresh instance for each file:

```python
# WRONG
wb = xlsxwriter.Workbook('file1.xlsx')
# ... work ...
wb.close()
wb.save('file2.xlsx')  # ERROR

# CORRECT
wb1 = xlsxwriter.Workbook('file1.xlsx')
# ... work ...
wb1.close()
wb2 = xlsxwriter.Workbook('file2.xlsx')
# ... work ...
wb2.close()
```

### 8. Read-Only Mode: Must Close Workbook

```python
wb = load_workbook('file.xlsx', read_only=True)
# ... process ...
wb.close()  # MANDATORY — file handle stays open without this
```

### 9. Write-Only Mode: No Cell Access After Write

In write-only mode, you cannot go back and modify previously written rows. Data must be written in order, top to bottom.

### 10. Conditional Formatting Rule Precedence

Rules added first take priority. If two rules conflict, the earlier one wins. Add the most specific rules first.

### 11. openpyxl Doesn't Create Sparklines

openpyxl has no sparkline support. Use xlsxwriter for sparklines, or create mini-charts manually.

### 12. pandas ExcelWriter Engine Conflicts

```python
# WRONG — openpyxl engine doesn't support xlsxwriter features
with pd.ExcelWriter('file.xlsx', engine='openpyxl') as writer:
    wb = writer.book
    wb.add_format({...})  # AttributeError — this is xlsxwriter API

# CORRECT — match the engine
with pd.ExcelWriter('file.xlsx', engine='xlsxwriter') as writer:
    wb = writer.book
    fmt = wb.add_format({...})  # xlsxwriter API
```

### 13. Excel 65,536 Row Limit (.xls) vs. 1,048,576 (.xlsx)

The .xlsx format supports up to 1,048,576 rows and 16,384 columns. The old .xls format is limited to 65,536 rows and 256 columns. Always use .xlsx.

### 14. openpyxl formatInformation / Styles Conflict

When loading and re-saving files with complex styles, openpyxl may duplicate or corrupt style definitions. To minimize issues:
```python
wb = load_workbook('file.xlsx')
# Modify only what you need
# Don't create unnecessary new styles
wb.save('file.xlsx')
```

### Troubleshooting Quick Reference

| Symptom | Cause | Fix |
|---------|-------|-----|
| File won't open after save | Unclosed Workbook or corrupted styles | Ensure `wb.close()` or use `with` context |
| Green triangle on numbers | Number stored as text string | Write actual numbers, not strings |
| Column shows `###` | Column too narrow for content | Widen column or use auto-fit pattern |
| Conditional formatting not showing | Rules added in wrong order | Most specific rules first |
| read_only mode: dimension wrong | Source app wrote incorrect dimensions | Set `ws.max_row` and `ws.max_column` manually |
| Formula shows as text | String starts with `=` in quotes | Write formula without quotes: `ws['A1'] = '=SUM(B:B)'` |
| Styles lost after pandas write | Pandas overwrites entire sheet | Use `if_sheet_exists='overlay'` with openpyxl engine |
| Memory error on large file | Loading entire file into memory | Use `read_only=True` or `write_only=True` |
| xlsxwriter sparkline not showing | Wrong range format | Use sheet reference: `'Sheet1!B2:F2'` |
| VBA macro not running | File saved as .xlsx not .xlsm | Use `.xlsm` extension |
| Image not positioned correctly | Using cell reference instead of string | Use `'D2'` string, not `ws['D2']` object |
| Header/footer image missing | openpyxl doesn't support this | Use xlsxwriter instead |
