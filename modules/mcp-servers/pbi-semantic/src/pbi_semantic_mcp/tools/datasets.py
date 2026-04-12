"""MCP tools: list_datasets, get_schema."""

from __future__ import annotations

from mcp.server.fastmcp import Context, FastMCP


def register(mcp: FastMCP) -> None:
    """Register dataset tools with the MCP server."""

    @mcp.tool()
    async def list_datasets(
        ctx: Context,
        search: str = "",
        include_live: bool = False,
    ) -> str:
        """List all available Power BI semantic models.

        Args:
            search: Optional search term to filter datasets by name/description.
            include_live: If True, also queries the PBI REST API for live dataset list
                          (requires credentials). Default: False (metadata-only).

        Returns:
            Markdown table of datasets with name, description, stream, and table count.
        """
        lifespan = ctx.request_context.lifespan_context
        registry = lifespan["registry"]
        pbi_client = lifespan["pbi_client"]

        if search:
            datasets = registry.search_datasets(search)
        else:
            datasets = registry.datasets

        if not datasets and not include_live:
            return "No datasets found in metadata. Try `include_live=True` to query the PBI API."

        lines = ["| Dataset | Description | Stream | Tables |", "|---------|-------------|--------|--------|"]
        for ds in datasets:
            desc = (ds.description[:60] + "...") if len(ds.description) > 60 else ds.description
            lines.append(f"| {ds.name} | {desc} | {ds.stream} | {len(ds.tables)} |")

        result = "\n".join(lines)

        # Optionally append live API results
        if include_live and pbi_client._access_token:
            try:
                live = await pbi_client.list_workspace_datasets()
                result += f"\n\n**Live API**: {len(live)} datasets in workspace\n"
                for d in live[:20]:
                    result += f"- `{d.get('name', '?')}` (ID: `{d.get('id', '?')}`)\n"
            except Exception as e:
                result += f"\n\n*Live API error: {e}*"

        return result

    @mcp.tool()
    async def get_schema(
        ctx: Context,
        dataset: str,
        table: str = "",
    ) -> str:
        """Get the schema (tables, columns, types) for a Power BI dataset.

        Args:
            dataset: Dataset name or ID.
            table: Optional — filter to a specific table name.

        Returns:
            Markdown-formatted schema with column names, types, and descriptions.
        """
        lifespan = ctx.request_context.lifespan_context
        registry = lifespan["registry"]

        ds = registry.get_dataset(dataset)
        if not ds:
            return f"Dataset '{dataset}' not found. Use `list_datasets` to see available datasets."

        if table:
            tbl = ds.get_table(table)
            if not tbl:
                return (
                    f"Table '{table}' not found in '{ds.name}'. "
                    f"Available: {', '.join(ds.table_names)}"
                )
            return _format_table_schema(ds.name, tbl)

        # Show all tables
        parts = [f"# {ds.name}\n\n{ds.description}\n"]
        parts.append(f"**Stream**: {ds.stream}  |  **Tables**: {len(ds.tables)}  |  **Workspace**: {ds.workspace}\n")

        for tbl in ds.tables:
            parts.append(_format_table_schema(ds.name, tbl))

        if ds.relationships:
            parts.append("\n## Relationships\n")
            parts.append("| From | To | Cardinality |")
            parts.append("|------|----|-------------|")
            for r in ds.relationships:
                parts.append(
                    f"| {r.from_table}[{r.from_column}] | "
                    f"{r.to_table}[{r.to_column}] | {r.cardinality} |"
                )

        return "\n".join(parts)


def _format_table_schema(dataset_name: str, tbl: TableMeta) -> str:
    """Format a single table's schema as markdown."""
    lines = [f"\n## {tbl.name}\n"]
    if tbl.description:
        lines.append(f"{tbl.description}\n")
    if tbl.row_count_estimate:
        lines.append(f"*~{tbl.row_count_estimate:,} rows*\n")

    if tbl.columns:
        lines.append("| Column | Type | Key | Description |")
        lines.append("|--------|------|-----|-------------|")
        for col in tbl.columns:
            key = "PK" if col.is_key and not col.fk_table else (
                f"FK→{col.fk_table}" if col.fk_table else ""
            )
            desc = col.description or col.business_definition
            lines.append(f"| {col.name} | {col.data_type} | {key} | {desc} |")

    if tbl.measures:
        lines.append(f"\n### Measures ({len(tbl.measures)})\n")
        lines.append("| Measure | Format | Description |")
        lines.append("|---------|--------|-------------|")
        for m in tbl.measures:
            lines.append(f"| {m.name} | {m.format_string} | {m.description} |")

    return "\n".join(lines)


# Import needed for type hint in _format_table_schema
from pbi_semantic_mcp.metadata.models import TableMeta  # noqa: E402
