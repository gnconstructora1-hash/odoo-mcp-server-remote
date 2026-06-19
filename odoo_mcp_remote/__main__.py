"""Entry point: python -m odoo_mcp_remote"""

import argparse
import asyncio
import os

import uvicorn
from dotenv import load_dotenv

from .auth import BearerAuthMiddleware
from .server import mcp


def _build_app(api_key: str | None = None):
    """Build the ASGI app, optionally wrapping with bearer auth."""
    app = mcp.streamable_http_app()

    if api_key:
        app = BearerAuthMiddleware(app, api_key)
    return app


async def _serve(host: str, port: int, api_key: str | None = None):
    app = _build_app(api_key)
    config = uvicorn.Config(app, host=host, port=port, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()


def main():
    load_dotenv()

    parser = argparse.ArgumentParser(description="Odoo MCP Server (remote)")
    parser.add_argument("--host", default=os.environ.get("MCP_HOST", "0.0.0.0"))
    parser.add_argument("--port", type=int, default=int(os.environ.get("MCP_PORT", "8000")))
    args = parser.parse_args()

    api_key = os.environ.get("MCP_API_KEY")
    if not api_key:
        print("WARNING: MCP_API_KEY not set — server is running without authentication")

    print(f"Starting Odoo MCP server on {args.host}:{args.port}")
    asyncio.run(_serve(args.host, args.port, api_key))


if __name__ == "__main__":
    main()
