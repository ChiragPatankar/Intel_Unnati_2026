"""
Cloud OCR Service
Supports multiple cloud OCR APIs with fallback to local OCR.
APIs supported:
- Google Cloud Vision API
- AWS Textract
- Azure Computer Vision
"""
import os
import base64
import time
from pathlib import Path
from typing import Optional, Dict, Any, List
from enum import Enum

from app.config import OCR_CONFIDENCE_THRESHOLD
from app.models.schemas import OCRResult
from app.utils.logger import get_logger

logger = get_logger(__name__)


class OCRProvider(str, Enum):
    """Supported OCR providers"""
    OCR_SPACE = "ocr_space"  # Free OCR API - easiest to use
    GOOGLE_VISION = "google_vision"
    AWS_TEXTRACT = "aws_textract"
    AZURE_VISION = "azure_vision"
    LOCAL = "local"  # Fallback to Tesseract/EasyOCR


class CloudOCRService:
    """
    Cloud OCR Service with multiple provider support.
    Automatically selects the best available provider.
    """
    
    def __init__(self):
        """Initialize the cloud OCR service."""
        self.provider = self._detect_provider()
        logger.info(f"CloudOCRService initialized with provider: {self.provider}")
    
    def _detect_provider(self) -> OCRProvider:
        """Detect which OCR provider is available based on environment variables."""
        # Check for OCR.space (free and easiest)
        if os.getenv("OCR_SPACE_API_KEY"):
            return OCRProvider.OCR_SPACE
        
        # Check for Google Cloud Vision
        if os.getenv("GOOGLE_APPLICATION_CREDENTIALS") or os.getenv("GOOGLE_VISION_API_KEY"):
            return OCRProvider.GOOGLE_VISION
        
        # Check for AWS Textract
        if os.getenv("AWS_ACCESS_KEY_ID") and os.getenv("AWS_SECRET_ACCESS_KEY"):
            return OCRProvider.AWS_TEXTRACT
        
        # Check for Azure Vision
        if os.getenv("AZURE_VISION_KEY") and os.getenv("AZURE_VISION_ENDPOINT"):
            return OCRProvider.AZURE_VISION
        
        # Fallback to local OCR
        return OCRProvider.LOCAL
    
    def extract_text(self, file_path: Path) -> OCRResult:
        """
        Extract text from document using the configured OCR provider.
        
        Args:
            file_path: Path to the document (PDF or image)
            
        Returns:
            OCRResult with extracted text and metadata
        """
        start_time = time.time()
        logger.info(f"Starting cloud OCR extraction for: {file_path.name} using {self.provider}")
        
        try:
            if self.provider == OCRProvider.OCR_SPACE:
                result = self._extract_with_ocr_space(file_path)
            elif self.provider == OCRProvider.GOOGLE_VISION:
                result = self._extract_with_google_vision(file_path)
            elif self.provider == OCRProvider.AWS_TEXTRACT:
                result = self._extract_with_aws_textract(file_path)
            elif self.provider == OCRProvider.AZURE_VISION:
                result = self._extract_with_azure_vision(file_path)
            else:
                # Fallback to local OCR
                from app.services.ocr_service import OCRService
                local_ocr = OCRService()
                result = local_ocr.extract_text(file_path)
            
            processing_time_ms = int((time.time() - start_time) * 1000)
            logger.info(f"OCR extraction completed in {processing_time_ms}ms using {self.provider}")
            
            return result
            
        except Exception as e:
            logger.error(f"Cloud OCR extraction failed: {str(e)}")
            # Fallback to local OCR on error
            logger.info("Falling back to local OCR...")
            from app.services.ocr_service import OCRService
            local_ocr = OCRService()
            return local_ocr.extract_text(file_path)
    
    def _extract_with_ocr_space(self, file_path: Path) -> OCRResult:
        """Extract text using OCR.space Free OCR API."""
        try:
            import requests
            
            api_key = os.getenv("OCR_SPACE_API_KEY")
            if not api_key:
                raise ValueError("OCR_SPACE_API_KEY not set")
            
            # OCR.space API endpoint
            url = "https://api.ocr.space/parse/image"
            
            # Determine if it's a PDF or image
            is_pdf = file_path.suffix.lower() == '.pdf'
            
            # Prepare the request
            with open(file_path, 'rb') as f:
                files = {'file': (file_path.name, f, 'application/pdf' if is_pdf else 'image/jpeg')}
                data = {
                    'apikey': api_key,
                    'language': 'eng',  # OCR.space supports: eng, hin, or eng+hin (but eng+hin may not work, use eng for now)
                    'isOverlayRequired': False,
                    'detectOrientation': True,
                    'scale': True,
                    'OCREngine': 2,  # Use OCR Engine 2 (better accuracy)
                }
                
                # Try with Hindi if available, but fallback to English if it fails
                # OCR.space language codes: eng, hin, tam, tel, kan, mal, etc.
                # For multi-language, we'll use English first (most reliable)
                
                # For PDFs, add PDF-specific parameters
                if is_pdf:
                    data['filetype'] = 'PDF'
                
                response = requests.post(url, files=files, data=data, timeout=60)
                response.raise_for_status()
                
                result = response.json()
                
                # Check for errors
                if result.get('OCRExitCode') != 1:
                    error_message = result.get('ErrorMessage', ['Unknown error'])
                    if isinstance(error_message, list) and len(error_message) > 0:
                        error_message = error_message[0]
                    elif not isinstance(error_message, str):
                        error_message = str(error_message)
                    raise Exception(f"OCR.space API error: {error_message}")
                
                # Extract text from all pages
                full_text = ""
                parsed_results = result.get('ParsedResults', [])
                
                for parsed_result in parsed_results:
                    page_text = parsed_result.get('ParsedText', '')
                    if page_text:
                        full_text += page_text + '\n\n'
                
                # Try Hindi extraction if English didn't get much text (for Hindi text in documents)
                if len(full_text.strip()) < 50:
                    try:
                        # Reopen file for second call with Hindi language
                        with open(file_path, 'rb') as f_hin:
                            files_hin = {'file': (file_path.name, f_hin, 'application/pdf' if is_pdf else 'image/jpeg')}
                            data_hin = data.copy()
                            data_hin['language'] = 'hin'
                            if is_pdf:
                                data_hin['filetype'] = 'PDF'
                            
                            response_hin = requests.post(url, files=files_hin, data=data_hin, timeout=60)
                            response_hin.raise_for_status()
                            result_hin = response_hin.json()
                            
                            if result_hin.get('OCRExitCode') == 1:
                                hin_text = ""
                                for parsed_result in result_hin.get('ParsedResults', []):
                                    hin_text += parsed_result.get('ParsedText', '') + '\n\n'
                                # Use Hindi result if it's longer (more text extracted)
                                if len(hin_text.strip()) > len(full_text.strip()):
                                    full_text = hin_text
                    except Exception as e:
                        logger.debug(f"Hindi extraction fallback failed: {str(e)}, using English result")
                        pass  # If Hindi extraction fails, use English result
                
                # Calculate confidence (OCR.space doesn't provide per-word confidence)
                # Estimate based on exit code and result quality
                confidence = 85.0 if result.get('OCRExitCode') == 1 else 50.0
                
                # If text is very short, lower confidence
                if len(full_text.strip()) < 10:
                    confidence = 30.0
                
                return OCRResult(
                    raw_text=full_text.strip(),
                    confidence=confidence,
                    processing_time_ms=0,
                    language="en"
                )
                
        except ImportError:
            raise Exception("requests not installed. Install with: pip install requests")
        except Exception as e:
            logger.error(f"OCR.space extraction failed: {str(e)}")
            raise
    
    def _extract_with_google_vision(self, file_path: Path) -> OCRResult:
        """Extract text using Google Cloud Vision API."""
        try:
            from google.cloud import vision
            from google.oauth2 import service_account
            
            # Initialize client
            credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
            if credentials_path:
                credentials = service_account.Credentials.from_service_account_file(credentials_path)
                client = vision.ImageAnnotatorClient(credentials=credentials)
            else:
                # Use API key
                api_key = os.getenv("GOOGLE_VISION_API_KEY")
                if not api_key:
                    raise ValueError("GOOGLE_VISION_API_KEY not set")
                # For API key, we'll use REST API
                return self._extract_with_google_vision_rest(file_path, api_key)
            
            # Read file
            with open(file_path, 'rb') as image_file:
                content = image_file.read()
            
            # For PDFs, use async batch processing
            if file_path.suffix.lower() == '.pdf':
                return self._extract_pdf_with_google_vision(file_path, client)
            
            # For images, use direct OCR
            image = vision.Image(content=content)
            response = client.document_text_detection(image=image)
            
            if response.error.message:
                raise Exception(f"Google Vision API error: {response.error.message}")
            
            full_text = response.full_text_annotation.text if response.full_text_annotation else ""
            confidence = 95.0  # Google Vision doesn't provide per-word confidence, assume high
            
            return OCRResult(
                raw_text=full_text,
                confidence=confidence,
                processing_time_ms=0,
                language="en"
            )
            
        except ImportError:
            raise Exception("google-cloud-vision not installed. Install with: pip install google-cloud-vision")
        except Exception as e:
            logger.error(f"Google Vision extraction failed: {str(e)}")
            raise
    
    def _extract_with_google_vision_rest(self, file_path: Path, api_key: str) -> OCRResult:
        """Extract text using Google Vision REST API (for API key authentication)."""
        import requests
        
        # Read and encode image
        with open(file_path, 'rb') as image_file:
            image_content = base64.b64encode(image_file.read()).decode('utf-8')
        
        # API endpoint
        url = f"https://vision.googleapis.com/v1/images:annotate?key={api_key}"
        
        # Request payload
        payload = {
            "requests": [{
                "image": {"content": image_content},
                "features": [{"type": "DOCUMENT_TEXT_DETECTION"}]
            }]
        }
        
        response = requests.post(url, json=payload)
        response.raise_for_status()
        
        result = response.json()
        if 'responses' in result and result['responses']:
            text_annotations = result['responses'][0].get('textAnnotations', [])
            if text_annotations:
                full_text = text_annotations[0].get('description', '')
                confidence = 95.0
                
                return OCRResult(
                    raw_text=full_text,
                    confidence=confidence,
                    processing_time_ms=0,
                    language="en"
                )
        
        return OCRResult(
            raw_text="",
            confidence=0,
            processing_time_ms=0,
            language="en"
        )
    
    def _extract_pdf_with_google_vision(self, file_path: Path, client) -> OCRResult:
        """Extract text from PDF using Google Vision (requires async batch processing)."""
        # For now, convert PDF to images and process
        from app.services.ocr_service import OCRService
        local_ocr = OCRService()
        return local_ocr.extract_text(file_path)
    
    def _extract_with_aws_textract(self, file_path: Path) -> OCRResult:
        """Extract text using AWS Textract."""
        try:
            import boto3
            
            # Initialize Textract client
            textract = boto3.client('textract',
                                  aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                                  aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
                                  region_name=os.getenv("AWS_REGION", "us-east-1"))
            
            # Read file
            with open(file_path, 'rb') as document:
                image_bytes = document.read()
            
            # For PDFs, use async job
            if file_path.suffix.lower() == '.pdf':
                return self._extract_pdf_with_textract(file_path, textract)
            
            # For images, use synchronous detection
            response = textract.detect_document_text(Document={'Bytes': image_bytes})
            
            # Extract text and confidence
            full_text = ""
            confidences = []
            
            for block in response.get('Blocks', []):
                if block['BlockType'] == 'LINE':
                    full_text += block.get('Text', '') + '\n'
                if 'Confidence' in block:
                    confidences.append(block['Confidence'])
            
            avg_confidence = sum(confidences) / len(confidences) if confidences else 90.0
            
            return OCRResult(
                raw_text=full_text.strip(),
                confidence=avg_confidence,
                processing_time_ms=0,
                language="en"
            )
            
        except ImportError:
            raise Exception("boto3 not installed. Install with: pip install boto3")
        except Exception as e:
            logger.error(f"AWS Textract extraction failed: {str(e)}")
            raise
    
    def _extract_pdf_with_textract(self, file_path: Path, textract) -> OCRResult:
        """Extract text from PDF using AWS Textract async job."""
        # Start async job
        with open(file_path, 'rb') as document:
            job_id = textract.start_document_text_detection(
                DocumentLocation={'S3Object': {'Bucket': 'temp', 'Name': str(file_path)}}
            )['JobId']
        
        # For now, fallback to local OCR for PDFs
        from app.services.ocr_service import OCRService
        local_ocr = OCRService()
        return local_ocr.extract_text(file_path)
    
    def _extract_with_azure_vision(self, file_path: Path) -> OCRResult:
        """Extract text using Azure Computer Vision API."""
        try:
            from azure.cognitiveservices.vision.computervision import ComputerVisionClient
            from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
            from msrest.authentication import CognitiveServicesCredentials
            
            # Initialize client
            endpoint = os.getenv("AZURE_VISION_ENDPOINT")
            key = os.getenv("AZURE_VISION_KEY")
            
            if not endpoint or not key:
                raise ValueError("AZURE_VISION_ENDPOINT and AZURE_VISION_KEY must be set")
            
            client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(key))
            
            # Read file
            with open(file_path, 'rb') as image_file:
                image_data = image_file.read()
            
            # For PDFs, use read API (async)
            if file_path.suffix.lower() == '.pdf':
                return self._extract_pdf_with_azure_vision(file_path, client, image_data)
            
            # For images, use OCR API
            result = client.recognize_printed_text_in_stream(image_data)
            
            # Extract text
            full_text = ""
            for region in result.regions:
                for line in region.lines:
                    for word in line.words:
                        full_text += word.text + " "
                    full_text += "\n"
            
            # Calculate average confidence
            confidences = []
            for region in result.regions:
                for line in region.lines:
                    for word in line.words:
                        if hasattr(word, 'confidence'):
                            confidences.append(word.confidence * 100)
            
            avg_confidence = sum(confidences) / len(confidences) if confidences else 90.0
            
            return OCRResult(
                raw_text=full_text.strip(),
                confidence=avg_confidence,
                processing_time_ms=0,
                language="en"
            )
            
        except ImportError:
            raise Exception("azure-cognitiveservices-vision-computervision not installed. Install with: pip install azure-cognitiveservices-vision-computervision")
        except Exception as e:
            logger.error(f"Azure Vision extraction failed: {str(e)}")
            raise
    
    def _extract_pdf_with_azure_vision(self, file_path: Path, client, image_data) -> OCRResult:
        """Extract text from PDF using Azure Vision read API."""
        # For now, fallback to local OCR for PDFs
        from app.services.ocr_service import OCRService
        local_ocr = OCRService()
        return local_ocr.extract_text(file_path)

