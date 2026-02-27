import os
import uvicorn

# region agent log
import json
import sys
from time import time as _time

try:
    _log_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "debug-bb96b9.log",
    )
    with open(_log_path, "a", encoding="utf-8") as _f:
        _f.write(
            json.dumps(
                {
                    "sessionId": "bb96b9",
                    "runId": "pre-fix",
                    "hypothesisId": "H1-H3",
                    "location": "start.py:before_models_import",
                    "message": "Before importing models in start.py",
                    "data": {
                        "cwd": os.getcwd(),
                        "sysPath": sys.path,
                    },
                    "timestamp": int(_time() * 1000),
                }
            )
            + "\n"
        )
except Exception:
    # Logging failure should not prevent app start
    pass
# endregion

from models import init_db

init_db()

import seed  # this runs the seeding code on import

from main import app

if __name__ == "__main__":
    print("Server starting at http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)