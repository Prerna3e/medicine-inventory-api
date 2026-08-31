import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.database import connect_to_mongo, close_mongo_connection
from app.routers import auth, medicines, orders

logger = logging.getLogger("uvicorn.error")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for startup and shutdown database connections & indexes."""
    await connect_to_mongo()
    yield
    await close_mongo_connection()

app = FastAPI(
    title="Medicine Inventory & Order API",
    description="A secure and robust backend API for managing medicine inventory and placing orders.",
    version="1.0.0",
    lifespan=lifespan
)

# Global exception handler for unhandled internal errors
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Catch-all exception handler to prevent leaking raw tracebacks to clients.
    Logs error internally and returns a clean 500 JSON response.
    """
    logger.error(f"Unhandled exception on {request.method} {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"}
    )

# Include API Routers
app.include_router(auth.router)
app.include_router(medicines.router)
app.include_router(orders.router)

@app.get("/", tags=["Health"])
def root():
    """Root health-check endpoint."""
    return {"status": "ok", "service": "Medicine Inventory & Order API"}