import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.v1 import auth, emg, health, sessions
from app.core.config import settings
from app.core.database import init_db
from app.core.middleware import SecurityAndTracingMiddleware, limiter
from app.services.mqtt_service import start_mqtt_client, stop_mqtt_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    start_mqtt_client()
    yield
    stop_mqtt_client()


app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)

# Rate Limiter & Security Middleware
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SecurityAndTracingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Serve branded 404.html for missing frontend pages and JSON envelopes for API errors."""
    if exc.status_code == 404 and not request.url.path.startswith("/api"):
        not_found_page = os.path.join(settings.FRONTEND_DIR, "404.html")
        if os.path.isfile(not_found_page):
            return FileResponse(not_found_page, status_code=404)

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.detail if isinstance(exc.detail, str) else "Request failed",
            "data": None,
            "error": str(exc.detail),
            "detail": exc.detail,
        },
    )


# Register modular API v1 routers
app.include_router(health.router)
app.include_router(auth.router)
app.include_router(sessions.router)
app.include_router(emg.router)

# Mount frontend static assets
if os.path.isdir(settings.FRONTEND_DIR):
    app.mount("/", StaticFiles(directory=settings.FRONTEND_DIR, html=True), name="frontend")
