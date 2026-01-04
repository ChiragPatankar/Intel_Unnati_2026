"""
Form Mapping Service
Maps extracted entities to government form templates.
"""

from typing import List, Dict, Optional
from app.config import FORM_TEMPLATES
from app.models.schemas import (
    ExtractedEntity,
    FormField,
    FormMappingResult,
    EntityExtractionResult
)
from app.utils.logger import get_logger

logger = get_logger(__name__)


class FormMappingService:
    """
    Service for mapping extracted entities to form templates.
    
    This service takes extracted entities and maps them to 
    the appropriate fields in government form templates.
    
    TODO: Add intelligent field matching using NLP
    TODO: Support custom form template uploads
    """
    
    def __init__(self):
        """Initialize the form mapping service."""
        self.templates = FORM_TEMPLATES
        logger.info(f"FormMappingService initialized with {len(self.templates)} templates")
    
    def get_available_templates(self) -> List[Dict[str, str]]:
        """
        Get list of available form templates.
        
        Returns:
            List of template info dictionaries
        """
        return [
            {"id": template_id, "name": template["name"]}
            for template_id, template in self.templates.items()
        ]
    
    def _find_entity_value(
        self, 
        field_name: str, 
        entities: List[ExtractedEntity]
    ) -> Optional[ExtractedEntity]:
        """
        Find an entity that matches the given field name.
        
        Args:
            field_name: The form field name to match
            entities: List of extracted entities
            
        Returns:
            Matching ExtractedEntity or None
        """
        # Direct match
        for entity in entities:
            if entity.field_name == field_name:
                return entity
        
        # TODO: Add fuzzy matching and synonyms
        # e.g., 'name' should match 'full_name', 'candidate_name', etc.
        
        # Mapping of common field variations
        field_aliases = {
            'full_name': ['name', 'candidate_name', 'applicant_name'],
            'father_name': ['fathers_name', 'guardian_name', 'parent_name'],
            'dob': ['date_of_birth', 'birth_date'],
            'address': ['residential_address', 'permanent_address', 'current_address'],
            'aadhaar_number': ['aadhaar', 'uid', 'aadhaar_no'],
            'pan_number': ['pan', 'pan_no'],
        }
        
        # Check aliases
        for canonical, aliases in field_aliases.items():
            if field_name in aliases or field_name == canonical:
                for entity in entities:
                    if entity.field_name == canonical or entity.field_name in aliases:
                        return entity
        
        return None
    
    def map_to_form(
        self, 
        extraction_result: EntityExtractionResult, 
        form_id: str
    ) -> FormMappingResult:
        """
        Map extracted entities to a specific form template.
        
        Args:
            extraction_result: The entity extraction result
            form_id: ID of the target form template
            
        Returns:
            FormMappingResult with mapped fields
        """
        logger.info(f"Mapping entities to form: {form_id}")
        
        # Get the form template
        if form_id not in self.templates:
            logger.error(f"Form template not found: {form_id}")
            raise ValueError(f"Form template '{form_id}' not found")
        
        template = self.templates[form_id]
        entities = extraction_result.entities
        
        mapped_fields: List[FormField] = []
        mapped_entity_names: set = set()
        filled_count = 0
        
        # Map each form field
        for field_name in template['fields']:
            entity = self._find_entity_value(field_name, entities)
            
            if entity:
                mapped_fields.append(FormField(
                    field_id=field_name,
                    field_label=self._format_field_label(field_name),
                    value=entity.value,
                    confidence=entity.confidence,
                    is_required=True,
                    needs_review=entity.confidence < 70
                ))
                mapped_entity_names.add(entity.field_name)
                filled_count += 1
            else:
                # Field exists in form but no matching entity found
                mapped_fields.append(FormField(
                    field_id=field_name,
                    field_label=self._format_field_label(field_name),
                    value=None,
                    confidence=None,
                    is_required=True,
                    needs_review=True
                ))
        
        # Find unmapped entities (extracted but not used in this form)
        unmapped = [
            entity.field_name 
            for entity in entities 
            if entity.field_name not in mapped_entity_names
        ]
        
        # Calculate completion percentage
        total_fields = len(template['fields'])
        completion = (filled_count / total_fields * 100) if total_fields > 0 else 0
        
        logger.info(
            f"Form mapping complete: {filled_count}/{total_fields} fields filled "
            f"({completion:.1f}% complete)"
        )
        
        return FormMappingResult(
            form_name=template['name'],
            form_id=form_id,
            fields=mapped_fields,
            completion_percentage=round(completion, 2),
            unmapped_entities=unmapped
        )
    
    def _format_field_label(self, field_name: str) -> str:
        """
        Convert field_name to human-readable label.
        
        Args:
            field_name: Snake_case field name
            
        Returns:
            Human-readable label
        """
        return field_name.replace('_', ' ').title()
    
    def suggest_best_form(
        self, 
        extraction_result: EntityExtractionResult
    ) -> Optional[str]:
        """
        Suggest the best matching form template based on extracted entities.
        
        Args:
            extraction_result: The entity extraction result
            
        Returns:
            form_id of the best matching template, or None
        """
        entity_names = {e.field_name for e in extraction_result.entities}
        
        best_match = None
        best_score = 0
        
        for form_id, template in self.templates.items():
            form_fields = set(template['fields'])
            
            # Calculate overlap score
            overlap = len(entity_names.intersection(form_fields))
            coverage = overlap / len(form_fields) if form_fields else 0
            
            if coverage > best_score:
                best_score = coverage
                best_match = form_id
        
        if best_match:
            logger.info(f"Best matching form: {best_match} (score: {best_score:.2f})")
        
        return best_match


# Singleton instance
form_mapping_service = FormMappingService()

