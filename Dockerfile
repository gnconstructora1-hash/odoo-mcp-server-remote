FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml .
COPY odoo_mcp_remote/ odoo_mcp_remote/

RUN pip install --no-cache-dir .

EXPOSE 8000

CMD ["python", "-m", "odoo_mcp_remote"]
