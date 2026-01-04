# Cloud OCR API Setup Guide

This guide explains how to configure cloud OCR APIs for better accuracy than local OCR.

## Supported Providers

1. **Google Cloud Vision API** - Excellent accuracy, good for documents
2. **AWS Textract** - Best for forms and structured documents
3. **Azure Computer Vision** - Good accuracy, Microsoft ecosystem

## Quick Setup

### Option 1: Google Cloud Vision API (Recommended)

1. **Get API Key:**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing
   - Enable "Cloud Vision API"
   - Go to "APIs & Services" > "Credentials"
   - Create API Key
   - Restrict the key to "Cloud Vision API" for security

2. **Set Environment Variable:**
   ```bash
   export GOOGLE_VISION_API_KEY="your_api_key_here"
   ```

   Or create a `.env` file in the backend directory:
   ```
   GOOGLE_VISION_API_KEY=your_api_key_here
   ```

3. **Install Dependencies (Optional - for REST API):**
   ```bash
   pip install requests
   ```

### Option 2: AWS Textract

1. **Get AWS Credentials:**
   - Go to [AWS Console](https://console.aws.amazon.com/)
   - Create IAM user with Textract permissions
   - Generate Access Key ID and Secret Access Key

2. **Set Environment Variables:**
   ```bash
   export AWS_ACCESS_KEY_ID="your_access_key"
   export AWS_SECRET_ACCESS_KEY="your_secret_key"
   export AWS_REGION="us-east-1"
   ```

   Or in `.env` file:
   ```
   AWS_ACCESS_KEY_ID=your_access_key
   AWS_SECRET_ACCESS_KEY=your_secret_key
   AWS_REGION=us-east-1
   ```

3. **Install Dependencies:**
   ```bash
   pip install boto3
   ```

### Option 3: Azure Computer Vision

1. **Create Azure Resource:**
   - Go to [Azure Portal](https://portal.azure.com/)
   - Create "Computer Vision" resource
   - Get the endpoint URL and API key

2. **Set Environment Variables:**
   ```bash
   export AZURE_VISION_KEY="your_api_key"
   export AZURE_VISION_ENDPOINT="https://your-resource.cognitiveservices.azure.com/"
   ```

   Or in `.env` file:
   ```
   AZURE_VISION_KEY=your_api_key
   AZURE_VISION_ENDPOINT=https://your-resource.cognitiveservices.azure.com/
   ```

3. **Install Dependencies:**
   ```bash
   pip install azure-cognitiveservices-vision-computervision
   ```

## How It Works

1. The system automatically detects which API keys are configured
2. It selects the best available provider in this order:
   - Google Vision (if `GOOGLE_VISION_API_KEY` is set)
   - AWS Textract (if AWS credentials are set)
   - Azure Vision (if Azure credentials are set)
   - Local OCR (fallback if no cloud APIs configured)

3. If cloud OCR fails, it automatically falls back to local OCR

## Pricing (Approximate)

- **Google Vision:** $1.50 per 1,000 images (first 1,000 free/month)
- **AWS Textract:** $1.50 per 1,000 pages (first 1,000 free/month)
- **Azure Vision:** $1.00 per 1,000 transactions (first 5,000 free/month)

## Testing

After setting up, restart the backend server. Check the logs to see which OCR provider is being used:

```
INFO: Using cloud OCR provider: google_vision
```

or

```
INFO: Using local OCR (no cloud API keys configured)
```

## Benefits of Cloud OCR

- **Much better accuracy** (especially for Aadhaar cards and forms)
- **Better handling of multiple languages** (Hindi + English)
- **Structured text extraction** (tables, forms, etc.)
- **No local dependencies** (no need for Tesseract installation)

## Troubleshooting

1. **"Cloud OCR not available"** - Make sure environment variables are set correctly
2. **"API key invalid"** - Check that the API key is correct and has proper permissions
3. **"Rate limit exceeded"** - You've hit the API quota, wait or upgrade plan
4. **Falling back to local OCR** - Check backend logs for error messages

