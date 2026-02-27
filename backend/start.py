import os
import uvicorn

from models import init_db

init_db()

import seed  # this runs the seeding code on import

from main import app

if __name__ == "__main__":
    print("Server starting at http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)