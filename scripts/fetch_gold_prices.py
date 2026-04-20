from __future__ import annotations

import urllib.request
from pathlib import Path

DATA_URL = "https://datahub.io/core/gold-prices/_r/-/data/monthly-processed.csv"


def fetch_gold_prices(output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(DATA_URL) as response:
        output_path.write_bytes(response.read())
    return output_path


if __name__ == "__main__":
    target = Path("data/raw/gold_prices_monthly.csv")
    saved_path = fetch_gold_prices(target)
    print(f"Saved gold price data to {saved_path}")
