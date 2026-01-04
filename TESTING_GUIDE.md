# Form Filling Assistant - Testing Guide

## 🧪 Automated Test Results

| Test Category | Status | Details |
|--------------|--------|---------|
| Profile Creation | ✅ PASS | Created with 16 fields |
| Profile Retrieval | ✅ PASS | All fields retrieved |
| Autofill Aliases | ✅ PASS | 32 fields (with aliases like firstname, lastname) |
| Profile Update | ✅ PASS | Fields merged correctly |
| Profile List | ✅ PASS | Lists all profiles |
| Profile Delete | ✅ PASS | Deleted successfully |
| Security Status | ✅ PASS | Encryption enabled |
| Aadhaar Pattern | ✅ PASS | Regex validated |
| PAN Pattern | ✅ PASS | Regex validated |
| Passport Pattern | ✅ PASS | Regex validated |

## 🔐 Security Testing (Encryption)

### Verified Working:
1. **Set Master Password**: `POST /api/v1/security/set-password`
2. **Lock Encryption**: `POST /api/v1/security/lock`
3. **Unlock Encryption**: `POST /api/v1/security/unlock`
4. **Wrong Password Rejected**: Returns 401 Unauthorized
5. **Status Check**: `GET /api/v1/security/status`

### Test Commands (PowerShell):
```powershell
# Check status
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/security/status"

# Set password (first time only)
$body = @{password="YourPassword123!"} | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/security/set-password" -Method POST -ContentType "application/json" -Body $body

# Lock
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/security/lock" -Method POST

# Unlock
$body = @{password="YourPassword123!"} | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/security/unlock" -Method POST -ContentType "application/json" -Body $body
```

## 🌙 Dark Mode Testing

### Frontend (http://localhost:5173)
1. Click the 🌙/☀️ button in the header
2. Mode should toggle between light and dark
3. Refresh the page - mode should persist
4. **Persistence**: Stored in `localStorage.theme`

### Chrome Extension
1. Click extension icon
2. Click the 🌙/☀️ button in popup header
3. Theme should change
4. Close and reopen - should persist

## 🔍 Fuzzy Field Matching - Test Websites

### Test on DemoQA (https://demoqa.com/automation-practice-form)
Fields to match:
- First Name → `first_name` or `firstname`
- Last Name → `last_name` or `lastname`
- Email → `email`
- Gender (Radio) → `gender`
- Mobile → `phone` or `mobile`
- Current Address → `address`

### Test on W3Schools (https://www.w3schools.com/html/tryit.asp?filename=tryhtml_form_submit)
Basic form with `fname`, `lname` fields.

### Test on LinkedIn (https://www.linkedin.com/signup)
- First name → `first_name`
- Last name → `last_name`
- Email → `email`

### Expected Matching Behavior:
| Form Field Name | Should Match Profile Field |
|----------------|---------------------------|
| fname, firstName, first_name | first_name |
| lname, lastName, last_name | last_name |
| email, emailAddress, email_id | email |
| phone, mobile, tel, contact | phone |
| dob, dateOfBirth, birth_date | dob |
| addr, address, street | address |
| pin, pincode, zip, postal | pincode |
| gender, sex | gender |

## ⌨️ Keyboard Shortcut Testing

1. Navigate to any form page
2. Install and enable the Chrome extension
3. Select a profile in the extension popup
4. Press **Ctrl+Shift+F** (or **Cmd+Shift+F** on Mac)
5. Form should auto-fill with profile data

## 📊 Console Logging

### Browser Console (F12 → Console)
When auto-fill runs, you should see:
```
[Form Filler] DEBUG Found 12 form elements
[Form Filler] DEBUG Data keys: ["full_name", "email", ...]
[FieldMatcher] Analyzing: firstName { signals: {...} }
[FieldMatcher] Match found: firstName → first_name (score: 95.0, via: name-exact, pattern)
[Form Filler] ✓ Filled first_name = "RAJESH" (95% confidence)
...
[Form Filler] Fill complete: 8/12 fields
```

### Backend Console
When extracting entities:
```
INFO | app.services.ocr_service | OCR completed: 151 chars, confidence: 76.6%, time: 21748ms
INFO | app.services.entity_extraction | Starting enhanced entity extraction
INFO | app.services.entity_extraction | Document type detected: aadhaar (confidence: 0.95)
INFO | app.services.entity_extraction | Enhanced extraction complete: 5 entities, overall confidence: 0.65, needs_review: True, time: 4ms
```

## 🏃 Running Tests

```bash
# Navigate to backend
cd backend

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Run automated tests
python tests/test_workflow.py

# Or with pytest
pytest tests/test_workflow.py -v
```

## 📝 Manual Testing Checklist

### Profile Management
- [ ] Create profile with name
- [ ] Upload Aadhaar document
- [ ] Upload PAN document
- [ ] Verify extracted fields
- [ ] Edit a field manually
- [ ] Delete a profile

### Auto-Fill
- [ ] Open a form website
- [ ] Click extension icon
- [ ] Select profile
- [ ] Click "Auto-Fill This Page"
- [ ] Verify fields are filled
- [ ] Check console for confidence scores

### Dark Mode
- [ ] Toggle dark mode in web app
- [ ] Refresh page - mode persists
- [ ] Toggle in extension popup
- [ ] Close/reopen popup - mode persists

### Security
- [ ] Set master password
- [ ] Lock encryption
- [ ] Try to unlock with wrong password (should fail)
- [ ] Unlock with correct password

## 🐛 Known Issues

1. **Tesseract not in PATH**: Install Tesseract and add to system PATH
2. **OCR taking long**: First request loads EasyOCR models (~10s)
3. **GPU not detected**: EasyOCR runs on CPU if no CUDA available

## 📧 Support

For issues, check:
1. Backend logs in terminal running uvicorn
2. Browser console (F12) for frontend/extension errors
3. API docs at http://localhost:8000/docs

