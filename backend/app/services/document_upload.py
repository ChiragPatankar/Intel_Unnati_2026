"""
Document Upload Service
Handles file validation, saving, and management of uploaded documents.
"""

import os
import uuid
import shutil
from pathlib import Path
from typing import Tuple, Optional
from fastapi import UploadFile, HTTPException

from app.config import UPLOAD_DIR, ALLOWED_EXTENSIONS, MAX_FILE_SIZE
from app.utils.logger import get_logger

logger = get_logger(__name__)


class DocumentUploadService:
    """
    Service for handling document uploads.
    Manages file validation, storage, and retrieval.
    """
    
    def __init__(self, upload_dir: Path = UPLOAD_DIR):
        """
        Initialize the upload service.
        
        Args:
            upload_dir: Directory for storing uploaded files
        """
        self.upload_dir = upload_dir
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"DocumentUploadService initialized. Upload dir: {self.upload_dir}")
    
    def validate_file(self, file: UploadFile) -> Tuple[bool, str]:
        """
        Validate uploaded file for extension and size.
        
        Args:
            file: The uploaded file object
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check if file exists
        if not file or not file.filename:
            return False, "No file provided"
        
        # Check file extension
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            return False, f"File type '{file_ext}' not allowed. Allowed: {ALLOWED_EXTENSIONS}"
        
        logger.debug(f"File validation passed: {file.filename}")
        return True, ""
    
    async def save_file(self, file: UploadFile) -> Tuple[str, Path]:
        """
        Save uploaded file to disk with a unique identifier.
        
        Args:
            file: The uploaded file object
            
        Returns:
            Tuple of (file_id, file_path)
            
        Raises:
            HTTPException: If file validation fails or save fails
        """
        # Validate file
        is_valid, error_msg = self.validate_file(file)
        if not is_valid:
            logger.error(f"File validation failed: {error_msg}")
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Generate unique file ID
        file_id = str(uuid.uuid4())
        file_ext = Path(file.filename).suffix.lower()
        
        # Create unique filename
        unique_filename = f"{file_id}{file_ext}"
        file_path = self.upload_dir / unique_filename
        
        try:
            # Check file size while saving
            total_size = 0
            with open(file_path, "wb") as buffer:
                while chunk := await file.read(8192):  # Read in 8KB chunks
                    total_size += len(chunk)
                    if total_size > MAX_FILE_SIZE:
                        # Clean up partial file
                        os.remove(file_path)
                        raise HTTPException(
                            status_code=413,
                            detail=f"File too large. Maximum size: {MAX_FILE_SIZE // (1024*1024)}MB"
                        )
                    buffer.write(chunk)
            
            logger.info(f"File saved successfully: {unique_filename} ({total_size} bytes)")
            return file_id, file_path
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to save file: {str(e)}")
            # Clean up if file was partially created
            if file_path.exists():
                os.remove(file_path)
            raise HTTPException(status_code=500, detail="Failed to save file")
    
    def get_file_path(self, file_id: str) -> Optional[Path]:
        """
        Get the file path for a given file ID.
        
        Args:
            file_id: The unique file identifier
            
        Returns:
            Path to the file if it exists, None otherwise
        """
        # Search for file with this ID (any extension)
        for ext in ALLOWED_EXTENSIONS:
            file_path = self.upload_dir / f"{file_id}{ext}"
            if file_path.exists():
                return file_path
        return None
    
    def delete_file(self, file_id: str) -> bool:
        """
        Delete a file by its ID.
        
        Args:
            file_id: The unique file identifier
            
        Returns:
            True if file was deleted, False if not found
        """
        file_path = self.get_file_path(file_id)
        if file_path and file_path.exists():
            os.remove(file_path)
            logger.info(f"File deleted: {file_id}")
            return True
        return False
    
    def get_file_type(self, file_path: Path) -> str:
        """
        Determine if file is PDF or image based on extension.
        
        Args:
            file_path: Path to the file
            
        Returns:
            'pdf' or 'image'
        """
        ext = file_path.suffix.lower()
        if ext == ".pdf":
            return "pdf"
        return "image"


# Singleton instance for the service
upload_service = DocumentUploadService()

