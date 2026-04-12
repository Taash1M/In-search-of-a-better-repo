"""CLI entry point: python -m pbi_semantic_mcp [--transport stdio|sse|streamable-http]."""

from __future__ import annotations

import argparse
import logging


def main() -> None:
    parser = argparse.ArgumentParser(description="UBI Power BI MCP Server")
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse", "streamable-http"],
        default=None,
        help="Transport mode (default: from .env or stdio)",
    )
    parser.add_argument("--port", type=int, default=None, help="HTTP port (for sse/streamable-http)")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO,
        format="%(asctime)s %(name)s %(levelname)s %(message)s",
    )

    from pbi_semantic_mcp.server import create_server

    mcp = create_server()

    # Determine transport
    transport = args.transport
    if not transport:
        from pbi_semantic_mcp.config import get_settings
        transport = get_settings().mcp_transport

    if transport == "stdio":
        mcp.run(transport="stdio")
    elif transport == "sse":
        port = args.port or get_settings().mcp_port if not args.port else args.port
        mcp.run(transport="sse", port=port)
    elif transport == "streamable-http":
        port = args.port or get_settings().mcp_port if not args.port else args.port
        mcp.run(transport="streamable-http", port=port)


if __name__ == "__main__":
    main()
