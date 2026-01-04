"""
Document Processing API Routes
Handles document upload, OCR, and entity extraction endpoints.
Includes comprehensive timing measurement across the pipeline.
"""

import time
from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from typing import Optional

from app.models.schemas import (
    UploadResponse,
    ProcessingStatus,
    ProcessingTiming,
    OCRResult,
    EntityExtractionResult,
    EnhancedExtractionResult,
    FormMappingResult
)
from app.services.document_upload import upload_service
from app.services.ocr_service import ocr_service
from app.services.entity_extraction import entity_extraction_service
from app.services.form_mapping import form_mapping_service
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Create router for document-related endpoints
router = APIRouter(prefix="/document", tags=["Document Processing"])


@router.post("/upload", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(..., description="PDF or image file (Aadhaar, PAN, Voter ID)"),
    run_ocr: bool = Query(True, description="Whether to run OCR on the uploaded document")
):
    """
    Upload a document and optionally run OCR.
    
    **Accepts:**
    - PDF files
    - Images: PNG, JPG, JPEG, TIFF, BMP
    
    **Process:**
    1. Validates the file type and size
    2. Saves the file with a unique ID
    3. Runs OCR if enabled
    4. Returns extracted text and metadata
    
    **Returns:**
    - File ID for future reference
    - OCR result with extracted text (if run_ocr=True)
    - Processing timing breakdown
    """
    request_start = time.time()
    logger.info(f"Upload request received: {file.filename}")
    
    try:
        # Step 1: Save the uploaded file
        upload_start = time.time()
        file_id, file_path = await upload_service.save_file(file)
        upload_time_ms = int((time.time() - upload_start) * 1000)
        
        ocr_result: Optional[OCRResult] = None
        ocr_time_ms: Optional[int] = None
        
        # Step 2: Run OCR if requested
        if run_ocr:
            logger.info(f"Running OCR on file: {file_id}")
            ocr_result = ocr_service.extract_text(file_path)
            ocr_time_ms = ocr_result.processing_time_ms
            
            if not ocr_result.raw_text:
                total_time_ms = int((time.time() - request_start) * 1000)
                timing = ProcessingTiming(
                    upload_time_ms=upload_time_ms,
                    ocr_time_ms=ocr_time_ms,
                    total_time_ms=total_time_ms
                )
                logger.info(f"Upload partial - Total: {total_time_ms}ms (upload: {upload_time_ms}ms, OCR: {ocr_time_ms}ms)")
                
                return UploadResponse(
                    status=ProcessingStatus.PARTIAL,
                    message="File uploaded but OCR could not extract text",
                    filename=file.filename,
                    file_id=file_id,
                    ocr_result=ocr_result,
                    timing=timing
                )
        
        total_time_ms = int((time.time() - request_start) * 1000)
        timing = ProcessingTiming(
            upload_time_ms=upload_time_ms,
            ocr_time_ms=ocr_time_ms,
            total_time_ms=total_time_ms
        )
        
        logger.info(f"Upload complete - Total: {total_time_ms}ms (upload: {upload_time_ms}ms, OCR: {ocr_time_ms}ms)")
        
        return UploadResponse(
            status=ProcessingStatus.SUCCESS,
            message="Document uploaded and processed successfully",
            filename=file.filename,
            file_id=file_id,
            ocr_result=ocr_result,
            timing=timing
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.post("/extract-entities", response_model=EntityExtractionResult)
async def extract_entities(
    file: UploadFile = File(..., description="PDF or image file to extract entities from")
):
    """
    Upload a document and extract structured entities (legacy format).
    
    **Process:**
    1. Uploads and saves the file
    2. Runs OCR
    3. Extracts entities (Name, DOB, Address, ID numbers)
    4. Detects document type (Aadhaar, PAN, Voter ID)
    
    **Returns:**
    - Document type detected
    - List of extracted entities with confidence scores
    - Flag indicating if user review is needed
    
    *For enhanced output format with timing, use `/extract-entities-enhanced`*
    """
    request_start = time.time()
    logger.info(f"Entity extraction request: {file.filename}")
    
    try:
        # Save file
        upload_start = time.time()
        file_id, file_path = await upload_service.save_file(file)
        upload_time_ms = int((time.time() - upload_start) * 1000)
        
        # Run OCR
        ocr_result = ocr_service.extract_text(file_path)
        ocr_time_ms = ocr_result.processing_time_ms
        
        if not ocr_result.raw_text:
            raise HTTPException(
                status_code=422,
                detail="Could not extract text from document. Please ensure the image is clear."
            )
        
        # Extract entities (legacy format)
        extraction_result, extraction_time_ms = entity_extraction_service.extract_entities(ocr_result.raw_text)
        
        total_time_ms = int((time.time() - request_start) * 1000)
        logger.info(
            f"Entity extraction complete - Total: {total_time_ms}ms "
            f"(upload: {upload_time_ms}ms, OCR: {ocr_time_ms}ms, extraction: {extraction_time_ms}ms)"
        )
        
        return extraction_result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Entity extraction failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Extraction failed: {str(e)}")


@router.post("/extract-entities-enhanced", response_model=EnhancedExtractionResult)
async def extract_entities_enhanced(
    file: UploadFile = File(..., description="PDF or image file to extract entities from")
):
    """
    Upload a document and extract entities with ENHANCED confidence scoring.
    
    **Enhanced Features:**
    - Multi-factor confidence scoring (regex strength, OCR confidence, validation)
    - Detailed match type information
    - Language detection
    - Extraction notes and warnings
    - **Complete timing breakdown** (OCR, extraction, total)
    
    **Process:**
    1. Uploads and saves the file
    2. Runs OCR
    3. Extracts entities with detailed confidence analysis
    4. Returns structured output with notes and timing
    
    **Output Format:**
    ```json
    {
        "entities": {
            "name": { "value": "JOHN DOE", "confidence": 0.85, "match_type": "labeled_regex" },
            "dob": { "value": "15/08/1990", "confidence": 0.92, "match_type": "exact_regex" }
        },
        "detected_language": "en",
        "notes": ["Hindi text detected but English extraction prioritized"],
        "overall_confidence": 0.88,
        "needs_review": false,
        "timing": {
            "ocr_time_ms": 2500,
            "extraction_time_ms": 45,
            "upload_time_ms": 150,
            "total_time_ms": 2695
        }
    }
    ```
    
    **Confidence Levels:**
    - HIGH (≥0.85): Auto-fill recommended
    - MEDIUM (0.60-0.84): Review suggested
    - LOW (<0.60): Manual entry recommended
    """
    request_start = time.time()
    logger.info(f"Enhanced entity extraction request: {file.filename}")
    
    try:
        # Save file with timing
        upload_start = time.time()
        file_id, file_path = await upload_service.save_file(file)
        upload_time_ms = int((time.time() - upload_start) * 1000)
        
        # Run OCR
        ocr_result = ocr_service.extract_text(file_path)
        ocr_time_ms = ocr_result.processing_time_ms
        
        if not ocr_result.raw_text:
            raise HTTPException(
                status_code=422,
                detail="Could not extract text from document. Please ensure the image is clear."
            )
        
        # Extract entities with enhanced confidence scoring
        # Pass OCR confidence to improve entity confidence calculation
        extraction_result, extraction_time_ms = entity_extraction_service.extract_entities_enhanced(
            text=ocr_result.raw_text,
            ocr_confidence=ocr_result.confidence
        )
        
        # Calculate total time and build timing object
        total_time_ms = int((time.time() - request_start) * 1000)
        timing = ProcessingTiming(
            upload_time_ms=upload_time_ms,
            ocr_time_ms=ocr_time_ms,
            extraction_time_ms=extraction_time_ms,
            total_time_ms=total_time_ms
        )
        
        # Add timing to the result
        extraction_result.timing = timing
        
        logger.info(
            f"Enhanced extraction complete - Total: {total_time_ms}ms "
            f"(upload: {upload_time_ms}ms, OCR: {ocr_time_ms}ms, extraction: {extraction_time_ms}ms)"
        )
        
        return extraction_result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Enhanced entity extraction failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Extraction failed: {str(e)}")


@router.post("/process-and-map", response_model=FormMappingResult)
async def process_and_map_to_form(
    file: UploadFile = File(..., description="PDF or image file"),
    form_id: str = Query(..., description="Target form template ID")
):
    """
    Complete pipeline: Upload → OCR → Extract → Map to Form.
    
    **Process:**
    1. Uploads the document
    2. Runs OCR
    3. Extracts entities
    4. Maps entities to the specified form template
    
    **Available Forms:**
    - passport_application
    - pan_application
    - voter_registration
    
    **Returns:**
    - Form fields with mapped values
    - Completion percentage
    - Fields that need review
    - **Complete timing breakdown** for each pipeline stage
    """
    request_start = time.time()
    logger.info(f"Full processing request: {file.filename} → {form_id}")
    
    try:
        # Save file with timing
        upload_start = time.time()
        file_id, file_path = await upload_service.save_file(file)
        upload_time_ms = int((time.time() - upload_start) * 1000)
        
        # Run OCR
        ocr_result = ocr_service.extract_text(file_path)
        ocr_time_ms = ocr_result.processing_time_ms
        
        if not ocr_result.raw_text:
            raise HTTPException(
                status_code=422,
                detail="Could not extract text from document"
            )
        
        # Extract entities
        extraction_result, extraction_time_ms = entity_extraction_service.extract_entities(ocr_result.raw_text)
        
        # Map to form with timing
        mapping_start = time.time()
        form_result = form_mapping_service.map_to_form(extraction_result, form_id)
        mapping_time_ms = int((time.time() - mapping_start) * 1000)
        
        # Calculate total time and build timing object
        total_time_ms = int((time.time() - request_start) * 1000)
        timing = ProcessingTiming(
            upload_time_ms=upload_time_ms,
            ocr_time_ms=ocr_time_ms,
            extraction_time_ms=extraction_time_ms,
            mapping_time_ms=mapping_time_ms,
            total_time_ms=total_time_ms
        )
        
        # Add timing to the result
        form_result.timing = timing
        
        logger.info(
            f"Full pipeline complete - Total: {total_time_ms}ms "
            f"(upload: {upload_time_ms}ms, OCR: {ocr_time_ms}ms, "
            f"extraction: {extraction_time_ms}ms, mapping: {mapping_time_ms}ms)"
        )
        
        return form_result
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Processing failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")


@router.get("/templates")
async def get_form_templates():
    """
    Get list of available form templates.
    
    **Returns:**
    List of form templates with their IDs and names.
    """
    return {
        "templates": form_mapping_service.get_available_templates()
    }


@router.delete("/{file_id}")
async def delete_document(file_id: str):
    """
    Delete an uploaded document by its ID.
    
    **Args:**
    - file_id: The unique identifier returned during upload
    
    **Returns:**
    - Success message if deleted
    - 404 if file not found
    """
    deleted = upload_service.delete_file(file_id)
    
    if deleted:
        return {"message": f"Document {file_id} deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Document not found")

