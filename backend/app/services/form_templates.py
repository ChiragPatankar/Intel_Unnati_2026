"""
Form Templates Service
Defines field mappings for different government forms
"""
import re
from typing import Dict, List, Optional
from enum import Enum


class FormType(str, Enum):
    """Supported government form types"""
    AADHAAR_UPDATE = "aadhaar_update"
    RATION_CARD = "ration_card"
    BIRTH_CERTIFICATE = "birth_certificate"
    DRIVING_LICENSE = "driving_license"
    PASSPORT = "passport"
    VOTER_ID = "voter_id"


class FormTemplate:
    """Represents a form template with field mappings"""
    
    def __init__(
        self,
        form_id: str,
        name: str,
        fields: Dict[str, Dict[str, any]]
    ):
        self.form_id = form_id
        self.name = name
        self.fields = fields  # {field_name: {label, required, type, validation}}


class FormTemplatesService:
    """Service for managing form templates and field mappings"""
    
    def __init__(self):
        self.templates = self._initialize_templates()
    
    def _initialize_templates(self) -> Dict[str, FormTemplate]:
        """Initialize all form templates"""
        return {
            FormType.AADHAAR_UPDATE.value: FormTemplate(
                form_id=FormType.AADHAAR_UPDATE.value,
                name="Aadhaar Update Form",
                fields={
                    "applicant_name": {
                        "label": "Applicant Name",
                        "required": True,
                        "type": "text",
                        "mapping": ["name", "full_name"]
                    },
                    "aadhaar_number": {
                        "label": "Aadhaar Number",
                        "required": True,
                        "type": "text",
                        "mapping": ["aadhaar_number", "aadhaar"]
                    },
                    "date_of_birth": {
                        "label": "Date of Birth",
                        "required": True,
                        "type": "date",
                        "mapping": ["dob", "date_of_birth", "birth_date"]
                    },
                    "gender": {
                        "label": "Gender",
                        "required": True,
                        "type": "select",
                        "options": ["Male", "Female", "Other"],
                        "mapping": ["gender", "sex"]
                    },
                    "address": {
                        "label": "Current Address",
                        "required": True,
                        "type": "textarea",
                        "mapping": ["address", "current_address", "residential_address"]
                    },
                    "mobile_number": {
                        "label": "Mobile Number",
                        "required": False,
                        "type": "tel",
                        "mapping": ["phone", "mobile", "mobile_number"]
                    },
                    "email": {
                        "label": "Email Address",
                        "required": False,
                        "type": "email",
                        "mapping": ["email", "email_address"]
                    }
                }
            ),
            FormType.RATION_CARD.value: FormTemplate(
                form_id=FormType.RATION_CARD.value,
                name="Ration Card Application",
                fields={
                    "head_of_family": {
                        "label": "Head of Family Name",
                        "required": True,
                        "type": "text",
                        "mapping": ["name", "full_name", "head_name"]
                    },
                    "aadhaar_number": {
                        "label": "Aadhaar Number",
                        "required": True,
                        "type": "text",
                        "mapping": ["aadhaar_number", "aadhaar"]
                    },
                    "date_of_birth": {
                        "label": "Date of Birth",
                        "required": True,
                        "type": "date",
                        "mapping": ["dob", "date_of_birth"]
                    },
                    "address": {
                        "label": "Residential Address",
                        "required": True,
                        "type": "textarea",
                        "mapping": ["address", "residential_address"]
                    },
                    "family_members": {
                        "label": "Number of Family Members",
                        "required": True,
                        "type": "number",
                        "mapping": []
                    },
                    "annual_income": {
                        "label": "Annual Income",
                        "required": False,
                        "type": "number",
                        "mapping": []
                    }
                }
            ),
            FormType.BIRTH_CERTIFICATE.value: FormTemplate(
                form_id=FormType.BIRTH_CERTIFICATE.value,
                name="Birth Certificate Request",
                fields={
                    "child_name": {
                        "label": "Child's Name",
                        "required": True,
                        "type": "text",
                        "mapping": ["name", "full_name"]
                    },
                    "date_of_birth": {
                        "label": "Date of Birth",
                        "required": True,
                        "type": "date",
                        "mapping": ["dob", "date_of_birth"]
                    },
                    "place_of_birth": {
                        "label": "Place of Birth",
                        "required": True,
                        "type": "text",
                        "mapping": ["birth_place", "place_of_birth"]
                    },
                    "father_name": {
                        "label": "Father's Name",
                        "required": True,
                        "type": "text",
                        "mapping": ["father_name", "fathers_name", "parent_name"]
                    },
                    "mother_name": {
                        "label": "Mother's Name",
                        "required": True,
                        "type": "text",
                        "mapping": ["mother_name", "mothers_name"]
                    },
                    "aadhaar_number": {
                        "label": "Aadhaar Number (if available)",
                        "required": False,
                        "type": "text",
                        "mapping": ["aadhaar_number", "aadhaar"]
                    }
                }
            ),
            FormType.DRIVING_LICENSE.value: FormTemplate(
                form_id=FormType.DRIVING_LICENSE.value,
                name="Driving License Application",
                fields={
                    "applicant_name": {
                        "label": "Applicant Name",
                        "required": True,
                        "type": "text",
                        "mapping": ["name", "full_name"]
                    },
                    "date_of_birth": {
                        "label": "Date of Birth",
                        "required": True,
                        "type": "date",
                        "mapping": ["dob", "date_of_birth"]
                    },
                    "aadhaar_number": {
                        "label": "Aadhaar Number",
                        "required": True,
                        "type": "text",
                        "mapping": ["aadhaar_number", "aadhaar"]
                    },
                    "address": {
                        "label": "Permanent Address",
                        "required": True,
                        "type": "textarea",
                        "mapping": ["address", "permanent_address"]
                    },
                    "license_type": {
                        "label": "License Type",
                        "required": True,
                        "type": "select",
                        "options": ["Learner's License", "Permanent License"],
                        "mapping": []
                    },
                    "vehicle_category": {
                        "label": "Vehicle Category",
                        "required": True,
                        "type": "select",
                        "options": ["MCWG", "LMV", "HMV", "MCWOG"],
                        "mapping": []
                    }
                }
            ),
            FormType.PASSPORT.value: FormTemplate(
                form_id=FormType.PASSPORT.value,
                name="Passport Application",
                fields={
                    "applicant_name": {
                        "label": "Applicant Name (as in Birth Certificate)",
                        "required": True,
                        "type": "text",
                        "mapping": ["name", "full_name"]
                    },
                    "date_of_birth": {
                        "label": "Date of Birth",
                        "required": True,
                        "type": "date",
                        "mapping": ["dob", "date_of_birth"]
                    },
                    "place_of_birth": {
                        "label": "Place of Birth",
                        "required": True,
                        "type": "text",
                        "mapping": ["birth_place", "place_of_birth"]
                    },
                    "father_name": {
                        "label": "Father's Name",
                        "required": True,
                        "type": "text",
                        "mapping": ["father_name", "fathers_name"]
                    },
                    "mother_name": {
                        "label": "Mother's Name",
                        "required": True,
                        "type": "text",
                        "mapping": ["mother_name", "mothers_name"]
                    },
                    "aadhaar_number": {
                        "label": "Aadhaar Number",
                        "required": True,
                        "type": "text",
                        "mapping": ["aadhaar_number", "aadhaar"]
                    },
                    "address": {
                        "label": "Current Address",
                        "required": True,
                        "type": "textarea",
                        "mapping": ["address", "current_address"]
                    },
                    "pan_number": {
                        "label": "PAN Number",
                        "required": False,
                        "type": "text",
                        "mapping": ["pan_number", "pan"]
                    }
                }
            ),
            FormType.VOTER_ID.value: FormTemplate(
                form_id=FormType.VOTER_ID.value,
                name="Voter ID Enrollment",
                fields={
                    "applicant_name": {
                        "label": "Applicant Name",
                        "required": True,
                        "type": "text",
                        "mapping": ["name", "full_name"]
                    },
                    "date_of_birth": {
                        "label": "Date of Birth",
                        "required": True,
                        "type": "date",
                        "mapping": ["dob", "date_of_birth"]
                    },
                    "gender": {
                        "label": "Gender",
                        "required": True,
                        "type": "select",
                        "options": ["Male", "Female", "Other"],
                        "mapping": ["gender", "sex"]
                    },
                    "aadhaar_number": {
                        "label": "Aadhaar Number",
                        "required": True,
                        "type": "text",
                        "mapping": ["aadhaar_number", "aadhaar"]
                    },
                    "address": {
                        "label": "Residential Address",
                        "required": True,
                        "type": "textarea",
                        "mapping": ["address", "residential_address"]
                    },
                    "family_member_name": {
                        "label": "Name of Family Member (if different)",
                        "required": False,
                        "type": "text",
                        "mapping": []
                    }
                }
            )
        }
    
    def get_template(self, form_id: str) -> Optional[FormTemplate]:
        """Get a form template by ID"""
        return self.templates.get(form_id)
    
    def list_templates(self) -> List[Dict]:
        """List all available templates"""
        return [
            {
                "id": template.form_id,
                "name": template.name,
                "field_count": len(template.fields)
            }
            for template in self.templates.values()
        ]
    
    def map_extracted_data_to_form(
        self,
        form_id: str,
        extracted_entities: Dict[str, any]
    ) -> Dict[str, any]:
        """
        Map extracted entities to form fields with enhanced fuzzy matching
        
        Args:
            form_id: The form template ID
            extracted_entities: Dictionary of extracted entities from OCR/NLP
            
        Returns:
            Dictionary mapping form field names to values
        """
        template = self.get_template(form_id)
        if not template:
            return {}
        
        mapped_data = {}
        
        # Normalize extracted entities keys for better matching
        normalized_entities = {}
        for key, value in extracted_entities.items():
            # Normalize key (lowercase, remove special chars)
            normalized_key = re.sub(r'[^\w]', '', key.lower())
            normalized_entities[normalized_key] = value
            # Also keep original for exact matches
            normalized_entities[key.lower()] = value
        
        for field_name, field_config in template.fields.items():
            # Try to find matching value from extracted entities
            value = None
            match_found = False
            
            # Check all possible mappings
            for mapping_key in field_config.get("mapping", []):
                normalized_mapping = re.sub(r'[^\w]', '', mapping_key.lower())
                
                # Try exact match (case-insensitive)
                for entity_key, entity_value in extracted_entities.items():
                    normalized_entity_key = re.sub(r'[^\w]', '', entity_key.lower())
                    if (entity_key.lower() == mapping_key.lower() or 
                        normalized_entity_key == normalized_mapping or
                        entity_key.lower() == normalized_mapping):
                        if isinstance(entity_value, dict):
                            value = entity_value.get("value")
                        else:
                            value = entity_value
                        if value:
                            match_found = True
                            break
                    if match_found:
                        break
                
                if match_found:
                    break
                
                # Try normalized match
                if normalized_mapping in normalized_entities:
                    entity_value = normalized_entities[normalized_mapping]
                    if isinstance(entity_value, dict):
                        value = entity_value.get("value")
                    else:
                        value = entity_value
                    if value:
                        match_found = True
                        break
                
                # Try fuzzy match (partial string match)
                if not match_found:
                    for entity_key in extracted_entities.keys():
                        normalized_entity_key = re.sub(r'[^\w]', '', entity_key.lower())
                        # Check if mapping key is contained in entity key or vice versa
                        if (normalized_mapping in normalized_entity_key or 
                            normalized_entity_key in normalized_mapping or
                            self._fuzzy_match(normalized_mapping, normalized_entity_key)):
                            entity_value = extracted_entities[entity_key]
                            if isinstance(entity_value, dict):
                                value = entity_value.get("value")
                            else:
                                value = entity_value
                            if value:
                                match_found = True
                                break
                    if match_found:
                        break
            
            mapped_data[field_name] = {
                "value": value or "",
                "label": field_config["label"],
                "required": field_config["required"],
                "type": field_config["type"],
                "filled": bool(value)
            }
        
        return mapped_data
    
    def _fuzzy_match(self, str1: str, str2: str, threshold: float = 0.7) -> bool:
        """Simple fuzzy matching using character overlap."""
        if not str1 or not str2:
            return False
        
        # Calculate Jaccard similarity (character bigrams)
        set1 = set(str1[i:i+2] for i in range(len(str1)-1))
        set2 = set(str2[i:i+2] for i in range(len(str2)-1))
        
        if not set1 or not set2:
            return False
        
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        similarity = intersection / union if union > 0 else 0
        
        return similarity >= threshold
    
    def get_required_fields(self, form_id: str) -> List[str]:
        """Get list of required field names for a form"""
        template = self.get_template(form_id)
        if not template:
            return []
        
        return [
            field_name
            for field_name, field_config in template.fields.items()
            if field_config.get("required", False)
        ]
    
    def validate_form_data(self, form_id: str, form_data: Dict[str, any]) -> Dict[str, any]:
        """
        Validate form data against template requirements
        
        Returns:
            Dictionary with 'valid' boolean and 'errors' list
        """
        template = self.get_template(form_id)
        if not template:
            return {"valid": False, "errors": ["Invalid form template"]}
        
        errors = []
        required_fields = self.get_required_fields(form_id)
        
        for field_name in required_fields:
            value = form_data.get(field_name, "")
            if not value or (isinstance(value, str) and not value.strip()):
                field_label = template.fields[field_name]["label"]
                errors.append(f"{field_label} is required")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }


# Singleton instance
form_templates_service = FormTemplatesService()

