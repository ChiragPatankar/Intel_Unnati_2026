# Form Filling Assistant - Frontend

Minimal React frontend for the AI-powered form filling assistant.

## Features

- 📄 Upload documents (PDF, PNG, JPG, etc.)
- 🔍 Extract data using backend OCR & NER
- ✏️ Edit extracted fields with confidence indicators
- 📥 Download results as JSON
- 📋 Copy to clipboard

## Quick Start

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

The app will be available at http://localhost:5173

## Requirements

- Node.js 18+
- Backend running on http://localhost:8000

## Project Structure

```
frontend/
├── src/
│   ├── main.jsx          # Entry point
│   ├── App.jsx           # Main component
│   ├── api.js            # Backend API calls
│   ├── index.css         # Minimal styling
│   └── components/
│       ├── FileUpload.jsx      # Document upload
│       └── ExtractedFields.jsx # Editable form display
├── index.html
├── package.json
└── vite.config.js
```

## API Integration

The frontend proxies `/api` requests to the backend at `localhost:8000`. This is configured in `vite.config.js`.

## Confidence Levels

| Level | Color | Score |
|-------|-------|-------|
| High | Green | ≥ 85% |
| Medium | Orange | 60-84% |
| Low | Red | < 60% |

Fields with low confidence are highlighted for review.

