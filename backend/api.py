import sys
from pathlib import Path

# Add project root to sys.path so ml, simran_all_in_one, etc. can be resolved
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Import all endpoints, objects, and FastAPI app instance from root api
from api import *
from api import app
