from __future__ import annotations

import json
from pathlib import Path

from goldscope.main import app


if __name__ == "__main__":
    target = Path("docs/generated/openapi.json")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(app.openapi(), indent=2), encoding="utf-8")
    print(f"OpenAPI schema exported to {target}")
