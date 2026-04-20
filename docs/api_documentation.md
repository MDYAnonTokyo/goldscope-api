# GoldScope API Documentation

## 1. Purpose

GoldScope API is a database-driven web service for querying historical gold prices, running analytics on price movements, and managing authenticated user price alerts. The project was built for the University of Leeds module `XJCO3011 Web Services and Web Data`.

The API combines three ideas in one coursework submission:

- historical market data access
- analytical endpoints that go beyond basic CRUD
- authenticated CRUD for user-owned alert resources

## 2. Base URL

- Local development: `http://127.0.0.1:8000`
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`
- Public deployment: `https://goldscope-api.onrender.com`
- Public Swagger UI: `https://goldscope-api.onrender.com/docs`
- Public ReDoc: `https://goldscope-api.onrender.com/redoc`

## 3. Authentication

Authentication uses JWT bearer tokens.

- Public endpoints: `/health`, `/gold/*`, `/auth/*`
- Protected endpoints: `/alerts/*`

Include the access token in the `Authorization` header:

```http
Authorization: Bearer <access_token>
```

## 4. Error Response Format

The API returns JSON for both success and error responses.

HTTP errors follow this shape:

```json
{
  "error": "not_found",
  "message": "No gold price data found for the requested range.",
  "path": "/gold/analytics/summary"
}
```

Validation errors use this shape:

```json
{
  "error": "validation_error",
  "message": "Request validation failed.",
  "path": "/gold/analytics/volatility",
  "details": []
}
```

## 5. Status Codes

| Status code | Meaning |
| --- | --- |
| `200` | Request completed successfully |
| `201` | Resource created successfully |
| `204` | Resource deleted successfully with no response body |
| `401` | Missing or invalid authentication token |
| `404` | Resource not found, or no data exists for the requested range |
| `409` | Conflict, such as duplicate user registration |
| `422` | Request body or query parameter validation failed |

## 6. Endpoint Summary

| Method | Path | Auth required | Description |
| --- | --- | --- | --- |
| `GET` | `/health` | No | Service health check |
| `POST` | `/auth/register` | No | Register a new user |
| `POST` | `/auth/login` | No | Authenticate and return a JWT |
| `GET` | `/gold/prices` | No | Query historical gold prices |
| `GET` | `/gold/prices/latest` | No | Return the latest gold price record |
| `GET` | `/gold/analytics/summary` | No | Summary statistics for a date range |
| `GET` | `/gold/analytics/returns` | No | Returns across multiple lookback windows |
| `GET` | `/gold/analytics/volatility` | No | Annualised historical volatility |
| `GET` | `/gold/analytics/drawdown` | No | Maximum drawdown for a date range |
| `GET` | `/gold/analytics/anomalies` | No | Detect unusual price changes |
| `GET` | `/gold/analytics/regime` | No | Classify the current market regime |
| `POST` | `/alerts` | Yes | Create a price alert |
| `GET` | `/alerts` | Yes | List alerts for the current user |
| `GET` | `/alerts/{id}` | Yes | Retrieve one alert |
| `PATCH` | `/alerts/{id}` | Yes | Partially update one alert |
| `DELETE` | `/alerts/{id}` | Yes | Delete one alert |

## 7. Endpoint Details

### `GET /health`

Purpose: confirm that the API is running.

Auth required: No

Success response: `200 OK`

Example response:

```json
{
  "status": "ok",
  "service": "GoldScope API",
  "environment": "development"
}
```

### `POST /auth/register`

Purpose: create a new user account.

Auth required: No

Status codes:

- `201` created
- `409` duplicate email
- `422` invalid email or password length

Request body:

```json
{
  "email": "student@example.com",
  "password": "supersecure123"
}
```

Success response:

```json
{
  "id": 1,
  "email": "student@example.com",
  "created_at": "2026-04-20T12:00:00Z"
}
```

Conflict response example:

```json
{
  "error": "conflict",
  "message": "A user with this email already exists.",
  "path": "/auth/register"
}
```

### `POST /auth/login`

Purpose: authenticate a user and return a bearer token.

Auth required: No

Status codes:

- `200` success
- `401` invalid credentials
- `422` invalid request body

Request body:

```json
{
  "email": "student@example.com",
  "password": "supersecure123"
}
```

Success response:

```json
{
  "access_token": "jwt-token",
  "token_type": "bearer",
  "expires_at": "2026-04-21T12:00:00Z",
  "user": {
    "id": 1,
    "email": "student@example.com",
    "created_at": "2026-04-20T12:00:00Z"
  }
}
```

Error response example:

```json
{
  "error": "unauthorized",
  "message": "Invalid email or password.",
  "path": "/auth/login"
}
```

### `GET /gold/prices`

Purpose: list historical gold price records.

Auth required: No

Query parameters:

| Name | Type | Required | Notes |
| --- | --- | --- | --- |
| `start_date` | `YYYY-MM-DD` | No | Lower bound of the date range |
| `end_date` | `YYYY-MM-DD` | No | Upper bound of the date range |
| `limit` | integer | No | Default `120`, minimum `0`, maximum `5000` |

Success response: `200 OK`

Example request:

```http
GET /gold/prices?start_date=2024-01-01&end_date=2024-12-31&limit=24
```

Example response:

```json
{
  "count": 12,
  "start_date": "2024-01-01",
  "end_date": "2024-12-01",
  "items": [
    {
      "id": 1,
      "price_date": "2024-01-01",
      "usd_oz": 2063.73,
      "gbp_oz": 1628.24,
      "eur_oz": 1903.52,
      "source_name": "DataHub gold-prices snapshot (derived from WGC)"
    }
  ]
}
```

### `GET /gold/prices/latest`

Purpose: retrieve the most recent gold price observation.

Auth required: No

Status codes:

- `200` success
- `404` no price data available

Example response:

```json
{
  "item": {
    "id": 317,
    "price_date": "2026-03-01",
    "usd_oz": 4855.54,
    "gbp_oz": null,
    "eur_oz": null,
    "source_name": "DataHub gold-prices snapshot (derived from WGC)"
  }
}
```

### `GET /gold/analytics/summary`

Purpose: return summary statistics for a selected date range.

Auth required: No

Query parameters:

| Name | Type | Required | Notes |
| --- | --- | --- | --- |
| `start_date` | `YYYY-MM-DD` | No | Start of analysis window |
| `end_date` | `YYYY-MM-DD` | No | End of analysis window |

Status codes:

- `200` success
- `404` no data in the requested range

Example response:

```json
{
  "start_date": "2024-01-01",
  "end_date": "2025-12-01",
  "observation_count": 24,
  "observation_frequency": "monthly",
  "latest_price": 4372.04,
  "latest_date": "2025-12-01",
  "min_price": 2063.73,
  "max_price": 4372.04,
  "average_price": 2871.33,
  "absolute_change": 2308.31,
  "percent_change": 111.86
}
```

### `GET /gold/analytics/returns`

Purpose: calculate returns for several lookback periods using the latest available observation.

Auth required: No

Status codes:

- `200` success
- `404` insufficient data

Example response:

```json
{
  "as_of_date": "2026-03-01",
  "observation_frequency": "monthly",
  "items": [
    {
      "period_label": "30d",
      "lookback_days": 30,
      "matched_date": "2026-02-01",
      "matched_price": 4688.89,
      "latest_price": 4855.54,
      "absolute_return": 166.65,
      "percent_return": 3.55
    }
  ]
}
```

### `GET /gold/analytics/volatility`

Purpose: calculate annualised historical volatility from recent observations.

Auth required: No

Query parameters:

| Name | Type | Required | Notes |
| --- | --- | --- | --- |
| `window_points` | integer | No | Default `12`, minimum `2`, maximum `120` |

Status codes:

- `200` success
- `404` insufficient data
- `422` invalid window size

Example response:

```json
{
  "as_of_date": "2026-03-01",
  "observation_frequency": "monthly",
  "window_points": 12,
  "annualized_volatility": 0.2184,
  "return_count": 11
}
```

### `GET /gold/analytics/drawdown`

Purpose: return the maximum drawdown in a chosen time range.

Auth required: No

Query parameters:

| Name | Type | Required | Notes |
| --- | --- | --- | --- |
| `start_date` | `YYYY-MM-DD` | No | Start of analysis window |
| `end_date` | `YYYY-MM-DD` | No | End of analysis window |

Status codes:

- `200` success
- `404` no data in the requested range

Example response:

```json
{
  "start_date": "2018-01-01",
  "end_date": "2025-12-31",
  "max_drawdown_pct": -0.1821,
  "peak_date": "2020-08-01",
  "trough_date": "2021-03-01",
  "recovery_date": "2023-12-01"
}
```

### `GET /gold/analytics/anomalies`

Purpose: identify unusual percentage changes using a z-score threshold.

Auth required: No

Query parameters:

| Name | Type | Required | Notes |
| --- | --- | --- | --- |
| `start_date` | `YYYY-MM-DD` | No | Start of analysis window |
| `end_date` | `YYYY-MM-DD` | No | End of analysis window |
| `threshold` | float | No | Default `1.5`, minimum `0.5`, maximum `5.0` |

Status codes:

- `200` success
- `404` no data in the requested range
- `422` invalid threshold

Example response:

```json
{
  "start_date": "2018-01-01",
  "end_date": "2025-12-31",
  "threshold": 1.5,
  "count": 5,
  "observation_frequency": "monthly",
  "items": [
    {
      "price_date": "2020-03-01",
      "usd_oz": 1591.9,
      "pct_change": -4.62,
      "z_score": -2.11
    }
  ]
}
```

### `GET /gold/analytics/regime`

Purpose: classify the latest market regime using short and long moving averages.

Auth required: No

Query parameters:

| Name | Type | Required | Notes |
| --- | --- | --- | --- |
| `short_window` | integer | No | Default `3`, minimum `2`, maximum `12` |
| `long_window` | integer | No | Default `6`, minimum `3`, maximum `24` |

Status codes:

- `200` success
- `404` insufficient data
- `422` invalid moving-average window

Example response:

```json
{
  "as_of_date": "2026-03-01",
  "short_window": 3,
  "long_window": 6,
  "short_moving_average": 4705.43,
  "long_moving_average": 4459.88,
  "regime": "bull"
}
```

### `POST /alerts`

Purpose: create a new alert owned by the authenticated user.

Auth required: Yes

Status codes:

- `201` created
- `401` missing or invalid token
- `422` invalid request body

Request body:

```json
{
  "name": "Breakout Watch",
  "condition_type": "above",
  "threshold_value": 3200.0,
  "notes": "Watch for a breakout above resistance.",
  "active": true
}
```

Success response:

```json
{
  "id": 1,
  "user_id": 1,
  "name": "Breakout Watch",
  "condition_type": "above",
  "threshold_value": 3200.0,
  "notes": "Watch for a breakout above resistance.",
  "active": true,
  "created_at": "2026-04-20T12:10:00Z",
  "updated_at": "2026-04-20T12:10:00Z"
}
```

### `GET /alerts`

Purpose: list all alerts owned by the authenticated user.

Auth required: Yes

Status codes:

- `200` success
- `401` missing or invalid token

Example response:

```json
{
  "count": 1,
  "items": [
    {
      "id": 1,
      "user_id": 1,
      "name": "Breakout Watch",
      "condition_type": "above",
      "threshold_value": 3200.0,
      "notes": "Watch for a breakout above resistance.",
      "active": true,
      "created_at": "2026-04-20T12:10:00Z",
      "updated_at": "2026-04-20T12:10:00Z"
    }
  ]
}
```

### `GET /alerts/{id}`

Purpose: retrieve one alert by identifier.

Auth required: Yes

Status codes:

- `200` success
- `401` missing or invalid token
- `404` alert not found

### `PATCH /alerts/{id}`

Purpose: partially update an alert.

Auth required: Yes

Status codes:

- `200` success
- `401` missing or invalid token
- `404` alert not found
- `422` invalid request body

Example request:

```json
{
  "active": false,
  "threshold_value": 3300.0
}
```

Example response:

```json
{
  "id": 1,
  "user_id": 1,
  "name": "Breakout Watch",
  "condition_type": "above",
  "threshold_value": 3300.0,
  "notes": "Watch for a breakout above resistance.",
  "active": false,
  "created_at": "2026-04-20T12:10:00Z",
  "updated_at": "2026-04-20T12:30:00Z"
}
```

### `DELETE /alerts/{id}`

Purpose: delete an alert.

Auth required: Yes

Status codes:

- `204` success
- `401` missing or invalid token
- `404` alert not found

No response body is returned on success.

## 8. Notes for Assessment

- The API returns JSON consistently, including error responses.
- `422` is used for validation failures because the application relies on FastAPI and Pydantic request validation.
- Alert CRUD demonstrates the required database-backed create, read, update, and delete operations.
- Analytics endpoints are intentionally included to move the project beyond a minimal CRUD submission.
