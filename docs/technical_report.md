# GoldScope API Technical Report

## 1. Project Aim

GoldScope API is a data-driven web API for historical gold prices, market analytics, and user-managed price alerts. It was developed for `XJCO3011 Web Services and Web Data` with the aim of exceeding a minimum CRUD submission by combining a relational database, authenticated resources, analytical endpoints, automated testing, documentation, and public deployment.

The project theme was chosen deliberately. Gold prices provide a recognisable real-world context and support stronger discussion in the oral examination than a generic task manager. The dataset also makes it possible to justify analytical endpoints such as volatility, drawdown, anomaly detection, and market regime classification.

## 2. Technology Choices and Architecture

FastAPI was chosen instead of Flask because it provides automatic OpenAPI generation, strong request validation, and a clean development workflow for API-first projects. SQLAlchemy 2.0 was used for model definition and database portability, while Alembic was included for explicit schema management. JWT bearer authentication was selected to separate public resources from user-owned alert resources in a way that is easy to explain and demonstrate.

The codebase follows a layered design. Routers define the HTTP interface, schemas define request and response contracts, models define persistent entities, and service modules contain business logic. This separation keeps endpoint handlers small, improves testability, and avoids a single-file coursework prototype.

## 3. Database and Data Strategy

The database contains three tables: `users`, `gold_prices`, and `price_alerts`. `users` stores account identity and password hashes, `gold_prices` stores the historical monthly dataset used by the public API, and `price_alerts` stores authenticated user-defined rules such as price-above or price-below conditions. This design satisfies the database-backed CRUD requirement while also demonstrating ownership and access control.

SQLite was used for local development because it is fast to set up and reliable for offline marking. PostgreSQL on Render was used for public deployment to provide a more realistic production-style environment. Historical gold prices are imported from the bundled file `data/raw/gold_prices_monthly.csv`. A local snapshot was preferred to a live commercial feed because it guarantees reproducibility, avoids API-key risk, and makes the submission easier for examiners to run.

## 4. API Design, Validation, and Error Handling

The API exposes public endpoints for price queries and analytics, plus authenticated endpoints for alert CRUD. Public routes include `/gold/prices`, `/gold/prices/latest`, and analytical endpoints for summary statistics, returns, volatility, drawdown, anomalies, and regime classification. Protected routes under `/alerts` implement create, read, update, and delete operations for the current user.

The service returns JSON consistently and uses standard HTTP status codes including `200`, `201`, `204`, `401`, `404`, `409`, and `422`. Validation is handled through Pydantic schemas and constrained query parameters, which makes incorrect payloads fail predictably. This was important because the brief explicitly requires appropriate JSON responses and correct status codes rather than only working happy paths.

## 5. Testing and Deployment

Testing was implemented with `pytest` and FastAPI `TestClient`. The suite covers registration, login, duplicate account conflicts, protected-route authorization, alert CRUD, price queries, analytical endpoints, and validation failures. This approach demonstrates both happy-path behavior and important failure cases without inflating the report with low-value test counts.

The repository includes reproducible local setup, OpenAPI export, generated PDFs, and a public Render deployment at `https://goldscope-api.onrender.com`. This deployment strengthens the project against higher marking bands because the API can be demonstrated through a live `/health` endpoint and Swagger interface rather than only through localhost.

## 6. Challenges, Limitations, and Future Work

The main design challenge was balancing originality against delivery risk. A live metals API or forecasting model would appear more ambitious, but it would also increase dependency risk close to the deadline. The final design therefore prioritised a stable core with clear analytical value, test coverage, and a deployment story that could be defended confidently in the oral examination.

The current version does not ingest live commercial data, send real notifications, or include predictive modelling. Future work would focus on scheduled live data updates, alert delivery by email or SMS, and broader correlation analysis with exchange rates, inflation, or interest-rate data.

## 7. Generative AI Use

Generative AI was used as a development support tool for planning, design exploration, documentation drafting, test-scenario generation, and implementation support. All outputs were reviewed and edited manually before inclusion in the project. Final responsibility for the code, documentation, testing, and oral defence remains with the student. A representative exported conversation log is included as `docs/generated/genai_conversation_logs.pdf`, and the original shared conversation record is available at `https://chatgpt.com/share/69e72e13-3380-839e-a4c9-9106fd8a84f2`. The PDF should be attached as supplementary material in the final Minerva submission.

## 8. Submission Links

- GitHub repository: https://github.com/MDYAnonTokyo/goldscope-api
- Public API base URL: https://goldscope-api.onrender.com
- Public Swagger UI: https://goldscope-api.onrender.com/docs
- API documentation PDF: https://github.com/MDYAnonTokyo/goldscope-api/blob/main/docs/generated/api_documentation.pdf
- Technical report PDF: https://github.com/MDYAnonTokyo/goldscope-api/blob/main/docs/generated/technical_report.pdf
- Presentation slides: https://github.com/MDYAnonTokyo/goldscope-api/blob/main/docs/generated/goldscope_presentation.pptx
- GenAI conversation logs PDF: https://github.com/MDYAnonTokyo/goldscope-api/blob/main/docs/generated/genai_conversation_logs.pdf
- Shared GenAI conversation link: https://chatgpt.com/share/69e72e13-3380-839e-a4c9-9106fd8a84f2

## References

- FastAPI. https://fastapi.tiangolo.com/
- SQLAlchemy. https://docs.sqlalchemy.org/
- Alembic. https://alembic.sqlalchemy.org/
- Render Documentation. https://render.com/docs
- DataHub Gold Prices Dataset. https://datahub.io/core/gold-prices
