"""Verify package imports."""

def test_triage_package_imports():
    """Ensure triage package can be imported."""
    import triage
    assert triage.__version__ == "0.1.0"
