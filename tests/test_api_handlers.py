"""Handler tests for the two Python API entry points (api/index.py, api/calculate.py).

These cover the behaviour the deployment depends on: the balancer probes /api/health on the
MCP container (apg-infra alb-health.py), so a probe that cannot fail is a real defect.
"""

from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "api"))
sys.path.insert(0, str(ROOT / "src"))

calculate = importlib.import_module("calculate")
mcp = importlib.import_module("index")


def test_calculate_404s_paths_it_does_not_own():
    code, _, _ = calculate.handle_request("GET", "/api/auth/session", None)
    assert code == 404


def test_mcp_404s_paths_it_does_not_own():
    code, _, _ = mcp.handle_request("GET", "/api/webhooks/stripe", None)
    assert code == 404


def test_mcp_404s_the_old_api_prefix():
    # /api/* belongs to the Next.js app; the MCP endpoint moved to /mcp so the two stop
    # competing for one prefix.
    assert mcp.handle_request("POST", "/api", "{}")[0] == 404


@pytest.mark.parametrize("path", ["/mcp", "/mcp/"])
def test_the_mcp_endpoint_rejects_get(path):
    # The transport spec has the server answer 405 to GET on the endpoint; a 200 here is
    # what makes a client read the endpoint as a REST API and give up.
    code, headers, body = mcp.handle_request("GET", path, None)
    assert code == 405
    assert headers.get("Allow") == "POST, OPTIONS"
    assert b"METHOD_NOT_ALLOWED" in body


@pytest.mark.parametrize("path", ["/api/calculate", "/api/health"])
def test_calculate_serves_its_declared_paths(path):
    assert calculate.handle_request("GET", path, None)[0] == 200


@pytest.mark.parametrize("path", ["/mcp", "/mcp/", "/api/health"])
def test_mcp_serves_its_declared_paths(path):
    # /api/health is the balancer's probe path (apg-infra alb-health.py), POST /mcp is MCP.
    code = mcp.handle_request("POST" if path.startswith("/mcp") else "GET", path, "{}")[0]
    assert code == 200


def test_head_is_supported():
    # A BaseHTTPRequestHandler without do_HEAD answered 501, which monitors read as an outage.
    assert calculate.handle_request("HEAD", "/api/health", None)[0] == 200
    assert mcp.handle_request("HEAD", "/api/health", None)[0] == 200


def test_health_is_200_when_the_library_computes():
    for handler in (calculate, mcp):
        code, _, body = handler.handle_request("GET", "/api/health", None)
        assert code == 200
        assert json.loads(body)["status"] == "ok"


def test_health_returns_503_when_the_computation_fails(monkeypatch):
    # The probe has to fail with the thing it is probing, or the balancer cannot tell a
    # broken instance from a healthy one.
    def boom(*_args, **_kwargs):
        raise RuntimeError("library is broken")

    monkeypatch.setattr(calculate.tv, "present_value", boom)
    code, _, body = calculate.handle_request("GET", "/api/health", None)
    assert code == 503
    assert json.loads(body)["status"] == "failing"

    monkeypatch.setattr(mcp, "call_tool", boom)
    code, _, body = mcp.handle_request("GET", "/api/health", None)
    assert code == 503
    assert json.loads(body)["status"] == "failing"


def test_calculate_rejects_malformed_json():
    code, _, body = calculate.handle_request("POST", "/api/calculate", "{not json")
    assert code == 400
    assert json.loads(body)["error"] == "PARSE_ERROR"


def test_calculate_rejects_null_params():
    code, _, _ = calculate.handle_request("POST", "/api/calculate", json.dumps({"method": "scorecard", "params": None}))
    assert code == 400


def test_calculate_rejects_non_finite_input():
    code, _, body = calculate.handle_request(
        "POST", "/api/calculate", '{"method":"pe_ratio","params":{"market_cap":NaN,"net_income":1}}'
    )
    assert code == 400
    assert json.loads(body)["error"] == "NON_FINITE_INPUT"


def test_calculate_reports_library_validation_as_400():
    # A domain ValueError is the caller's input being wrong, not a server fault.
    code, _, body = calculate.handle_request(
        "POST",
        "/api/calculate",
        json.dumps({"method": "portfolio_beta", "params": {"weights": [0.5, 0.6], "betas": [1, 1]}}),
    )
    assert code == 400
    assert json.loads(body)["error"] == "VALIDATION_ERROR"


def test_calculate_computes():
    code, _, body = calculate.handle_request(
        "POST", "/api/calculate", json.dumps({"method": "pe_ratio", "params": {"market_cap": 1000, "net_income": 100}})
    )
    assert code == 200
    payload = json.loads(body)
    assert payload["value"] == pytest.approx(10.0)
    assert payload["library_version"] == calculate.LIBRARY_VERSION


def test_mcp_initialize_answers():
    code, _, body = mcp.handle_request("POST", "/mcp", json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize"}))
    assert code == 200
    assert json.loads(body)["result"]["serverInfo"]["name"]
