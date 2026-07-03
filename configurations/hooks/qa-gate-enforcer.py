#!/usr/bin/env python3
"""
QA Gate Enforcer Hook (SubagentStop)
------------------------------------
Makes the `qa-gate` sub-agent a HARD, non-skippable terminal gate.

Identity & decision model (hardened after 3-persona review):
  * A qa-gate run is POSITIVELY identified by the sentinel line `QA-GATE-VERDICT-V1`
    emitted by the agent (agents/qa-gate.md). Identity does NOT depend on parsing
    the JSON, so we can tell "a qa-gate ran" apart from "failed to parse a verdict."
  * If the sentinel is ABSENT  -> not a qa-gate run -> ALLOW (exit 0). This is what
    keeps the global hook from wedging unrelated sub-agents.
  * If the sentinel is PRESENT:
       - parse the verdict JSON;
       - verdict == PASS (zero blocker/major)            -> ALLOW (exit 0);
       - verdict == FAIL, OR no parseable PASS verdict    -> BLOCK (exit 2).
    i.e. a qa-gate run that ran but whose verdict we cannot read as PASS is treated
    as FAIL (fail-CLOSED) — matching the agent's "default to FAIL when unsure."
  * Honors `stop_hook_active` to avoid stop-hook re-entrancy loops.
  * Read-only except for appending one NDJSON line to a durable gate-ledger (audit).

SubagentStop payload (https://code.claude.com/docs/en/hooks.md): session_id,
transcript_path, stop_hook_active. Agent name is not guaranteed -> sentinel-based ID.

Exit codes: 0 = allow; 2 = block (stderr shown to the model as the reason).
"""

import json
import os
import re
import sys
from datetime import datetime

SENTINEL = "QA-GATE-VERDICT-V1"
LEDGER = os.path.join(os.path.expanduser("~"), ".claude", "qa_gate_ledger.ndjson")


def _iter_texts(transcript_path):
    """Yield text content from EVERY transcript record (not role-gated).

    We do NOT gate on role: a real qa-gate verdict must be found wherever the
    harness writes it (DE round-2 P1-1). We only read `type=="text"` blocks (or
    string content), so a sentinel echoed inside a tool_use command string is NOT
    treated as gate output.
    """
    if not transcript_path or not os.path.exists(transcript_path):
        return
    try:
        with open(transcript_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except json.JSONDecodeError:
                    continue
                msg = rec.get("message", rec)
                if not isinstance(msg, dict):
                    continue
                content = msg.get("content", "")
                if isinstance(content, str):
                    yield content
                elif isinstance(content, list):
                    parts = [b.get("text", "") for b in content
                             if isinstance(b, dict) and b.get("type") == "text"]
                    if parts:
                        yield "\n".join(parts)
    except Exception:
        return


def _balanced_objects(text):
    """Yield top-level {...} substrings with balanced braces (handles nesting).

    String-aware: braces inside JSON string literals are ignored (DE P3), so a
    finding like {"required_fix": "use {x}"} does not mis-balance.
    """
    depth = 0
    start = -1
    in_str = False
    esc = False
    for i, ch in enumerate(text):
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
            continue
        if ch == '"':
            in_str = True
        elif ch == "{":
            if depth == 0:
                start = i
            depth += 1
        elif ch == "}":
            if depth > 0:
                depth -= 1
                if depth == 0 and start != -1:
                    yield text[start:i + 1]
                    start = -1


def _collect_verdicts(text):
    """Yield every qa-gate verdict dict in a text.

    Identity is the PARSED object carrying `gate == "qa-gate"` (not a bare string
    match), so a quoted/echoed contract example without that marker is ignored.
    Robust to fenced/unfenced, nested findings, and trailing content via the
    balanced-brace scanner.
    """
    if not text:
        return
    for blob in _balanced_objects(text):
        if '"verdict"' not in blob:
            continue
        try:
            obj = json.loads(blob)
        except json.JSONDecodeError:
            continue
        if isinstance(obj, dict) and obj.get("gate") == "qa-gate" and "verdict" in obj:
            yield obj


def _blockers(verdict_obj):
    findings = verdict_obj.get("findings", []) if isinstance(verdict_obj, dict) else []
    if not isinstance(findings, list):   # malformed findings (str/int/etc.) -> treat as none (DE P1)
        findings = []
    return [f for f in findings if isinstance(f, dict)
            and str(f.get("severity", "")).lower() in ("blocker", "major")]


def _is_pass(verdict_obj):
    """A verdict is PASS only if it says PASS AND carries no blocker/major finding
    (re-enforce the accept rule — DE round-2 P2-2; tolerate whitespace/case)."""
    v = str(verdict_obj.get("verdict", "")).strip().upper()
    return v == "PASS" and not _blockers(verdict_obj)


def _append_ledger(row):
    try:
        os.makedirs(os.path.dirname(LEDGER), exist_ok=True)
        with open(LEDGER, "a", encoding="utf-8") as f:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    except Exception:
        pass  # auditing must never block the gate decision


def _record(session_id, verdict_obj, decision, reason=""):
    blockers = _blockers(verdict_obj) if isinstance(verdict_obj, dict) else []
    _append_ledger({
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "session_id": session_id,
        "artifact": (verdict_obj or {}).get("artifact", ""),
        "artifact_type": (verdict_obj or {}).get("artifact_type", ""),
        "verdict": (verdict_obj or {}).get("verdict", "UNPARSEABLE"),
        "decision": decision,            # "allow" | "block"
        "blocker_major_count": len(blockers),
        "reason": reason,
    })
    return blockers


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        sys.exit(0)

    # Avoid stop-hook re-entrancy loops.
    if data.get("stop_hook_active"):
        sys.exit(0)

    session_id = data.get("session_id", "")
    transcript_path = data.get("transcript_path", "")

    # Deliberate fail-open if the transcript can't be read: identity cannot be
    # established, and blocking on unestablishable identity would wedge every
    # sub-agent. A qa-gate run whose transcript is unreadable is therefore allowed
    # (inherent limitation; logged for audit).
    texts = list(_iter_texts(transcript_path))
    if not texts and not os.path.exists(transcript_path or ""):
        _append_ledger({"timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "session_id": session_id, "decision": "allow",
                        "reason": "no/unreadable transcript", "verdict": "N/A"})
        sys.exit(0)
    raw = "\n".join(texts)

    # Collect every parsed qa-gate verdict (identity = gate=="qa-gate" in the object).
    verdicts = []
    for t in texts:
        verdicts.extend(_collect_verdicts(t))

    # Positive identity (two independent signals):
    #   1) a PARSED verdict object carrying gate=="qa-gate"; or
    #   2) the sentinel on its OWN line PAIRED WITH a brace-object that mentions
    #      "qa-gate" (even if it won't JSON-parse). A lone documented sentinel line
    #      with no gate object is NOT a gate run, so an agent merely *explaining*
    #      the contract isn't wedged (DE round-3 P2); a real run with a malformed
    #      verdict still fail-closes (it has the qa-gate brace object).
    sentinel_on_own_line = any(ln.strip() == SENTINEL for ln in raw.splitlines())
    has_gate_object = any("qa-gate" in blob for blob in _balanced_objects(raw))
    is_gate_run = bool(verdicts) or (sentinel_on_own_line and has_gate_object)
    if not is_gate_run:
        sys.exit(0)  # not a qa-gate run -> allow (never wedge other sub-agents)

    # It IS a qa-gate run. Any surprise in the decision below fails CLOSED (block),
    # never crash-to-exit-1 (which would be non-blocking = allow) (DE round-3 P1).
    try:
        # Decision is FAIL-DOMINANT (DE round-2 P2-1):
        #   - any non-PASS verdict (or PASS-with-blocker) anywhere -> BLOCK
        #   - PASS only if >=1 verdict and ALL verdicts pass
        #   - gate run but NO parseable verdict -> BLOCK (fail-closed)
        if not verdicts:
            _record(session_id, None, "block", "gate run, verdict unparseable")
            sys.stderr.write(
                "QA GATE: a qa-gate run was detected but no parseable verdict was found. "
                "Treating as FAIL. Re-run the qa-gate and emit the QA-GATE-VERDICT-V1 sentinel "
                "+ a valid ```json verdict block carrying \"gate\":\"qa-gate\".\n")
            sys.exit(2)

        failing = [v for v in verdicts if not _is_pass(v)]
        if not failing:
            _record(session_id, verdicts[-1], "allow", f"PASS ({len(verdicts)} verdict(s), all pass)")
            sys.exit(0)

        worst = failing[-1]
        blockers = _record(session_id, worst, "block",
                           f"FAIL ({len(failing)}/{len(verdicts)} verdict(s) not PASS)")
        artifact = worst.get("artifact", "the artifact")
        lines = [
            f"QA GATE FAILED for {artifact}. This artifact is NOT accepted.",
            "Remediate the blocker/major findings below, then re-run the qa-gate sub-agent until PASS:",
        ]
        for f in blockers[:20]:
            lines.append(f"  - [{f.get('severity')}] {f.get('location','?')}: "
                         f"{f.get('issue','')} -> FIX: {f.get('required_fix','')}")
        if not blockers:
            lines.append("  - (non-PASS verdict with no blocker/major findings listed; re-run for specifics.)")
        sys.stderr.write("\n".join(lines) + "\n")
        sys.exit(2)
    except SystemExit:
        raise
    except Exception as e:
        _record(session_id, None, "block", f"enforcer error on gate run: {e}")
        sys.stderr.write(f"QA GATE: enforcer error on a qa-gate run ({e}); failing CLOSED.\n")
        sys.exit(2)


if __name__ == "__main__":
    main()
