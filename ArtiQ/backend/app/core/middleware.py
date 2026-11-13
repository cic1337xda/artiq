import uuid
from urllib.parse import urlparse
from fastapi import Request
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from starlette.middleware.base import BaseHTTPMiddleware

limiter = Limiter(key_func=get_remote_address)

STATE_CHANGING_METHODS = {"POST", "PUT", "DELETE", "PATCH"}


class SecurityAndTracingMiddleware(BaseHTTPMiddleware):
    """Enforces HTTP security headers, CSRF Origin/Referer validation, and X-Request-ID tracing."""

    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        # CSRF Protection on state-changing requests using Origin / Referer validation
        if request.method in STATE_CHANGING_METHODS:
            host = (
                request.headers.get("x-forwarded-host")
                or request.headers.get("host")
                or ""
            ).split(",")[0].strip().lower()

            origin = request.headers.get("origin")
            referer = request.headers.get("referer")

            if origin:
                origin_host = urlparse(origin).netloc.lower()
                if host and origin_host and origin_host != host:
                    return JSONResponse(
                        status_code=403,
                        content={
                            "success": False,
                            "message": "CSRF origin validation failed",
                            "data": None,
                            "error": "Cross-origin state mutation is not permitted.",
                        },
                        headers={"X-Request-ID": request_id},
                    )
            elif referer:
                referer_host = urlparse(referer).netloc.lower()
                if host and referer_host and referer_host != host:
                    return JSONResponse(
                        status_code=403,
                        content={
                            "success": False,
                            "message": "CSRF referer validation failed",
                            "data": None,
                            "error": "Cross-site referer mutation is not permitted.",
                        },
                        headers={"X-Request-ID": request_id},
                    )

        response = await call_next(request)

        # Standard HTTP Security Headers
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        return response
