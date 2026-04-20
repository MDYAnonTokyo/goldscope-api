# GoldScope Presentation Outline

## 1. Project Goal

- Build a gold price intelligence API rather than a basic CRUD-only service
- Satisfy coursework deliverables while demonstrating modern API engineering
- Combine data, analytics, authentication, testing, documentation, and deployment readiness

## 2. System Architecture

- FastAPI application with modular routers, schemas, services, and models
- SQLite for local development and Render Postgres for public deployment
- JWT Bearer authentication for user-owned alert resources

## 3. Database Design

- `users` stores credentials and account identity
- `gold_prices` stores historical monthly gold price observations
- `price_alerts` stores authenticated user-defined alert rules

## 4. API Design

- Public endpoints expose prices and analytics
- Protected endpoints manage alert CRUD
- JSON responses and standard HTTP status codes are used consistently

## 5. Analytics Features

- Summary statistics
- Returns across multiple windows
- Annualized volatility
- Maximum drawdown
- Anomaly detection with z-score
- Market regime classification using moving averages

## 6. Version Control and Deployment

- Repository structured for clear incremental commits
- Alembic migrations included for schema tracking
- Render Blueprint prepared for public deployment

## 7. Documentation and Testing

- README with setup and run instructions
- API documentation in Markdown and PDF
- Technical report in Markdown and PDF
- pytest coverage for auth, CRUD, analytics, and error cases

## 8. Challenges, Trade-offs, and Future Work

- Chose stable snapshot data over risky live paid APIs
- Prioritized reproducibility and strong submission quality near the deadline
- Future work includes real-time feeds, alert notifications, and broader market correlations
