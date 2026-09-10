"""Pytest configuration and shared fixtures."""
import sys
from pathlib import Path

# Add project root to sys.path so imports work
ROOT = Path(__file__).parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
