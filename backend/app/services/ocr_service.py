"""
OCR Service
Handles text extraction from documents using Tesseract and EasyOCR.
Automatically uses GPU (CUDA) if available, otherwise falls back to CPU.
"""

import time
from pathlib import Path
from typing import Optional, Dict, Any, List
import re

from app.config import TESSERACT_LANG, EASYOCR_LANGS, OCR_CONFIDENCE_THRESHOLD
from app.models.schemas import OCRResult
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Lazy imports for OCR libraries (only load when needed)
_pytesseract = None
_easyocr_reader = None
_pdf2image = None
_PIL_Image = None


def _get_pytesseract():
    """Lazy load pytesseract."""
    global _pytesseract
    if _pytesseract is None:
        import pytesseract
        _pytesseract = pytesseract
        logger.info("Pytesseract loaded successfully")
    return _pytesseract


def _get_easyocr_reader():
    """
    Lazy load EasyOCR reader.
    EasyOCR is loaded only once and reused (it's heavy to initialize).
    """
    global _easyocr_reader
    if _easyocr_reader is None:
        import easyocr
        import torch
        
        # Use GPU if available, otherwise fall back to CPU
        use_gpu = torch.cuda.is_available()
        _easyocr_reader = easyocr.Reader(EASYOCR_LANGS, gpu=use_gpu)
        device = "GPU (CUDA)" if use_gpu else "CPU"
        logger.info(f"EasyOCR reader loaded with languages: {EASYOCR_LANGS} on {device}")
    return _easyocr_reader


def _get_pdf2image():
    """Lazy load pdf2image."""
    global _pdf2image
    if _pdf2image is None:
        from pdf2image import convert_from_path
        _pdf2image = convert_from_path
        logger.info("pdf2image loaded successfully")
    return _pdf2image


def _get_pil_image():
    """Lazy load PIL Image."""
    global _PIL_Image
    if _PIL_Image is None:
        from PIL import Image
        _PIL_Image = Image
    return _PIL_Image


class OCRService:
    """
    OCR Service for extracting text from documents.
    Uses Tesseract as primary OCR and EasyOCR as fallback for better accuracy.
    """
    
    def __init__(self):
        """Initialize the OCR service."""
        logger.info("OCRService initialized")
    
    def _pdf_to_images(self, pdf_path: Path) -> List[Any]:
        """
        Convert PDF pages to images for OCR processing.
        Uses high DPI (300) for better OCR accuracy.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            List of PIL Image objects (one per page)
        """
        convert_from_path = _get_pdf2image()
        Image = _get_pil_image()
        try:
            # Use 300 DPI for better OCR accuracy (standard for OCR)
            images = convert_from_path(pdf_path, dpi=300, fmt='png')
            logger.info(f"PDF converted to {len(images)} page(s) at 300 DPI")
            
            # Preprocess images for better OCR
            processed_images = []
            for img in images:
                processed = self._preprocess_image(img)
                processed_images.append(processed)
            
            return processed_images
        except Exception as e:
            logger.error(f"PDF to image conversion failed: {str(e)}")
            raise
    
    def _preprocess_image(self, image) -> Any:
        """
        Preprocess image to improve OCR accuracy with aggressive enhancement.
        - Converts to RGB if needed
        - Denoises image
        - Enhances contrast aggressively
        - Sharpens image
        - Converts to grayscale for better OCR
        - Applies adaptive thresholding for better text recognition
        
        Args:
            image: PIL Image object
            
        Returns:
            Preprocessed PIL Image
        """
        Image = _get_pil_image()
        from PIL import ImageEnhance, ImageFilter
        import numpy as np
        
        try:
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Convert to grayscale for better OCR (removes color noise)
            if image.mode != 'L':
                image = image.convert('L')
            
            # Denoise first (reduce noise before enhancement)
            image = image.filter(ImageFilter.MedianFilter(size=3))
            
            # Aggressive contrast enhancement (important for scanned documents)
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(2.0)  # Increase contrast by 100% (was 1.5)
            
            # Brightness adjustment (make text darker, background lighter)
            enhancer = ImageEnhance.Brightness(image)
            image = enhancer.enhance(0.9)  # Slightly darker
            
            # Sharpen image (helps with blurry text)
            image = image.filter(ImageFilter.SHARPEN)
            image = image.filter(ImageFilter.SHARPEN)  # Apply twice for better effect
            
            # Enhance sharpness
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(1.5)  # Increase sharpness by 50% (was 1.2)
            
            # Convert to numpy for advanced processing (optional enhancement)
            try:
                import numpy as np
                img_array = np.array(image)
                
                # Apply adaptive thresholding (better than global threshold for varying lighting)
                # This makes text more distinct from background
                try:
                    from scipy import ndimage
                    # Use local mean for adaptive thresholding
                    local_mean = ndimage.uniform_filter(img_array.astype(np.float32), size=15)
                    threshold = local_mean - 10  # Slight offset
                    img_array = np.where(img_array > threshold, 255, 0).astype(np.uint8)
                except ImportError:
                    # If scipy not available, use simple thresholding
                    threshold_value = np.mean(img_array) - 20
                    img_array = np.where(img_array > threshold_value, 255, 0).astype(np.uint8)
                
                # Convert back to PIL Image
                image = Image.fromarray(img_array)
            except ImportError:
                # If numpy not available, skip advanced preprocessing
                logger.debug("numpy not available, skipping advanced preprocessing")
            except Exception as e:
                logger.debug(f"Advanced preprocessing failed: {str(e)}, using basic preprocessing")
            
            return image
        except Exception as e:
            logger.warning(f"Image preprocessing failed: {str(e)}, using original")
            return image
    
    def _extract_with_tesseract(self, image) -> Dict[str, Any]:
        """
        Extract text using Tesseract OCR.
        
        Args:
            image: PIL Image object
            
        Returns:
            Dict with 'text' and 'confidence'
        """
        pytesseract = _get_pytesseract()
        
        try:
            # Try multiple PSM modes for better accuracy on structured documents like Aadhaar
            # PSM 6: Single uniform block (default for documents)
            # PSM 11: Sparse text (good for forms with labels)
            # PSM 12: Single line (good for extracting specific fields)
            # PSM 4: Single column (good for structured cards)
            
            best_text = ""
            best_confidence = 0
            best_config = r'--oem 3 --psm 6'
            
            # Try different PSM modes and pick the best result
            psm_modes = [
                (6, r'--oem 3 --psm 6'),   # Single uniform block
                (11, r'--oem 3 --psm 11'), # Sparse text (forms)
                (4, r'--oem 3 --psm 4'),   # Single column
                (12, r'--oem 3 --psm 12'), # Single line
            ]
            
            for psm_num, config in psm_modes:
                try:
                    # Get detailed data including confidence
                    data = pytesseract.image_to_data(
                        image, 
                        lang=TESSERACT_LANG,
                        config=config,
                        output_type=pytesseract.Output.DICT
                    )
                    
                    # Calculate average confidence (excluding -1 values which mean no text)
                    confidences = [
                        conf for conf in data['conf'] 
                        if isinstance(conf, (int, float)) and conf >= 0
                    ]
                    avg_confidence = sum(confidences) / len(confidences) if confidences else 0
                    
                    # Get full text with same config
                    text = pytesseract.image_to_string(image, lang=TESSERACT_LANG, config=config)
                    
                    # Prefer longer text with good confidence
                    text_length = len(text.strip())
                    score = avg_confidence * 0.7 + (min(text_length, 500) / 500) * 30
                    
                    if score > best_confidence or (text_length > len(best_text) and avg_confidence > 50):
                        best_text = text
                        best_confidence = avg_confidence
                        best_config = config
                except Exception as e:
                    logger.debug(f"PSM {psm_num} failed: {str(e)}")
                    continue
            
            # Use the best result
            text = best_text
            avg_confidence = best_confidence
            
            # If we got no good result, fall back to default
            if not text.strip():
                custom_config = r'--oem 3 --psm 6'
                data = pytesseract.image_to_data(
                    image, 
                    lang=TESSERACT_LANG,
                    config=custom_config,
                    output_type=pytesseract.Output.DICT
                )
                confidences = [
                    conf for conf in data['conf'] 
                    if isinstance(conf, (int, float)) and conf >= 0
                ]
                avg_confidence = sum(confidences) / len(confidences) if confidences else 0
                text = pytesseract.image_to_string(image, lang=TESSERACT_LANG, config=custom_config)
            
            # Clean up text (remove excessive whitespace but preserve line breaks)
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            text = '\n'.join(lines)
            
            # Apply OCR error correction for common mistakes
            text = self._correct_ocr_errors(text)
            
            return {
                'text': text.strip(),
                'confidence': avg_confidence
            }
        except Exception as e:
            logger.warning(f"Tesseract extraction failed: {str(e)}")
            return {'text': '', 'confidence': 0}
    
    def _extract_with_easyocr(self, image_path: str) -> Dict[str, Any]:
        """
        Extract text using EasyOCR (better for Indian languages).
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Dict with 'text' and 'confidence'
        """
        reader = _get_easyocr_reader()
        
        try:
            # EasyOCR returns list of (bbox, text, confidence)
            results = reader.readtext(image_path)
            
            if not results:
                return {'text': '', 'confidence': 0}
            
            # Combine all text and calculate average confidence
            texts = []
            confidences = []
            
            for (bbox, text, conf) in results:
                texts.append(text)
                confidences.append(conf * 100)  # Convert to percentage
            
            full_text = ' '.join(texts)
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            return {
                'text': full_text,
                'confidence': avg_confidence
            }
        except Exception as e:
            logger.warning(f"EasyOCR extraction failed: {str(e)}")
            return {'text': '', 'confidence': 0}
    
    def _correct_ocr_errors(self, text: str) -> str:
        """
        Correct common OCR errors in extracted text.
        Helps fix character misrecognitions common in OCR.
        """
        # Common OCR error corrections
        corrections = {
            # Common character misrecognitions
            r'\b0\b': 'O',  # Zero to O (context-dependent, be careful)
            r'rn': 'm',     # rn often misread as m
            r'vv': 'w',     # vv often misread as w
            r'ii': 'n',     # ii often misread as n
            r'cl': 'd',     # cl often misread as d
            # Common word corrections for addresses
            r'\bFlat\s+no\b': 'Flat no',
            r'\bWing\b': 'Wing',
            r'\bRoad\b': 'Road',
            r'\bArea\b': 'Area',
            r'\bWest\b': 'West',
            r'\bEast\b': 'East',
            r'\bNorth\b': 'North',
            r'\bSouth\b': 'South',
            # Fix common spacing issues
            r'(\d)\s+(\d)': r'\1\2',  # Remove spaces between digits
            r'([A-Z])\s+([a-z])': r'\1\2',  # Fix space between capital and lowercase
        }
        
        # Apply corrections (be conservative to avoid over-correction)
        for pattern, replacement in corrections.items():
            try:
                text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
            except:
                pass  # Skip if pattern fails
        
        return text
    
    def _detect_language(self, text: str) -> str:
        """
        Simple language detection based on character analysis.
        
        Args:
            text: The extracted text
            
        Returns:
            Detected language code ('en', 'hi', etc.)
        """
        # Check for Devanagari script (Hindi)
        hindi_pattern = re.compile(r'[\u0900-\u097F]')
        if hindi_pattern.search(text):
            return 'hi'  # Hindi detected
        
        # TODO: Add detection for other Indian languages (Tamil, Telugu, etc.)
        
        return 'en'  # Default to English
    
    def extract_text(self, file_path: Path, use_easyocr: bool = True) -> OCRResult:
        """
        Main method to extract text from a document.
        
        Pipeline:
        1. If PDF: Convert to images
        2. Run Tesseract OCR
        3. If confidence is low, try EasyOCR
        4. Return best result
        
        Args:
            file_path: Path to the document (PDF or image)
            use_easyocr: Whether to use EasyOCR as fallback
            
        Returns:
            OCRResult with extracted text and metadata
        """
        start_time = time.time()
        logger.info(f"Starting OCR extraction for: {file_path.name}")
        
        file_ext = file_path.suffix.lower()
        Image = _get_pil_image()
        
        all_text = []
        all_confidences = []
        
        try:
            # Determine images to process
            if file_ext == '.pdf':
                images = self._pdf_to_images(file_path)
                is_pdf = True
            else:
                # Load and preprocess regular images too
                img = Image.open(file_path)
                processed_img = self._preprocess_image(img)
                images = [processed_img]
                is_pdf = False
            
            # Process each image/page
            for idx, image in enumerate(images):
                logger.debug(f"Processing page/image {idx + 1}")
                
                # For PDFs, always try both OCR engines and use the best result
                # For images, try Tesseract first, then EasyOCR if confidence is low
                tess_result = self._extract_with_tesseract(image)
                
                # Save image temporarily for EasyOCR (needs file path)
                temp_path = None
                try:
                    if is_pdf:
                        temp_path = file_path.parent / f"temp_page_{idx}_{int(time.time())}.png"
                    else:
                        temp_path = file_path.parent / f"temp_img_{int(time.time())}.png"
                    
                    image.save(temp_path, 'PNG', quality=95)
                    
                    # For PDFs, always try EasyOCR; for images, only if Tesseract confidence is low
                    should_try_easyocr = (is_pdf or tess_result['confidence'] < OCR_CONFIDENCE_THRESHOLD) and use_easyocr
                    
                    if should_try_easyocr:
                        logger.debug(f"Trying EasyOCR (Tesseract confidence: {tess_result['confidence']:.1f})")
                        easy_result = self._extract_with_easyocr(str(temp_path))
                        
                        # Use the result with more text or higher confidence
                        tess_text_len = len(tess_result['text'].strip())
                        easy_text_len = len(easy_result['text'].strip())
                        
                        # Prefer result with more text, or higher confidence if text length is similar
                        if easy_text_len > tess_text_len * 1.2:  # EasyOCR has 20% more text
                            all_text.append(easy_result['text'])
                            all_confidences.append(easy_result['confidence'])
                            logger.debug(f"Using EasyOCR result (text: {easy_text_len} chars, confidence: {easy_result['confidence']:.1f})")
                        elif easy_result['confidence'] > tess_result['confidence'] * 1.1:  # EasyOCR has 10% higher confidence
                            all_text.append(easy_result['text'])
                            all_confidences.append(easy_result['confidence'])
                            logger.debug(f"Using EasyOCR result (confidence: {easy_result['confidence']:.1f})")
                        else:
                            all_text.append(tess_result['text'])
                            all_confidences.append(tess_result['confidence'])
                            logger.debug(f"Using Tesseract result (text: {tess_text_len} chars, confidence: {tess_result['confidence']:.1f})")
                    else:
                        all_text.append(tess_result['text'])
                        all_confidences.append(tess_result['confidence'])
                finally:
                    # Clean up temp file
                    if temp_path and temp_path.exists():
                        try:
                            temp_path.unlink()
                        except Exception as e:
                            logger.warning(f"Failed to delete temp file {temp_path}: {str(e)}")
            
            # Combine results
            combined_text = '\n\n'.join(all_text)
            avg_confidence = sum(all_confidences) / len(all_confidences) if all_confidences else 0
            
            # Detect primary language
            language = self._detect_language(combined_text)
            
            processing_time = int((time.time() - start_time) * 1000)
            
            logger.info(
                f"OCR completed: {len(combined_text)} chars, "
                f"confidence: {avg_confidence:.1f}%, "
                f"time: {processing_time}ms"
            )
            
            return OCRResult(
                raw_text=combined_text,
                confidence=round(avg_confidence, 2),
                language_detected=language,
                processing_time_ms=processing_time
            )
            
        except Exception as e:
            logger.error(f"OCR extraction failed: {str(e)}")
            processing_time = int((time.time() - start_time) * 1000)
            
            # Return empty result with error indication
            return OCRResult(
                raw_text="",
                confidence=0,
                language_detected=None,
                processing_time_ms=processing_time
            )


# Singleton instance
ocr_service = OCRService()

