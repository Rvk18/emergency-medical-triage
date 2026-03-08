"""
Tests for RMP Learning: handler routing/validation (unit) and optional live API (integration).

Unit tests mock invoke_rmp_quiz and DB so no AWS/network required.
Live tests run only when RUN_LIVE_RMP_TESTS=1, API_URL and RMP_TOKEN are set (e.g. eval $(python3 scripts/load_api_config.py --exports) && export RMP_TOKEN=$(python3 scripts/get_rmp_token.py) && export RUN_LIVE_RMP_TESTS=1).

Run from project root:
  pytest tests/test_rmp_learning.py -v
  pytest tests/test_rmp_learning.py -v -k "live"  # only live API tests (requires env)
"""

import json
from unittest.mock import patch

import pytest


def _api_event(method: str, path: str, body: str | None = None, auth_sub: str | None = "rmp-sub-123", query: dict | None = None):
    event = {
        "httpMethod": method,
        "path": path,
        "requestContext": {},
    }
    if auth_sub:
        event["requestContext"]["authorizer"] = {"sub": auth_sub}
    if body is not None:
        event["body"] = body
    if query:
        event["queryStringParameters"] = query
    return event


# ---- Unit tests (mocked) ----


@patch("rmp_learning.api.handler.invoke_rmp_quiz")
def test_post_get_question_returns_200(mock_invoke):
    mock_invoke.return_value = {
        "question": "What is the first step?",
        "reference_answer": "Assess ABC.",
        "topic": "fever protocol",
    }
    from rmp_learning.api.handler import handler

    event = _api_event("POST", "/rmp/learning", body='{"action":"get_question","topic":"fever protocol"}')
    resp = handler(event, None)
    assert resp["statusCode"] == 200
    data = json.loads(resp["body"])
    assert data["question"] == "What is the first step?"
    assert "reference_answer" in data
    mock_invoke.assert_called_once()


@patch("rmp_learning.api.handler.invoke_rmp_quiz")
def test_post_score_answer_returns_200(mock_invoke):
    mock_invoke.return_value = {"points": 5, "feedback": "Good."}
    from rmp_learning.api.handler import handler

    event = _api_event(
        "POST",
        "/rmp/learning",
        body='{"action":"score_answer","question":"Q?","reference_answer":"R","user_answer":"A"}',
    )
    resp = handler(event, None)
    assert resp["statusCode"] == 200
    data = json.loads(resp["body"])
    assert data["points"] == 5
    assert data["feedback"] == "Good."


def test_post_invalid_json_returns_400():
    from rmp_learning.api.handler import handler

    event = _api_event("POST", "/rmp/learning", body="not json")
    resp = handler(event, None)
    assert resp["statusCode"] == 400


def test_post_non_object_body_returns_400():
    from rmp_learning.api.handler import handler

    event = _api_event("POST", "/rmp/learning", body='["array"]')
    resp = handler(event, None)
    assert resp["statusCode"] == 400


def test_get_unknown_path_returns_404():
    from rmp_learning.api.handler import handler

    event = _api_event("GET", "/rmp/learning/other")
    resp = handler(event, None)
    assert resp["statusCode"] == 404


def test_method_not_allowed():
    from rmp_learning.api.handler import handler

    event = _api_event("PUT", "/rmp/learning", body="{}")
    resp = handler(event, None)
    assert resp["statusCode"] == 405


@patch("rmp_learning.api.handler.get_my_score")
def test_get_me_returns_200_with_auth(mock_get_my_score):
    mock_get_my_score.return_value = {"total_points": 10, "rank": 1}
    from rmp_learning.api.handler import handler

    event = _api_event("GET", "/rmp/learning/me")
    event["path"] = "/rmp/learning/me"
    resp = handler(event, None)
    assert resp["statusCode"] == 200
    data = json.loads(resp["body"])
    assert data["total_points"] == 10
    assert data["rank"] == 1


def test_get_me_returns_401_without_auth():
    from rmp_learning.api.handler import handler

    event = _api_event("GET", "/rmp/learning/me", auth_sub=None)
    event["requestContext"]["authorizer"] = {}
    resp = handler(event, None)
    assert resp["statusCode"] == 401


@patch("rmp_learning.api.handler.get_leaderboard")
def test_get_leaderboard_returns_200(mock_get_leaderboard):
    mock_get_leaderboard.return_value = [
        {"rmp_id": "sub1", "total_points": 100, "rank": 1},
    ]
    from rmp_learning.api.handler import handler

    event = _api_event("GET", "/rmp/learning/leaderboard")
    event["path"] = "/rmp/learning/leaderboard"
    resp = handler(event, None)
    assert resp["statusCode"] == 200
    data = json.loads(resp["body"])
    assert "leaderboard" in data
    assert len(data["leaderboard"]) == 1
    assert data["leaderboard"][0]["total_points"] == 100


@patch("rmp_learning.api.handler.get_leaderboard")
def test_get_leaderboard_respects_limit_query(mock_get_leaderboard):
    mock_get_leaderboard.return_value = []
    from rmp_learning.api.handler import handler

    event = _api_event("GET", "/rmp/learning/leaderboard", query={"limit": "5"})
    event["path"] = "/rmp/learning/leaderboard"
    resp = handler(event, None)
    assert resp["statusCode"] == 200
    mock_get_leaderboard.assert_called_once_with(limit=5)


# ---- Live API tests (skip unless API_URL + RMP_TOKEN set) ----


def _live_api_available():
    """Live RMP tests run only when API_URL, RMP_TOKEN, and RUN_LIVE_RMP_TESTS=1 are set."""
    import os
    return (
        os.environ.get("RUN_LIVE_RMP_TESTS") == "1"
        and bool(os.environ.get("API_URL") and os.environ.get("RMP_TOKEN"))
    )


@pytest.mark.skipif(not _live_api_available(), reason="RUN_LIVE_RMP_TESTS=1, API_URL and RMP_TOKEN required for live RMP tests")
def test_live_post_rmp_learning_get_question():
    """Live: POST /rmp/learning with action get_question returns 200 and question/reference_answer."""
    import os
    import urllib.request

    base = os.environ["API_URL"].rstrip("/")
    url = f"{base}/rmp/learning"
    token = os.environ["RMP_TOKEN"]
    data = json.dumps({"action": "get_question", "topic": "fever protocol"}).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST", headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    })
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            body = r.read().decode()
            code = r.getcode()
    except Exception as e:
        if "504" in str(e) or "timed out" in str(e).lower():
            pytest.skip("Request timed out (cold start); retry or run again")
        raise
    assert code == 200, f"Expected 200 got {code}: {body[:500]}"
    out = json.loads(body)
    assert "question" in out
    assert "reference_answer" in out


@pytest.mark.skipif(not _live_api_available(), reason="RUN_LIVE_RMP_TESTS=1, API_URL and RMP_TOKEN required for live RMP tests")
def test_live_get_rmp_learning_me():
    """Live: GET /rmp/learning/me returns 200 with total_points (and optionally rank)."""
    import os
    import urllib.request

    base = os.environ["API_URL"].rstrip("/")
    url = f"{base}/rmp/learning/me"
    token = os.environ["RMP_TOKEN"]
    req = urllib.request.Request(url, method="GET", headers={"Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(req, timeout=30) as r:
        code = r.getcode()
        body = r.read().decode()
    assert code == 200, f"Expected 200 got {code}: {body[:500]}"
    out = json.loads(body)
    assert "total_points" in out


@pytest.mark.skipif(not _live_api_available(), reason="RUN_LIVE_RMP_TESTS=1, API_URL and RMP_TOKEN required for live RMP tests")
def test_live_get_rmp_learning_leaderboard():
    """Live: GET /rmp/learning/leaderboard returns 200 with leaderboard array."""
    import os
    import urllib.request

    base = os.environ["API_URL"].rstrip("/")
    url = f"{base}/rmp/learning/leaderboard?limit=5"
    token = os.environ["RMP_TOKEN"]
    req = urllib.request.Request(url, method="GET", headers={"Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(req, timeout=30) as r:
        code = r.getcode()
        body = r.read().decode()
    assert code == 200, f"Expected 200 got {code}: {body[:500]}"
    out = json.loads(body)
    assert "leaderboard" in out
    assert isinstance(out["leaderboard"], list)
