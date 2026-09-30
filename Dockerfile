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
# The MCP server ships inside the library (startup_valuation.mcp) and installs
# the `startup-valuation-mcp` console script.
COPY pyproject.toml README.md LICENSE ./
COPY src ./src
RUN pip install ".[mcp]"

CMD ["startup-valuation-mcp"]
