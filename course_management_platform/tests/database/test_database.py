"""Simple database connectivity tests."""
import sys
from pathlib import Path

from sqlalchemy import text

# Ensure backend package is importable
sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))

from app.database import engine


def test_engine_exists():
    assert engine is not None
    assert engine.url is not None


def test_select_one():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        assert result.scalar() == 1
