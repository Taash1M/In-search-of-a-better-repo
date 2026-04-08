#!/usr/bin/env python3
"""
Dangerous Command Blocker Hook
Multi-level security system for blocking dangerous shell commands.
Adapted for Fluke UBI / Azure environment.
"""

import json
import sys
import re

# Load command from stdin
data = json.load(sys.stdin)
cmd = data.get('tool_input', {}).get('command', '')

# === LEVEL 1: CATASTROPHIC COMMANDS (ALWAYS BLOCK) ===
catastrophic_patterns = [
    (r'\brm\s+.*\s+/\s*$', 'rm on root directory'),
    (r'\brm\s+.*\s+~\s*$', 'rm on home directory'),
    (r'\brm\s+.*\s+\*\s*$', 'rm with star wildcard'),
    (r'\brm\s+-[rfRF]*[rfRF]+.*\*', 'rm -rf with wildcards'),
    (r'\b(dd\s+if=|dd\s+of=/dev)', 'dd disk operations'),
    (r'\b(mkfs\.|mkswap\s|fdisk\s)', 'filesystem formatting'),
    (r'\b:(\(\))?\s*\{\s*:\s*\|\s*:\s*&\s*\}', 'fork bomb'),
    (r'>\s*/dev/sd[a-z]', 'direct disk write'),
    (r'\bchmod\s+(-R\s+)?777\s+/', 'chmod 777 on root'),
    (r'\bchown\s+(-R\s+)?.*\s+/$', 'chown on root directory'),
]

for pattern, desc in catastrophic_patterns:
    if re.search(pattern, cmd, re.IGNORECASE):
        print(f'BLOCKED: Catastrophic command detected!', file=sys.stderr)
        print(f'', file=sys.stderr)
        print(f'Reason: {desc}', file=sys.stderr)
        print(f'Command: {cmd[:100]}', file=sys.stderr)
        print(f'', file=sys.stderr)
        print(f'This command could cause IRREVERSIBLE system damage or data loss.', file=sys.stderr)
        print(f'', file=sys.stderr)
        print(f'Safety tips:', file=sys.stderr)
        print(f'  - Never use rm -rf with /, ~, or * wildcards', file=sys.stderr)
        print(f'  - Use specific file paths instead of wildcards', file=sys.stderr)
        print(f'  - For cleanup, target specific directories', file=sys.stderr)
        sys.exit(2)

# === LEVEL 2: CRITICAL PATH PROTECTION ===
critical_paths = [
    (r'\b(rm|mv)\s+(-[rfRF]+\s+)?\.claude(/|$|\s)', 'Claude Code configuration'),
    (r'\b(rm|mv)\s+(-[rfRF]+\s+)?\.git(/|$|\s)', 'Git repository'),
    (r'\b(rm|mv)\s+(-[rfRF]+\s+)?node_modules(/|$|\s)', 'Node.js dependencies'),
    (r'\b(rm|mv)\s+(-[rfRF]+\s+)?[^\s]*\.env\b', 'Environment variables'),
    (r'\b(rm|mv)\s+(-[rfRF]+\s+)?[^\s]*package\.json\b', 'Package manifest'),
    (r'\b(rm|mv)\s+(-[rfRF]+\s+)?[^\s]*package-lock\.json\b', 'Lock file'),
    (r'\b(rm|mv)\s+(-[rfRF]+\s+)?[^\s]*requirements\.txt\b', 'Python dependencies'),
    # Databricks/ADF specific protections
    (r'\b(rm|mv)\s+(-[rfRF]+\s+)?.*AzureDataBricks(/|\\)', 'Databricks repository'),
    (r'\b(rm|mv)\s+(-[rfRF]+\s+)?.*ADF(/|\\)', 'ADF repository'),
    (r'\b(rm|mv)\s+(-[rfRF]+\s+)?[^\s]*settings\.json\b', 'Settings file'),
]

for pattern, desc in critical_paths:
    if re.search(pattern, cmd, re.IGNORECASE):
        print(f'BLOCKED: Critical path protection activated!', file=sys.stderr)
        print(f'', file=sys.stderr)
        print(f'Protected resource: {desc}', file=sys.stderr)
        print(f'Command: {cmd[:100]}', file=sys.stderr)
        print(f'', file=sys.stderr)
        print(f'This path contains critical project files.', file=sys.stderr)
        print(f'', file=sys.stderr)
        print(f'If you really need to do this:', file=sys.stderr)
        print(f'  1. Execute the command manually in your terminal', file=sys.stderr)
        print(f'  2. Or modify specific files instead of using rm/mv on directories', file=sys.stderr)
        sys.exit(2)

# === LEVEL 3: SUSPICIOUS PATTERNS (WARNING ONLY) ===
suspicious_patterns = [
    (r'\brm\s+.*\s+&&', 'chained rm commands'),
    (r'\brm\s+[^\s/]*\*', 'rm with wildcards'),
    (r'\bfind\s+.*-delete', 'find -delete operation'),
    (r'\bxargs\s+.*\brm', 'xargs with rm'),
]

for pattern, desc in suspicious_patterns:
    if re.search(pattern, cmd, re.IGNORECASE):
        print(f'WARNING: Suspicious command pattern detected!', file=sys.stderr)
        print(f'', file=sys.stderr)
        print(f'Pattern: {desc}', file=sys.stderr)
        print(f'Command: {cmd[:100]}', file=sys.stderr)
        print(f'', file=sys.stderr)
        print(f'Review carefully before execution.', file=sys.stderr)
        # Exit 0 to allow but with warning
        sys.exit(0)

# Command is safe
sys.exit(0)
