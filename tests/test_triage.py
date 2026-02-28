"""Tests for triage models and handler."""

import json

import pytest

from triage.models.triage import SeverityLevel, TriageRequest, TriageResult


def test_triage_request_valid():
    """TriageRequest accepts valid input."""
    r = TriageRequest(symptoms=["chest pain"], vitals={"bp": 180})
    assert r.symptoms == ["chest pain"]
    assert r.vitals == {"bp": 180}


def test_triage_request_min_symptoms():
    """TriageRequest requires at least one symptom."""
    with pytest.raises(Exception):
        TriageRequest(symptoms=[], vitals={})


def test_triage_result_valid():
    """TriageResult accepts valid severity and confidence."""
    t = TriageResult(
        severity="high",
        confidence=0.9,
        recommendations=["Seek care"],
        force_high_priority=False,
    )
    assert t.severity == "high"
    assert t.confidence == 0.9


def test_triage_result_severity_enum():
    """TriageResult severity must be critical/high/medium/low."""
    for sev in ["critical", "high", "medium", "low"]:
        t = TriageResult(severity=sev, confidence=0.8, recommendations=[])
        assert t.severity == sev


def test_triage_result_confidence_bounds():
    """TriageResult confidence must be 0-1."""
    TriageResult(severity="low", confidence=0.0, recommendations=[])
    TriageResult(severity="high", confidence=1.0, recommendations=[])
    with pytest.raises(Exception):
        TriageResult(severity="low", confidence=1.5, recommendations=[])


def test_handler_rejects_get():
    """Handler returns 405 for GET."""
    from triage.api.handler import handler

    r = handler({"httpMethod": "GET"}, None)
    assert r["statusCode"] == 405


def test_handler_validates_body():
    """Handler returns 400 for invalid body."""
    from triage.api.handler import handler

    r = handler({"httpMethod": "POST", "body": '{"symptoms": []}'}, None)
    assert r["statusCode"] == 400
