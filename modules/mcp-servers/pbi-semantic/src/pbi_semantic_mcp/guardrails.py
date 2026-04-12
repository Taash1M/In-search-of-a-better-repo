"""DAX query guardrails — validation, row limits, audit logging, rate limiting."""

from __future__ import annotations

import json
import logging
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import sqlparse

logger = logging.getLogger(__name__)

# ── Blocked DAX keywords (mutating operations) ───────────────────────
BLOCKED_KEYWORDS = re.compile(
    r"\b(CREATE|ALTER|DROP|DELETE|INSERT|UPDATE|TRUNCATE|MERGE|GRANT|REVOKE|EXEC|EXECUTE)\b",
    re.IGNORECASE,
)

# Match existing TOPN to check if user already limited rows
TOPN_PATTERN = re.compile(r"\bTOPN\s*\(", re.IGNORECASE)


class DAXValidationError(Exception):
    """Raised when a DAX query fails validation."""


def validate_dax(query: str) -> str:
    """Validate a DAX query is read-only and safe to execute.

    Args:
        query: Raw DAX query string.

    Returns:
        Cleaned query string.

    Raises:
        DAXValidationError: If the query contains blocked operations.
    """
    cleaned = query.strip()

    if not cleaned:
        raise DAXValidationError("Empty query")

    # Check for blocked keywords
    match = BLOCKED_KEYWORDS.search(cleaned)
    if match:
        raise DAXValidationError(
            f"Blocked operation: '{match.group()}' — only read-only DAX queries are allowed"
        )

    # Parse with sqlparse for additional structural validation
    try:
        statements = sqlparse.parse(cleaned)
        if len(statements) > 1:
            raise DAXValidationError("Multiple statements not allowed — send one query at a time")
    except Exception:
        pass  # sqlparse may not handle all DAX; the keyword check is the primary guard

    return cleaned


def inject_row_limit(query: str, max_rows: int) -> str:
    """Wrap query with TOPN if no row limit is already present.

    Only injects TOPN for EVALUATE queries that don't already use TOPN.
    DEFINE blocks and ROW() expressions are left as-is since they're inherently limited.

    Args:
        query: Validated DAX query.
        max_rows: Maximum rows to return.

    Returns:
        Query with row limit injected if needed.
    """
    upper = query.upper().strip()

    # Skip if already has TOPN
    if TOPN_PATTERN.search(query):
        return query

    # Skip if it's a ROW expression (returns exactly 1 row)
    if "ROW(" in upper:
        return query

    # For simple EVALUATE queries, wrap with TOPN
    if upper.startswith("EVALUATE"):
        body = query[len("EVALUATE"):].strip()
        return f"EVALUATE TOPN({max_rows}, {body})"

    # DEFINE ... EVALUATE — inject TOPN after EVALUATE
    eval_match = re.search(r"\bEVALUATE\b", query, re.IGNORECASE)
    if eval_match:
        before = query[:eval_match.end()]
        after = query[eval_match.end():].strip()
        return f"{before} TOPN({max_rows}, {after})"

    return query


# ── Audit Logger ──────────────────────────────────────────────────────

class AuditLogger:
    """Append-only JSON-lines audit log for all DAX queries."""

    def __init__(self, log_path: str | Path | None = None) -> None:
        self._path = Path(log_path) if log_path else None
        if self._path:
            self._path.parent.mkdir(parents=True, exist_ok=True)

    def log(
        self,
        *,
        query: str,
        dataset_id: str,
        workspace: str,
        row_count: int,
        elapsed_seconds: float,
        success: bool,
        error: str | None = None,
        user: str = "mcp_client",
    ) -> None:
        """Write a single audit entry."""
        entry: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "user": user,
            "workspace": workspace,
            "dataset_id": dataset_id,
            "query": query[:2000],  # truncate very long queries
            "row_count": row_count,
            "elapsed_seconds": elapsed_seconds,
            "success": success,
        }
        if error:
            entry["error"] = error[:500]

        logger.info(
            "DAX audit: workspace=%s dataset=%s rows=%d elapsed=%.3fs success=%s",
            workspace, dataset_id, row_count, elapsed_seconds, success,
        )

        if self._path:
            with open(self._path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")


# ── Rate Limiter (Token Bucket) ──────────────────────────────────────

class RateLimiter:
    """Simple token-bucket rate limiter."""

    def __init__(self, max_per_minute: int = 30) -> None:
        self._max = max_per_minute
        self._tokens = float(max_per_minute)
        self._last_refill = time.monotonic()

    def acquire(self) -> bool:
        """Try to acquire a token. Returns True if allowed, False if rate-limited."""
        now = time.monotonic()
        elapsed = now - self._last_refill
        self._tokens = min(self._max, self._tokens + elapsed * (self._max / 60.0))
        self._last_refill = now

        if self._tokens >= 1.0:
            self._tokens -= 1.0
            return True
        return False

    @property
    def wait_seconds(self) -> float:
        """Seconds until next token is available."""
        if self._tokens >= 1.0:
            return 0.0
        deficit = 1.0 - self._tokens
        return deficit / (self._max / 60.0)
