"""MCP tools: get_measures, get_dax_examples."""

from __future__ import annotations

from mcp.server.fastmcp import Context, FastMCP


def register(mcp: FastMCP) -> None:
    """Register measure tools with the MCP server."""

    @mcp.tool()
    async def get_measures(
        ctx: Context,
        dataset: str,
        table: str = "",
    ) -> str:
        """Get all DAX measures defined in a Power BI dataset.

        Args:
            dataset: Dataset name or ID.
            table: Optional — filter to measures in a specific table.

        Returns:
            Markdown list of measures with their DAX expressions, formats, and descriptions.
        """
        lifespan = ctx.request_context.lifespan_context
        registry = lifespan["registry"]

        ds = registry.get_dataset(dataset)
        if not ds:
            return f"Dataset '{dataset}' not found. Use `list_datasets` to see available datasets."

        measures = []
        if table:
            tbl = ds.get_table(table)
            if not tbl:
                return f"Table '{table}' not found in '{ds.name}'."
            measures = tbl.measures
        else:
            measures = ds.all_measures

        if not measures:
            return f"No measures found in '{ds.name}'" + (f" table '{table}'" if table else "") + "."

        lines = [f"# Measures in {ds.name}\n"]
        for m in measures:
            lines.append(f"### {m.name}")
            if m.description:
                lines.append(f"{m.description}")
            if m.expression:
                lines.append(f"```dax\n{m.expression}\n```")
            if m.format_string:
                lines.append(f"Format: `{m.format_string}`")
            if m.folder:
                lines.append(f"Folder: {m.folder}")
            lines.append("")

        return "\n".join(lines)

    @mcp.tool()
    async def get_dax_examples(
        ctx: Context,
        dataset: str = "",
        category: str = "",
    ) -> str:
        """Get curated DAX query examples for learning or reference.

        Args:
            dataset: Optional — filter examples relevant to a specific dataset.
            category: Optional — filter by category (e.g., "aggregation",
                      "time-intelligence", "filtering", "ranking").

        Returns:
            Markdown-formatted examples with questions, DAX queries, and explanations.
        """
        lifespan = ctx.request_context.lifespan_context
        registry = lifespan["registry"]

        examples = registry.get_dax_examples(
            dataset_name=dataset or None,
            category=category or None,
        )

        if not examples:
            parts = []
            if dataset:
                parts.append(f"dataset='{dataset}'")
            if category:
                parts.append(f"category='{category}'")
            filter_desc = " for " + ", ".join(parts) if parts else ""
            return f"No DAX examples found{filter_desc}."

        lines = ["# DAX Examples\n"]
        for ex in examples:
            lines.append(f"### {ex.question}")
            if ex.category:
                lines.append(f"*Category: {ex.category}*\n")
            lines.append(f"```dax\n{ex.query}\n```")
            if ex.explanation:
                lines.append(f"_{ex.explanation}_\n")
            lines.append("")

        return "\n".join(lines)
