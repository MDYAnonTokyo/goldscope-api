from fastapi import APIRouter

from goldscope.api.routes import alerts, auth, gold, health

api_router = APIRouter()
api_router.include_router(health.router, tags=["Health"])
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(gold.router, prefix="/gold", tags=["Gold Data"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["Alerts"])
