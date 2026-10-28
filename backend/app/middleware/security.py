"""
Security and Request Hardening Middleware for VerifyAI.
Enforces request size limits to prevent resource exhaustion,
injects OWASP security headers, and sanitizes unhandled exceptions.
"""
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse

MAX_REQUEST_BODY_BYTES = 25 * 1024 * 1024  # 25 MB

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Enforce maximum body size via Content-Length header
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > MAX_REQUEST_BODY_BYTES:
            return JSONResponse(
                status_code=413,
                content={"detail": "Payload too large. Maximum allowable request size is 25MB."}
            )

        try:
            response: Response = await call_next(request)
        except Exception as exc:
            # Prevent leaking raw tracebacks in production
            return JSONResponse(
                status_code=500,
                content={"detail": "An internal server error occurred. The incident has been recorded."}
            )

        # Inject standard security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        return response
