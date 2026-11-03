from pathlib import Path
import sys

BACKEND = Path(__file__).resolve().parents[1] / "backend"
sys.path.insert(0, str(BACKEND))

from app.db import init_db  # noqa: E402
from app.fundamentals import load_fundamentals_fixture  # noqa: E402
from app.promised_vs_delivered import load_commitments_fixture  # noqa: E402

if __name__ == "__main__":
    db_file = str(BACKEND / "finn.db")
    init_db(db_file)
    print("Initialised backend/finn.db schema")
    try:
        load_fundamentals_fixture()
        print("Loaded fundamentals fixtures")
    except Exception as e:
        print(f"Fundamentals fixture notice: {e}")
    try:
        load_commitments_fixture()
        print("Loaded promised vs delivered fixtures")
    except Exception as e:
        print(f"Commitments fixture notice: {e}")
    print("Database ready for production deployment.")

