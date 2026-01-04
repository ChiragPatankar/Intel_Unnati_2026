"""
Form-related API routes
Handles form template selection, mapping, and PDF generation
"""
from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import Response, StreamingResponse
from typing import Optional
import io

from app.services.form_templates import form_templates_service, FormType
from app.services.pdf_generator import pdf_generator_service
from app.services.entity_extraction import EntityExtractionService
from app.services.ocr_service import OCRService
from app.services.document_upload import DocumentUploadService

# Try to import cloud OCR (optional)
try:
    from app.services.cloud_ocr_service import CloudOCRService
    CLOUD_OCR_AVAILABLE = True
except ImportError:
    CLOUD_OCR_AVAILABLE = False
    CloudOCRService = None
from app.models.schemas import EnhancedExtractionResult
from app.utils.logger import get_logger
from app.utils.data_validation import (
    validate_aadhaar, validate_pan, validate_pincode, 
    clean_name, clean_date, clean_address
)

router = APIRouter(prefix="/forms", tags=["forms"])

logger = get_logger(__name__)

# Use cloud OCR if API keys are configured, otherwise fallback to local OCR
# Note: .env file should be loaded by main.py before this module is imported
if CLOUD_OCR_AVAILABLE:
    try:
        cloud_ocr_service = CloudOCRService()
        # Check if cloud OCR is actually available (not just local fallback)
        if cloud_ocr_service.provider.value != "local":
            ocr_service = cloud_ocr_service
            logger.info(f"✓ Using cloud OCR provider: {cloud_ocr_service.provider.value}")
        else:
            ocr_service = OCRService()
            logger.info("Using local OCR (no cloud API keys configured)")
    except Exception as e:
        logger.warning(f"Cloud OCR initialization failed: {str(e)}, using local OCR")
        ocr_service = OCRService()
else:
    ocr_service = OCRService()
    logger.info("Using local OCR (cloud OCR not available)")

entity_extraction_service = EntityExtractionService()
upload_service = DocumentUploadService()


def _clean_entity_value(key: str, value: str) -> str:
    """Clean and validate entity value based on field type."""
    if not value:
        return ""
    
    value = str(value).strip()
    
    # Clean based on field type
    if 'aadhaar' in key.lower():
        is_valid, cleaned = validate_aadhaar(value)
        return cleaned if is_valid else value
    elif 'pan' in key.lower():
        is_valid, cleaned = validate_pan(value)
        return cleaned if is_valid else value
    elif 'pincode' in key.lower() or 'pin' in key.lower():
        is_valid, cleaned = validate_pincode(value)
        return cleaned if is_valid else value
    elif 'name' in key.lower():
        return clean_name(value)
    elif 'dob' in key.lower() or 'date' in key.lower():
        cleaned = clean_date(value)
        if cleaned:
            # Convert to YYYY-MM-DD format for HTML date inputs
            # Try to parse DD/MM/YYYY or DD-MM-YYYY
            import re
            date_match = re.match(r'(\d{1,2})[/\-](\d{1,2})[/\-](\d{4})', cleaned)
            if date_match:
                day, month, year = date_match.groups()
                # Format as YYYY-MM-DD for HTML date input
                return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
            # Try YYYY-MM-DD format (already correct)
            if re.match(r'\d{4}-\d{2}-\d{2}', cleaned):
                return cleaned
        return cleaned if cleaned else value
    elif 'address' in key.lower():
        return clean_address(value)
    else:
        return value


@router.get("/templates")
async def list_form_templates():
    """Get list of available form templates"""
    templates = form_templates_service.list_templates()
    return {"templates": templates}


@router.get("/templates/{form_id}")
async def get_form_template(form_id: str):
    """Get details of a specific form template"""
    template = form_templates_service.get_template(form_id)
    if not template:
        raise HTTPException(status_code=404, detail=f"Form template '{form_id}' not found")
    
    return {
        "id": template.form_id,
        "name": template.name,
        "fields": {
            field_name: {
                "label": config["label"],
                "required": config["required"],
                "type": config["type"],
                "options": config.get("options", [])  # Include options for select fields
            }
            for field_name, config in template.fields.items()
        }
    }


@router.post("/map-data/{form_id}")
async def map_extracted_data_to_form(
    form_id: str,
    extracted_data: dict
):
    """
    Map extracted entities to form fields
    
    Body should contain:
    {
        "entities": {
            "name": {"value": "...", "confidence": 0.9},
            "dob": {"value": "...", "confidence": 0.8},
            ...
        }
    }
    """
    # Validate form_id exists
    template = form_templates_service.get_template(form_id)
    if not template:
        raise HTTPException(status_code=404, detail=f"Form template '{form_id}' not found")
    
    entities = extracted_data.get("entities", {})
    
    # Extract just the values for mapping
    entity_values = {}
    for key, value in entities.items():
        if isinstance(value, dict):
            entity_values[key] = value.get("value", "")
        else:
            entity_values[key] = value
    
    mapped_data = form_templates_service.map_extracted_data_to_form(
        form_id=form_id,
        extracted_entities=entity_values
    )
    
    return {
        "form_id": form_id,
        "mapped_fields": mapped_data,
        "completion_rate": sum(1 for f in mapped_data.values() if f.get("filled")) / len(mapped_data) if mapped_data else 0
    }


@router.post("/generate/{form_id}")
async def generate_filled_form_pdf(
    form_id: str,
    form_data: dict
):
    """
    Generate a filled PDF form
    
    Body should contain:
    {
        "form_data": {
            "applicant_name": "Rajesh Kumar",
            "aadhaar_number": "1234-5678-9012",
            ...
        },
        "extracted_entities": {...}  # Optional, for reference
    }
    """
    # Validate form_id exists
    template = form_templates_service.get_template(form_id)
    if not template:
        raise HTTPException(status_code=404, detail=f"Form template '{form_id}' not found")
    
    # Validate form data
    validation = form_templates_service.validate_form_data(form_id, form_data.get("form_data", {}))
    if not validation["valid"]:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "Form validation failed",
                "errors": validation["errors"]
            }
        )
    
    try:
        # Generate PDF
        pdf_bytes = pdf_generator_service.generate_filled_form(
            form_id=form_id,
            form_data=form_data.get("form_data", {}),
            extracted_entities=form_data.get("extracted_entities")
        )
        
        # Return PDF as download
        filename = f"{template.name.replace(' ', '_')}_{form_id}.pdf"
        
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF: {str(e)}")


@router.post("/upload-and-map/{form_id}")
async def upload_document_and_map_to_form(
    form_id: str,
    file: UploadFile = File(...)
):
    """
    Upload document, extract entities, and map to form fields
    All-in-one endpoint for the form filling flow
    """
    # Validate form_id exists
    template = form_templates_service.get_template(form_id)
    if not template:
        raise HTTPException(status_code=404, detail=f"Form template '{form_id}' not found")
    
    try:
        # 1. Save the uploaded file
        logger.info(f"Uploading file: {file.filename}")
        file_id, file_path = await upload_service.save_file(file)
        logger.info(f"File saved: {file_id} at {file_path}")
        
        # 2. Perform OCR
        logger.info("Starting OCR extraction...")
        ocr_result = ocr_service.extract_text(file_path)
        logger.info(f"OCR completed. Text length: {len(ocr_result.raw_text)}, Confidence: {ocr_result.confidence}")
        
        # Log first 500 chars of OCR text for debugging
        ocr_preview = ocr_result.raw_text[:500] if ocr_result.raw_text else ""
        logger.info(f"OCR text preview (first 500 chars): {ocr_preview}")
        
        if not ocr_result.raw_text or len(ocr_result.raw_text.strip()) == 0:
            raise HTTPException(
                status_code=422,
                detail="OCR could not extract any text from the document. Please ensure the document is clear and readable."
            )
        
        # 3. Extract entities
        logger.info("Starting entity extraction...")
        extracted_result, extraction_time = entity_extraction_service.extract_entities_enhanced(
            text=ocr_result.raw_text,
            ocr_confidence=ocr_result.confidence
        )
        
        logger.info(f"Entity extraction completed. Found {len(extracted_result.entities)} entities")
        logger.info(f"Entity keys: {list(extracted_result.entities.keys())}")
        logger.info(f"Document type: {extracted_result.document_type}")
        
        # Log extracted values for debugging
        for key, entity in extracted_result.entities.items():
            if hasattr(entity, 'value'):
                logger.info(f"Extracted {key}: {entity.value} (confidence: {entity.confidence:.2f})")
            else:
                logger.info(f"Extracted {key}: {entity}")
        
        # 3. Map to form fields with validation and cleaning
        # EntityValue is a Pydantic model, access .value attribute
        entity_values = {}
        for key, entity_value in extracted_result.entities.items():
            # EntityValue has a .value attribute
            if hasattr(entity_value, 'value'):
                raw_value = entity_value.value
            elif isinstance(entity_value, dict):
                raw_value = entity_value.get("value", "")
            else:
                raw_value = str(entity_value) if entity_value else ""
            
            # Clean and validate based on field type
            cleaned_value = _clean_entity_value(key, raw_value)
            entity_values[key] = cleaned_value
        
        logger.info(f"Mapped entity values: {entity_values}")
        
        # 4. Map to form fields
        mapped_data = form_templates_service.map_extracted_data_to_form(
            form_id=form_id,
            extracted_entities=entity_values
        )
        
        logger.info(f"Form mapping completed. Mapped {len(mapped_data)} fields")
        filled_count = sum(1 for f in mapped_data.values() if f.get("filled"))
        logger.info(f"Filled fields: {filled_count}/{len(mapped_data)}")
        
        return {
            "form_id": form_id,
            "mapped_fields": mapped_data,
            "extracted_entities": extracted_result.model_dump(),
            "completion_rate": filled_count / len(mapped_data) if mapped_data else 0,
            "processing_time_ms": extraction_time
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Processing failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")


