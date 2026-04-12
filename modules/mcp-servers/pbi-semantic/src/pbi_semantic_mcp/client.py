"""Power BI REST API client with auto token refresh and multi-dataset support.

Refactored from data_agent/adapters/powerbi_adapter.py with key improvements:
- Auto token refresh before 60-min expiry
- Multi-dataset support (dataset_id per call)
- Connection pooling via shared httpx.AsyncClient
- Structured result format (columns + rows + metadata)
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any

import httpx

from pbi_semantic_mcp.config import Settings

logger = logging.getLogger(__name__)

PBI_API_BASE = "https://api.powerbi.com/v1.0/myorg"
PBI_SCOPE = "https://analysis.windows.net/powerbi/api/.default"
TOKEN_REFRESH_MARGIN = 300  # refresh 5 min before expiry


@dataclass
class QueryResult:
    """Structured result from a DAX query."""

    columns: list[str]
    rows: list[list[Any]]
    row_count: int
    metadata: dict[str, Any] = field(default_factory=dict)


class PowerBIClient:
    """Async Power BI REST API client for MCP server use.

    Manages a single httpx.AsyncClient with automatic token refresh.
    Supports querying any dataset in any configured workspace.
    """

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._client: httpx.AsyncClient | None = None
        self._access_token: str | None = None
        self._token_acquired_at: float = 0.0
        self._token_expires_in: int = 3600  # Azure AD default

    async def start(self) -> None:
        """Initialize the HTTP client and acquire first token."""
        if self._settings.has_credentials:
            await self._refresh_token()
        self._client = httpx.AsyncClient(
            timeout=httpx.Timeout(self._settings.dax_timeout_seconds, connect=10.0),
        )
        logger.info("PowerBIClient started (workspace=%s)", self._settings.pbi_default_workspace)

    async def stop(self) -> None:
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None
        self._access_token = None
        logger.info("PowerBIClient stopped")

    async def execute_dax(
        self,
        dax_query: str,
        dataset_id: str,
        workspace: str | None = None,
    ) -> QueryResult:
        """Execute a DAX query against a specific dataset.

        Args:
            dax_query: The DAX query (must start with EVALUATE, DEFINE, or ROW).
            dataset_id: Target dataset/semantic model ID.
            workspace: Workspace name (prod/dev/qa) or None for default.

        Returns:
            QueryResult with columns, rows, and metadata.
        """
        if not self._client:
            raise RuntimeError("Client not started. Call start() first.")

        await self._ensure_token()

        workspace_id = self._resolve_workspace(workspace)
        url = f"{PBI_API_BASE}/groups/{workspace_id}/datasets/{dataset_id}/executeQueries"

        payload = {
            "queries": [{"query": dax_query}],
            "serializerSettings": {"includeNulls": True},
        }

        start_time = time.monotonic()
        response = await self._client.post(
            url,
            json=payload,
            headers={
                "Authorization": f"Bearer {self._access_token}",
                "Content-Type": "application/json",
            },
        )
        elapsed = time.monotonic() - start_time

        if response.status_code != 200:
            error_detail = response.text[:500]
            raise ValueError(
                f"Power BI API error (HTTP {response.status_code}): {error_detail}"
            )

        data = response.json()
        result = self._parse_response(data, dax_query)
        result.metadata["elapsed_seconds"] = round(elapsed, 3)
        result.metadata["workspace"] = workspace or self._settings.pbi_default_workspace
        result.metadata["dataset_id"] = dataset_id
        return result

    async def list_workspace_datasets(self, workspace: str | None = None) -> list[dict[str, Any]]:
        """List all datasets in a workspace via REST API.

        Returns list of dicts with id, name, description, etc.
        """
        if not self._client:
            raise RuntimeError("Client not started. Call start() first.")

        await self._ensure_token()
        workspace_id = self._resolve_workspace(workspace)
        url = f"{PBI_API_BASE}/groups/{workspace_id}/datasets"

        response = await self._client.get(
            url,
            headers={"Authorization": f"Bearer {self._access_token}"},
        )
        if response.status_code != 200:
            raise ValueError(f"Failed to list datasets: {response.text[:500]}")

        return response.json().get("value", [])

    async def health_check(self) -> bool:
        """Verify connectivity by executing a trivial DAX query."""
        try:
            datasets = await self.list_workspace_datasets()
            return len(datasets) > 0
        except Exception:
            return False

    # ── Token management ──────────────────────────────────────────────

    async def _ensure_token(self) -> None:
        """Refresh token if expired or about to expire."""
        if not self._access_token:
            await self._refresh_token()
            return

        elapsed = time.monotonic() - self._token_acquired_at
        if elapsed >= (self._token_expires_in - TOKEN_REFRESH_MARGIN):
            logger.info("Token nearing expiry (%.0fs elapsed), refreshing...", elapsed)
            await self._refresh_token()

    async def _refresh_token(self) -> None:
        """Acquire a new access token via Service Principal client credentials."""
        s = self._settings
        if not s.has_credentials:
            raise RuntimeError(
                "Azure AD credentials not configured. Set AZURE_TENANT_ID, "
                "AZURE_CLIENT_ID, AZURE_CLIENT_SECRET."
            )

        token_url = f"https://login.microsoftonline.com/{s.azure_tenant_id}/oauth2/v2.0/token"

        async with httpx.AsyncClient() as client:
            response = await client.post(
                token_url,
                data={
                    "grant_type": "client_credentials",
                    "client_id": s.azure_client_id,
                    "client_secret": s.azure_client_secret,
                    "scope": PBI_SCOPE,
                },
            )
            if response.status_code != 200:
                raise ConnectionError(f"Token acquisition failed: {response.text[:300]}")

            token_data = response.json()
            self._access_token = token_data["access_token"]
            self._token_expires_in = token_data.get("expires_in", 3600)
            self._token_acquired_at = time.monotonic()
            logger.info("Token acquired (expires_in=%ds)", self._token_expires_in)

    # ── Response parsing ──────────────────────────────────────────────

    @staticmethod
    def _parse_response(data: dict[str, Any], query: str) -> QueryResult:
        """Parse Power BI executeQueries JSON response."""
        results = data.get("results", [])
        if not results:
            return QueryResult(columns=[], rows=[], row_count=0, metadata={"query": query})

        tables = results[0].get("tables", [])
        if not tables:
            return QueryResult(columns=[], rows=[], row_count=0, metadata={"query": query})

        table = tables[0]
        raw_rows: list[dict[str, Any]] = table.get("rows", [])
        if not raw_rows:
            return QueryResult(columns=[], rows=[], row_count=0, metadata={"query": query})

        # Extract and clean column names (PBI prefixes: [Table].[Column])
        raw_columns = list(raw_rows[0].keys())
        clean_columns = [
            col.split("].[")[-1].rstrip("]") if "].[" in col else col
            for col in raw_columns
        ]

        rows = [[row.get(col) for col in raw_columns] for row in raw_rows]

        return QueryResult(
            columns=clean_columns,
            rows=rows,
            row_count=len(rows),
            metadata={"query": query, "raw_columns": raw_columns},
        )

    # ── Helpers ───────────────────────────────────────────────────────

    def _resolve_workspace(self, workspace: str | None) -> str:
        """Resolve workspace name to ID."""
        name = workspace or self._settings.pbi_default_workspace
        ws_id = self._settings.workspace_ids.get(name)
        if not ws_id:
            raise ValueError(f"Unknown workspace '{name}'. Use prod/dev/qa.")
        return ws_id
