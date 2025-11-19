"""
Main FastAPI application
"""
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
from app.core.config import settings
from app.core.database import connect_to_mongo, close_mongo_connection
from app.routes import auth, bookings, payments, operators, partners, waitlist, partnerships, questions

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting Ovu Transport Aggregator...")
    await connect_to_mongo()
    logger.info("Connected to MongoDB")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Ovu Transport Aggregator...")
    await close_mongo_connection()
    logger.info("Closed MongoDB connection")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="Transport Aggregator for Nigeria - Flights, Buses, and Trains",
    version=settings.API_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)


# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting middleware
from app.middleware.rate_limit import add_rate_limit_headers
app.middleware("http")(add_rate_limit_headers)


# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Global exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error",
            "type": "server_error"
        }
    )


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.API_VERSION,
        "environment": settings.APP_ENV,
    }


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Ovu Transport Aggregator",
        "version": settings.API_VERSION,
        "docs": "/docs",
        "health": "/health",
    }


# Include routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(bookings.router, prefix="/api/v1")
app.include_router(payments.router, prefix="/api/v1")
app.include_router(operators.router, prefix="/api/v1")
app.include_router(partners.router)

# Partner authentication routes
from app.routes import partner_auth
app.include_router(partner_auth.router)
app.include_router(partner_auth.admin_router)

app.include_router(waitlist.router, prefix="/api/v1")
app.include_router(partnerships.router)
app.include_router(questions.router, prefix="/api/v1")


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info",
    )
