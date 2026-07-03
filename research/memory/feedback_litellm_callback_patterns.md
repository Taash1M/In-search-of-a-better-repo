---
name: feedback-litellm-callback-patterns
description: "LiteLLM custom callback gotchas — v1.30+ required for CustomLogger, call_type is \"acompletion\" not \"completion\", YAML inline list, in-place mutation, non-Claude model awareness"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 9055eea3-6ef7-4501-b1af-5635c15c4b21
---

LiteLLM proxy `async_pre_call_hook` uses `call_type="acompletion"` (async), NOT `"completion"` (sync). Always accept both: `if call_type not in ("completion", "acompletion"): return`.

**Why:** LiteLLM proxy internally uses async completions for all requests. The sync `"completion"` value is only used in direct library calls, not proxy mode. This is undocumented and caused a silent skip of all requests in the enterprise prompt injector.

**How to apply:**
- Requires LiteLLM v1.30+ — the `from litellm.integrations.custom_logger import CustomLogger` import path changed around that version. Older versions use a different callback interface.
- Any `async_pre_call_hook` filtering on `call_type` must accept both variants
- YAML `callbacks:` must use inline list `[a, b, c]` — multi-line dash format silently fails to load custom module callbacks
- Use in-place `messages.insert(0, msg)` instead of `data["messages"] = [new] + old` — more robust against LiteLLM's reference handling
- Pre-call hooks fire on ALL model requests (Claude, GPT, Gemini, etc.) — add a model name check if you need Claude-only behavior. XML-tagged prompts are optimized for Claude but harmless on other models.
- Debug with `print(..., file=sys.stderr, flush=True)` — stderr IS captured in App Service `default_docker.log`
- Add `PROMPT_VERSION` constant + first-injection INFO log for audit trail
- Related: [[feedback-litellm-no-connected-db]], [[project-prompt-injector-pack]]
