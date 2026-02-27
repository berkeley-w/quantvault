import os
import uvicorn
import json, time, sys
from models import init_db

# region agent log
try:
    _log_path = os.path.join(os.path.dirname(__file__), "..", "debug-e51511.log")
    with open(_log_path, "a", encoding="utf-8") as _f:
        _f.write(
            json.dumps(
                {
                    "sessionId": "e51511",
                    "runId": "pre-fix",
                    "hypothesisId": "H1",
                    "location": "backend/start.py:6",
                    "message": "start.py entry",
                    "data": {
                        "sys_executable": sys.executable,
                        "virtual_env": os.getenv("VIRTUAL_ENV"),
                    },
                    "timestamp": int(time.time() * 1000),
                }
            )
            + "\n"
        )
except Exception:
    pass
# endregion

init_db()

import seed  # this runs the seeding code on import

from main import app

if __name__ == "__main__":
    print("Server starting at http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)