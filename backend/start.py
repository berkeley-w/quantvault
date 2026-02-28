import os

import uvicorn

from app.database import init_db

init_db()

import seed  # runs seeding on import

from main import app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)