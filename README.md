# Odoo MCP Server (Remote)

Remote MCP server for Odoo ERP — exposes Odoo operations over Streamable HTTP with bearer token authentication.

## Quick Start

```bash
cp .env.example .env
# Edit .env with your Odoo credentials and MCP_API_KEY

pip install -e .
python -m odoo_mcp_remote
```

## Docker

```bash
cp .env.example .env
docker compose up --build
```

## Client Configuration

### Claude Desktop / Claude Code

If your client supports `streamable-http` natively:

```json
{
  "mcpServers": {
    "odoo": {
      "type": "streamable-http",
      "url": "http://your-server:8000/mcp",
      "headers": {
        "Authorization": "Bearer your-secret-api-key-here"
      }
    }
  }
}
```

### Using supergateway (stdio bridge)

If your client only supports stdio transport (e.g. some Claude Desktop versions), use [supergateway](https://github.com/nicholasgriffintn/supergateway) to bridge the connection:

```json
{
  "mcpServers": {
    "odoo": {
      "command": "npx",
      "args": [
        "-y",
        "supergateway",
        "--streamableHttp",
        "http://your-server:8000/mcp",
        "--header",
        "Authorization: Bearer your-secret-api-key-here"
      ]
    }
  }
}
```

## Tools

| Tool | Description |
|------|-------------|
| `search_records` | Search Odoo records with domain filters |
| `get_record` | Get records by ID |
| `create_record` | Create new records |
| `update_record` | Update existing records |
| `delete_record` | Delete records |
| `list_models` | List available Odoo models |
| `get_model_fields` | Get field definitions for a model |
