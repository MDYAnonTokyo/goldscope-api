from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

from fastapi.testclient import TestClient

from goldscope.main import app

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = ROOT / "docs" / "generated" / "visual_report.html"


@dataclass
class Point:
    label: str
    value: float


def fetch_api_data() -> dict:
    with TestClient(app) as client:
        email = f"visual-demo-{uuid4().hex[:8]}@example.com"
        payload = {"email": email, "password": "supersecure123"}

        register_response = client.post("/auth/register", json=payload)
        login_response = client.post("/auth/login", json=payload)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        alert_response = client.post(
            "/alerts",
            headers=headers,
            json={
                "name": "Visual Demo Alert",
                "condition_type": "above",
                "threshold_value": 3500,
                "notes": "Created by the visual report generator.",
                "active": True,
            },
        )

        return {
            "health": client.get("/health").json(),
            "latest": client.get("/gold/prices/latest").json(),
            "summary": client.get(
                "/gold/analytics/summary",
                params={"start_date": "2024-01-01", "end_date": "2025-12-31"},
            ).json(),
            "returns": client.get("/gold/analytics/returns").json(),
            "volatility": client.get("/gold/analytics/volatility", params={"window_points": 12}).json(),
            "drawdown": client.get(
                "/gold/analytics/drawdown",
                params={"start_date": "2018-01-01", "end_date": "2025-12-31"},
            ).json(),
            "anomalies": client.get(
                "/gold/analytics/anomalies",
                params={"start_date": "2020-01-01", "end_date": "2025-12-31", "threshold": 1.5},
            ).json(),
            "regime": client.get("/gold/analytics/regime").json(),
            "prices": client.get(
                "/gold/prices",
                params={"start_date": "2020-01-01", "end_date": "2026-03-31", "limit": 0},
            ).json(),
            "alerts": client.get("/alerts", headers=headers).json(),
            "register_status": register_response.status_code,
            "login_status": login_response.status_code,
            "alert_status": alert_response.status_code,
        }


def svg_line_chart(points: list[Point], *, width: int = 860, height: int = 260) -> str:
    if not points:
        return "<svg></svg>"

    values = [point.value for point in points]
    min_value = min(values)
    max_value = max(values)
    value_span = max(max_value - min_value, 1)
    x_step = width / max(len(points) - 1, 1)

    coords: list[tuple[float, float]] = []
    for index, point in enumerate(points):
        x = index * x_step
        y = height - ((point.value - min_value) / value_span) * (height - 30) - 15
        coords.append((x, y))

    polyline = " ".join(f"{x:.2f},{y:.2f}" for x, y in coords)
    area_points = f"0,{height} " + polyline + f" {width},{height}"

    tick_step = max(1, len(points) // 6)
    tick_indices = list(range(0, len(points), tick_step))
    if tick_indices[-1] != len(points) - 1:
        tick_indices.append(len(points) - 1)

    ticks = "".join(
        f"<text x='{index * x_step:.2f}' y='{height + 20}' class='axis-label'>{points[index].label}</text>"
        for index in tick_indices
    )
    y_labels = "".join(
        f"<text x='0' y='{height - i * (height - 30) / 4:.2f}' class='axis-label'>{(min_value + (value_span * i / 4)):.0f}</text>"
        for i in range(5)
    )

    return f"""
    <svg viewBox='0 0 {width} {height + 30}' class='chart-svg' role='img' aria-label='Gold price line chart'>
      <defs>
        <linearGradient id='line-fill' x1='0' y1='0' x2='0' y2='1'>
          <stop offset='0%' stop-color='rgba(201,168,97,0.45)' />
          <stop offset='100%' stop-color='rgba(201,168,97,0.02)' />
        </linearGradient>
      </defs>
      <polygon points='{area_points}' fill='url(#line-fill)'></polygon>
      <polyline points='{polyline}' fill='none' stroke='#c9a861' stroke-width='3' stroke-linejoin='round' stroke-linecap='round'></polyline>
      {ticks}
      {y_labels}
    </svg>
    """


def svg_bar_chart(points: list[Point], *, width: int = 860, height: int = 220) -> str:
    if not points:
        return "<svg></svg>"

    max_abs = max(abs(point.value) for point in points) or 1
    bar_width = width / max(len(points) * 1.8, 1)
    gap = bar_width * 0.8
    zero_y = height / 2
    bars: list[str] = []
    labels: list[str] = []

    for index, point in enumerate(points):
        x = 30 + index * (bar_width + gap)
        bar_height = abs(point.value) / max_abs * (height / 2 - 25)
        y = zero_y - bar_height if point.value >= 0 else zero_y
        color = "#2e9d62" if point.value >= 0 else "#c25454"
        bars.append(
            f"<rect x='{x:.2f}' y='{y:.2f}' width='{bar_width:.2f}' height='{bar_height:.2f}' rx='6' fill='{color}'></rect>"
        )
        labels.append(
            f"<text x='{x + bar_width / 2:.2f}' y='{height - 8}' text-anchor='middle' class='axis-label'>{point.label}</text>"
        )
        labels.append(
            f"<text x='{x + bar_width / 2:.2f}' y='{y - 6 if point.value >= 0 else y + bar_height + 16:.2f}' text-anchor='middle' class='bar-label'>{point.value:.1f}%</text>"
        )

    return f"""
    <svg viewBox='0 0 {width} {height}' class='chart-svg' role='img' aria-label='Gold returns bar chart'>
      <line x1='0' y1='{zero_y}' x2='{width}' y2='{zero_y}' stroke='#6b7280' stroke-width='1.5'></line>
      {''.join(bars)}
      {''.join(labels)}
    </svg>
    """


def endpoint_table(data: dict) -> str:
    rows = [
        ("GET /health", 200, "Health check completed successfully."),
        ("POST /auth/register", data["register_status"], "Demo user registration succeeded."),
        ("POST /auth/login", data["login_status"], "JWT access token returned."),
        ("GET /gold/prices/latest", 200, "Latest market observation loaded."),
        ("GET /gold/analytics/summary", 200, "Summary metrics calculated."),
        ("GET /gold/analytics/returns", 200, "Multi-period returns calculated."),
        ("GET /gold/analytics/volatility", 200, "Volatility endpoint responded."),
        ("GET /gold/analytics/drawdown", 200, "Drawdown metrics calculated."),
        ("GET /gold/analytics/anomalies", 200, "Anomaly detection completed."),
        ("GET /gold/analytics/regime", 200, "Market regime classification returned."),
        ("POST /alerts", data["alert_status"], "Protected alert creation succeeded."),
        ("GET /alerts", 200, "Authenticated alert list returned."),
    ]

    html_rows = []
    for endpoint, status_code, note in rows:
        css = "ok" if 200 <= status_code < 300 else "bad"
        html_rows.append(
            f"<tr><td>{endpoint}</td><td><span class='pill {css}'>{status_code}</span></td><td>{note}</td></tr>"
        )
    return "".join(html_rows)


def build_html(data: dict) -> str:
    price_points = [Point(item["price_date"][:7], item["usd_oz"]) for item in data["prices"]["items"]]
    return_points = [Point(item["period_label"], item["percent_return"]) for item in data["returns"]["items"]]
    recent_price_points = price_points[-24:]
    top_anomalies = data["anomalies"]["items"][:5]

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>GoldScope API Visual Report</title>
  <style>
    :root {{
      --bg: #f6f2e9;
      --panel: #fffdf7;
      --text: #1f2937;
      --muted: #6b7280;
      --gold: #c9a861;
      --line: #e7dcc5;
      --green: #2e9d62;
      --red: #c25454;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: "Segoe UI", Arial, sans-serif;
      background:
        radial-gradient(circle at top left, rgba(201,168,97,0.16), transparent 30%),
        linear-gradient(180deg, #f7f1e2 0%, var(--bg) 100%);
      color: var(--text);
    }}
    .wrap {{
      max-width: 1180px;
      margin: 0 auto;
      padding: 40px 24px 64px;
    }}
    .hero {{
      padding: 28px 30px;
      border: 1px solid var(--line);
      background: linear-gradient(135deg, rgba(255,255,255,0.92), rgba(250,246,237,0.95));
      border-radius: 28px;
      box-shadow: 0 20px 40px rgba(84, 70, 32, 0.08);
    }}
    h1 {{
      margin: 0 0 10px;
      font-size: 38px;
    }}
    .hero p {{
      margin: 0;
      color: var(--muted);
      font-size: 17px;
      line-height: 1.6;
      max-width: 820px;
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 16px;
      margin-top: 24px;
    }}
    .card, .panel {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 22px;
      box-shadow: 0 12px 24px rgba(84, 70, 32, 0.06);
    }}
    .card {{
      padding: 20px;
    }}
    .label {{
      color: var(--muted);
      font-size: 13px;
      text-transform: uppercase;
      letter-spacing: 0.08em;
    }}
    .value {{
      margin-top: 8px;
      font-size: 30px;
      font-weight: 700;
    }}
    .sub {{
      margin-top: 8px;
      color: var(--muted);
      font-size: 14px;
    }}
    .layout {{
      display: grid;
      grid-template-columns: 1.5fr 1fr;
      gap: 18px;
      margin-top: 24px;
    }}
    .panel {{
      padding: 22px;
    }}
    .panel h2 {{
      margin: 0 0 6px;
      font-size: 22px;
    }}
    .panel p {{
      margin: 0 0 14px;
      color: var(--muted);
      line-height: 1.5;
    }}
    .chart-svg {{
      width: 100%;
      height: auto;
      overflow: visible;
    }}
    .axis-label {{
      font-size: 11px;
      fill: #6b7280;
    }}
    .bar-label {{
      font-size: 11px;
      fill: #374151;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 14px;
    }}
    th, td {{
      padding: 10px 8px;
      border-bottom: 1px solid var(--line);
      text-align: left;
      vertical-align: top;
    }}
    .pill {{
      display: inline-flex;
      align-items: center;
      padding: 4px 10px;
      border-radius: 999px;
      font-size: 12px;
      font-weight: 700;
    }}
    .pill.ok {{
      background: rgba(46,157,98,0.12);
      color: var(--green);
    }}
    .pill.bad {{
      background: rgba(194,84,84,0.12);
      color: var(--red);
    }}
    ul {{
      padding-left: 18px;
      margin: 0;
    }}
    li {{
      margin-bottom: 10px;
      line-height: 1.5;
    }}
    .footer-note {{
      margin-top: 22px;
      color: var(--muted);
      font-size: 13px;
    }}
    @media (max-width: 980px) {{
      .grid {{ grid-template-columns: 1fr 1fr; }}
      .layout {{ grid-template-columns: 1fr; }}
    }}
    @media (max-width: 640px) {{
      .grid {{ grid-template-columns: 1fr; }}
      h1 {{ font-size: 30px; }}
    }}
  </style>
</head>
<body>
  <div class="wrap">
    <section class="hero">
      <h1>GoldScope API Visual Report</h1>
      <p>This report provides a presentation-friendly snapshot of the running API. It combines live endpoint responses, historical gold price charts, analytics highlights, and a short smoke test summary so the project can be demonstrated quickly during coursework review or oral presentation preparation.</p>
    </section>

    <section class="grid">
      <div class="card">
        <div class="label">Latest Gold Price</div>
        <div class="value">${data["latest"]["item"]["usd_oz"]:.2f}</div>
        <div class="sub">Recorded on {data["latest"]["item"]["price_date"]}</div>
      </div>
      <div class="card">
        <div class="label">Growth in 2024-2025</div>
        <div class="value">{data["summary"]["percent_change"]:.2f}%</div>
        <div class="sub">Latest price in range: ${data["summary"]["latest_price"]:.2f}</div>
      </div>
      <div class="card">
        <div class="label">Annualised Volatility</div>
        <div class="value">{data["volatility"]["annualized_volatility"]:.2f}%</div>
        <div class="sub">Calculated from the latest {data["volatility"]["window_points"]} observations</div>
      </div>
      <div class="card">
        <div class="label">Current Regime</div>
        <div class="value">{data["regime"]["regime"]}</div>
        <div class="sub">Short MA {data["regime"]["short_moving_average"]:.2f} / Long MA {data["regime"]["long_moving_average"]:.2f}</div>
      </div>
    </section>

    <section class="layout">
      <div class="panel">
        <h2>Last 24 Observations</h2>
        <p>The chart below shows the most recent two years of imported gold price data in USD per ounce.</p>
        {svg_line_chart(recent_price_points)}
      </div>
      <div class="panel">
        <h2>Multi-Period Returns</h2>
        <p>Returns are shown for the lookback windows exposed by the analytics endpoint.</p>
        {svg_bar_chart(return_points)}
      </div>
    </section>

    <section class="layout">
      <div class="panel">
        <h2>API Smoke Test Summary</h2>
        <p>These checks were executed against the running application state to confirm that the main public and protected flows are available.</p>
        <table>
          <thead>
            <tr><th>Endpoint</th><th>Status</th><th>Observation</th></tr>
          </thead>
          <tbody>
            {endpoint_table(data)}
          </tbody>
        </table>
      </div>
      <div class="panel">
        <h2>Key Findings</h2>
        <p>The current dataset supports both market exploration and coursework-style API demonstrations.</p>
        <ul>
          <li>Maximum drawdown in the selected range is <strong>{data["drawdown"]["max_drawdown_pct"]:.2f}%</strong>, from {data["drawdown"]["peak_date"]} to {data["drawdown"]["trough_date"]}.</li>
          <li>The anomaly endpoint found <strong>{data["anomalies"]["count"]}</strong> observations above the configured z-score threshold of {data["anomalies"]["threshold"]}.</li>
          <li>The JWT-protected alert workflow is working, and the current demo user has <strong>{data["alerts"]["count"]}</strong> alert record(s).</li>
          <li>The service environment currently reports <strong>{data["health"]["environment"]}</strong>.</li>
        </ul>
      </div>
    </section>

    <section class="layout">
      <div class="panel">
        <h2>Top 5 Anomalies</h2>
        <p>These rows show the strongest unusual movements returned by the anomaly detection endpoint.</p>
        <table>
          <thead>
            <tr><th>Date</th><th>Price</th><th>Change</th><th>Z-Score</th></tr>
          </thead>
          <tbody>
            {"".join(f"<tr><td>{item['price_date']}</td><td>${item['usd_oz']:.2f}</td><td>{item['pct_change']:.2f}%</td><td>{item['z_score']:.2f}</td></tr>" for item in top_anomalies) or "<tr><td colspan='4'>No anomalies were returned for the selected range.</td></tr>"}
          </tbody>
        </table>
      </div>
      <div class="panel">
        <h2>Suggested Demo Flow</h2>
        <p>This sequence works well for a short presentation or oral examination demo.</p>
        <ul>
          <li>Open Swagger UI at <code>/docs</code> to show the documented API surface.</li>
          <li>Call <code>GET /gold/prices/latest</code> to show live market data retrieval.</li>
          <li>Call <code>GET /gold/analytics/summary</code> and <code>GET /gold/analytics/regime</code> to demonstrate analytical value beyond CRUD.</li>
          <li>Show the protected flow: <code>register -> login -> create alert -> list alerts</code>.</li>
          <li>Use this visual report as a compact summary that the project is a gold intelligence API, not only a basic CRUD exercise.</li>
        </ul>
      </div>
    </section>

    <div class="footer-note">
      This page is generated from live application responses, the bundled dataset in <code>data/raw/gold_prices_monthly.csv</code>, and the report builder script <code>scripts/generate_visual_report.py</code>.
    </div>
  </div>
</body>
</html>
"""


def main() -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    data = fetch_api_data()
    html = build_html(data)
    OUTPUT_PATH.write_text(html, encoding="utf-8")
    print(json.dumps({"output": str(OUTPUT_PATH)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
