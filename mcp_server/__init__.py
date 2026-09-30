"""Compatibility shim for the relocated MCP server.

The MCP server now lives in the ``startup_valuation.mcp`` subpackage and ships
inside the ``startup-valuation`` distribution (console script
``startup-valuation-mcp``). This package is retained only so tooling pinned to
the historical ``mcp_server/server.py`` path — for example a hosted runner that
has not re-synced its build — keeps working.
"""
