"""
Configuration settings for the Form Filling Assistant backend.
All configurable parameters are centralized here for easy management.
"""

import os
from pathlib import Path

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    # Load .env file from backend directory
    env_path = Path(__file__).resolve().parent.parent / '.env'
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
        print(f"Loaded .env file from: {env_path}")
    else:
        print(f".env file not found at: {env_path}")
except ImportError:
    print("python-dotenv not installed, skipping .env file loading")
except Exception as e:
    print(f"Error loading .env file: {e}")

# =============================================================================
# PATH CONFIGURATIONS
# =============================================================================

# Base directory of the application
BASE_DIR = Path(__file__).resolve().parent.parent

# Directory for storing uploaded documents
UPLOAD_DIR = BASE_DIR / "uploads"

# Ensure upload directory exists
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# =============================================================================
# FILE UPLOAD SETTINGS
# =============================================================================

# Allowed file extensions for document upload
ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg", ".tiff", ".bmp"}

# Maximum file size in bytes (10 MB)
MAX_FILE_SIZE = 10 * 1024 * 1024

# =============================================================================
# OCR SETTINGS
# =============================================================================

# Tesseract configuration for Indian documents
# Using English + Hindi by default, can be extended
TESSERACT_LANG = "eng+hin"

# EasyOCR languages (English + Hindi for MVP)
EASYOCR_LANGS = ["en", "hi"]

# OCR confidence threshold (0-100)
# Text below this confidence is flagged for review
OCR_CONFIDENCE_THRESHOLD = 60

# =============================================================================
# CLOUD OCR API SETTINGS
# =============================================================================

# OCR Provider preference (ocr_space, google_vision, aws_textract, azure_vision, local)
# Set via environment variable OCR_PROVIDER
OCR_PROVIDER = os.getenv("OCR_PROVIDER", "local")

# OCR.space Free OCR API (Recommended - Free and Easy)
OCR_SPACE_API_KEY = os.getenv("OCR_SPACE_API_KEY", "")

# Google Cloud Vision API
GOOGLE_VISION_API_KEY = os.getenv("GOOGLE_VISION_API_KEY", "")
GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "")

# AWS Textract
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

# Azure Computer Vision
AZURE_VISION_KEY = os.getenv("AZURE_VISION_KEY", "")
AZURE_VISION_ENDPOINT = os.getenv("AZURE_VISION_ENDPOINT", "")

# =============================================================================
# API SETTINGS
# =============================================================================

# API version
API_VERSION = "v1"

# CORS origins (for development)
CORS_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",  # Vite default
    "http://127.0.0.1:5173",
]

# =============================================================================
# LOGGING SETTINGS
# =============================================================================

# Log level: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Log format
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"

# =============================================================================
# DOCUMENT TYPE IDENTIFIERS
# =============================================================================

# Patterns to identify document types (used in entity extraction)
DOCUMENT_PATTERNS = {
    "aadhaar": {
        "patterns": ["aadhaar", "आधार", "uidai", "unique identification", "government of india"],
        "id_regex": r"\d{4}\s?\d{4}\s?\d{4}",  # 12-digit Aadhaar format
        "priority": 1,
    },
    "pan": {
        "patterns": ["permanent account number", "income tax", "pan card", "आयकर विभाग"],
        "id_regex": r"[A-Z]{5}[0-9]{4}[A-Z]{1}",  # PAN format: ABCDE1234F
        "priority": 2,
    },
    "voter_id": {
        "patterns": ["election commission", "voter", "epic", "निर्वाचन", "electoral"],
        "id_regex": r"[A-Z]{3}[0-9]{7}",  # Voter ID format
        "priority": 3,
    },
    "passport": {
        "patterns": ["passport", "republic of india", "पासपोर्ट", "travel document", 
                     "nationality", "place of birth", "date of expiry"],
        "id_regex": r"[A-Z][0-9]{7}",  # Passport format: A1234567
        "priority": 4,
    },
    "driving_license": {
        "patterns": ["driving licence", "driving license", "motor vehicle", 
                     "transport department", "dl no", "licence no", "rto"],
        "id_regex": r"[A-Z]{2}[0-9]{2}\s?[0-9]{11}|[A-Z]{2}-[0-9]{13}",  # DL format varies by state
        "priority": 5,
    },
    "bank_statement": {
        "patterns": ["bank statement", "account statement", "transaction history",
                     "account number", "ifsc", "opening balance", "closing balance"],
        "id_regex": r"\d{9,18}",  # Bank account number (varies)
        "priority": 6,
    },
}

# =============================================================================
# FORM TEMPLATES (MVP - Basic structure)
# =============================================================================

# TODO: Load form templates from JSON files for production
# These define what fields each government form requires
FORM_TEMPLATES = {
    "passport_application": {
        "name": "Passport Application Form",
        "fields": ["full_name", "dob", "gender", "address", "aadhaar_number", "pan_number"],
    },
    "pan_application": {
        "name": "PAN Card Application",
        "fields": ["full_name", "father_name", "dob", "address", "aadhaar_number"],
    },
    "voter_registration": {
        "name": "Voter ID Registration",
        "fields": ["full_name", "father_name", "dob", "gender", "address"],
    },
}

