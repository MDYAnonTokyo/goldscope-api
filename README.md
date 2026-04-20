# GoldScope API

GoldScope API is a FastAPI-based gold price intelligence service created for the University of Leeds module `XJCO3011 Web Services and Web Data`. The project combines historical gold price data, analytics endpoints, JWT authentication, and user-managed price alerts in a database-driven web API.

The coursework goal is not only to implement CRUD with a database, but also to demonstrate clear software engineering decisions, documentation quality, testing discipline, and readiness for oral presentation. This repository is structured to support all of those assessment areas.

## Features

- Historical gold price query endpoints backed by SQLAlchemy models
- Analytics endpoints for summary statistics, returns, volatility, drawdown, anomaly detection, and market regime classification
- JWT-based authentication with registration and login
- Full CRUD for user-owned gold price alerts
- OpenAPI schema and interactive Swagger UI
- Automated tests with `pytest`
- Generated submission assets including API documentation PDF, technical report PDF, presentation deck, and visual report

## Tech Stack

- FastAPI
- SQLAlchemy 2.0
- Alembic
- Pydantic Settings
- JWT authentication
- SQLite for local development
- Render Postgres for planned cloud deployment
- pytest
- reportlab
- python-pptx

## Repository Structure

```text
src/goldscope/         Application package
alembic/               Database migration configuration
data/raw/              Gold price CSV snapshot used for local import
docs/                  Markdown source files for documentation and report
docs/generated/        Generated PDF, PPTX, OpenAPI, and visual assets
scripts/               Utility scripts for bootstrap, export, and asset generation
tests/                 Automated test suite
render.yaml            Render deployment blueprint
```

## Local Setup

### Prerequisites

- Python 3.11 or newer
- `uv` installed locally

### 1. Create the environment file

```powershell
Copy-Item .env.example .env
```

### 2. Install dependencies

```powershell
$env:UV_CACHE_DIR=(Resolve-Path .uv-cache)
uv sync
```

### 3. Bootstrap the local database

```powershell
uv run python scripts/bootstrap_db.py
```

This creates the local SQLite database file `goldscope.db` and imports the bundled gold price dataset if the database is empty.

### 4. Start the API server

```powershell
uv run uvicorn goldscope.main:app --reload
```

### 5. Open the local application

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`
- Health check: `http://127.0.0.1:8000/health`

## Environment Variables

The main settings provided in `.env.example` are:

- `DATABASE_URL`
- `SECRET_KEY`
- `ACCESS_TOKEN_EXPIRE_MINUTES`
- `TOKEN_ISSUER`
- `TOKEN_AUDIENCE`
- `GOLD_PRICES_SOURCE_NAME`
- `GOLD_PRICES_SOURCE_URL`
- `PUBLIC_BASE_URL`

## Database Notes

- Local development uses SQLite through `goldscope.db`.
- The included dataset is stored in [data/raw/gold_prices_monthly.csv](data/raw/gold_prices_monthly.csv).
- The seed dataset is based on the public DataHub gold prices snapshot, referenced in `.env.example` as a derived public source.
- The project includes Alembic configuration and an initial migration in [alembic/versions](alembic/versions).
- The intended production deployment target is PostgreSQL on Render.

## API Overview

### Public endpoints

- `GET /health`
- `GET /gold/prices`
- `GET /gold/prices/latest`
- `GET /gold/analytics/summary`
- `GET /gold/analytics/returns`
- `GET /gold/analytics/volatility`
- `GET /gold/analytics/drawdown`
- `GET /gold/analytics/anomalies`
- `GET /gold/analytics/regime`

### Authentication endpoints

- `POST /auth/register`
- `POST /auth/login`

### Protected alert endpoints

- `POST /alerts`
- `GET /alerts`
- `GET /alerts/{id}`
- `PATCH /alerts/{id}`
- `DELETE /alerts/{id}`

## Testing

Run the automated test suite with:

```powershell
$env:UV_CACHE_DIR=(Resolve-Path .uv-cache)
uv run pytest
```

At the time of local verification, the suite passed successfully with `12 passed`.

## Documentation and Submission Assets

### Markdown source files

- [API documentation](docs/api_documentation.md)
- [Technical report](docs/technical_report.md)
- [GenAI declaration](docs/genai_declaration.md)
- [Presentation outline](docs/presentation_outline.md)

### Generated assets

- [OpenAPI JSON](docs/generated/openapi.json)
- [API documentation PDF](docs/generated/api_documentation.pdf)
- [Technical report PDF](docs/generated/technical_report.pdf)
- [Presentation deck](docs/generated/goldscope_presentation.pptx)
- [Visual report](docs/generated/visual_report.html)

### Regenerate submission assets

```powershell
uv run python scripts/export_openapi.py
uv run python scripts/generate_submission_assets.py
uv run python scripts/generate_visual_report.py
```

## Deployment

The repository includes a Render deployment blueprint in [render.yaml](render.yaml).

Recommended Render Free stack for coursework:

- Web service: Render Free Web Service
- Database: Render Free Postgres

Current status:

- Local execution is complete
- Deployment configuration is prepared
- Public GitHub hosting and public Render deployment still need to be completed by the repository owner

Render-specific notes:

- The application is configured to use PostgreSQL on Render instead of SQLite.
- On Render Free, database migrations run at service startup because `preDeployCommand` is not available on the free web service tier.
- The app seeds gold price data automatically on first startup if the database is empty.
- A PostgreSQL connection string from Render is normalized to a SQLAlchemy-compatible `postgresql+psycopg://` URL.
- `healthCheckPath` is set to `/health`, which is a better fit for Render web service health checks.
- Free Render Postgres is suitable for coursework demos, but it has time and storage limits in Render's free tier.

## Submission Checklist

Before final submission, make sure the following items are completed:

- Push this repository to a public GitHub repository
- Maintain visible commit history
- Upload the generated PDF documentation files to GitHub
- Add the public repository link, API documentation link, and slide link to the final report PDF
- Attach exported GenAI conversation logs as supplementary material
- Deploy the API publicly if you want to strengthen the project for higher mark bands

## Coursework Context

This project was designed to exceed the minimum pass criteria by including:

- a relational database model
- full CRUD through authenticated alert management
- more than four HTTP endpoints
- structured JSON responses and industry-standard status codes
- automated testing
- technical documentation and presentation assets
- a deployment path suitable for public demonstration

## References

- FastAPI documentation: https://fastapi.tiangolo.com/
- SQLAlchemy documentation: https://docs.sqlalchemy.org/
- Alembic documentation: https://alembic.sqlalchemy.org/
- Render documentation: https://render.com/docs
- DataHub gold prices dataset: https://datahub.io/core/gold-prices
