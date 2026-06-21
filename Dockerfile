FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml .
COPY README.md .
COPY odoo_mcp_remote/ odoo_mcp_remote/

RUN pip install --no-cache-dir "mcp[cli]>=1.9.0,<1.10" && pip install --no-cache-dir .

EXPOSE 8000

CMD ["python", "-m", "odoo_mcp_remote"]
