from contextlib import asynccontextmanager

from fastapi import FastAPI

from goldscope.api.router import api_router
from goldscope.core.config import get_settings
from goldscope.core.errors import register_exception_handlers
from goldscope.db.bootstrap import bootstrap_database


@asynccontextmanager
async def lifespan(_: FastAPI):
    bootstrap_database()
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        summary="Gold price intelligence API with analytics and alerts.",
        description=(
            "GoldScope API provides historical gold price data, analytics endpoints, "
            "JWT authentication, and user-managed price alerts."
        ),
        lifespan=lifespan,
    )

    register_exception_handlers(app)
    app.include_router(api_router)

    return app
