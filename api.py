"""
ReviewSense - Root API Launcher
Forwards execution to backend/api.py for full root backward compatibility.
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
BACKEND_DIR = PROJECT_ROOT / "backend"

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

# Import app and key objects from backend.api
from backend.api import (
    app,
    root,
    health,
    predict_single,
    predict_batch,
    run_prediction,
    run_batch,
    PREDICTOR_IS_REAL,
)

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("api:app", host="0.0.0.0", port=port, reload=True)
