"""Entry point: python -m odoo_mcp_remote"""

import asyncio
import os

import uvicorn
from dotenv import load_dotenv
from starlette.applications import Starlette

from .auth import BearerAuthMiddleware
from .server import mcp


def _build_app(api_key: str | None = None):
        """Build the ASGI app with redirect_slashes disabled to avoid 307 issues."""
        mcp_app = mcp.streamable_http_app()
        # Wrap in Starlette with redirect_slashes=False to prevent 307 redirects
        # that break Railway's reverse proxy
        app = Starlette(routes=[], redirect_slashes=False)
        app.mount("/mcp", mcp_app)
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

    host = os.environ.get("MCP_HOST", "0.0.0.0")
    port = int(os.environ.get("MCP_PORT", "8000"))
    api_key = os.environ.get("MCP_API_KEY")

    if not api_key:
                print("WARNING: MCP_API_KEY not set — server is running without authentication")

    print(f"Starting Odoo MCP server on {host}:{port}")
    asyncio.run(_serve(host, port, api_key))


if __name__ == "__main__":
        main()
