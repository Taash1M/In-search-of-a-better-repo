---
name: Git push SSL fix for corporate proxy
description: git push fails with OpenSSL on large payloads through Fluke corporate proxy — use schannel SSL backend and bundle workflow
type: feedback
originSessionId: aa210407-a09e-461f-aa2f-83d0e2fa4475
---
Git push to GitHub fails with `ssl/tls alert bad record mac` when pushing large payloads (>50MB) from OneDrive-synced clones through Fluke corporate proxy.

**Why:** The default OpenSSL SSL backend in Git for Windows doesn't handle large RPC payloads through the Fluke corporate HTTPS inspection proxy. The Windows-native SChannel backend works because it uses the Windows certificate store and TLS stack.

**How to apply:**
1. Always set `git config http.sslBackend schannel` on any clone that needs to push
2. For large pushes from OneDrive paths, use the bundle workflow: commit in OneDrive clone → `git bundle create` → pull into local clone at `<USER_HOME>/In-search-of-a-better-repo` → push from local clone
3. Use `push_to_github.py` which automates this entire workflow
4. Setting `http.postBuffer 524288000` alone does NOT fix the issue — the SSL backend must be changed
