"""
AI-Powered Form Filling Assistant for Indian Citizen Services
Main FastAPI Application

This application helps Indian citizens fill government forms by:
1. Extracting information from uploaded ID documents (Aadhaar, PAN, Voter ID)
2. Using OCR to read scanned/photographed documents
3. Auto-mapping extracted data to government form templates
"""

# Load environment variables FIRST, before any other imports
from pathlib import Path
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).resolve().parent.parent / '.env'
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
        print(f"✓ Loaded .env file from: {env_path}")
except ImportError:
    pass
except Exception as e:
    print(f"Warning: Could not load .env file: {e}")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import API_VERSION, CORS_ORIGINS
from app.api.routes.document import router as document_router
from app.api.routes.profile import router as profile_router
from app.api.routes.security import router as security_router
from app.api.routes.forms import router as forms_router
from app.models.schemas import HealthCheckResponse
from app.utils.logger import get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    """
    # Startup
    logger.info("=" * 60)
    logger.info("Form Filling Assistant API Starting...")
    logger.info(f"API Version: {API_VERSION}")
    logger.info("=" * 60)
    
    # TODO: Initialize ML models here (spaCy, Whisper, etc.)
    # TODO: Pre-load OCR engines for faster first request
    
    yield
    
    # Shutdown
    logger.info("Form Filling Assistant API Shutting down...")


# Create FastAPI application
app = FastAPI(
    title="AI Form Filling Assistant",
    description="""
    ## 🇮🇳 AI-Powered Form Filling Assistant for Indian Citizen Services
    
    This API helps automatically fill Indian government service forms using:
    - **Document Upload**: PDF and Image support (Aadhaar, PAN, Voter ID)
    - **OCR Processing**: Tesseract + EasyOCR for text extraction
    - **Entity Extraction**: Automatic extraction of Name, DOB, Address, ID numbers
    - **Form Mapping**: Auto-map extracted data to government form templates
    
    ### Supported Documents
    - Aadhaar Card
    - PAN Card
    - Voter ID (EPIC)
    
    ### Supported Languages
    - English
    - Hindi (हिंदी)
    
    *More languages coming soon!*
    """,
    version=API_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure CORS for frontend and Chrome extension access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for Chrome extension
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================================================================
# ROUTES
# =============================================================================

# Include document processing routes
app.include_router(document_router, prefix=f"/api/{API_VERSION}")

# Include profile management routes
app.include_router(profile_router, prefix=f"/api/{API_VERSION}")

# Include security routes
app.include_router(security_router, prefix=f"/api/{API_VERSION}")

# Include form routes
app.include_router(forms_router, prefix=f"/api/{API_VERSION}")


@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint with API information.
    """
    return {
        "name": "AI Form Filling Assistant",
        "version": API_VERSION,
        "description": "AI-Powered Form Filling for Indian Citizen Services",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthCheckResponse, tags=["Health"])
async def health_check():
    """
    Health check endpoint for monitoring.
    """
    return HealthCheckResponse(
        status="healthy",
        version=API_VERSION
    )


# =============================================================================
# ERROR HANDLERS
# =============================================================================

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Global exception handler for unhandled errors.
    """
    logger.error(f"Unhandled error: {str(exc)}")
    return {
        "status": "error",
        "message": "An unexpected error occurred",
        "detail": str(exc) if app.debug else None
    }


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    
    # Run the server (development mode)
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Enable auto-reload for development
        log_level="info"
    )

