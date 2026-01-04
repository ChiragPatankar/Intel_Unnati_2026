# AI-Powered Form Filling Assistant - Design Document

## 📋 Project Overview

An AI-powered tool that auto-fills Indian government service forms using uploaded documents (Aadhaar, PAN, Voter ID, Passport, Driving License) and voice input, reducing manual effort and errors at Seva Kendras.

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              USER INTERFACE                                  │
├─────────────────────┬─────────────────────┬─────────────────────────────────┤
│   React Web App     │  Chrome Extension   │     Voice Input Module          │
│   (localhost:5173)  │  (Manifest V3)      │     (Web Speech API)            │
└─────────────────────┴─────────────────────┴─────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           FASTAPI BACKEND                                    │
│                         (localhost:8000)                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │  Document   │  │    OCR      │  │   Entity    │  │   Form Mapping      │ │
│  │   Upload    │→ │  Service    │→ │ Extraction  │→ │    Service          │ │
│  │  Service    │  │             │  │  Service    │  │                     │ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────────────┘ │
│         │                │                │                    │            │
│         ▼                ▼                ▼                    ▼            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │   Profile   │  │ Encryption  │  │   Logger    │  │   Template          │ │
│  │  Storage    │  │  Service    │  │   Utility   │  │   Engine            │ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          STORAGE LAYER                                       │
├──────────────────────────┬──────────────────────────────────────────────────┤
│    Local File System     │           Encrypted JSON Profiles                │
│    (uploads/, profiles/) │           (AES-256 Encryption)                   │
└──────────────────────────┴──────────────────────────────────────────────────┘
```

---

## 📊 Data Flow Diagram

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Document   │     │     OCR      │     │    Entity    │     │     Form     │
│    Upload    │────▶│   Process    │────▶│  Extraction  │────▶│   Mapping    │
│  (PDF/Image) │     │              │     │              │     │              │
└──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
       │                    │                    │                    │
       │                    │                    │                    │
       ▼                    ▼                    ▼                    ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  File saved  │     │  Raw text    │     │  Structured  │     │  Filled      │
│  to uploads/ │     │  extracted   │     │  entities    │     │  template    │
│              │     │  (Tesseract  │     │  with        │     │  (JSON/PDF)  │
│              │     │  + EasyOCR)  │     │  confidence  │     │              │
└──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘

                    ┌─────────────────────────────────────┐
                    │          VOICE INPUT FLOW           │
                    │                                     │
                    │  🎤 → Web Speech API → Text →       │
                    │       Pattern Matching → Fields     │
                    └─────────────────────────────────────┘
```

---

## 🔧 Component Details

### 1. Document Upload Service (`document_upload.py`)
- **Purpose**: Handle file uploads, validation, and storage
- **Supported Formats**: PDF, PNG, JPG, JPEG
- **Max File Size**: 10MB
- **Storage**: Local filesystem with UUID-based naming

### 2. OCR Service (`ocr_service.py`)
- **Primary Engine**: Tesseract OCR (CPU-optimized)
- **Secondary Engine**: EasyOCR (GPU-accelerated, multi-language)
- **Supported Languages**: English, Hindi
- **PDF Handling**: pdf2image for page conversion
- **Output**: Raw text with confidence scores

### 3. Entity Extraction Service (`entity_extraction.py`)
- **Method**: Rule-based regex with confidence scoring
- **Supported Documents**:
  | Document Type | Extracted Fields |
  |--------------|------------------|
  | Aadhaar | Number, Name, DOB, Gender, Address |
  | PAN | Number, Name, Father's Name, DOB |
  | Passport | Number, Name, DOB, Place of Issue |
  | Voter ID | EPIC Number, Name, Father's Name, Address |
  | Driving License | DL Number, Name, DOB, Address |
  | Bank Statement | Account Number, IFSC Code |

- **Confidence Scoring**:
  ```
  Confidence = (Pattern Match × 0.4) + (Context Match × 0.3) + (Format Validation × 0.3)
  ```

### 4. Form Mapping Service (`form_mapping.py`)
- **Templates**: Passport, Voter ID Registration, Generic
- **Mapping Logic**: Field name normalization + fuzzy matching
- **Output Format**: JSON with field mappings

### 5. Profile Storage Service (`profile_storage.py`)
- **Storage Format**: JSON files
- **Encryption**: AES-256 (Fernet)
- **Features**: CRUD operations, document linking

### 6. Encryption Service (`encryption_service.py`)
- **Algorithm**: AES-256 via Fernet
- **Key Derivation**: PBKDF2-HMAC-SHA256 (480,000 iterations)
- **Master Password**: Required for encryption/decryption
- **Salt Storage**: Per-installation unique salt

---

## 🌐 API Documentation

### Base URL: `http://localhost:8000/api/v1`

### Document Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/document/upload` | Upload document for OCR |
| POST | `/document/extract-entities` | Extract entities from document |
| POST | `/document/extract-entities-enhanced` | Extract with confidence scores |
| POST | `/document/process-and-map` | Full pipeline: OCR → Extract → Map |
| GET | `/document/templates` | Get available form templates |
| DELETE | `/document/{file_id}` | Delete uploaded document |

### Profile Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/profile/create` | Create new profile |
| GET | `/profile/list` | List all profiles |
| GET | `/profile/{id}` | Get profile by ID |
| PUT | `/profile/{id}` | Update profile |
| DELETE | `/profile/{id}` | Delete profile |
| POST | `/profile/{id}/upload-document` | Add document to profile |
| GET | `/profile/{id}/autofill` | Get autofill data with aliases |

### Security Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/security/status` | Check encryption status |
| POST | `/security/set-password` | Set master password |
| POST | `/security/unlock` | Unlock with password |
| POST | `/security/lock` | Lock encryption |
| POST | `/security/change-password` | Change master password |

### Health Check

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | API health status |

---

## 📱 Chrome Extension Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    CHROME EXTENSION                          │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────────┐  │
│  │   Popup     │    │   Content   │    │  Field Matcher  │  │
│  │  (popup.js) │◄──▶│   Script    │◄──▶│ (fuzzy match)   │  │
│  └─────────────┘    └─────────────┘    └─────────────────┘  │
│         │                  │                                 │
│         ▼                  ▼                                 │
│  ┌─────────────┐    ┌─────────────┐                         │
│  │  Backend    │    │   Form      │                         │
│  │    API      │    │  Auto-Fill  │                         │
│  └─────────────┘    └─────────────┘                         │
└─────────────────────────────────────────────────────────────┘
```

### Field Matching Algorithm
1. **Signal Collection**: name, id, placeholder, aria-label, label text
2. **Pattern Matching**: Regex against field database
3. **Fuzzy Matching**: Levenshtein distance for similarity
4. **Confidence Calculation**: Weighted score (0-100)
5. **Threshold Filter**: Only fill fields with confidence > 30%

---

## 🎤 Voice Input Module

### Supported Languages
- Hindi (hi-IN)
- English (en-IN)
- Tamil (ta-IN)
- Telugu (te-IN)
- Marathi (mr-IN)
- Bengali (bn-IN)
- Gujarati (gu-IN)
- Kannada (kn-IN)
- Malayalam (ml-IN)
- Punjabi (pa-IN)

### Voice Commands
| Command | Example |
|---------|---------|
| Name | "My name is Rajesh Kumar" / "मेरा नाम राजेश कुमार" |
| Father's Name | "Father's name is Suresh" |
| Phone | "Phone number is 9876543210" |
| Address | "I live at 123 Main Street" |
| Aadhaar | "Aadhaar number is 1234 5678 9012" |

---

## 🔒 Security Model

```
┌─────────────────────────────────────────────────────────────┐
│                    SECURITY LAYERS                           │
├─────────────────────────────────────────────────────────────┤
│  Layer 1: Master Password                                    │
│  ├── PBKDF2-HMAC-SHA256 (480K iterations)                   │
│  └── Password never stored, only verification hash          │
├─────────────────────────────────────────────────────────────┤
│  Layer 2: Data Encryption                                    │
│  ├── AES-256 (Fernet)                                       │
│  └── Per-profile encryption                                  │
├─────────────────────────────────────────────────────────────┤
│  Layer 3: Local Storage                                      │
│  ├── No cloud storage                                        │
│  └── All data stays on user's device                        │
└─────────────────────────────────────────────────────────────┘
```

---

## 📈 Performance Specifications

| Metric | Target | Actual |
|--------|--------|--------|
| OCR Latency (CPU) | ≤ 5s | 3-8s (depends on quality) |
| OCR Latency (GPU) | ≤ 2s | 1-3s |
| Entity Extraction | ≤ 500ms | ~200ms |
| Form Mapping | ≤ 100ms | ~50ms |
| Total Pipeline | ≤ 5s | 3-10s |
| Entity Accuracy | > 90% | ~92% (clean docs) |

---

## 📁 Project Structure

```
Intel_Unnati/
├── backend/
│   ├── app/
│   │   ├── api/routes/          # API endpoints
│   │   ├── models/              # Pydantic schemas
│   │   ├── services/            # Business logic
│   │   └── utils/               # Helpers
│   ├── profiles/                # User profiles (JSON)
│   ├── uploads/                 # Uploaded documents
│   ├── tests/                   # Test files
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/          # React components
│   │   ├── api.js               # API client
│   │   └── App.jsx              # Main app
│   └── package.json
├── chrome-extension/
│   ├── manifest.json
│   ├── popup.html/js/css
│   ├── content.js
│   └── field-matcher.js
├── DESIGN.md                    # This document
├── TESTING_GUIDE.md
└── README.md
```

---

## 🧪 Testing Strategy

1. **Unit Tests**: Entity extraction patterns
2. **Integration Tests**: API endpoints
3. **E2E Tests**: Full document pipeline
4. **Performance Tests**: Latency benchmarks

---

## 🚀 Deployment

### Development
```bash
# Backend
cd backend
python -m venv venv
.\venv\Scripts\activate  # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend
npm install
npm run dev
```

### Chrome Extension
1. Go to `chrome://extensions/`
2. Enable Developer mode
3. Click "Load unpacked"
4. Select `chrome-extension/` folder

---

## 📊 Future Enhancements

1. **DigiLocker Integration**: Direct document fetch
2. **Government API**: Direct form submission
3. **Handwritten Text**: Specialized OCR models
4. **Offline Mode**: Service workers for offline capability
5. **Mobile App**: React Native version

---

## 👥 Authors

- Intel Unnati Project Team

## 📄 License

MIT License

