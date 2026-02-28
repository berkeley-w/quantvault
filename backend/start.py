import os
import sys
import json
import uvicorn
# #region agent log
try:
    import jose
    _logpath = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "debug-d879a6.log"))
    with open(_logpath, "a") as _f:
        _f.write(json.dumps({"sessionId": "d879a6", "runId": "post-fix", "hypothesisId": "H1", "location": "start.py:import jose", "message": "jose import ok", "data": {"executable": sys.executable}, "timestamp": __import__("time").time() * 1000}) + "\n")
except Exception as e:
    _logpath = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "debug-d879a6.log"))
    with open(_logpath, "a") as f:
        f.write(json.dumps({"sessionId": "d879a6", "hypothesisId": "H1", "location": "start.py:import jose", "message": "jose import check", "data": {"error": type(e).__name__, "error_msg": str(e), "executable": sys.executable}, "timestamp": __import__("time").time() * 1000}) + "\n")
    raise
# #endregion
from app.database import init_db

init_db()

import seed  # this runs the seeding code on import

from main import app

if __name__ == "__main__":
    import logging
    logger = logging.getLogger(__name__)
    logger.info("Server starting at http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)