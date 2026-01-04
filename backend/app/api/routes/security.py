"""
Security API Routes
Handles master password and encryption management.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.encryption_service import encryption_service
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/security", tags=["Security"])


# =============================================================================
# REQUEST/RESPONSE MODELS
# =============================================================================

class SetPasswordRequest(BaseModel):
    """Request to set master password."""
    password: str = Field(..., min_length=8, description="Master password (min 8 chars)")


class UnlockRequest(BaseModel):
    """Request to unlock encryption."""
    password: str = Field(..., description="Master password")


class ChangePasswordRequest(BaseModel):
    """Request to change master password."""
    old_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, description="New password")


class SecurityStatusResponse(BaseModel):
    """Security status response."""
    password_set: bool
    unlocked: bool
    encryption_enabled: bool = True


# =============================================================================
# ENDPOINTS
# =============================================================================

@router.get("/status", response_model=SecurityStatusResponse)
async def get_security_status():
    """
    Get current security/encryption status.
    
    Returns whether master password is set and if encryption is unlocked.
    """
    return SecurityStatusResponse(
        password_set=encryption_service.is_master_password_set(),
        unlocked=encryption_service.is_unlocked(),
    )


@router.post("/set-password")
async def set_master_password(request: SetPasswordRequest):
    """
    Set the master password for encryption.
    
    Must be called before encryption can be used.
    Password must be at least 8 characters.
    """
    try:
        encryption_service.set_master_password(request.password)
        return {"message": "Master password set successfully", "unlocked": True}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/unlock")
async def unlock_encryption(request: UnlockRequest):
    """
    Unlock encryption with the master password.
    
    Must be called after server restart to access encrypted data.
    """
    if not encryption_service.is_master_password_set():
        raise HTTPException(
            status_code=400, 
            detail="No master password set. Call /security/set-password first."
        )
    
    success = encryption_service.unlock(request.password)
    
    if not success:
        raise HTTPException(status_code=401, detail="Invalid password")
    
    return {"message": "Encryption unlocked", "unlocked": True}


@router.post("/lock")
async def lock_encryption():
    """
    Lock encryption.
    
    Clears the encryption key from memory.
    Requires password to unlock again.
    """
    encryption_service.lock()
    return {"message": "Encryption locked", "unlocked": False}


@router.post("/change-password")
async def change_master_password(request: ChangePasswordRequest):
    """
    Change the master password.
    
    Requires the current password for verification.
    """
    try:
        success = encryption_service.change_password(
            request.old_password, 
            request.new_password
        )
        
        if not success:
            raise HTTPException(status_code=401, detail="Invalid current password")
        
        return {"message": "Password changed successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

