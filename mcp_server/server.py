"""Compatibility entry point for the relocated MCP server.

The canonical entry points are ``startup-valuation-mcp`` (console script) and
``python -m startup_valuation.mcp``. This module only re-exports the server so
runners still invoking ``mcp_server/server.py`` continue to work.
"""

from startup_valuation.mcp.server import main

if __name__ == "__main__":
    main()
