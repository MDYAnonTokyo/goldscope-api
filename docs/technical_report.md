# GoldScope API Technical Report

## 1. Introduction

GoldScope API is a data-driven web API built around historical gold price information. The project was designed for the module `XJCO3011 Web Services and Web Data` and aims to satisfy the coursework requirements while also demonstrating stronger engineering practice than a minimum-pass CRUD submission.

The final system provides database-backed endpoints for historical gold prices, analytical endpoints for market interpretation, JWT-based authentication, and full CRUD operations for user-owned price alerts. In addition to the API itself, the repository includes tests, documentation, generated submission assets, and deployment configuration.

## 2. Project Objective and Rationale

The core idea was to build a gold price intelligence API rather than a generic task manager or notes application. Gold was chosen because it offers a recognisable real-world financial context and produces a richer design space for analytics. Historical price series make it possible to discuss volatility, drawdown, abnormal movements, and market regimes, which helps the project demonstrate curiosity and independent exploration beyond simple CRUD.

This theme also supports a stronger oral presentation. It is easier to justify why the system exists, why the analytical endpoints are useful, and why the data model has been separated into public market data and user-specific alert resources.

## 3. Technology Choices and Justification

FastAPI was selected as the main framework instead of Flask because it provides a modern API development workflow with automatic OpenAPI generation, strong request validation through type hints, and a clean developer experience for coursework-scale services. These features reduce boilerplate and make it easier to produce a professional API that is also easy to explain during the oral examination.

SQLAlchemy 2.0 was chosen as the ORM because it supports clear model definitions and keeps the application portable across databases. SQLite was used for local development because it is simple to set up, requires no extra infrastructure, and is reliable for offline demonstrations. PostgreSQL on Render was reserved as the intended production target because it provides a more realistic deployment story and aligns with a higher-quality submission strategy.

Alembic was included to manage schema evolution explicitly rather than relying only on ad hoc table creation. JWT bearer authentication was selected because it is widely used in industry and creates a meaningful distinction between public and protected resources.

## 4. System Architecture

The application follows a layered structure. Route handlers define the HTTP interface, schemas define request and response contracts, models define database entities, and service modules contain business logic. This separation was intentional: it keeps route handlers short, makes the code easier to test, and improves maintainability.

The API is divided into three functional areas:

- authentication endpoints for registration and login
- public gold price and analytics endpoints
- protected alert endpoints for user-owned CRUD operations

This structure makes the permission model easy to explain. Market data is public, while alert data belongs to individual users and therefore requires authentication.

## 5. Database Design

The database contains three core tables: `users`, `gold_prices`, and `price_alerts`.

The `users` table stores account identity and authentication-related data. The `gold_prices` table stores the historical dataset that powers the public endpoints. The `price_alerts` table stores rules created by authenticated users, such as `above 3200` or `below 2500`. Each alert belongs to a specific user, which allows the project to demonstrate ownership and access control rather than a single global table.

This design satisfies the coursework requirement for a relational database-backed model with create, read, update, and delete functionality. It also shows a cleaner design decision than placing unrelated information into one table.

## 6. Data Source and Ingestion Strategy

The project uses a bundled snapshot of public gold price data stored in `data/raw/gold_prices_monthly.csv`. A bootstrap script imports the dataset into the local database. This approach was chosen for reliability and reproducibility. It avoids the risk of third-party API failures, API key requirements, rate limits, or network restrictions shortly before the submission deadline.

This was a deliberate engineering trade-off. A live commercial gold price feed might look more advanced on paper, but it would also increase delivery risk. For coursework purposes, a reproducible import pipeline is easier to defend because it ensures that examiners can run the project locally without external dependencies.

## 7. API Design

The API exposes more than four endpoints and clearly exceeds the minimum technical requirement. The public part of the API includes historical price queries and analytical endpoints such as summary statistics, returns, volatility, drawdown, anomalies, and market regime classification. These endpoints were added to give the API a stronger identity as an intelligence service rather than just a storage layer.

The protected part of the API is the alert subsystem. Authenticated users can create, list, inspect, update, and delete their own alerts. This provides the full CRUD requirement in a way that is both practical and easy to demonstrate live.

The application returns JSON consistently and uses standard status codes such as `200`, `201`, `204`, `401`, `404`, `409`, and `422`. Using `422` for validation failures is appropriate because the service uses FastAPI and Pydantic validation, which naturally maps invalid request bodies and query parameters to that response code.

## 8. Validation and Error Handling

Validation is handled through typed Pydantic schemas and constrained query parameters. Examples include minimum password length, allowed alert condition values, positive threshold values, and bounded analytical window parameters.

The project also defines consistent JSON error responses. Duplicate registration returns `409`, invalid credentials return `401`, missing data returns `404`, and request validation failures return `422`. This consistency is important for both software quality and coursework marking because the brief explicitly requires appropriate JSON responses and correct status codes.

## 9. Testing Approach

Testing was implemented with `pytest` and FastAPI's `TestClient`. The tests focus on the behavior that matters most for the assessment:

- successful registration and login
- duplicate registration conflict handling
- invalid login handling
- authentication protection on alert endpoints
- full alert CRUD flow
- latest price and historical price query behavior
- analytical endpoint behavior
- invalid query parameter handling with `422`
- empty range handling with `404`

This approach prioritises meaningful behaviour coverage over artificially large test counts. The goal was to demonstrate that both the happy paths and the important failure paths were considered during development.

## 10. Deployment and Engineering Readiness

The repository includes `render.yaml`, environment configuration, migration support, and scripts for generating documentation assets. Local execution is complete and fully reproducible. Public deployment has also been completed on Render at `https://goldscope-api.onrender.com`, which allows the API to be demonstrated through a live Swagger interface and a public health endpoint.

Even before public deployment, the project already reflects an engineering workflow rather than a single-file prototype. The repository includes source code, tests, seed data, OpenAPI export, PDF-ready documentation, and a presentation deck. This supports the submission requirements beyond the API implementation alone.

## 11. Challenges and Solutions

One challenge was balancing originality against delivery risk. A more ambitious version of the project could have relied on real-time commercial market APIs or predictive models, but that would have made the system harder to reproduce and harder to defend under time pressure. The solution was to focus on a strong, stable core with a clean architecture and clear analytical value.

Another challenge was producing a project that could score well across multiple marking dimensions at once. The response was to treat the coursework as a package: API implementation, testing, documentation, generated artifacts, and deployment preparation were all developed as part of the same submission strategy.

## 12. Limitations

The current version does not yet consume live commercial gold price feeds. It also does not send real email or SMS notifications when alert conditions are met, and it does not include forecasting or machine learning components.

These limitations are acceptable for the current coursework stage because the implemented system is stable, explainable, and clearly aligned with the assignment requirements. However, they remain valid areas for future enhancement.

## 13. Future Improvements

Several extensions would make the project stronger in a production setting:

- integrate a live gold price API for scheduled updates
- add email or SMS delivery for triggered alerts
- compare gold prices with inflation, exchange rates, or interest rate data
- expose the service through an MCP-compatible layer
- add dashboards or richer visual analytics for end users

These features were intentionally deferred so that the core submission would remain reliable and easy to present.

## 14. Generative AI Usage Declaration

Generative AI was used throughout the project as a development support tool. It was used for planning the project scope, exploring alternative designs, structuring the repository, refining documentation, drafting test scenarios, and accelerating implementation tasks.

All generated material was manually reviewed, edited, and verified before being included in the project. The final responsibility for design decisions, code behaviour, documentation accuracy, and oral defence remains with the student. AI was used to improve productivity and support higher-level exploration, not to bypass understanding or submit unverified output.

## 15. Submission Notes

The public repository and generated submission assets are available at the following locations:

- GitHub repository: https://github.com/MDYAnonTokyo/goldscope-api
- Public API base URL: https://goldscope-api.onrender.com
- Public Swagger UI: https://goldscope-api.onrender.com/docs
- API documentation PDF: https://github.com/MDYAnonTokyo/goldscope-api/blob/main/docs/generated/api_documentation.pdf
- Technical report PDF: https://github.com/MDYAnonTokyo/goldscope-api/blob/main/docs/generated/technical_report.pdf
- Presentation slides: https://github.com/MDYAnonTokyo/goldscope-api/blob/main/docs/generated/goldscope_presentation.pptx
- Visual report: https://github.com/MDYAnonTokyo/goldscope-api/blob/main/docs/generated/visual_report.html

Supplementary exported GenAI conversation logs should still be attached separately in the final Minerva submission if they are not already hosted in the repository.

## References

- FastAPI. https://fastapi.tiangolo.com/
- SQLAlchemy. https://docs.sqlalchemy.org/
- Alembic. https://alembic.sqlalchemy.org/
- Render Documentation. https://render.com/docs
- DataHub Gold Prices Dataset. https://datahub.io/core/gold-prices
