"""MCP server with Odoo tools — runs over Streamable HTTP."""

import asyncio
import json
import os
from typing import Any

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings
from pydantic import ValidationError

from .odoo_client import OdooClient, OdooConfig

load_dotenv()

mcp = FastMCP(
    "odoo-mcp-server",
    stateless_http=True,
    json_response=True,
    host="0.0.0.0",
    transport_security=TransportSecuritySettings(
        enable_dns_rebinding_protection=False,
    ),
)

_odoo_client: OdooClient | None = None


def _get_client() -> OdooClient:
    global _odoo_client
    if _odoo_client is None:
        verify_ssl = os.environ.get("ODOO_VERIFY_SSL", "false").lower() in ("true", "1", "yes")
        try:
            config = OdooConfig(
                url=os.environ["ODOO_URL"],
                database=os.environ["ODOO_DB"],
                username=os.environ["ODOO_USERNAME"],
                password=os.environ.get("ODOO_PASSWORD"),
                api_key=os.environ.get("ODOO_API_KEY"),
                timeout=int(os.environ.get("ODOO_TIMEOUT", "120")),
                verify_ssl=verify_ssl,
            )
            _odoo_client = OdooClient(config)
        except (KeyError, ValidationError) as e:
            raise ValueError(f"Invalid Odoo configuration: {e}") from e
    return _odoo_client


@mcp.tool()
async def search_records(
    model: str,
    domain: list[Any] | None = None,
    fields: list[str] | None = None,
    limit: int | None = None,
    offset: int = 0,
    order: str | None = None,
) -> str:
    """Search for Odoo records.

    Args:
        model: Odoo model name (e.g. 'res.partner', 'sale.order')
        domain: Search domain in Odoo format (e.g. [['name', 'ilike', 'john']])
        fields: List of fields to return
        limit: Maximum number of records to return
        offset: Number of records to skip
        order: Sort order (e.g. 'name asc, id desc')
    """
    client = _get_client()
    result = await asyncio.to_thread(
        client.search_read,
        model=model,
        domain=domain or [],
        fields=fields,
        offset=offset,
        limit=limit,
        order=order,
    )
    return json.dumps(result, indent=2, default=str)


@mcp.tool()
async def get_record(
    model: str,
    ids: list[int],
    fields: list[str] | None = None,
) -> str:
    """Get specific Odoo records by ID.

    Args:
        model: Odoo model name
        ids: List of record IDs to retrieve
        fields: List of fields to return
    """
    client = _get_client()
    result = await asyncio.to_thread(
        client.read,
        model=model,
        ids=ids,
        fields=fields,
    )
    return json.dumps(result, indent=2, default=str)


@mcp.tool()
async def create_record(
    model: str,
    values: dict[str, Any],
) -> str:
    """Create a new Odoo record.

    Args:
        model: Odoo model name
        values: Field values for the new record
    """
    client = _get_client()
    result = await asyncio.to_thread(
        client.create,
        model=model,
        values=values,
    )
    return f"Created record with ID: {result}"


@mcp.tool()
async def update_record(
    model: str,
    ids: list[int],
    values: dict[str, Any],
) -> str:
    """Update existing Odoo records.

    Args:
        model: Odoo model name
        ids: List of record IDs to update
        values: Field values to update
    """
    client = _get_client()
    success = await asyncio.to_thread(
        client.write,
        model=model,
        ids=ids,
        values=values,
    )
    return f"Update {'successful' if success else 'failed'} for IDs: {ids}"


@mcp.tool()
async def delete_record(
    model: str,
    ids: list[int],
) -> str:
    """Delete Odoo records.

    Args:
        model: Odoo model name
        ids: List of record IDs to delete
    """
    client = _get_client()
    success = await asyncio.to_thread(
        client.unlink,
        model=model,
        ids=ids,
    )
    return f"Delete {'successful' if success else 'failed'} for IDs: {ids}"


@mcp.tool()
async def list_models(
    transient: bool = False,
) -> str:
    """List all available Odoo models.

    Args:
        transient: Include transient (wizard) models
    """
    client = _get_client()
    models = await asyncio.to_thread(client.get_model_list)
    if not transient:
        models = [m for m in models if not m.get("transient", False)]
    output = "Available Odoo models:\n"
    for model in sorted(models, key=lambda x: x["model"]):
        output += f"- {model['model']}: {model['name']}\n"
    return output


@mcp.tool()
async def get_model_fields(
    model: str,
    fields: list[str] | None = None,
) -> str:
    """Get field definitions for an Odoo model.

    Args:
        model: Odoo model name
        fields: Specific fields to get info for (optional)
    """
    client = _get_client()
    result = await asyncio.to_thread(
        client.fields_get,
        model=model,
        fields=fields,
    )
    return json.dumps(result, indent=2, default=str)
