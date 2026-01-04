"""
Enhanced Entity Extraction Patterns
Improved regex patterns and extraction logic for better accuracy
"""
import re
from typing import List, Tuple, Optional

# Enhanced name patterns for Indian documents
ENHANCED_NAME_PATTERNS = [
    # Aadhaar card patterns
    (r'(?:Name|Full Name|NAME OF THE HOLDER|नाम)\s*[:\-]?\s*([A-Z][A-Za-z\s]{2,50}?)(?:\n|DOB|Date|Father|Mother|Gender|$)', True, 'aadhaar'),
    # PAN card patterns
    (r'(?:Name|INCOME TAX DEPARTMENT|Name as it appears)\s*[:\-]?\s*([A-Z][A-Za-z\s]{2,50}?)(?:\n|Father|DOB|$)', True, 'pan'),
    # Passport patterns
    (r'(?:Surname|Given Name|Name)\s*[:\-]?\s*([A-Z][A-Za-z\s]{2,50}?)(?:\n|Nationality|Date|$)', True, 'passport'),
    # Voter ID patterns
    (r'(?:Name|Elector\'s Name|नाम)\s*[:\-]?\s*([A-Z][A-Za-z\s]{2,50}?)(?:\n|Father|Husband|Age|$)', True, 'voter'),
    # Generic labeled patterns
    (r'(?:Name|Full Name)\s*[:\-]?\s*([A-Z][A-Za-z\s]{2,50}?)(?:\n|$)', True, 'generic'),
    # Name before DOB (very common pattern)
    (r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,4})[\s\S]{0,50}?(?:DOB|Date of Birth|जन्म)', False, 'contextual'),
    # Name after DOB
    (r'(?:DOB|Date of Birth|जन्म)[\s\S]{0,50}?([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,4})', False, 'contextual'),
    # All caps name (common in older documents)
    (r'([A-Z]{2,}(?:\s+[A-Z]{2,}){1,4})(?:\s|$)', False, 'allcaps'),
]

# Enhanced date patterns
ENHANCED_DATE_PATTERNS = [
    # DD/MM/YYYY with label
    (r'(?:DOB|Date of Birth|जन्म तिथि|Birth|D\.O\.B|Date)\s*[:\-]?\s*(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{4})', True, 'ddmmyyyy'),
    # DD-MM-YYYY
    (r'(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{4})', False, 'ddmmyyyy'),
    # DD MMM YYYY (e.g., 15 Aug 1990)
    (r'(?:DOB|Date of Birth)\s*[:\-]?\s*(\d{1,2}\s+[A-Za-z]{3,9}\s+\d{4})', True, 'ddmmmyyyy'),
    # YYYY-MM-DD (ISO format, sometimes used)
    (r'(\d{4}[\/\-\.]\d{1,2}[\/\-\.]\d{1,2})', False, 'yyyymmdd'),
    # DD MMMM YYYY (e.g., 15 August 1990)
    (r'(\d{1,2}\s+[A-Za-z]{3,9}\s+\d{4})', False, 'ddmmmyyyy'),
]

# Enhanced address patterns
ENHANCED_ADDRESS_PATTERNS = [
    # Address with PIN code
    (r'(?:Address|पता|Addr|Residence|Permanent Address)\s*[:\-]?\s*([\s\S]{10,300}?)(\d{6})(?:\s|$)', True, True),
    # Address without PIN
    (r'(?:Address|पता|Addr|Residence)\s*[:\-]?\s*([\s\S]{10,200}?)(?:\n\n|\n[A-Z]|$)', True, False),
    # Multi-line address block (common in Aadhaar)
    (r'(?:Address|पता)[\s\S]{0,20}?([A-Za-z0-9\s,\.\-\/]{20,200}?)(\d{6})', True, True),
]

def clean_name(name: str) -> str:
    """Clean and normalize extracted name."""
    # Remove extra whitespace
    name = ' '.join(name.split())
    # Remove common OCR errors
    name = re.sub(r'[^\w\s]', '', name)  # Remove special chars except spaces
    # Capitalize properly
    words = name.split()
    cleaned = ' '.join(word.capitalize() for word in words)
    return cleaned.strip()

def normalize_date(date_str: str, format_hint: str = 'ddmmyyyy') -> Optional[str]:
    """Normalize date to DD/MM/YYYY format."""
    try:
        # Remove extra whitespace
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
    return date_str  # Return original if normalization fails

def clean_address(address: str) -> str:
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
    }
    for pattern, replacement in replacements.items():
        address = re.sub(pattern, replacement, address, flags=re.IGNORECASE)
    return address.strip()

def extract_multi_line_address(text: str, start_marker: str = 'Address') -> Optional[str]:
    """Extract multi-line address block."""
    # Find address section
    addr_match = re.search(rf'{start_marker}[\s\S]{{0,30}}?([A-Za-z0-9\s,\.\-\/]{{20,300}}?)(\d{{6}})', text, re.IGNORECASE)
    if addr_match:
        address = addr_match.group(1).strip()
        pincode = addr_match.group(2)
        # Clean up address lines
        lines = [line.strip() for line in address.split('\n') if line.strip()]
        cleaned_address = ', '.join(lines)
        return f"{cleaned_address} - {pincode}"
    return None

