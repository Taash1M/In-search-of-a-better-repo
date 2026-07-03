---
name: dll-discovery-windows
description: Python 3.8+ DLL search change — ctypes.CDLL preload required for cffi-based packages; sitecustomize.py is the permanent fix
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 08c5d4d2-4f9c-4e86-9f3a-c03eb1f00dad
---

Python 3.8+ removed PATH from DLL search on Windows (security). cffi's `ffi.dlopen()` also ignores `os.add_dll_directory()`. The ONLY reliable fix is `ctypes.CDLL(full_path)` preloading.

**Why:** Wasted 30+ minutes debugging cairosvg "no library called cairo-2 was found" when the DLLs existed at two locations on disk. The GTK2-Runtime from Chocolatey was also useless (32-bit stub with zero DLLs).

**How to apply:**
- `sitecustomize.py` at `<USER_HOME>/Python312\Lib\` auto-preloads all DLLs from known directories on every Python start — eliminates manual workarounds in scripts
- When adding new native-dep packages, add their DLL directory to `_KNOWN_DLL_DIRS` in sitecustomize.py
- Run `python <USER_HOME>/tools/inventory.py` to audit what's installed and test native deps
- DLLs live at `<USER_HOME>/tools\cairo-dlls\` (38 MSYS2 mingw64 DLLs)
- See [[cairosvg-windows-setup]] for full details
