"""
Data Validation and Cleaning Utilities
Provides functions to validate and clean extracted data
"""
import re
from typing import Optional, Tuple

def validate_aadhaar(aadhaar: str) -> Tuple[bool, Optional[str]]:
    """Validate Aadhaar number format."""
    # Remove spaces and dashes
    cleaned = re.sub(r'[\s\-]', '', aadhaar)
    
    # Must be 12 digits
    if not re.match(r'^\d{12}$', cleaned):
        return False, "Aadhaar must be 12 digits"
    
    # Cannot be all same digit (e.g., 1111 1111 1111)
    if len(set(cleaned)) == 1:
        return False, "Invalid Aadhaar format"
    
    # Format: XXXX XXXX XXXX
    formatted = f"{cleaned[:4]} {cleaned[4:8]} {cleaned[8:]}"
    return True, formatted

def validate_pan(pan: str) -> Tuple[bool, Optional[str]]:
    """Validate PAN number format."""
    # Remove spaces
    cleaned = re.sub(r'\s', '', pan.upper())
    
    # Format: ABCDE1234F (5 letters, 4 digits, 1 letter)
    if not re.match(r'^[A-Z]{5}\d{4}[A-Z]{1}$', cleaned):
        return False, "PAN must be in format ABCDE1234F"
    
    return True, cleaned

def validate_pincode(pincode: str) -> Tuple[bool, Optional[str]]:
    """Validate Indian PIN code."""
    # Remove spaces
    cleaned = re.sub(r'\s', '', pincode)
    
    # Must be 6 digits, first digit 1-8
    if not re.match(r'^[1-8]\d{5}$', cleaned):
        return False, "PIN code must be 6 digits starting with 1-8"
    
    return True, cleaned

def validate_mobile(mobile: str) -> Tuple[bool, Optional[str]]:
    """Validate Indian mobile number."""
    # Remove spaces, dashes, plus
    cleaned = re.sub(r'[\s\-\+]', '', mobile)
    
    # Remove country code if present
    if cleaned.startswith('91'):
        cleaned = cleaned[2:]
    
    # Must be 10 digits starting with 6-9
    if not re.match(r'^[6-9]\d{9}$', cleaned):
        return False, "Mobile must be 10 digits starting with 6-9"
    
    return True, cleaned

def clean_name(name: str) -> str:
    """Clean and normalize name."""
    if not name:
        return ""
    
    # Remove extra whitespace
    name = ' '.join(name.split())
    
    # Remove special characters except spaces and hyphens
    name = re.sub(r'[^\w\s\-]', '', name)
    
    # Capitalize properly
    words = name.split()
    cleaned = ' '.join(word.capitalize() for word in words)
    
    return cleaned.strip()

def clean_date(date_str: str) -> Optional[str]:
    """Clean and normalize date string."""
    if not date_str:
        return None
    
    # Remove extra whitespace
    date_str = date_str.strip()
    
    # Handle DD/MM/YYYY or DD-MM-YYYY
    if '/' in date_str or '-' in date_str:
        parts = re.split(r'[\/\-\s]+', date_str)
        if len(parts) >= 3:
            day = parts[0].zfill(2)
            month = parts[1].zfill(2)
            year = parts[2]
            if len(year) == 4:
                return f"{day}/{month}/{year}"
    
    return date_str

def clean_address(address: str) -> str:
    """Clean and normalize address."""
    if not address:
        return ""
    
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

def validate_email(email: str) -> Tuple[bool, Optional[str]]:
    """Validate email format."""
    if not email:
        return False, "Email is required"
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return False, "Invalid email format"
    
    return True, email.lower().strip()

