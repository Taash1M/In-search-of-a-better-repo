---
name: cairosvg Windows Setup
description: How to make cairosvg work on Windows 64-bit — requires MSYS2 64-bit cairo DLLs in PATH before import
type: reference
---

## cairosvg on Windows (64-bit Python 3.12)

cairosvg depends on cairocffi which uses ctypes to load `libcairo-2.dll`. pycairo bundles cairo as a `.pyd` extension, NOT as a standalone DLL — cairocffi cannot use it.

**Why:** Needed for converting Azure SVG icons to PNG for embedding in matplotlib architecture diagrams and DOCX/PPTX documents.

**How to apply:** Every script that imports cairosvg must set the DLL path BEFORE import:

```python
import os
os.add_dll_directory(r'C:\Users\tmanyang\tools\cairo-dlls')
os.environ['PATH'] = r'C:\Users\tmanyang\tools\cairo-dlls;' + os.environ.get('PATH', '')
import cairosvg  # NOW this works
```

### DLL Location
`C:\Users\tmanyang\tools\cairo-dlls\` — 38 DLLs from MSYS2 mingw64 packages

### Key DLLs (dependency chain)
libwinpthread-1.dll → libgcc_s_seh-1.dll → libstdc++-6.dll → libpixman-1-0.dll, libfreetype-6.dll, libfontconfig-1.dll, libharfbuzz-0.dll → **libcairo-2.dll**

### Source Packages (MSYS2 mingw64)
- mingw-w64-x86_64-cairo-1.18.4-1
- mingw-w64-x86_64-libwinpthread-14.0.0.r2
- mingw-w64-x86_64-gcc-libs-15.1.0-1
- mingw-w64-x86_64-pixman-0.44.2-1
- mingw-w64-x86_64-freetype-2.13.3-1
- mingw-w64-x86_64-fontconfig-2.16.0-1
- mingw-w64-x86_64-harfbuzz-11.2.1-1
- mingw-w64-x86_64-glib2-2.84.1-1
- + libpng, zlib, expat, pcre2, libffi, gettext-runtime, libiconv, brotli, graphite2, bzip2

### Common Errors
- `OSError: no library called "cairo-2" was found` → DLLs not in PATH
- `error 0xc1` → 32-bit DLL with 64-bit Python (GTK2-Runtime from choco is 32-bit)
- `error 0x7e` → DLL or its dependency not found
- `AttributeError: function/symbol 'cairo_image_surface_create' not found` → loaded pycairo .pyd instead of real libcairo-2.dll

### Installed 2026-04-06
