"""Tests for Gateway and Eka integration (triage tool config, gateway client)."""

import os

import pytest


def test_triage_tool_config_without_gateway_returns_single_tool():
    """Without GATEWAY_* env, get_triage_tool_config_with_eka returns single-tool config."""
    for key in ("GATEWAY_MCP_URL", "GATEWAY_CLIENT_ID", "GATEWAY_CLIENT_SECRET", "GATEWAY_TOKEN_ENDPOINT"):
        os.environ.pop(key, None)
    from triage.core.tools import get_triage_tool_config_with_eka

    c = get_triage_tool_config_with_eka()
    assert len(c["tools"]) == 1
    assert c["tools"][0]["toolSpec"]["name"] == "submit_triage_result"
    assert c["toolChoice"]["tool"]["name"] == "submit_triage_result"


def test_triage_tool_config_with_gateway_includes_eka_tools():
    """With GATEWAY_* env set, get_triage_tool_config_with_eka includes Eka tools and toolChoice any."""
    os.environ["GATEWAY_MCP_URL"] = "https://test.example/mcp"
    os.environ["GATEWAY_CLIENT_ID"] = "cid"
    os.environ["GATEWAY_CLIENT_SECRET"] = "secret"
    os.environ["GATEWAY_TOKEN_ENDPOINT"] = "https://auth.example/token"
    try:
        from triage.core.tools import get_triage_tool_config_with_eka

        c = get_triage_tool_config_with_eka()
        names = [t["toolSpec"]["name"] for t in c["tools"]]
        assert "search_indian_medications" in names
        assert "search_treatment_protocols" in names
        assert "submit_triage_result" in names
        assert c["toolChoice"]["tool"]["name"] == "any"
    finally:
        for key in ("GATEWAY_MCP_URL", "GATEWAY_CLIENT_ID", "GATEWAY_CLIENT_SECRET", "GATEWAY_TOKEN_ENDPOINT"):
            os.environ.pop(key, None)


def test_gateway_client_not_configured():
    """is_gateway_configured is False when GATEWAY_MCP_URL is unset."""
    os.environ.pop("GATEWAY_MCP_URL", None)
    os.environ.pop("GATEWAY_CLIENT_ID", None)
    os.environ.pop("GATEWAY_CLIENT_SECRET", None)
    os.environ.pop("GATEWAY_TOKEN_ENDPOINT", None)
    from triage.core.gateway_client import is_gateway_configured

    assert is_gateway_configured() is False


def test_gateway_client_configured():
    """is_gateway_configured is True when all required env vars are set."""
    os.environ["GATEWAY_MCP_URL"] = "https://x/mcp"
    os.environ["GATEWAY_CLIENT_ID"] = "c"
    os.environ["GATEWAY_CLIENT_SECRET"] = "s"
    os.environ["GATEWAY_TOKEN_ENDPOINT"] = "https://t/token"
    try:
        from triage.core.gateway_client import is_gateway_configured

        assert is_gateway_configured() is True
    finally:
        for key in ("GATEWAY_MCP_URL", "GATEWAY_CLIENT_ID", "GATEWAY_CLIENT_SECRET", "GATEWAY_TOKEN_ENDPOINT"):
            os.environ.pop(key, None)
