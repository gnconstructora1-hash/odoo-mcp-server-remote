"""Odoo XML-RPC client using odooly."""

import os
import ssl
import http.client
import xmlrpc.client
from typing import Any
from urllib.parse import urlparse

from pydantic import BaseModel, Field

try:
    from odooly import Client as OdoolyClient
except Exception:
    OdoolyClient = None


class CustomHTTPTransport(xmlrpc.client.Transport):
    """Transport for plain HTTP connections with optional custom headers."""

    def send_headers(self, connection, headers):
        header_name = os.getenv("ODOO_CUSTOM_HEADER_NAME")
        header_value = os.getenv("ODOO_CUSTOM_HEADER_VALUE")
        if header_name and header_value:
            connection.putheader(header_name, header_value)
        super().send_headers(connection, headers)


class CustomHTTPSTransport(xmlrpc.client.SafeTransport):
    """Transport for HTTPS connections with SSL control and optional custom headers."""

    def __init__(self, context=None, verify_ssl: bool = False):
        self.verify_ssl = verify_ssl
        if context is None:
            if verify_ssl:
                context = ssl.create_default_context()
            else:
                context = ssl._create_unverified_context()
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
                context.options |= ssl.OP_NO_SSLv2 | ssl.OP_NO_SSLv3
                context.set_ciphers("DEFAULT")
        self.context = context
        super().__init__(context)

    def make_connection(self, host):
        if not self.verify_ssl:
            self.context.check_hostname = False
            self.context.verify_mode = ssl.CERT_NONE
        if ":" in host:
            host_str, port_str = host.rsplit(":", 1)
            try:
                port = int(port_str)
                host = host_str
            except ValueError:
                port = 443
        else:
            port = 443
        return http.client.HTTPSConnection(host, port, context=self.context)

    def send_headers(self, connection, headers):
        header_name = os.getenv("ODOO_CUSTOM_HEADER_NAME")
        header_value = os.getenv("ODOO_CUSTOM_HEADER_VALUE")
        if header_name and header_value:
            connection.putheader(header_name, header_value)
        super().send_headers(connection, headers)


class OdooConfig(BaseModel):
    """Configuration for Odoo connection."""

    model_config = {"arbitrary_types_allowed": True}

    url: str = Field(..., description="Odoo instance URL")
    database: str = Field(..., description="Odoo database name")
    username: str = Field(..., description="Odoo username")
    password: str | None = Field(None, description="Odoo password")
    api_key: str | None = Field(None, description="Odoo API key")
    timeout: int = Field(120, description="Request timeout in seconds")
    verify_ssl: bool = Field(False, description="Enable SSL certificate verification")

    def model_post_init(self, __context: Any) -> None:
        if not self.password and not self.api_key:
            raise ValueError("Either password or api_key must be provided")


class OdooClient:
    """Client for interacting with Odoo via odooly."""

    def __init__(self, config: OdooConfig) -> None:
        if OdoolyClient is None:
            raise ImportError("odooly is required")

        self.config = config
        self.url = config.url.rstrip("/")
        self.database = config.database
        self.username = config.username
        self.password = config.api_key or config.password
        self.timeout = config.timeout
        self.uid: int | None = None

        parsed_url = urlparse(self.url)
        if parsed_url.scheme == "https":
            self.transport = CustomHTTPSTransport(verify_ssl=config.verify_ssl)
        else:
            self.transport = CustomHTTPTransport()

        self.client = OdoolyClient(
            self.url,
            self.database,
            self.username,
            self.password,
            transport=self.transport,
        )
        self.env = self.client.env

    def search_read(
        self,
        model: str,
        domain: list[list[Any]] | None = None,
        fields: list[str] | None = None,
        offset: int = 0,
        limit: int | None = None,
        order: str | None = None,
    ) -> Any:
        domain = domain or []
        kwargs: dict[str, Any] = {"offset": offset}
        if fields is not None:
            kwargs["fields"] = fields
        if limit is not None:
            kwargs["limit"] = limit
        if order is not None:
            kwargs["order"] = order
        return self.env[model].search_read(domain, **kwargs)

    def read(
        self,
        model: str,
        ids: int | list[int],
        fields: list[str] | None = None,
    ) -> Any:
        if isinstance(ids, int):
            ids = [ids]
        kwargs: dict[str, Any] = {}
        if fields is not None:
            kwargs["fields"] = fields
        result = self.env[model].read(ids, **kwargs)
        return result[0] if len(ids) == 1 else result

    def create(
        self,
        model: str,
        values: dict[str, Any] | list[dict[str, Any]],
    ) -> Any:
        if isinstance(values, dict):
            return self.env[model].create(values)
        return [self.env[model].create(v) for v in values]

    def write(
        self,
        model: str,
        ids: int | list[int],
        values: dict[str, Any],
    ) -> Any:
        if isinstance(ids, int):
            ids = [ids]
        return self.env[model].write(ids, values)

    def unlink(
        self,
        model: str,
        ids: int | list[int],
    ) -> Any:
        if isinstance(ids, int):
            ids = [ids]
        return self.env[model].unlink(ids)

    def fields_get(
        self,
        model: str,
        fields: list[str] | None = None,
        attributes: list[str] | None = None,
    ) -> Any:
        kwargs: dict[str, Any] = {}
        if fields is not None:
            kwargs["fields"] = fields
        if attributes is not None:
            kwargs["attributes"] = attributes
        return self.env[model].fields_get(**kwargs)

    def get_model_list(self) -> Any:
        return self.env["ir.model"].search_read([], ["model", "name", "transient"])
