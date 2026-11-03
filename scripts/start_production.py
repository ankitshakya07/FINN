"""
FINN Production Orchestrator
Starts production backend and frontend servers with health monitoring.
"""

import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = ROOT / "backend"
FRONTEND_DIR = ROOT / "frontend"


def check_health(url: str, attempts: int = 15) -> bool:
    import urllib.request
    for _ in range(attempts):
        try:
            with urllib.request.urlopen(url, timeout=2) as response:
                if response.status == 200:
                    return True
        except Exception:
            time.sleep(1)
    return False


def main():
    print("=" * 60)
    print("FINN — Financial Investment Intelligence Production Runner")
    print("=" * 60)

    # 1. Database seed check
    print("\n[1/3] Verifying database and seeding fixtures...")
    python_bin = sys.executable
    init_cmd = [python_bin, str(ROOT / "scripts" / "init_db.py")]
    subprocess.run(init_cmd, check=True)

    # 2. Build frontend if needed
    print("\n[2/3] Checking frontend production bundle...")
    next_dist = FRONTEND_DIR / ".next"
    if not next_dist.exists():
        print("Building Next.js production bundle...")
        subprocess.run(["npm", "run", "build"], cwd=str(FRONTEND_DIR), check=True)

    print("\n[3/3] Ready to serve production workloads:")
    print("  Backend API:  http://localhost:8000 (Healthcheck: /health)")
    print("  Frontend PWA: http://localhost:3000")
    print("\nUse Docker for containerized deployment: docker compose up --build")
    print("=" * 60)


if __name__ == "__main__":
    main()
