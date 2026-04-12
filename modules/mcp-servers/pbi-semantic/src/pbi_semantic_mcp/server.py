"""FastMCP server instance with lifespan management.

Initializes the Power BI client, metadata registry, and guardrails on startup.
Registers all tools and resources from sub-modules.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncIterator

from mcp.server.fastmcp import FastMCP

from pbi_semantic_mcp.client import PowerBIClient
from pbi_semantic_mcp.config import Settings, get_settings
from pbi_semantic_mcp.guardrails import AuditLogger, RateLimiter
from pbi_semantic_mcp.metadata.loader import MetadataLoader
from pbi_semantic_mcp.metadata.registry import MetadataRegistry

logger = logging.getLogger(__name__)


@asynccontextmanager
async def server_lifespan(server: FastMCP) -> AsyncIterator[dict]:
    """Manage PBI client and metadata lifecycle.

    Yields a context dict available to all tools via `ctx.request_context.lifespan_context`.
    """
    settings = get_settings()

    # Initialize PBI client
    pbi_client = PowerBIClient(settings)
    if settings.has_credentials:
        await pbi_client.start()
        logger.info("PBI client connected")
    else:
        logger.warning("No Azure AD credentials — PBI client running in metadata-only mode")

    # Load metadata from YAML
    data_dir = Path(settings.metadata_dir) if settings.metadata_dir else (
        Path(__file__).parent / "data"
    )
    loader = MetadataLoader(data_dir)
    registry = loader.load()
    logger.info("Metadata loaded: %d datasets", len(registry.datasets))

    # Initialize guardrails
    audit_logger = AuditLogger(data_dir.parent / "logs" / "audit.jsonl")
    rate_limiter = RateLimiter(settings.rate_limit_per_minute)

    context = {
        "settings": settings,
        "pbi_client": pbi_client,
        "registry": registry,
        "audit_logger": audit_logger,
        "rate_limiter": rate_limiter,
    }

    try:
        yield context
    finally:
        if settings.has_credentials:
            await pbi_client.stop()
        logger.info("Server shutdown complete")


def create_server() -> FastMCP:
    """Create and configure the MCP server with all tools and resources."""
    mcp = FastMCP(
        "UBI Power BI",
        instructions=(
            "MCP server for UBI Power BI semantic models. "
            "Provides schema browsing, metadata lookup, DAX query execution (read-only), "
            "and data dictionary access for all UBI datasets. "
            "Use list_datasets to discover available models, get_schema to understand "
            "table structures, and query_data to execute DAX queries with automatic guardrails."
        ),
        lifespan=server_lifespan,
    )

    # Import and register tools (side-effect: decorators register with mcp)
    from pbi_semantic_mcp.tools import datasets, measures, query  # noqa: F401

    # Register tools by passing the mcp instance
    datasets.register(mcp)
    query.register(mcp)
    measures.register(mcp)

    return mcp
