# 🇮🇳 AI-Powered Form Filling Assistant for Indian Citizen Services

An intelligent web application that automatically fills Indian government service forms using uploaded documents (Aadhaar, PAN, Voter ID) and voice input.

## 🎯 Project Overview

This MVP helps Indian citizens quickly fill government forms by:
1. **Uploading ID documents** (PDF/Image)
2. **Extracting information** using OCR
3. **Auto-mapping data** to form templates
4. **Reviewing and editing** before submission

## 📁 Project Structure

```
Intel_Unnati/
├── backend/                 # FastAPI Backend
│   ├── app/
│   │   ├── main.py         # FastAPI application
│   │   ├── config.py       # Configuration
│   │   ├── api/routes/     # API endpoints
│   │   ├── services/       # Business logic
│   │   ├── models/         # Pydantic schemas
│   │   └── utils/          # Utilities
│   ├── uploads/            # Document storage
│   └── requirements.txt
│
└── frontend/               # React Frontend (Coming Soon)
    └── (Vite React App)
```

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| **Frontend** | React (Vite) |
| **Backend** | FastAPI (Python) |
| **OCR** | Tesseract + EasyOCR |
| **NLP** | spaCy (rule-based → ML) |
| **Voice** | Whisper (planned) |
| **PDF** | PyPDF2 + ReportLab |
| **Storage** | Local filesystem |

## 🚀 Quick Start

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/macOS

# Install dependencies
pip install -r requirements.txt

# Setup environment variables (optional - for cloud OCR)
# Copy .env.example to .env and add your API keys
cp .env.example .env  # Linux/macOS
copy .env.example .env  # Windows

# Run the server
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The frontend will be available at http://localhost:5173

### Access API Documentation
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 📊 Processing Pipeline

```
┌─────────────────┐
│ Document Upload │ ─── PDF/Image (Aadhaar, PAN, Voter ID)
└────────┬────────┘
         ▼
┌─────────────────┐
│   OCR Engine    │ ─── Tesseract + EasyOCR
└────────┬────────┘
         ▼
┌─────────────────┐
│ Entity Extract  │ ─── Name, DOB, Address, ID Numbers
└────────┬────────┘
         ▼
┌─────────────────┐
│  Form Mapping   │ ─── Match to government form templates
└────────┬────────┘
         ▼
┌─────────────────┐
│ Preview & Edit  │ ─── User review before submission
└─────────────────┘
```

## 📡 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/document/upload` | POST | Upload document & run OCR |
| `/api/v1/document/extract-entities` | POST | Extract structured data |
| `/api/v1/document/process-and-map` | POST | Full pipeline processing |
| `/api/v1/document/templates` | GET | List form templates |

## 🎯 Supported Documents

- ✅ Aadhaar Card
- ✅ PAN Card
- ✅ Voter ID (EPIC)

## 🌐 Supported Languages

- ✅ **UI Languages (8):** English, Hindi, Tamil, Telugu, Marathi, Bengali, Gujarati, Kannada
- ✅ **Voice Input (10):** All above + Malayalam, Punjabi

## ✅ Implemented Features

### Core Features ✅
- [x] Document upload (PDF/Image) with drag & drop
- [x] OCR processing (Tesseract + EasyOCR + Cloud OCR)
- [x] Entity extraction with confidence scoring
- [x] Form field mapping to 6 government templates
- [x] React frontend with modern UI
- [x] Voice input with multi-language support
- [x] Multi-language UI (8 languages)
- [x] PDF generation and preview
- [x] Form preview and editing
- [x] Performance benchmarks

### Government Form Templates ✅
1. Aadhaar Update Form
2. Ration Card Application
3. Birth Certificate Request
4. Driving License Application
5. Passport Application
6. Voter ID Enrollment

### Cloud OCR Support ✅
- Google Cloud Vision API
- AWS Textract
- Azure Computer Vision
- OCR.space API
- Automatic fallback to local OCR

## 📋 Future Enhancements

- [ ] Handwritten text recognition
- [ ] ML-based NER for better accuracy
- [ ] DigiLocker integration
- [ ] Document verification
- [ ] Digital signature support

## 🤝 Contributing

Contributions are welcome! Please read our contributing guidelines before submitting PRs.

## 📜 License

MIT License - See LICENSE for details.

---

Built with ❤️ for Indian Citizens | Intel Unnati Project

