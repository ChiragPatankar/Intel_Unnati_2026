"""
Profile Storage Service
Stores user profiles with extracted document data.
Uses local JSON storage for MVP (can be upgraded to database later).
"""

import json
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

from app.config import BASE_DIR
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Storage directory for profiles
PROFILES_DIR = BASE_DIR / "profiles"
PROFILES_DIR.mkdir(parents=True, exist_ok=True)


class ProfileStorageService:
    """
    Service for storing and retrieving user profiles.
    
    Each profile contains:
    - Personal information extracted from documents
    - Document metadata
    - User-edited fields
    """
    
    def __init__(self):
        """Initialize the profile storage service."""
        self.profiles_dir = PROFILES_DIR
        logger.info(f"ProfileStorageService initialized. Profiles dir: {self.profiles_dir}")
    
    def _get_profile_path(self, profile_id: str) -> Path:
        """Get the file path for a profile."""
        return self.profiles_dir / f"{profile_id}.json"
    
    def create_profile(self, name: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Create a new profile.
        
        Args:
            name: Profile name (e.g., "My Aadhaar", "Work Documents")
            data: Initial data to store
            
        Returns:
            Created profile with ID
        """
        profile_id = str(uuid.uuid4())[:8]  # Short ID for convenience
        
        profile = {
            "id": profile_id,
            "name": name,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "documents": [],  # List of uploaded document metadata
            "fields": data or {},  # Extracted/edited fields
        }
        
        # Save to file
        profile_path = self._get_profile_path(profile_id)
        with open(profile_path, 'w', encoding='utf-8') as f:
            json.dump(profile, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Profile created: {profile_id} - {name}")
        return profile
    
    def get_profile(self, profile_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a profile by ID.
        
        Returns:
            Profile data or None if not found
        """
        profile_path = self._get_profile_path(profile_id)
        
        if not profile_path.exists():
            return None
        
        with open(profile_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def update_profile(self, profile_id: str, fields: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update profile fields.
        
        Args:
            profile_id: Profile ID
            fields: Fields to update/add
            
        Returns:
            Updated profile or None if not found
        """
        profile = self.get_profile(profile_id)
        
        if not profile:
            return None
        
        # Merge fields
        profile['fields'].update(fields)
        profile['updated_at'] = datetime.now().isoformat()
        
        # Save
        profile_path = self._get_profile_path(profile_id)
        with open(profile_path, 'w', encoding='utf-8') as f:
            json.dump(profile, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Profile updated: {profile_id}")
        return profile
    
    def add_document_to_profile(
        self, 
        profile_id: str, 
        document_type: str,
        extracted_fields: Dict[str, Any],
        file_id: str = None
    ) -> Optional[Dict[str, Any]]:
        """
        Add a document's extracted data to a profile.
        
        Args:
            profile_id: Profile ID
            document_type: Type of document (aadhaar, pan, voter_id)
            extracted_fields: Extracted entity data
            file_id: Optional file ID reference
            
        Returns:
            Updated profile
        """
        profile = self.get_profile(profile_id)
        
        if not profile:
            return None
        
        # Add document metadata
        doc_entry = {
            "type": document_type,
            "file_id": file_id,
            "added_at": datetime.now().isoformat(),
        }
        profile['documents'].append(doc_entry)
        
        # Merge extracted fields into profile
        for field_name, field_data in extracted_fields.items():
            if isinstance(field_data, dict) and 'value' in field_data:
                # Enhanced format
                profile['fields'][field_name] = field_data['value']
            else:
                # Simple format
                profile['fields'][field_name] = field_data
        
        profile['updated_at'] = datetime.now().isoformat()
        
        # Save
        profile_path = self._get_profile_path(profile_id)
        with open(profile_path, 'w', encoding='utf-8') as f:
            json.dump(profile, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Document added to profile: {profile_id} - {document_type}")
        return profile
    
    def list_profiles(self) -> List[Dict[str, Any]]:
        """
        List all profiles (summary only).
        
        Returns:
            List of profile summaries
        """
        profiles = []
        
        for profile_path in self.profiles_dir.glob("*.json"):
            try:
                with open(profile_path, 'r', encoding='utf-8') as f:
                    profile = json.load(f)
                    # Return summary only
                    profiles.append({
                        "id": profile['id'],
                        "name": profile['name'],
                        "created_at": profile['created_at'],
                        "updated_at": profile['updated_at'],
                        "document_count": len(profile.get('documents', [])),
                        "field_count": len(profile.get('fields', {})),
                    })
            except Exception as e:
                logger.error(f"Error reading profile {profile_path}: {e}")
        
        # Sort by updated_at descending
        profiles.sort(key=lambda x: x['updated_at'], reverse=True)
        return profiles
    
    def delete_profile(self, profile_id: str) -> bool:
        """
        Delete a profile.
        
        Returns:
            True if deleted, False if not found
        """
        profile_path = self._get_profile_path(profile_id)
        
        if profile_path.exists():
            profile_path.unlink()
            logger.info(f"Profile deleted: {profile_id}")
            return True
        
        return False
    
    def get_profile_for_autofill(self, profile_id: str) -> Optional[Dict[str, str]]:
        """
        Get profile fields in a flat format suitable for auto-fill.
        
        Returns:
            Dictionary of field_name: value pairs
        """
        profile = self.get_profile(profile_id)
        
        if not profile:
            return None
        
        # Return flat fields dictionary
        return profile.get('fields', {})


# Singleton instance
profile_storage_service = ProfileStorageService()

