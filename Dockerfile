# Startup Valuation MCP server — stdio transport.
#
# Builds the Python library plus the FastMCP server and runs the stdio
# entrypoint, for local use or a registry (e.g. Glama) that wraps stdio with
# mcp-proxy. No environment variables or network access required.
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install the library + MCP extra (fastmcp). Build context is the repo root.
COPY pyproject.toml README.md LICENSE ./
COPY src ./src
RUN pip install ".[mcp]"

# The tool surface + stdio entrypoint. Regenerate with scripts/generate_mcp.py.
COPY mcp_server ./mcp_server

CMD ["python", "mcp_server/server.py"]
