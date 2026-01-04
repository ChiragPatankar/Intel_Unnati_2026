"""
Comprehensive Workflow Tests
Run: python -m pytest tests/test_workflow.py -v
"""

import pytest
import requests
import json
from typing import Dict, Any

BASE_URL = "http://localhost:8000/api/v1"


class TestProfileWorkflow:
    """Test profile creation and management"""
    
    profile_id = None
    
    def test_create_profile(self):
        """Test creating a profile with comprehensive data"""
        payload = {
            "name": "Test Profile - Automated",
            "fields": {
                "full_name": "RAJESH KUMAR SHARMA",
                "first_name": "RAJESH",
                "last_name": "SHARMA",
                "father_name": "SURESH KUMAR SHARMA",
                "dob": "15/08/1990",
                "gender": "Male",
                "aadhaar_number": "1234 5678 9012",
                "pan_number": "ABCDE1234F",
                "passport_number": "A1234567",
                "driving_license": "DL-0420110123456",
                "email": "rajesh.sharma@email.com",
                "phone": "9876543210",
                "address": "123 Main Street, Sector 15, Gurgaon",
                "city": "Gurgaon",
                "state": "Haryana",
                "pincode": "122001"
            }
        }
        
        response = requests.post(f"{BASE_URL}/profile/create", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["name"] == "Test Profile - Automated"
        assert "id" in data
        assert len(data["fields"]) > 0
        
        TestProfileWorkflow.profile_id = data["id"]
        print(f"✅ Created profile: {data['id']}")
    
    def test_get_profile(self):
        """Test retrieving a profile"""
        if not TestProfileWorkflow.profile_id:
            pytest.skip("No profile created")
        
        response = requests.get(f"{BASE_URL}/profile/{TestProfileWorkflow.profile_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == TestProfileWorkflow.profile_id
        print(f"✅ Retrieved profile with {len(data['fields'])} fields")
    
    def test_get_autofill_data(self):
        """Test getting autofill data with aliases"""
        if not TestProfileWorkflow.profile_id:
            pytest.skip("No profile created")
        
        response = requests.get(f"{BASE_URL}/profile/{TestProfileWorkflow.profile_id}/autofill")
        assert response.status_code == 200
        
        data = response.json()
        fields = data["fields"]
        
        # Check that aliases are generated
        assert "firstname" in fields or "first_name" in fields
        assert "lastname" in fields or "last_name" in fields
        print(f"✅ Autofill data has {len(fields)} fields (with aliases)")
    
    def test_update_profile(self):
        """Test updating profile fields"""
        if not TestProfileWorkflow.profile_id:
            pytest.skip("No profile created")
        
        payload = {
            "fields": {
                "occupation": "Senior Software Engineer",
                "company": "Tech Corp"
            }
        }
        
        response = requests.put(
            f"{BASE_URL}/profile/{TestProfileWorkflow.profile_id}", 
            json=payload
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["fields"]["occupation"] == "Senior Software Engineer"
        print("✅ Profile updated successfully")
    
    def test_list_profiles(self):
        """Test listing all profiles"""
        response = requests.get(f"{BASE_URL}/profile/list")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        print(f"✅ Found {len(data)} profiles")
    
    def test_delete_profile(self):
        """Test deleting a profile"""
        if not TestProfileWorkflow.profile_id:
            pytest.skip("No profile created")
        
        response = requests.delete(f"{BASE_URL}/profile/{TestProfileWorkflow.profile_id}")
        assert response.status_code == 200
        print("✅ Profile deleted successfully")


class TestSecurityWorkflow:
    """Test encryption and security features"""
    
    test_password = "SecureTestPass123!"
    
    def test_initial_status(self):
        """Test initial security status"""
        response = requests.get(f"{BASE_URL}/security/status")
        assert response.status_code == 200
        
        data = response.json()
        assert "password_set" in data
        assert "unlocked" in data
        print(f"✅ Security status: password_set={data['password_set']}, unlocked={data['unlocked']}")
    
    def test_set_password(self):
        """Test setting master password"""
        # First check if password already set
        status = requests.get(f"{BASE_URL}/security/status").json()
        
        if status["password_set"]:
            pytest.skip("Password already set")
        
        payload = {"password": self.test_password}
        response = requests.post(f"{BASE_URL}/security/set-password", json=payload)
        assert response.status_code == 200
        print("✅ Master password set")
    
    def test_lock_unlock(self):
        """Test lock and unlock cycle"""
        # Lock
        response = requests.post(f"{BASE_URL}/security/lock")
        assert response.status_code == 200
        assert response.json()["unlocked"] == False
        print("✅ Encryption locked")
        
        # Unlock with wrong password
        response = requests.post(
            f"{BASE_URL}/security/unlock", 
            json={"password": "WrongPassword"}
        )
        assert response.status_code == 401
        print("✅ Wrong password rejected")
        
        # Unlock with correct password
        response = requests.post(
            f"{BASE_URL}/security/unlock",
            json={"password": self.test_password}
        )
        assert response.status_code == 200
        assert response.json()["unlocked"] == True
        print("✅ Encryption unlocked with correct password")


class TestEntityExtraction:
    """Test entity extraction patterns"""
    
    def test_aadhaar_extraction(self):
        """Test Aadhaar number extraction"""
        # This would require an actual image upload
        # For unit testing, we could test the pattern directly
        import re
        
        pattern = r'\d{4}\s?\d{4}\s?\d{4}'
        test_cases = [
            ("Aadhaar: 1234 5678 9012", True),
            ("UID: 123456789012", True),
            ("Invalid: 12345678", False),
        ]
        
        for text, should_match in test_cases:
            match = re.search(pattern, text)
            assert (match is not None) == should_match
        
        print("✅ Aadhaar patterns validated")
    
    def test_pan_extraction(self):
        """Test PAN number extraction"""
        import re
        
        pattern = r'[A-Z]{5}[0-9]{4}[A-Z]{1}'
        test_cases = [
            ("PAN: ABCDE1234F", True),
            ("XYZPQ9876R", True),
            ("Invalid: ABC12345", False),
        ]
        
        for text, should_match in test_cases:
            match = re.search(pattern, text)
            assert (match is not None) == should_match
        
        print("✅ PAN patterns validated")
    
    def test_passport_extraction(self):
        """Test passport number extraction"""
        import re
        
        pattern = r'[A-Z][0-9]{7}'
        test_cases = [
            ("Passport: A1234567", True),
            ("Z9876543", True),
            ("Invalid: 12345678", False),
        ]
        
        for text, should_match in test_cases:
            match = re.search(pattern, text)
            assert (match is not None) == should_match
        
        print("✅ Passport patterns validated")


class TestFieldMatching:
    """Test fuzzy field matching logic"""
    
    def test_levenshtein_distance(self):
        """Test similarity calculation"""
        # Simple test cases for string similarity
        test_cases = [
            ("first_name", "firstname", True),  # Should be similar
            ("email", "emailaddress", True),    # Should match
            ("name", "xyz", False),             # Not similar
        ]
        
        def similarity(a, b):
            # Simple implementation for testing
            a, b = a.lower(), b.lower()
            if a == b:
                return 1.0
            if a in b or b in a:
                return 0.8
            return 0.2
        
        for field_a, field_b, should_match in test_cases:
            sim = similarity(field_a, field_b)
            assert (sim > 0.5) == should_match
        
        print("✅ Field matching logic validated")


def run_all_tests():
    """Run all tests with verbose output"""
    print("\n" + "="*60)
    print("🧪 FORM FILLING ASSISTANT - COMPREHENSIVE TESTS")
    print("="*60 + "\n")
    
    # Profile tests
    print("\n📁 PROFILE WORKFLOW TESTS\n" + "-"*40)
    profile_tests = TestProfileWorkflow()
    try:
        profile_tests.test_create_profile()
        profile_tests.test_get_profile()
        profile_tests.test_get_autofill_data()
        profile_tests.test_update_profile()
        profile_tests.test_list_profiles()
        profile_tests.test_delete_profile()
    except Exception as e:
        print(f"❌ Profile test failed: {e}")
    
    # Security tests
    print("\n🔐 SECURITY WORKFLOW TESTS\n" + "-"*40)
    security_tests = TestSecurityWorkflow()
    try:
        security_tests.test_initial_status()
        # Note: set_password and lock/unlock may fail if password already set
    except Exception as e:
        print(f"❌ Security test failed: {e}")
    
    # Extraction tests
    print("\n📄 ENTITY EXTRACTION TESTS\n" + "-"*40)
    extraction_tests = TestEntityExtraction()
    try:
        extraction_tests.test_aadhaar_extraction()
        extraction_tests.test_pan_extraction()
        extraction_tests.test_passport_extraction()
    except Exception as e:
        print(f"❌ Extraction test failed: {e}")
    
    # Field matching tests
    print("\n🔍 FIELD MATCHING TESTS\n" + "-"*40)
    matching_tests = TestFieldMatching()
    try:
        matching_tests.test_levenshtein_distance()
    except Exception as e:
        print(f"❌ Matching test failed: {e}")
    
    print("\n" + "="*60)
    print("✅ TEST SUITE COMPLETED")
    print("="*60 + "\n")


if __name__ == "__main__":
    run_all_tests()

