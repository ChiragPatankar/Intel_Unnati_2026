"""
Profile Management API Routes
Handles user profile CRUD and document association.
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Query
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

from app.services.profile_storage import profile_storage_service
from app.services.document_upload import upload_service
from app.services.ocr_service import ocr_service
from app.services.entity_extraction import entity_extraction_service
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/profile", tags=["Profile Management"])


# =============================================================================
# REQUEST/RESPONSE MODELS
# =============================================================================

class CreateProfileRequest(BaseModel):
    """Request to create a new profile."""
    name: str = Field(..., min_length=1, max_length=100, description="Profile name")
    fields: Optional[Dict[str, str]] = Field(default=None, description="Initial fields")


class UpdateProfileRequest(BaseModel):
    """Request to update profile fields."""
    fields: Dict[str, str] = Field(..., description="Fields to update")


class ProfileSummary(BaseModel):
    """Profile summary for listing."""
    id: str
    name: str
    created_at: str
    updated_at: str
    document_count: int
    field_count: int


class ProfileResponse(BaseModel):
    """Full profile response."""
    id: str
    name: str
    created_at: str
    updated_at: str
    documents: List[Dict[str, Any]]
    fields: Dict[str, Any]


# =============================================================================
# ENDPOINTS
# =============================================================================

@router.post("/create", response_model=ProfileResponse)
async def create_profile(request: CreateProfileRequest):
    """
    Create a new profile to store document data.
    
    Profiles allow you to:
    - Store extracted document information
    - Access data via Chrome extension
    - Auto-fill forms on any website
    """
    profile = profile_storage_service.create_profile(
        name=request.name,
        data=request.fields
    )
    return profile


@router.get("/list", response_model=List[ProfileSummary])
async def list_profiles():
    """
    List all profiles.
    
    Returns summary information for each profile.
    """
    return profile_storage_service.list_profiles()


@router.get("/{profile_id}", response_model=ProfileResponse)
async def get_profile(profile_id: str):
    """
    Get a profile by ID.
    
    Returns full profile data including all fields.
    """
    profile = profile_storage_service.get_profile(profile_id)
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    return profile


@router.put("/{profile_id}", response_model=ProfileResponse)
async def update_profile(profile_id: str, request: UpdateProfileRequest):
    """
    Update profile fields.
    
    Merges new fields with existing ones.
    """
    profile = profile_storage_service.update_profile(profile_id, request.fields)
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    return profile


@router.delete("/{profile_id}")
async def delete_profile(profile_id: str):
    """
    Delete a profile.
    """
    deleted = profile_storage_service.delete_profile(profile_id)
    
    if not deleted:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    return {"message": f"Profile {profile_id} deleted"}


@router.post("/{profile_id}/upload-document")
async def upload_document_to_profile(
    profile_id: str,
    file: UploadFile = File(..., description="Document to upload and extract")
):
    """
    Upload a document, extract data, and add to profile.
    
    Complete flow:
    1. Upload document
    2. Run OCR
    3. Extract entities
    4. Save to profile
    """
    # Verify profile exists
    profile = profile_storage_service.get_profile(profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    logger.info(f"Uploading document to profile {profile_id}: {file.filename}")
    
    try:
        # Save file
        file_id, file_path = await upload_service.save_file(file)
        
        # Run OCR
        ocr_result = ocr_service.extract_text(file_path)
        
        if not ocr_result.raw_text:
            raise HTTPException(
                status_code=422,
                detail="Could not extract text from document"
            )
        
        # Extract entities
        extraction_result, _ = entity_extraction_service.extract_entities_enhanced(
            text=ocr_result.raw_text,
            ocr_confidence=ocr_result.confidence
        )
        
        # Convert entities to simple dict
        extracted_fields = {
            name: entity.value
            for name, entity in extraction_result.entities.items()
        }
        
        # Add to profile
        updated_profile = profile_storage_service.add_document_to_profile(
            profile_id=profile_id,
            document_type=extraction_result.document_type.value,
            extracted_fields=extracted_fields,
            file_id=file_id
        )
        
        return {
            "message": "Document processed and added to profile",
            "document_type": extraction_result.document_type.value,
            "extracted_fields": extracted_fields,
            "profile": updated_profile
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Document upload to profile failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{profile_id}/autofill")
async def get_autofill_data(profile_id: str):
    """
    Get profile data formatted for auto-fill.
    
    Returns a flat key-value dictionary suitable for
    form auto-filling via the Chrome extension.
    """
    fields = profile_storage_service.get_profile_for_autofill(profile_id)
    
    if fields is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    # Also include common field aliases for better form matching
    autofill_data = {**fields}
    
    # Add common aliases
    if 'full_name' in fields:
        autofill_data['name'] = fields['full_name']
        autofill_data['fullname'] = fields['full_name']
        # Split name for first/last name fields
        name_parts = fields['full_name'].split()
        if len(name_parts) >= 2:
            autofill_data['first_name'] = name_parts[0]
            autofill_data['firstname'] = name_parts[0]
            autofill_data['last_name'] = name_parts[-1]
            autofill_data['lastname'] = name_parts[-1]
            if len(name_parts) > 2:
                autofill_data['middle_name'] = ' '.join(name_parts[1:-1])
    
    if 'dob' in fields:
        autofill_data['date_of_birth'] = fields['dob']
        autofill_data['dateofbirth'] = fields['dob']
        autofill_data['birthdate'] = fields['dob']
    
    if 'aadhaar_number' in fields:
        autofill_data['aadhaar'] = fields['aadhaar_number']
        autofill_data['uid'] = fields['aadhaar_number']
    
    if 'pan_number' in fields:
        autofill_data['pan'] = fields['pan_number']
    
    if 'father_name' in fields:
        autofill_data['fathername'] = fields['father_name']
        autofill_data['fathers_name'] = fields['father_name']
    
    if 'pincode' in fields:
        autofill_data['pin'] = fields['pincode']
        autofill_data['postal_code'] = fields['pincode']
        autofill_data['zip'] = fields['pincode']
    
    return {
        "profile_id": profile_id,
        "fields": autofill_data
    }

