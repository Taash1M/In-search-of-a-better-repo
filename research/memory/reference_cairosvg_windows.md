---
name: cairosvg-windows-setup
description: How to make cairosvg work on Windows 64-bit — requires MSYS2 64-bit cairo DLLs in PATH before import
metadata: 
  node_type: memory
  type: reference
  originSessionId: 08c5d4d2-4f9c-4e86-9f3a-c03eb1f00dad
---

## cairosvg on Windows (64-bit Python 3.12)

cairosvg depends on cairocffi which uses ctypes to load `libcairo-2.dll`. pycairo bundles cairo as a `.pyd` extension, NOT as a standalone DLL — cairocffi cannot use it.

**Why:** Needed for converting Azure SVG icons to PNG for embedding in matplotlib architecture diagrams and DOCX/PPTX documents.

**How to apply:** Every script that imports cairosvg must preload the DLL via `ctypes.CDLL()` BEFORE import. `os.add_dll_directory()` alone is NOT sufficient — cairocffi uses cffi's dlopen which has its own search path that ignores `add_dll_directory`.

```python
import os, ctypes
# MUST preload the DLL directly — add_dll_directory alone won't work for cairocffi
ctypes.CDLL(os.path.join(r'<USER_HOME>/tools\cairo-dlls', 'libcairo-2.dll'))
import cairosvg  # NOW this works
```

### DLL Locations (two copies exist)
- `<USER_HOME>/tools\cairo-dlls\` — primary (38 MSYS2 DLLs)
- `<ADMIN_HOME>/cairo_dlls\` — backup copy

### Why ctypes.CDLL is required (not just PATH)
cairocffi uses `cffi.dlopen()` internally, which does NOT respect `os.add_dll_directory()`. It only checks the standard DLL search order (system32, Windows, PATH). Loading via `ctypes.CDLL()` first puts the library in the process's loaded-module table, so cffi finds it on the second attempt. This is the ONLY reliable approach on Windows.

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
