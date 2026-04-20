from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


def _http_error_slug(status_code: int) -> str:
    mapping = {
        400: "bad_request",
        401: "unauthorized",
        403: "forbidden",
        404: "not_found",
        409: "conflict",
        422: "validation_error",
        500: "internal_server_error",
    }
    return mapping.get(status_code, "http_error")


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(HTTPException)
    async def http_exception_handler(
        request: Request,
        exc: HTTPException,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": _http_error_slug(exc.status_code),
                "message": exc.detail,
                "path": str(request.url.path),
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content={
                "error": "validation_error",
                "message": "Request validation failed.",
                "path": str(request.url.path),
                "details": exc.errors(),
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request,
        exc: Exception,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=500,
            content={
                "error": "internal_server_error",
                "message": "An unexpected server error occurred.",
                "path": str(request.url.path),
            },
        )
