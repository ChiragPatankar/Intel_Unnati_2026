# 🇮🇳 AI Form Filling Assistant - Backend

AI-powered backend service for automatically filling Indian government forms using uploaded documents (Aadhaar, PAN, Voter ID).

## 🏗️ Architecture

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration settings
│   ├── api/
│   │   └── routes/
│   │       └── document.py  # Document processing endpoints
│   ├── models/
│   │   └── schemas.py       # Pydantic models for request/response
│   ├── services/
│   │   ├── document_upload.py   # File handling service
│   │   ├── ocr_service.py       # OCR processing (Tesseract + EasyOCR)
│   │   ├── entity_extraction.py # Entity extraction (Name, DOB, etc.)
│   │   └── form_mapping.py      # Form template mapping
│   └── utils/
│       └── logger.py        # Logging configuration
├── uploads/                 # Uploaded documents storage
├── requirements.txt         # Python dependencies
└── README.md
```

## 🚀 Quick Start

### 1. Install System Dependencies

**Windows:**
```powershell
# Install Tesseract OCR
# Download from: https://github.com/UB-Mannheim/tesseract/wiki
# Add to PATH after installation

# Install Poppler (for PDF processing)
# Download from: https://github.com/osborn/poppler-windows/releases
# Add bin folder to PATH
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr tesseract-ocr-hin poppler-utils
```

### 2. Create Virtual Environment

```bash
cd backend
python -m venv venv

# Windows
.\venv\Scripts\activate

# Linux/macOS
source venv/bin/activate
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Server

```bash
# Development mode with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Access the API

- **API Docs (Swagger):** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **Health Check:** http://localhost:8000/health

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/document/upload` | Upload document and run OCR |
| `POST` | `/api/v1/document/extract-entities` | Extract entities from document |
| `POST` | `/api/v1/document/process-and-map` | Full pipeline: OCR → Extract → Map |
| `GET` | `/api/v1/document/templates` | List available form templates |
| `DELETE` | `/api/v1/document/{file_id}` | Delete uploaded document |

## 📝 Example Usage

### Upload and OCR a Document

```bash
curl -X POST "http://localhost:8000/api/v1/document/upload" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@aadhaar_card.pdf"
```

**Response:**
```json
{
  "status": "success",
  "message": "Document uploaded and processed successfully",
  "filename": "aadhaar_card.pdf",
  "file_id": "abc123-def456",
  "ocr_result": {
    "raw_text": "GOVERNMENT OF INDIA\nJohn Doe\n1234 5678 9012...",
    "confidence": 85.5,
    "language_detected": "en",
    "processing_time_ms": 2500
  }
}
```

### Extract Entities

```bash
curl -X POST "http://localhost:8000/api/v1/document/extract-entities" \
  -F "file=@aadhaar_card.jpg"
```

### Map to Form Template

```bash
curl -X POST "http://localhost:8000/api/v1/document/process-and-map?form_id=passport_application" \
  -F "file=@pan_card.pdf"
```

## 🔧 Configuration

Edit `app/config.py` to customize:

- **UPLOAD_DIR**: Where uploaded files are stored
- **ALLOWED_EXTENSIONS**: Accepted file types
- **MAX_FILE_SIZE**: Maximum upload size (default: 10MB)
- **TESSERACT_LANG**: OCR languages (default: `eng+hin`)
- **OCR_CONFIDENCE_THRESHOLD**: Minimum confidence for auto-fill

## 🎯 Supported Documents

| Document | ID Format | Fields Extracted |
|----------|-----------|------------------|
| Aadhaar Card | XXXX XXXX XXXX | Name, DOB, Gender, Address, Aadhaar Number |
| PAN Card | ABCDE1234F | Name, Father's Name, DOB, PAN Number |
| Voter ID | ABC1234567 | Name, Father's Name, Address, Voter ID |

## 🛣️ Roadmap

- [ ] spaCy NER integration for better entity extraction
- [ ] Whisper voice input integration
- [ ] More Indian language support (Tamil, Telugu, etc.)
- [ ] Custom form template upload
- [ ] PDF form filling and generation
- [ ] Document verification/validation

## 📜 License

MIT License - See LICENSE file for details.

