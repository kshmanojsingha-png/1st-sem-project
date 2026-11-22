"""
ReviewSense - Root Streamlit Launcher
Forwards execution to frontend/app.py for backwards compatibility
"""
import runpy
import sys
from pathlib import Path

FRONTEND_DIR = Path(__file__).resolve().parent / "frontend"
if str(FRONTEND_DIR) not in sys.path:
    sys.path.insert(0, str(FRONTEND_DIR))

target = FRONTEND_DIR / "app.py"
runpy.run_path(str(target), run_name="__main__")
