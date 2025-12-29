from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi import Request
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging

from app.config import settings
from app.routes import upload, jobs, download

# Configure logging
logging.basicConfig(level=settings.log_level)
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


@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler."""
    logger.info("Shutting down AI Video Editor API")
