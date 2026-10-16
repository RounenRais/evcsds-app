"""Testler `backend/` klasörünü kök kabul eder; onu modül yoluna ekler."""

import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parent.parent / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))
