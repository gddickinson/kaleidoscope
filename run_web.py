"""Start the Music-Reactive Kaleidoscope web app on http://127.0.0.1:8224 (local only).

    pip install -r requirements-web.txt
    python run_web.py [--port 8224]
"""
import argparse

import uvicorn

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--port", type=int, default=8224)
    a = ap.parse_args()
    print(f"Kaleidoscope web app: http://127.0.0.1:{a.port}")
    uvicorn.run("src.web.app:app", host="127.0.0.1", port=a.port)
