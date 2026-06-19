# CLAUDE.md

## Project Overview

Remote MCP server for Odoo ERP. Exposes Odoo operations over Streamable HTTP so AI assistants (Claude Desktop, Claude Code, etc.) can connect from anywhere.

## Commands

```bash
pip install -e .
pip install -e ".[dev]"

# Run locally
python -m odoo_mcp_remote
python -m odoo_mcp_remote --host 0.0.0.0 --port 8000

# Docker
docker compose up --build

# Tests
pytest
ruff check .
ruff format .
```

## Architecture

- `server.py` — FastMCP instance with 7 Odoo tools (search, get, create, update, delete, list_models, get_model_fields)
- `odoo_client.py` — XML-RPC client via odooly
- `auth.py` — ASGI middleware for Bearer token authentication
- `__main__.py` — Entry point, builds ASGI app with auth wrapper and runs uvicorn

Transport: Streamable HTTP (stateless, JSON responses)
Auth: Bearer token via `MCP_API_KEY` env var

## Environment Variables

Required for Odoo connection:
- `ODOO_URL`, `ODOO_DB`, `ODOO_USERNAME`
- `ODOO_PASSWORD` or `ODOO_API_KEY`

Optional:
- `ODOO_VERIFY_SSL` (default: false)
- `ODOO_TIMEOUT` (default: 120)
- `ODOO_CUSTOM_HEADER_NAME` / `ODOO_CUSTOM_HEADER_VALUE`
- `MCP_API_KEY` — required for bearer auth (server runs unauthenticated without it)
- `MCP_HOST` (default: 0.0.0.0)
- `MCP_PORT` (default: 8000)
