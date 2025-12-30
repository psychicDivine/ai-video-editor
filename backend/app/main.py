from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi import Request
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging

from app.config import settings
from app.routes import upload, jobs, download
try:
    from app.routes import transition_routes
except Exception:
    transition_routes = None

try:
    from app.routes import frei0r_routes
except Exception:
    frei0r_routes = None

# Optional observability integrations (imported if available)
try:
    import sentry_sdk
    from sentry_sdk.integrations.logging import LoggingIntegration as SentryLoggingIntegration
except Exception:
    sentry_sdk = None
    SentryLoggingIntegration = None

try:
    from pythonjsonlogger import jsonlogger
except Exception:
    jsonlogger = None

# Configure structured logging (JSON if python-json-logger available)
level = logging.getLevelName(settings.log_level.upper()) if isinstance(settings.log_level, str) else settings.log_level
root_logger = logging.getLogger()
handler = logging.StreamHandler()
if jsonlogger:
    fmt = '%(asctime)s %(name)s %(levelname)s %(message)s'
    formatter = jsonlogger.JsonFormatter(fmt)
else:
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
root_logger.setLevel(level)
# Replace existing handlers with our configured handler for predictable output
for h in list(root_logger.handlers):
    root_logger.removeHandler(h)
root_logger.addHandler(handler)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="AI Video Editor",
    description="AI-powered video editor with beat-synced transitions and audio mixing",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(upload.router)
app.include_router(jobs.router)
app.include_router(download.router)
if transition_routes:
    app.include_router(transition_routes.router)
if frei0r_routes:
    app.include_router(frei0r_routes.router)


def _error_payload(status_code: int, message: str, detail: str | None = None):
    payload = {
        "error": True,
        "status_code": status_code,
        "message": message,
    }
    if detail:
        payload["detail"] = detail
    return payload


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    logger.warning(f"HTTP error for {request.url}: {exc.detail}")
    return JSONResponse(status_code=exc.status_code, content=_error_payload(exc.status_code, str(exc.detail)))


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning(f"Validation error for {request.url}: {exc}")
    return JSONResponse(status_code=422, content=_error_payload(422, "Invalid request", detail=str(exc)))


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception for {request.url}: {str(exc)}", exc_info=True)
    # Send to Sentry when available
    if sentry_sdk:
        try:
            sentry_sdk.capture_exception(exc)
        except Exception:
            logger.exception("Failed to capture exception with Sentry")
    # Avoid leaking internal details in production
    message = "Internal server error"
    detail = str(exc) if settings.debug else None
    return JSONResponse(status_code=500, content=_error_payload(500, message, detail=detail))


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return JSONResponse(
        status_code=200,
        content={"status": "ok", "message": "AI Video Editor API is running"},
    )


@app.get("/")
async def root():
    """Root endpoint."""
    return JSONResponse(
        status_code=200,
        content={
            "message": "Welcome to AI Video Editor API",
            "docs": "/docs",
            "openapi": "/openapi.json",
        },
    )


@app.on_event("startup")
async def startup_event():
    """Startup event handler."""
    logger.info("Starting AI Video Editor API")
    logger.info(f"Database URL: {settings.database_url}")
    logger.info(f"Redis URL: {settings.redis_url}")

    # Initialize Sentry only when DSN provided and sentry-sdk is available
    if settings.sentry_dsn and sentry_sdk:
        try:
            sentry_logging = SentryLoggingIntegration(level=level, event_level=logging.ERROR)
            sentry_sdk.init(dsn=settings.sentry_dsn, integrations=[sentry_logging], traces_sample_rate=0.0 if settings.debug else 0.1)
            logger.info("Sentry initialized")
        except Exception:
            logger.exception("Failed to initialize Sentry")
    elif settings.sentry_dsn and not sentry_sdk:
        logger.warning("Sentry DSN configured but sentry-sdk is not installed; skipping initialization")


@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler."""
    logger.info("Shutting down AI Video Editor API")
