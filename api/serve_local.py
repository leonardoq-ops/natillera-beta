"""Local-only dev runner: adds ../app to sys.path (mirrors what the
Dockerfile's COPY does for the real deploy) and points TURSO_DATABASE_URL
at a local sqlite file so this can run without real Turso/Drive/Cowork
credentials. Not used in production - Cloud Run runs the Dockerfile."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "app"))
os.environ.setdefault("TURSO_DATABASE_URL",
                       os.path.join(os.path.dirname(__file__), "..", "app", "local_natillera.db"))
os.environ.setdefault("UPLOAD_API_KEY", "local-dev-key")

import uvicorn  # noqa: E402

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080)
