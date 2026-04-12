"""MCP tools: query_data, get_sample_data."""

from __future__ import annotations

from mcp.server.fastmcp import Context, FastMCP

from pbi_semantic_mcp.guardrails import DAXValidationError, inject_row_limit, validate_dax


def register(mcp: FastMCP) -> None:
    """Register query tools with the MCP server."""

    @mcp.tool()
    async def query_data(
        ctx: Context,
        dax_query: str,
        dataset: str,
        workspace: str = "",
    ) -> str:
        """Execute a read-only DAX query against a Power BI semantic model.

        The query goes through guardrails:
        1. Validated for read-only operations (no CREATE/ALTER/DROP/DELETE/INSERT/UPDATE)
        2. Row limit injected (TOPN) if not already present
        3. Rate-limited and audit-logged

        Args:
            dax_query: DAX query starting with EVALUATE or DEFINE.
            dataset: Dataset name or ID to query.
            workspace: Workspace environment (prod/dev/qa). Default: from config.

        Returns:
            Markdown table of results, or error message.
        """
        lifespan = ctx.request_context.lifespan_context
        registry = lifespan["registry"]
        pbi_client = lifespan["pbi_client"]
        settings = lifespan["settings"]
        audit = lifespan["audit_logger"]
        limiter = lifespan["rate_limiter"]

        # Resolve dataset ID
        ds = registry.get_dataset(dataset)
        dataset_id = ds.id if ds else dataset  # fall back to treating input as ID
        ws = workspace or settings.pbi_default_workspace

        if not dataset_id:
            return (
                f"Cannot resolve dataset '{dataset}'. "
                "Provide a dataset name from `list_datasets` or a dataset ID."
            )

        # Rate limit
        if not limiter.acquire():
            wait = limiter.wait_seconds
            return f"Rate limited. Try again in {wait:.1f} seconds."

        # Validate and apply guardrails
        try:
            cleaned = validate_dax(dax_query)
        except DAXValidationError as e:
            audit.log(
                query=dax_query, dataset_id=dataset_id, workspace=ws,
                row_count=0, elapsed_seconds=0, success=False, error=str(e),
            )
            return f"**Validation error**: {e}"

        guarded_query = inject_row_limit(cleaned, settings.dax_max_rows)

        # Check credentials
        if not pbi_client._access_token:
            return (
                "**No PBI credentials configured.** "
                "Set AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET in .env"
            )

        # Execute
        try:
            result = pbi_client.execute_dax(guarded_query, dataset_id, ws)
            # Handle both coroutine and direct result
            if hasattr(result, "__await__"):
                result = await result
        except Exception as e:
            audit.log(
                query=guarded_query, dataset_id=dataset_id, workspace=ws,
                row_count=0, elapsed_seconds=0, success=False, error=str(e),
            )
            return f"**Query error**: {e}"

        # Audit
        audit.log(
            query=guarded_query, dataset_id=dataset_id, workspace=ws,
            row_count=result.row_count,
            elapsed_seconds=result.metadata.get("elapsed_seconds", 0),
            success=True,
        )

        # Format as markdown table
        if result.row_count == 0:
            return "Query returned 0 rows."

        return _format_result(result)

    @mcp.tool()
    async def get_sample_data(
        ctx: Context,
        dataset: str,
        table: str,
        n: int = 10,
        workspace: str = "",
    ) -> str:
        """Preview the top N rows of a table in a Power BI dataset.

        Generates and executes: EVALUATE TOPN({n}, '{table}')

        Args:
            dataset: Dataset name or ID.
            table: Table name to sample.
            n: Number of rows (default 10, max 100).
            workspace: Workspace environment (prod/dev/qa).

        Returns:
            Markdown table of sample rows.
        """
        n = min(max(1, n), 100)  # clamp to 1-100
        dax = f"EVALUATE TOPN({n}, '{table}')"

        # Delegate to query_data
        return await query_data(ctx, dax_query=dax, dataset=dataset, workspace=workspace)


def _format_result(result) -> str:
    """Format a QueryResult as a markdown table."""
    lines = [
        "| " + " | ".join(result.columns) + " |",
        "| " + " | ".join(["---"] * len(result.columns)) + " |",
    ]
    for row in result.rows[:200]:  # cap display at 200 rows
        cells = [_format_cell(v) for v in row]
        lines.append("| " + " | ".join(cells) + " |")

    footer = f"\n*{result.row_count} rows"
    elapsed = result.metadata.get("elapsed_seconds")
    if elapsed:
        footer += f" in {elapsed}s"
    footer += "*"
    lines.append(footer)

    return "\n".join(lines)


def _format_cell(value) -> str:
    """Format a single cell value for markdown display."""
    if value is None:
        return ""
    if isinstance(value, float):
        if value == int(value):
            return str(int(value))
        return f"{value:,.2f}"
    return str(value).replace("|", "\\|")
