# OCR.space API Setup (Free & Easy!)

OCR.space is a free OCR API that's perfect for getting started. It's easy to set up and provides good accuracy.

## Your API Key

Your OCR.space API key is: **K83977044988957**

## Quick Setup (3 Steps)

### Step 1: Install requests library

```bash
cd backend
pip install requests
```

Or if using virtual environment:
```bash
cd backend
.\venv\Scripts\Activate.ps1
pip install requests
```

### Step 2: Set Environment Variable

**Option A: PowerShell (Temporary - for this session only)**
```powershell
$env:OCR_SPACE_API_KEY="K83977044988957"
```

**Option B: Create .env file (Permanent - Recommended)**

Create a file named `.env` in the `backend` directory with:
```
OCR_SPACE_API_KEY=K83977044988957
```

### Step 3: Restart Backend Server

Stop the backend server (Ctrl+C) and restart it:
```bash
cd backend
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --port 8000
```

## Verify It's Working

Check the backend logs when it starts. You should see:
```
INFO: Using cloud OCR provider: ocr_space
```

If you see:
```
INFO: Using local OCR (no cloud API keys configured)
```

Then the environment variable wasn't set correctly. Make sure:
1. The `.env` file is in the `backend` directory (same folder as `app`)
2. The file is named exactly `.env` (not `.env.txt`)
3. The backend server was restarted after creating the file

## Benefits of OCR.space

✅ **Free** - 25,000 requests per day (free tier)  
✅ **Easy Setup** - Just an API key, no complex configuration  
✅ **Good Accuracy** - Better than local OCR for documents  
✅ **Multi-language** - Supports English + Hindi  
✅ **PDF Support** - Works with PDFs and images  

## Testing

After setup, try uploading an Aadhaar card or other document. The extraction should be much better than before!

## Troubleshooting

1. **"requests not installed"** - Run `pip install requests`
2. **Still using local OCR** - Check that `.env` file exists and backend was restarted
3. **API errors** - Check that the API key is correct (K83977044988957)
4. **Rate limit** - Free tier allows 25,000 requests/day, should be plenty for testing

## API Key Limits

- **Free Tier:** 25,000 requests per day
- **Rate Limit:** 2 requests per second
- **File Size:** Max 1 MB (images), 4 MB (PDFs)

For production use, you might want to upgrade to a paid plan or use Google Vision/AWS Textract.

