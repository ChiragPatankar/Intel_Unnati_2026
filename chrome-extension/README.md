# Form Filling Assistant - Chrome Extension

Auto-fill forms on any website using your stored Indian ID documents.

## Installation

1. Open Chrome and go to `chrome://extensions/`
2. Enable **Developer mode** (toggle in top right)
3. Click **Load unpacked**
4. Select the `chrome-extension` folder

## Setup

Before using the extension:

1. Make sure the backend is running: `http://localhost:8000`
2. Make sure the frontend is running: `http://localhost:5173`
3. Create at least one profile in the web app and upload your documents

## Usage

1. Click the extension icon in Chrome toolbar
2. Select a profile from the dropdown
3. Navigate to any form you want to fill
4. Click **Auto-Fill This Page**

## Adding Icons

Replace the placeholder icons in the `icons/` folder:
- `icon16.png` - 16x16 pixels (toolbar icon)
- `icon48.png` - 48x48 pixels (extensions page)
- `icon128.png` - 128x128 pixels (Chrome Web Store)

## Features

- ✅ Profile selection from saved data
- ✅ Auto-detect form fields
- ✅ Smart field matching (name, DOB, address, etc.)
- ✅ Visual feedback when fields are filled
- ✅ Floating button on pages with forms
- ✅ Masks sensitive data (Aadhaar, PAN) in preview

## Supported Form Fields

- Name (full, first, last, middle, father's)
- Date of Birth
- Aadhaar Number
- PAN Number
- Voter ID
- Address, Pincode, City, State
- Gender
- Email, Phone

## Troubleshooting

**Extension shows "Server not running"**
- Start the backend: `cd backend && uvicorn app.main:app --reload --port 8000`

**No profiles available**
- Open the web app and create a profile first
- Upload at least one document to the profile

**Fields not being filled**
- Check if the form uses standard input fields
- Some forms use custom components that may not be detected

