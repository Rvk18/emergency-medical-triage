"""Pytest configuration and shared fixtures."""

import sys
from pathlib import Path

# Add src to path so `import triage` works when running pytest from project root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
