from __future__ import annotations

from goldscope.db.bootstrap import bootstrap_database


if __name__ == "__main__":
    bootstrap_database()
    print("Database bootstrapped successfully.")
