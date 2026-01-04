"""
Entity Extraction Service (Enhanced)
Extracts structured information (Name, DOB, Address, ID numbers) from OCR text.
Uses rule-based approach with sophisticated confidence scoring.

Confidence Scoring Factors:
1. Regex match strength (exact vs fuzzy)
2. OCR confidence passthrough
3. Label context presence
4. Value validation checks
5. Heuristic adjustments
"""

import re
import time
from typing import Dict, Optional, List, Tuple, Any
from dataclasses import dataclass

from app.config import DOCUMENT_PATTERNS, OCR_CONFIDENCE_THRESHOLD
from app.models.schemas import (
    DocumentType,
    MatchType,
    ConfidenceLevel,
    EntityValue,
    EnhancedExtractionResult,
    # Legacy imports for backward compatibility
    ExtractedEntity,
    EntityExtractionResult
)
from app.utils.logger import get_logger

logger = get_logger(__name__)


# =============================================================================
# CONFIDENCE SCORING CONFIGURATION
# =============================================================================

@dataclass
class ConfidenceWeights:
    """Weights for different confidence factors."""
    regex_match: float = 0.40      # How well the pattern matched
    label_context: float = 0.25   # Was there a label (e.g., "Name:")
    value_validation: float = 0.20  # Does the value pass validation
    ocr_passthrough: float = 0.15   # OCR engine confidence


# Base confidence scores by match type
BASE_CONFIDENCE = {
    MatchType.EXACT_REGEX: 0.95,      # Perfect format match (e.g., PAN: ABCDE1234F)
    MatchType.LABELED_REGEX: 0.88,    # Pattern with label context (increased from 0.85)
    MatchType.UNLABELED_REGEX: 0.72,  # Pattern without label (increased from 0.70)
    MatchType.HEURISTIC: 0.60,        # Fuzzy/heuristic match (increased from 0.55)
    MatchType.KEYWORD: 0.52,          # Simple keyword detection (increased from 0.50)
}

# Confidence adjustments (optimized for better accuracy)
CONFIDENCE_ADJUSTMENTS = {
    "label_found": 0.12,              # Boost if label was found (increased from 0.10)
    "validation_passed": 0.08,         # Boost if extra validation passed (increased from 0.05)
    "multiple_matches": -0.08,         # Penalty for ambiguous matches (reduced from -0.10)
    "short_value": -0.12,              # Penalty for suspiciously short values (reduced from -0.15)
    "ocr_low": -0.15,                  # Penalty if OCR confidence was low (reduced from -0.20)
    "document_context": 0.05,          # NEW: Boost for document-specific context
    "high_ocr": 0.03,                  # NEW: Small boost for high OCR confidence
}


def get_confidence_level(confidence: float) -> ConfidenceLevel:
    """Convert numeric confidence to categorical level."""
    if confidence >= 0.85:
        return ConfidenceLevel.HIGH
    elif confidence >= 0.60:
        return ConfidenceLevel.MEDIUM
    else:
        return ConfidenceLevel.LOW


# =============================================================================
# EXTRACTION RESULT DATACLASS
# =============================================================================

@dataclass
class ExtractionMatch:
    """Internal representation of an extraction match."""
    value: str
    raw_match: str
    confidence: float
    match_type: MatchType
    has_label: bool
    validation_passed: bool
    notes: List[str]


# =============================================================================
# ENTITY EXTRACTION SERVICE
# =============================================================================

class EntityExtractionService:
    """
    Enhanced service for extracting entities from OCR text.
    
    Features:
    - Multi-factor confidence scoring
    - Pattern strength analysis
    - OCR confidence integration
    - Detailed extraction notes
    
    Current Implementation: Rule-based pattern matching
    TODO: Integrate spaCy NER models for better accuracy
    TODO: Add custom NER model trained on Indian documents
    """
    
    def __init__(self):
        """Initialize the entity extraction service."""
        self.document_patterns = DOCUMENT_PATTERNS
        self.weights = ConfidenceWeights()
        logger.info("EntityExtractionService initialized with enhanced confidence scoring")
    
    # =========================================================================
    # CONFIDENCE CALCULATION
    # =========================================================================
    
    def _calculate_confidence(
        self,
        match_type: MatchType,
        has_label: bool,
        validation_passed: bool,
        value_length: int,
        ocr_confidence: Optional[float] = None,
        multiple_matches: bool = False
    ) -> Tuple[float, List[str]]:
        """
        Calculate final confidence score using multiple factors.
        
        Args:
            match_type: Type of pattern match
            has_label: Whether a label was found with the value
            validation_passed: Whether the value passed format validation
            value_length: Length of extracted value
            ocr_confidence: OCR engine confidence (0-100), if available
            multiple_matches: Whether multiple potential matches were found
            
        Returns:
            Tuple of (confidence_score, list_of_notes)
        """
        notes = []
        
        # Start with base confidence for match type
        confidence = BASE_CONFIDENCE[match_type]
        
        # Apply adjustments
        if has_label:
            confidence += CONFIDENCE_ADJUSTMENTS["label_found"]
            
        if validation_passed:
            confidence += CONFIDENCE_ADJUSTMENTS["validation_passed"]
            
        if multiple_matches:
            confidence += CONFIDENCE_ADJUSTMENTS["multiple_matches"]
            notes.append("Multiple potential matches found - manual review recommended")
            
        # Penalize very short values (likely OCR errors)
        if value_length < 3:
            confidence += CONFIDENCE_ADJUSTMENTS["short_value"]
            notes.append("Extracted value is unusually short")
            
        # Factor in OCR confidence if available
        if ocr_confidence is not None:
            ocr_factor = ocr_confidence / 100.0
            if ocr_factor < 0.6:
                confidence += CONFIDENCE_ADJUSTMENTS["ocr_low"]
                notes.append(f"Low OCR confidence ({ocr_confidence:.0f}%) may affect accuracy")
            else:
                # Blend with OCR confidence
                confidence = (confidence * 0.85) + (ocr_factor * 0.15)
        
        # Clamp to valid range
        confidence = max(0.0, min(1.0, confidence))
        
        return confidence, notes
    
    # =========================================================================
    # LANGUAGE DETECTION
    # =========================================================================
    
    def _detect_language(self, text: str) -> Tuple[str, List[str]]:
        """
        Detect primary language from text with notes.
        
        Returns:
            Tuple of (language_code, notes)
        """
        notes = []
        
        # Count character types
        hindi_chars = len(re.findall(r'[\u0900-\u097F]', text))
        tamil_chars = len(re.findall(r'[\u0B80-\u0BFF]', text))
        telugu_chars = len(re.findall(r'[\u0C00-\u0C7F]', text))
        english_chars = len(re.findall(r'[A-Za-z]', text))
        
        total_alpha = hindi_chars + tamil_chars + telugu_chars + english_chars
        
        if total_alpha == 0:
            return "unknown", ["No alphabetic characters detected"]
        
        # Determine dominant language
        if hindi_chars / total_alpha > 0.3:
            notes.append("Hindi/Devanagari script detected")
            if english_chars / total_alpha > 0.2:
                notes.append("Mixed Hindi-English content")
            return "hi", notes
        elif tamil_chars / total_alpha > 0.3:
            notes.append("Tamil script detected")
            return "ta", notes
        elif telugu_chars / total_alpha > 0.3:
            notes.append("Telugu script detected")
            return "te", notes
        else:
            if hindi_chars > 0:
                notes.append("Primarily English with some Hindi text")
            return "en", notes
    
    # =========================================================================
    # DOCUMENT TYPE DETECTION
    # =========================================================================
    
    def detect_document_type(self, text: str) -> Tuple[DocumentType, float, List[str]]:
        """
        Detect the type of Indian ID document with confidence.
        
        Returns:
            Tuple of (DocumentType, confidence, notes)
        """
        text_lower = text.lower()
        notes = []
        matches = []
        
        for doc_type, config in self.document_patterns.items():
            match_count = 0
            for pattern in config['patterns']:
                if pattern.lower() in text_lower:
                    match_count += 1
            
            if match_count > 0:
                matches.append((doc_type, match_count))
        
        if not matches:
            notes.append("Document type could not be determined from text")
            return DocumentType.UNKNOWN, 0.3, notes
        
        # Sort by match count
        matches.sort(key=lambda x: x[1], reverse=True)
        best_match = matches[0]
        
        # Calculate confidence based on match count
        confidence = min(0.95, 0.6 + (best_match[1] * 0.15))
        
        if len(matches) > 1:
            notes.append(f"Multiple document types detected, using {best_match[0]}")
            confidence -= 0.1
        
        logger.info(f"Document type detected: {best_match[0]} (confidence: {confidence:.2f})")
        return DocumentType(best_match[0]), confidence, notes
    
    # =========================================================================
    # ID NUMBER EXTRACTION (Enhanced)
    # =========================================================================
    
    def _extract_aadhaar_number(
        self, 
        text: str, 
        ocr_confidence: Optional[float] = None
    ) -> Optional[ExtractionMatch]:
        """
        Extract 12-digit Aadhaar number with confidence scoring.
        Format: XXXX XXXX XXXX or XXXXXXXXXXXX
        """
        # Patterns ordered by specificity (most specific first)
        patterns = [
            # With explicit label
            (r'(?:Aadhaar|आधार|UID)\s*(?:No|Number|नंबर)?[:\-]?\s*(\d{4}\s?\d{4}\s?\d{4})', True),
            # Spaced format without label
            (r'\b(\d{4}\s\d{4}\s\d{4})\b', False),
            # Continuous format
            (r'\b(\d{12})\b', False),
        ]
        
        all_matches = []
        
        for pattern, has_label in patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                aadhaar = match.group(1).replace(' ', '')
                
                # Validation: must be 12 digits, not all same digit
                if len(aadhaar) == 12 and aadhaar.isdigit():
                    if len(set(aadhaar)) > 1:  # Not all same digit
                        formatted = f"{aadhaar[:4]} {aadhaar[4:8]} {aadhaar[8:]}"
                        all_matches.append((formatted, match.group(0), has_label))
        
        if not all_matches:
            return None
        
        # Use first match (most specific pattern)
        value, raw_match, has_label = all_matches[0]
        match_type = MatchType.LABELED_REGEX if has_label else MatchType.EXACT_REGEX
        
        confidence, notes = self._calculate_confidence(
            match_type=match_type,
            has_label=has_label,
            validation_passed=True,  # Passed digit validation
            value_length=len(value),
            ocr_confidence=ocr_confidence,
            multiple_matches=len(all_matches) > 1
        )
        
        return ExtractionMatch(
            value=value,
            raw_match=raw_match,
            confidence=confidence,
            match_type=match_type,
            has_label=has_label,
            validation_passed=True,
            notes=notes
        )
    
    def _extract_pan_number(
        self, 
        text: str, 
        ocr_confidence: Optional[float] = None
    ) -> Optional[ExtractionMatch]:
        """
        Extract PAN card number with confidence scoring.
        Format: ABCDE1234F (5 letters + 4 digits + 1 letter)
        """
        patterns = [
            # With label
            (r'(?:PAN|Permanent Account Number)\s*(?:No|Number)?[:\-]?\s*([A-Z]{5}[0-9]{4}[A-Z])', True),
            # Without label
            (r'\b([A-Z]{5}[0-9]{4}[A-Z])\b', False),
        ]
        
        text_upper = text.upper()
        all_matches = []
        
        for pattern, has_label in patterns:
            for match in re.finditer(pattern, text_upper):
                pan = match.group(1)
                
                # Additional validation: 4th char indicates holder type
                # C=Company, P=Person, H=HUF, F=Firm, etc.
                fourth_char = pan[3]
                valid_types = 'CPHFATBLGJK'
                type_valid = fourth_char in valid_types
                
                all_matches.append((pan, match.group(0), has_label, type_valid))
        
        if not all_matches:
            return None
        
        # Prefer matches with valid type character
        valid_matches = [m for m in all_matches if m[3]]
        best_match = valid_matches[0] if valid_matches else all_matches[0]
        
        value, raw_match, has_label, type_valid = best_match
        match_type = MatchType.EXACT_REGEX  # PAN has strict format
        
        confidence, notes = self._calculate_confidence(
            match_type=match_type,
            has_label=has_label,
            validation_passed=type_valid,
            value_length=len(value),
            ocr_confidence=ocr_confidence,
            multiple_matches=len(all_matches) > 1
        )
        
        if not type_valid:
            notes.append("PAN 4th character doesn't match known entity types")
        
        return ExtractionMatch(
            value=value,
            raw_match=raw_match,
            confidence=confidence,
            match_type=match_type,
            has_label=has_label,
            validation_passed=type_valid,
            notes=notes
        )
    
    def _extract_voter_id(
        self, 
        text: str, 
        ocr_confidence: Optional[float] = None
    ) -> Optional[ExtractionMatch]:
        """
        Extract Voter ID (EPIC) number with confidence scoring.
        Format: ABC1234567 (3 letters + 7 digits)
        """
        patterns = [
            # With label
            (r'(?:EPIC|Voter\s*ID|Election|निर्वाचक)\s*(?:No|Number)?[:\-]?\s*([A-Z]{3}[0-9]{7})', True),
            # Without label
            (r'\b([A-Z]{3}[0-9]{7})\b', False),
        ]
        
        text_upper = text.upper()
        all_matches = []
        
        for pattern, has_label in patterns:
            for match in re.finditer(pattern, text_upper):
                voter_id = match.group(1)
                all_matches.append((voter_id, match.group(0), has_label))
        
        if not all_matches:
            return None
        
        value, raw_match, has_label = all_matches[0]
        match_type = MatchType.LABELED_REGEX if has_label else MatchType.EXACT_REGEX
        
        confidence, notes = self._calculate_confidence(
            match_type=match_type,
            has_label=has_label,
            validation_passed=True,
            value_length=len(value),
            ocr_confidence=ocr_confidence,
            multiple_matches=len(all_matches) > 1
        )
        
        return ExtractionMatch(
            value=value,
            raw_match=raw_match,
            confidence=confidence,
            match_type=match_type,
            has_label=has_label,
            validation_passed=True,
            notes=notes
        )
    
    def _extract_passport_number(
        self, 
        text: str, 
        ocr_confidence: Optional[float] = None
    ) -> Optional[ExtractionMatch]:
        """
        Extract Indian Passport number with confidence scoring.
        Format: A1234567 (1 letter + 7 digits)
        """
        patterns = [
            # With label
            (r'(?:Passport|पासपोर्ट)\s*(?:No|Number)?[:\-]?\s*([A-Z][0-9]{7})', True),
            (r'(?:File\s*No|Passport\s*No)[:\-]?\s*([A-Z][0-9]{7})', True),
            # Without label
            (r'\b([A-Z][0-9]{7})\b', False),
        ]
        
        text_upper = text.upper()
        all_matches = []
        
        for pattern, has_label in patterns:
            for match in re.finditer(pattern, text_upper):
                passport = match.group(1)
                # Validate: should not be a PAN (5 letters + 4 digits + 1 letter)
                if len(passport) == 8 and passport[0].isalpha():
                    all_matches.append((passport, match.group(0), has_label))
        
        if not all_matches:
            return None
        
        value, raw_match, has_label = all_matches[0]
        match_type = MatchType.LABELED_REGEX if has_label else MatchType.EXACT_REGEX
        
        confidence, notes = self._calculate_confidence(
            match_type=match_type,
            has_label=has_label,
            validation_passed=True,
            value_length=len(value),
            ocr_confidence=ocr_confidence,
            multiple_matches=len(all_matches) > 1
        )
        
        return ExtractionMatch(
            value=value,
            raw_match=raw_match,
            confidence=confidence,
            match_type=match_type,
            has_label=has_label,
            validation_passed=True,
            notes=notes
        )
    
    def _extract_driving_license(
        self, 
        text: str, 
        ocr_confidence: Optional[float] = None
    ) -> Optional[ExtractionMatch]:
        """
        Extract Indian Driving License number with confidence scoring.
        Format varies by state: 
        - Common: XX-YYYYYYYYYYYY (state code + 13 digits)
        - Or: XXYY YYYYYYYYYYYY (spaced)
        """
        patterns = [
            # With label
            (r'(?:D\.?L\.?|Driving\s*Licen[cs]e|Licence)\s*(?:No|Number)?[:\-]?\s*([A-Z]{2}[\s\-]?\d{2}[\s\-]?\d{11})', True),
            (r'(?:D\.?L\.?|Driving\s*Licen[cs]e|Licence)\s*(?:No|Number)?[:\-]?\s*([A-Z]{2}[\s\-]?\d{13})', True),
            # Without label
            (r'\b([A-Z]{2}[\-\s]?\d{2}[\-\s]?\d{4}[\-\s]?\d{7})\b', False),
            (r'\b([A-Z]{2}\d{13})\b', False),
        ]
        
        text_upper = text.upper()
        all_matches = []
        
        for pattern, has_label in patterns:
            for match in re.finditer(pattern, text_upper):
                dl_num = match.group(1).replace(' ', '').replace('-', '')
                # Validate: should be 15 characters (2 letters + 13 digits)
                if len(dl_num) >= 13 and dl_num[:2].isalpha():
                    formatted = f"{dl_num[:2]}-{dl_num[2:]}"
                    all_matches.append((formatted, match.group(0), has_label))
        
        if not all_matches:
            return None
        
        value, raw_match, has_label = all_matches[0]
        match_type = MatchType.LABELED_REGEX if has_label else MatchType.EXACT_REGEX
        
        confidence, notes = self._calculate_confidence(
            match_type=match_type,
            has_label=has_label,
            validation_passed=True,
            value_length=len(value),
            ocr_confidence=ocr_confidence,
            multiple_matches=len(all_matches) > 1
        )
        
        return ExtractionMatch(
            value=value,
            raw_match=raw_match,
            confidence=confidence,
            match_type=match_type,
            has_label=has_label,
            validation_passed=True,
            notes=notes
        )
    
    def _extract_bank_account(
        self, 
        text: str, 
        ocr_confidence: Optional[float] = None
    ) -> Optional[ExtractionMatch]:
        """
        Extract bank account number with confidence scoring.
        Format: 9-18 digits (varies by bank)
        """
        patterns = [
            # With label
            (r'(?:Account|A\/C|Acct)\s*(?:No|Number)?[:\-]?\s*(\d{9,18})', True),
            (r'(?:Bank\s*Account)[:\-]?\s*(\d{9,18})', True),
            # Near IFSC code (contextual match)
            (r'(?:IFSC|Branch).*?(\d{11,18})', False),
        ]
        
        all_matches = []
        
        for pattern, has_label in patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                acc_num = match.group(1)
                # Validate: reasonable length
                if 9 <= len(acc_num) <= 18 and len(set(acc_num)) > 2:  # Not all same digit
                    all_matches.append((acc_num, match.group(0), has_label))
        
        if not all_matches:
            return None
        
        value, raw_match, has_label = all_matches[0]
        match_type = MatchType.LABELED_REGEX if has_label else MatchType.HEURISTIC
        
        confidence, notes = self._calculate_confidence(
            match_type=match_type,
            has_label=has_label,
            validation_passed=True,
            value_length=len(value),
            ocr_confidence=ocr_confidence,
            multiple_matches=len(all_matches) > 1
        )
        
        return ExtractionMatch(
            value=value,
            raw_match=raw_match,
            confidence=confidence,
            match_type=match_type,
            has_label=has_label,
            validation_passed=True,
            notes=notes
        )
    
    def _extract_ifsc_code(
        self, 
        text: str, 
        ocr_confidence: Optional[float] = None
    ) -> Optional[ExtractionMatch]:
        """
        Extract IFSC code with confidence scoring.
        Format: AAAA0XXXXXX (4 letters + 0 + 6 alphanumeric)
        """
        patterns = [
            # With label
            (r'(?:IFSC|IFS\s*Code)[:\-]?\s*([A-Z]{4}0[A-Z0-9]{6})', True),
            # Without label
            (r'\b([A-Z]{4}0[A-Z0-9]{6})\b', False),
        ]
        
        text_upper = text.upper()
        all_matches = []
        
        for pattern, has_label in patterns:
            for match in re.finditer(pattern, text_upper):
                ifsc = match.group(1)
                # Validate IFSC format
                if len(ifsc) == 11 and ifsc[4] == '0':
                    all_matches.append((ifsc, match.group(0), has_label))
        
        if not all_matches:
            return None
        
        value, raw_match, has_label = all_matches[0]
        match_type = MatchType.LABELED_REGEX if has_label else MatchType.EXACT_REGEX
        
        confidence, notes = self._calculate_confidence(
            match_type=match_type,
            has_label=has_label,
            validation_passed=True,
            value_length=len(value),
            ocr_confidence=ocr_confidence,
            multiple_matches=len(all_matches) > 1
        )
        
        return ExtractionMatch(
            value=value,
            raw_match=raw_match,
            confidence=confidence,
            match_type=match_type,
            has_label=has_label,
            validation_passed=True,
            notes=notes
        )
    
    # =========================================================================
    # PERSONAL INFORMATION EXTRACTION (Enhanced)
    # =========================================================================
    
    def _extract_name(
        self, 
        text: str, 
        ocr_confidence: Optional[float] = None
    ) -> Optional[ExtractionMatch]:
        """
        Extract name with enhanced confidence scoring and better patterns.
        Handles Indian name patterns including father's name context.
        """
        # Enhanced patterns with document-specific context
        patterns = [
            # Aadhaar card patterns - English name after Hindi name
            (r'(?:Name|Full Name|NAME OF THE HOLDER|नाम)\s*[:\-]?\s*[^\n]{0,100}?([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,4})(?:\n|DOB|Date|Father|Mother|Gender|जन्म|$)', True, 'aadhaar'),
            # Aadhaar - name in English section (after photo)
            (r'(?:Name in English|Name|Full Name)\s*[:\-]?\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,4})(?:\n|DOB|Date|Gender|$)', True, 'aadhaar'),
            # Aadhaar - name before DOB (common pattern)
            (r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,4})\s*\n\s*(?:DOB|Date of Birth|जन्म तारीख|जन्म)', True, 'aadhaar'),
            # PAN card patterns
            (r'(?:Name|INCOME TAX DEPARTMENT|Name as it appears)\s*[:\-]?\s*([A-Z][A-Za-z\s]{2,50}?)(?:\n|Father|DOB|$)', True, 'pan'),
            # Passport patterns
            (r'(?:Surname|Given Name|Name)\s*[:\-]?\s*([A-Z][A-Za-z\s]{2,50}?)(?:\n|Nationality|Date|$)', True, 'passport'),
            # Voter ID patterns
            (r'(?:Name|Elector\'s Name|नाम)\s*[:\-]?\s*([A-Z][A-Za-z\s]{2,50}?)(?:\n|Father|Husband|Age|$)', True, 'voter'),
            # Hindi labeled
            (r'(?:नाम)\s*[:\-]?\s*([A-Za-z\s]{3,50}?)(?:\n|$)', True, 'hindi'),
            # Name before DOB (very common pattern)
            (r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,4})[\s\S]{0,50}?(?:DOB|Date of Birth|जन्म)', False, 'contextual'),
            # Name after DOB
            (r'(?:DOB|Date of Birth|जन्म)[\s\S]{0,50}?([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,4})', False, 'contextual'),
            # All caps name (common in older documents)
            (r'([A-Z]{2,}(?:\s+[A-Z]{2,}){1,4})(?:\s|$)', False, 'allcaps'),
        ]
        
        all_matches = []
        exclude_words = {
            'Government', 'India', 'Authority', 'Unique', 'Identification', 
            'Aadhaar', 'Card', 'Male', 'Female', 'Date', 'Birth', 'Address',
            'Republic', 'Department', 'Income', 'Tax', 'Election', 'Commission'
        }
        
        # Enhanced proper name pattern matching - be more strict
        # Look for proper case names (Firstname Lastname pattern)
        proper_name_pattern = r'\b([A-Z][a-z]{2,15}(?:\s+[A-Z][a-z]{2,15}){1,3})\b'
        for match in re.finditer(proper_name_pattern, text):
            name = match.group(1).strip()
            words = [w for w in name.split() if w]
            # Valid name: 2-4 words, each word 3+ chars (more strict to avoid OCR errors)
            if 2 <= len(words) <= 4 and all(len(w) >= 3 for w in words):
                # Exclude common non-name words and suspicious OCR errors
                if not any(w in exclude_words for w in words):
                    # Exclude words that look like OCR errors (too short, weird patterns)
                    if not any(len(w) < 3 or not w[0].isupper() for w in words):
                        # Check if it's near other personal info (DOB, Address, Father, etc.)
                        context = text[max(0, match.start()-100):min(len(text), match.end()+100)]
                        if any(marker in context for marker in ['DOB', 'Date', 'Address', 'Father', 'Gender', 'जन्म', 'पुरुष', 'महिला']):
                            all_matches.append((name, match.group(0), True, 'contextual'))
        
        for pattern, has_label, doc_type in patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE):
                name = match.group(1).strip()
                # Clean name
                name = ' '.join(name.split())  # Normalize whitespace
                name = re.sub(r'[^\w\s]', '', name)  # Remove special chars
                
                # Validation checks - be more strict
                if 5 <= len(name) <= 60:  # Minimum 5 chars (was 3)
                    # Should contain only letters and spaces
                    if re.match(r'^[A-Za-z\s]+$', name):
                        # Should have at least 5 characters that aren't spaces
                        if len(name.replace(' ', '')) >= 5:
                            words = name.split()
                            # Each word should be at least 3 chars (avoid OCR errors like "Ohg")
                            if all(len(w) >= 3 for w in words) and 2 <= len(words) <= 4:
                                # Exclude if contains common non-name words
                                if not any(w in exclude_words for w in words):
                                    # Exclude suspicious patterns (too many consonants, weird patterns)
                                    # Check if name looks reasonable (has vowels)
                                    has_vowels = any(c.lower() in 'aeiou' for c in name)
                                    if has_vowels:
                                        # Capitalize properly
                                        name = ' '.join(w.capitalize() for w in words)
                                        all_matches.append((name, match.group(0), has_label, doc_type))
        
        if not all_matches:
            return None
        
        # Prefer labeled matches, then contextual, then others
        labeled = [m for m in all_matches if m[2]]
        contextual = [m for m in all_matches if not m[2] and m[3] == 'contextual']
        
        if labeled:
            best_match = labeled[0]
        elif contextual:
            best_match = contextual[0]
        else:
            best_match = all_matches[0]
        
        value, raw_match, has_label, doc_type = best_match
        match_type = MatchType.LABELED_REGEX if has_label else MatchType.HEURISTIC
        
        confidence, notes = self._calculate_confidence(
            match_type=match_type,
            has_label=has_label,
            validation_passed=True,
            value_length=len(value),
            ocr_confidence=ocr_confidence,
            multiple_matches=len(all_matches) > 2
        )
        
        # Boost confidence for document-specific matches
        if doc_type in ['aadhaar', 'pan', 'passport', 'voter']:
            confidence = min(confidence + 0.05, 0.90)
        
        # Names are inherently less reliable from OCR
        confidence = min(confidence, 0.88)
        notes.append(f"Name extracted from {doc_type} context")
        
        return ExtractionMatch(
            value=value,
            raw_match=raw_match[:100] + "..." if len(raw_match) > 100 else raw_match,
            confidence=confidence,
            match_type=match_type,
            has_label=has_label,
            validation_passed=True,
            notes=notes
        )
    
    def _extract_father_name(
        self, 
        text: str, 
        ocr_confidence: Optional[float] = None
    ) -> Optional[ExtractionMatch]:
        """Extract father's/guardian's name with confidence scoring."""
        patterns = [
            (r"(?:Father'?s?\s*Name|Guardian|पिता का नाम|पिता)\s*[:\-]?\s*([A-Za-z\s]{3,40}?)(?:\n|$)", True),
            (r"(?:S/O|D/O|W/O|C/O)\s*[:\-.]?\s*([A-Za-z\s]{3,40}?)(?:\n|$)", True),
        ]
        
        all_matches = []
        
        for pattern, has_label in patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                name = match.group(1).strip()
                name = ' '.join(name.split())
                
                if len(name) >= 3 and re.match(r'^[A-Za-z\s]+$', name):
                    all_matches.append((name.upper(), match.group(0), has_label))
        
        if not all_matches:
            return None
        
        value, raw_match, has_label = all_matches[0]
        
        confidence, notes = self._calculate_confidence(
            match_type=MatchType.LABELED_REGEX,
            has_label=True,
            validation_passed=True,
            value_length=len(value),
            ocr_confidence=ocr_confidence,
            multiple_matches=len(all_matches) > 1
        )
        
        return ExtractionMatch(
            value=value,
            raw_match=raw_match,
            confidence=confidence,
            match_type=MatchType.LABELED_REGEX,
            has_label=True,
            validation_passed=True,
            notes=notes
        )
    
    def _extract_dob(
        self, 
        text: str, 
        ocr_confidence: Optional[float] = None
    ) -> Optional[ExtractionMatch]:
        """
        Extract date of birth with confidence scoring.
        Handles multiple date formats common in Indian documents.
        """
        patterns = [
            # Aadhaar specific: जन्म तारीख /DOB: 16/05/2004 (most specific first)
            (r'(?:जन्म तारीख|जन्म तिथि)\s*[/\-]?\s*(?:DOB|Date of Birth)?\s*[:\/\-]?\s*(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{4})', True, True),
            # Standard DOB pattern with label
            (r'(?:DOB|Date of Birth|Birth|D\.O\.B)\s*[:\/\-]?\s*(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{4})', True, True),
            # Labeled DD/MM/YYYY or DD-MM-YYYY (enhanced)
            (r'(?:DOB|Date of Birth|जन्म तिथि|Birth|D\.O\.B|Date)\s*[:\-]?\s*(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{4})', True, True),
            # Labeled DD MMM YYYY (e.g., 15 Aug 1990)
            (r'(?:DOB|Date of Birth|जन्म तिथि|Birth)\s*[:\-]?\s*(\d{1,2}\s+[A-Za-z]{3,9}\s+\d{4})', True, True),
            # Year of Birth
            (r'(?:Year of Birth|YOB|जन्म वर्ष)\s*[:\-]?\s*(\d{4})', True, False),
            # Unlabeled date patterns (multiple formats) - but prefer dates near DOB keywords
            (r'(?:DOB|जन्म)[\s\S]{0,30}?(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{4})', False, True),
            (r'\b(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{4})\b', False, True),
            # YYYY-MM-DD format (ISO, sometimes used)
            (r'\b(\d{4}[\/\-\.]\d{1,2}[\/\-\.]\d{1,2})\b', False, True),
        ]
        
        all_matches = []
        
        for pattern, has_label, is_full_date in patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                date_str = match.group(1).strip()
                
                # Normalize date format
                normalized_date = self._normalize_date(date_str)
                date_str = normalized_date if normalized_date else date_str
                
                # Enhanced validation
                validation_passed = True
                
                if is_full_date:
                    # Try to validate date components
                    date_parts = re.split(r'[\/\-\s\.]+', date_str)
                    if len(date_parts) >= 3:
                        try:
                            # Handle DD/MM/YYYY format
                            if len(date_parts[0]) <= 2 and len(date_parts[-1]) == 4:
                                day = int(date_parts[0])
                                month = int(date_parts[1])
                                year = int(date_parts[-1])
                            # Handle YYYY-MM-DD format
                            elif len(date_parts[0]) == 4:
                                year = int(date_parts[0])
                                month = int(date_parts[1])
                                day = int(date_parts[2])
                            else:
                                validation_passed = False
                                all_matches.append((date_str, match.group(0), has_label, validation_passed, is_full_date))
                                continue
                            
                            # Enhanced sanity checks
                            if not (1 <= day <= 31 and 1 <= month <= 12 and 1900 <= year <= 2025):
                                validation_passed = False
                            # Check for impossible dates
                            if month == 2 and day > 29:
                                validation_passed = False
                            if month in [4, 6, 9, 11] and day > 30:
                                validation_passed = False
                        except:
                            validation_passed = False
                
                all_matches.append((date_str, match.group(0), has_label, validation_passed, is_full_date))
        
        if not all_matches:
            return None
        
        # Prefer validated, labeled, full dates
        best_matches = sorted(all_matches, key=lambda x: (x[3], x[2], x[4]), reverse=True)
        value, raw_match, has_label, validation_passed, is_full_date = best_matches[0]
        
        match_type = MatchType.LABELED_REGEX if has_label else MatchType.UNLABELED_REGEX
        
        confidence, notes = self._calculate_confidence(
            match_type=match_type,
            has_label=has_label,
            validation_passed=validation_passed,
            value_length=len(value),
            ocr_confidence=ocr_confidence,
            multiple_matches=len(all_matches) > 2
        )
        
        if not is_full_date:
            notes.append("Only year extracted, full date not found")
            confidence -= 0.1
        
        return ExtractionMatch(
            value=value,
            raw_match=raw_match,
            confidence=max(0.0, confidence),
            match_type=match_type,
            has_label=has_label,
            validation_passed=validation_passed,
            notes=notes
        )
    
    def _extract_gender(
        self, 
        text: str, 
        ocr_confidence: Optional[float] = None
    ) -> Optional[ExtractionMatch]:
        """Extract gender with confidence scoring."""
        patterns = [
            # Aadhaar specific: पुरुष / MALE or Gender: MALE
            (r'(?:Gender|Sex|लिंग|पुरुष|महिला)\s*[:\/\-]?\s*(Male|Female|पुरुष|महिला|MALE|FEMALE|M|F)\b', True),
            (r'(?:Gender|Sex|लिंग)\s*[:\-]?\s*(Male|Female|पुरुष|महिला|M|F)\b', True),
            (r'\b(MALE|FEMALE|पुरुष|महिला)\b', False),
        ]
        
        text_check = text.upper()
        
        for pattern, has_label in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                raw_value = match.group(1).upper()
                
                # Normalize gender value
                if raw_value in ['MALE', 'M', 'पुरुष']:
                    value = 'Male'
                elif raw_value in ['FEMALE', 'F', 'महिला']:
                    value = 'Female'
                else:
                    value = raw_value.title()
                
                match_type = MatchType.LABELED_REGEX if has_label else MatchType.KEYWORD
                
                confidence, notes = self._calculate_confidence(
                    match_type=match_type,
                    has_label=has_label,
                    validation_passed=True,
                    value_length=len(value),
                    ocr_confidence=ocr_confidence
                )
                
                return ExtractionMatch(
                    value=value,
                    raw_match=match.group(0),
                    confidence=confidence,
                    match_type=match_type,
                    has_label=has_label,
                    validation_passed=True,
                    notes=notes
                )
        
        return None
    
    def _extract_address(
        self, 
        text: str, 
        ocr_confidence: Optional[float] = None,
        exclude_patterns: Optional[List[str]] = None
    ) -> Optional[ExtractionMatch]:
        """
        Extract address with enhanced confidence scoring and better multi-line handling.
        
        Args:
            text: OCR text to extract from
            ocr_confidence: OCR confidence score
            exclude_patterns: List of regex patterns to exclude from address (e.g., DOB, Gender)
        """
        # Remove DOB and Gender patterns from text before extracting address
        cleaned_text = text
        if exclude_patterns:
            for pattern in exclude_patterns:
                cleaned_text = re.sub(pattern, ' ', cleaned_text, flags=re.IGNORECASE)
        
        patterns = [
            # Address with PIN code (enhanced) - capture more text before PIN
            (r'(?:Address|पता|Addr|Residence|Permanent Address)\s*[:\-]?\s*([\s\S]{20,400}?)(\d{6})(?:\s|$|DOB|Gender|MALE|FEMALE|पुरुष|महिला|Mobile|Phone|Email)', True, True),
            # Address without PIN - stop before DOB/Gender/Mobile/Email
            (r'(?:Address|पता|Addr|Residence)\s*[:\-]?\s*([\s\S]{20,300}?)(?:\n\n|\n[A-Z]|DOB|Gender|MALE|FEMALE|Mobile|Phone|Email|$)', True, False),
            # Multi-line address block (common in Aadhaar) - capture more context
            (r'(?:Address|पता)[\s\S]{0,30}?([A-Za-z0-9\s,\.\-\/]{30,250}?)(\d{6})(?:\s|$|DOB|Gender|Mobile|Phone|Email)', True, True),
        ]
        
        all_matches = []
        
        for pattern, has_label, has_pin in patterns:
            for match in re.finditer(pattern, cleaned_text, re.IGNORECASE | re.MULTILINE):
                if has_pin:
                    address = match.group(1).strip()
                    pincode = match.group(2)
                    # Clean up multi-line address
                    address_lines = [line.strip() for line in address.split('\n') if line.strip()]
                    cleaned_address = ', '.join(address_lines)
                    address = f"{cleaned_address} - {pincode}"
                else:
                    address = match.group(1).strip()
                    # Clean up multi-line
                    address_lines = [line.strip() for line in address.split('\n') if line.strip()]
                    address = ', '.join(address_lines)
                
                # Clean up address
                address = self._clean_address(address)
                
                # Remove DOB and Gender patterns from address if they slipped through
                # Remove date patterns (DD/MM/YYYY or DD-MM-YYYY)
                address = re.sub(r'\b\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{4}\b', '', address)
                # Remove gender keywords and OCR errors (gea/, gea, etc.)
                address = re.sub(r'\b(MALE|FEMALE|Male|Female|पुरुष|महिला|gea|gea\/)\b', '', address, flags=re.IGNORECASE)
                # Remove common OCR errors that appear before address
                address = re.sub(r'^[^A-Za-z0-9]*', '', address)  # Remove leading non-alphanumeric
                # Clean up extra commas and spaces
                address = re.sub(r'[,]{2,}', ',', address)
                address = re.sub(r'--+', '-', address)  # Clean up multiple dashes
                address = ' '.join(address.split())
                
                if len(address) >= 10:
                    all_matches.append((address, match.group(0), has_label, has_pin))
        
        if not all_matches:
            # Enhanced fallback: look for PIN code and grab surrounding text (more context)
            pin_match = re.search(r'([A-Za-z0-9\s,\.\-\/]{30,200}?)(\d{6})(?:\s|$|Mobile|Phone|Email|@)', cleaned_text)
            if pin_match:
                address = pin_match.group(1).strip()
                pincode = pin_match.group(2)
                # Remove DOB, Gender, and OCR errors
                address = re.sub(r'\b\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{4}\b', '', address)
                address = re.sub(r'\b(MALE|FEMALE|Male|Female|पुरुष|महिला|gea|gea\/)\b', '', address, flags=re.IGNORECASE)
                address = re.sub(r'^[^A-Za-z0-9]*', '', address)
                # Clean up
                address_lines = [line.strip() for line in address.split('\n') if line.strip()]
                cleaned_address = ', '.join(address_lines)
                address = self._clean_address(f"{cleaned_address} - {pincode}")
                # Remove multiple dashes
                address = re.sub(r'--+', '-', address)
                if len(address) >= 10:
                    all_matches.append((address, pin_match.group(0), False, True))
        
        if not all_matches:
            return None
        
        # Prefer matches with PIN codes
        with_pin = [m for m in all_matches if m[3]]
        best_match = with_pin[0] if with_pin else all_matches[0]
        
        value, raw_match, has_label, has_pin = best_match
        match_type = MatchType.LABELED_REGEX if has_label else MatchType.HEURISTIC
        
        confidence, notes = self._calculate_confidence(
            match_type=match_type,
            has_label=has_label,
            validation_passed=has_pin,  # PIN code validates the address
            value_length=len(value),
            ocr_confidence=ocr_confidence,
            multiple_matches=len(all_matches) > 1
        )
        
        # Addresses are complex and error-prone
        confidence = min(confidence, 0.82)
        notes.append("Address extraction may need manual verification")
        
        if not has_pin:
            notes.append("PIN code not found in address")
            confidence -= 0.05
        
        return ExtractionMatch(
            value=value,
            raw_match=raw_match[:100] + "..." if len(raw_match) > 100 else raw_match,
            confidence=max(0.0, confidence),
            match_type=match_type,
            has_label=has_label,
            validation_passed=has_pin,
            notes=notes
        )
    
    def _normalize_date(self, date_str: str) -> Optional[str]:
        """Normalize date to DD/MM/YYYY format."""
        try:
            date_str = date_str.strip()
            
            # Handle DD/MM/YYYY or DD-MM-YYYY
            if '/' in date_str or '-' in date_str or '.' in date_str:
                parts = re.split(r'[\/\-\s\.]+', date_str)
                if len(parts) >= 3:
                    day = parts[0].zfill(2)
                    month = parts[1].zfill(2)
                    year = parts[2]
                    # Validate
                    if len(year) == 4 and 1900 <= int(year) <= 2025:
                        if 1 <= int(day) <= 31 and 1 <= int(month) <= 12:
                            return f"{day}/{month}/{year}"
            
            # Handle DD MMM YYYY format
            month_names = {
                'jan': '01', 'feb': '02', 'mar': '03', 'apr': '04',
                'may': '05', 'jun': '06', 'jul': '07', 'aug': '08',
                'sep': '09', 'oct': '10', 'nov': '11', 'dec': '12'
            }
            parts = date_str.split()
            if len(parts) >= 3:
                day = parts[0].zfill(2)
                month_str = parts[1].lower()[:3]
                year = parts[2]
                if month_str in month_names and len(year) == 4:
                    return f"{day}/{month_names[month_str]}/{year}"
        except:
            pass
        return None
    
    def _clean_address(self, address: str) -> str:
        """Clean and normalize extracted address."""
        # Remove extra whitespace and newlines
        address = ' '.join(address.split())
        # Remove excessive punctuation
        address = re.sub(r'[\.]{2,}', '.', address)
        # Normalize common abbreviations
        replacements = {
            r'\bSt\b': 'Street',
            r'\bRd\b': 'Road',
            r'\bAve\b': 'Avenue',
            r'\bP\.O\.': 'Post Office',
            r'\bDist\b': 'District',
            r'\bState\b': 'State',
        }
        for pattern, replacement in replacements.items():
            address = re.sub(pattern, replacement, address, flags=re.IGNORECASE)
        return address.strip()
    
    def _extract_pincode(
        self, 
        text: str, 
        ocr_confidence: Optional[float] = None
    ) -> Optional[ExtractionMatch]:
        """Extract 6-digit Indian PIN code with confidence scoring."""
        patterns = [
            (r'(?:PIN|Pincode|पिन)\s*[:\-]?\s*([1-9]\d{5})\b', True),
            (r'\b([1-9]\d{5})\b', False),
        ]
        
        all_matches = []
        
        for pattern, has_label in patterns:
            for match in re.finditer(pattern, text):
                pincode = match.group(1)
                # Basic validation: Indian PIN codes have specific ranges
                first_digit = int(pincode[0])
                # PIN codes 1-8 are valid (no state has 9 as first digit)
                valid_range = first_digit >= 1 and first_digit <= 8
                all_matches.append((pincode, match.group(0), has_label, valid_range))
        
        if not all_matches:
            return None
        
        # Prefer labeled, validated matches
        best_matches = sorted(all_matches, key=lambda x: (x[2], x[3]), reverse=True)
        value, raw_match, has_label, valid_range = best_matches[0]
        
        match_type = MatchType.LABELED_REGEX if has_label else MatchType.EXACT_REGEX
        
        confidence, notes = self._calculate_confidence(
            match_type=match_type,
            has_label=has_label,
            validation_passed=valid_range,
            value_length=6,
            ocr_confidence=ocr_confidence,
            multiple_matches=len(all_matches) > 3
        )
        
        return ExtractionMatch(
            value=value,
            raw_match=raw_match,
            confidence=confidence,
            match_type=match_type,
            has_label=has_label,
            validation_passed=valid_range,
            notes=notes
        )
    
    def _extract_phone(
        self,
        text: str,
        ocr_confidence: Optional[float] = None
    ) -> Optional[ExtractionMatch]:
        """Extract phone/mobile number."""
        patterns = [
            # Indian mobile: 10 digits starting with 6-9
            (r'(?:Mobile|Phone|Mob|Tel|Contact)\s*[:\-]?\s*(\+?91[\s\-]?)?([6-9]\d{9})\b', True),
            (r'\b(\+?91[\s\-]?)?([6-9]\d{9})\b', False),
        ]
        
        for pattern, has_label in patterns:
            match = re.search(pattern, text)
            if match:
                # Get the mobile number (last group)
                phone = match.group(-1) if match.groups() else match.group(0)
                if len(phone) == 10 and phone[0] in '6789':
                    match_type = MatchType.LABELED_REGEX if has_label else MatchType.UNLABELED_REGEX
                    confidence, notes = self._calculate_confidence(
                        match_type=match_type,
                        has_label=has_label,
                        validation_passed=True,
                        value_length=len(phone),
                        ocr_confidence=ocr_confidence
                    )
                    return ExtractionMatch(
                        value=phone,
                        raw_match=match.group(0),
                        confidence=confidence,
                        match_type=match_type,
                        has_label=has_label,
                        validation_passed=True,
                        notes=notes
                    )
        return None
    
    def _extract_email(
        self,
        text: str,
        ocr_confidence: Optional[float] = None
    ) -> Optional[ExtractionMatch]:
        """Extract email address."""
        # Email pattern - very specific to avoid matching addresses
        email_pattern = r'\b([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})\b'
        
        match = re.search(email_pattern, text)
        if match:
            email = match.group(1).lower()
            # Basic validation
            if '@' in email and '.' in email.split('@')[1]:
                match_type = MatchType.LABELED_REGEX
                confidence, notes = self._calculate_confidence(
                    match_type=match_type,
                    has_label=True,
                    validation_passed=True,
                    value_length=len(email),
                    ocr_confidence=ocr_confidence
                )
                return ExtractionMatch(
                    value=email,
                    raw_match=match.group(0),
                    confidence=confidence,
                    match_type=match_type,
                    has_label=True,
                    validation_passed=True,
                    notes=notes
                )
        return None
    
    # =========================================================================
    # MAIN EXTRACTION METHOD (Enhanced)
    # =========================================================================
    
    def extract_entities_enhanced(
        self, 
        text: str,
        ocr_confidence: Optional[float] = None
    ) -> Tuple[EnhancedExtractionResult, int]:
        """
        Main method to extract all entities with enhanced confidence scoring.
        
        Args:
            text: Raw OCR text
            ocr_confidence: Overall OCR confidence (0-100), if available
            
        Returns:
            Tuple of (EnhancedExtractionResult, extraction_time_ms) with structured output format:
            {
                "entities": {
                    "name": { "value": "", "confidence": 0.0, ... },
                    "dob": { "value": "", "confidence": 0.0, ... }
                },
                "detected_language": "",
                "notes": []
            }
        """
        start_time = time.time()
        logger.info("Starting enhanced entity extraction")
        logger.debug(f"Input text length: {len(text)}")
        logger.debug(f"Input text preview (first 300 chars): {text[:300]}")
        all_notes: List[str] = []
        
        if not text or not text.strip():
            logger.warning("Empty text provided for entity extraction")
            extraction_time_ms = int((time.time() - start_time) * 1000)
            return EnhancedExtractionResult(
                entities={},
                document_type=DocumentType.UNKNOWN,
                detected_language="unknown",
                notes=["Empty or invalid text provided"],
                overall_confidence=0.0,
                needs_review=True,
                extraction_stats={"entities_found": 0, "text_length": 0, "extraction_time_ms": extraction_time_ms}
            ), extraction_time_ms
        
        # Detect language
        detected_lang, lang_notes = self._detect_language(text)
        all_notes.extend(lang_notes)
        
        # Detect document type
        doc_type, doc_confidence, doc_notes = self.detect_document_type(text)
        all_notes.extend(doc_notes)
        
        # Define extraction methods
        extraction_methods = [
            ('aadhaar_number', self._extract_aadhaar_number),
            ('pan_number', self._extract_pan_number),
            ('voter_id', self._extract_voter_id),
            ('passport_number', self._extract_passport_number),
            ('driving_license', self._extract_driving_license),
            ('bank_account', self._extract_bank_account),
            ('ifsc_code', self._extract_ifsc_code),
            ('full_name', self._extract_name),
            ('father_name', self._extract_father_name),
            ('dob', self._extract_dob),
            ('gender', self._extract_gender),
            ('address', self._extract_address),
            ('pincode', self._extract_pincode),
            ('phone', self._extract_phone),
            ('email', self._extract_email),
        ]
        
        entities: Dict[str, EntityValue] = {}
        confidences: List[float] = []
        needs_review = False
        
        # Track extracted DOB and Gender to exclude from address
        extracted_dob = None
        extracted_gender = None
        
        for field_name, extract_func in extraction_methods:
            # For address extraction, pass exclude patterns if DOB/Gender were found
            if field_name == 'address' and (extracted_dob or extracted_gender):
                exclude_patterns = []
                if extracted_dob:
                    # Create pattern to exclude the extracted DOB
                    dob_value = extracted_dob.replace('/', r'[/\-]').replace('.', r'\.')
                    exclude_patterns.append(rf'\b{dob_value}\b')
                if extracted_gender:
                    # Exclude gender values
                    exclude_patterns.append(r'\b(MALE|FEMALE|Male|Female|पुरुष|महिला)\b')
                result = extract_func(text, ocr_confidence, exclude_patterns=exclude_patterns)
            else:
                result = extract_func(text, ocr_confidence)
            
            if result:
                # Track DOB and Gender for address exclusion (before creating EntityValue)
                if field_name == 'dob':
                    extracted_dob = result.value
                elif field_name == 'gender':
                    extracted_gender = result.value
                conf_level = get_confidence_level(result.confidence)
                
                entities[field_name] = EntityValue(
                    value=result.value,
                    confidence=round(result.confidence, 3),
                    confidence_level=conf_level,
                    match_type=result.match_type,
                    source="ocr",
                    raw_match=result.raw_match
                )
                
                confidences.append(result.confidence)
                all_notes.extend(result.notes)
                
                # Flag for review if confidence is low
                if result.confidence < 0.6:
                    needs_review = True
                    all_notes.append(f"Low confidence on {field_name} - review recommended")
        
        # Calculate overall confidence
        overall_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        
        # Calculate extraction time
        extraction_time_ms = int((time.time() - start_time) * 1000)
        
        # Build stats
        extraction_stats = {
            "entities_found": len(entities),
            "text_length": len(text),
            "document_type_confidence": round(doc_confidence, 3),
            "high_confidence_fields": sum(1 for e in entities.values() if e.confidence >= 0.85),
            "low_confidence_fields": sum(1 for e in entities.values() if e.confidence < 0.6),
            "extraction_time_ms": extraction_time_ms,
        }
        
        logger.info(
            f"Enhanced extraction complete: {len(entities)} entities, "
            f"overall confidence: {overall_confidence:.2f}, needs_review: {needs_review}, "
            f"time: {extraction_time_ms}ms"
        )
        
        return EnhancedExtractionResult(
            entities=entities,
            document_type=doc_type,
            detected_language=detected_lang,
            notes=list(set(all_notes)),  # Deduplicate notes
            overall_confidence=round(overall_confidence, 3),
            needs_review=needs_review,
            extraction_stats=extraction_stats
        ), extraction_time_ms
    
    # =========================================================================
    # LEGACY METHOD (for backward compatibility)
    # =========================================================================
    
    def extract_entities(self, text: str) -> Tuple[EntityExtractionResult, int]:
        """
        Legacy method for backward compatibility.
        Converts enhanced result to legacy format.
        
        Returns:
            Tuple of (EntityExtractionResult, extraction_time_ms)
        """
        enhanced, extraction_time_ms = self.extract_entities_enhanced(text)
        
        # Convert to legacy format
        entities = [
            ExtractedEntity(
                field_name=name,
                value=entity.value,
                confidence=entity.confidence * 100,  # Convert to 0-100 scale
                source=entity.source
            )
            for name, entity in enhanced.entities.items()
        ]
        
        return EntityExtractionResult(
            document_type=enhanced.document_type,
            entities=entities,
            raw_text=text,
            needs_review=enhanced.needs_review
        ), extraction_time_ms


# Singleton instance
entity_extraction_service = EntityExtractionService()
