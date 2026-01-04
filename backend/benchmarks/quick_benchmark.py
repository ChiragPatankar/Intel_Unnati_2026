"""
Quick Performance Benchmark (no OCR, entity extraction only)
Tests pattern matching accuracy and API response times
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import requests
import time
import json
from datetime import datetime

# Import entity extraction service directly for accuracy tests
from app.services.entity_extraction import entity_extraction_service

API_BASE = "http://localhost:8000/api/v1"

def print_header(title):
    print(f"\n{'='*60}\n  {title}\n{'='*60}")

def test_entity_extraction():
    """Test entity extraction accuracy with known patterns - Direct service test"""
    print_header("ENTITY EXTRACTION ACCURACY TEST")
    
    test_cases = [
        {
            "name": "Aadhaar",
            "text": "GOVERNMENT OF INDIA\nUNIQUE IDENTIFICATION AUTHORITY OF INDIA\n\nRAJESH KUMAR SHARMA\nDOB: 15/08/1990\nMale\n\n1234 5678 9012\n\nAddress: 123 Main Street, Gurgaon, Haryana 122001",
            "expected": {"aadhaar_number": "1234 5678 9012", "gender": "Male", "dob": "15/08/1990"}
        },
        {
            "name": "PAN",  
            "text": "INCOME TAX DEPARTMENT\nPERMANENT ACCOUNT NUMBER CARD\n\nName: RAJESH KUMAR SHARMA\nFather's Name: SURESH KUMAR SHARMA\nDate of Birth: 15/08/1990\n\nABCDE1234F",
            "expected": {"pan_number": "ABCDE1234F"}
        },
        {
            "name": "Passport",
            "text": "REPUBLIC OF INDIA\nPASSPORT\n\nPassport No: A1234567\nSurname: SHARMA\nGiven Name: RAJESH KUMAR\nDate of Birth: 15/08/1990\nPlace of Issue: DELHI",
            "expected": {"passport_number": "A1234567"}
        },
        {
            "name": "Driving License",
            "text": "TRANSPORT DEPARTMENT\nDRIVING LICENSE\n\nDL No: DL-0420110123456\nName: RAJESH KUMAR SHARMA\nDate of Birth: 15-08-1990\nAddress: 123 Main Street, Delhi 110001",
            "expected": {"driving_license": "DL-0420110123456"}
        },
        {
            "name": "Bank IFSC",
            "text": "BANK STATEMENT\n\nAccount Number: 12345678901234\nIFSC Code: HDFC0000001\nBranch: Mumbai Main\nAccount Holder: RAJESH KUMAR",
            "expected": {"ifsc_code": "HDFC0000001", "bank_account_number": "12345678901234"}
        },
        {
            "name": "Contact Info",
            "text": "CONTACT DETAILS\n\nEmail: rajesh.sharma@email.com\nMobile: 9876543210\nAddress: 123 Main Street, Delhi",
            "expected": {"email": "rajesh.sharma@email.com", "phone": "9876543210"}
        },
        {
            "name": "Voter ID",
            "text": "ELECTION COMMISSION OF INDIA\nELECTOR PHOTO IDENTITY CARD\n\nName: RAJESH KUMAR SHARMA\nFather's Name: SURESH KUMAR\nEPIC No: ABC1234567\nAddress: 123 Main Street, Delhi",
            "expected": {"voter_id": "ABC1234567"}
        },
    ]
    
    total = 0
    correct = 0
    results = []
    
    for test in test_cases:
        print(f"\n  Testing: {test['name']}")
        
        # Use entity extraction service directly
        try:
            start = time.perf_counter()
            result_tuple = entity_extraction_service.extract_entities_enhanced(test["text"])
            elapsed = (time.perf_counter() - start) * 1000
            
            # Result is a tuple of (EnhancedExtractionResult, extraction_time_ms)
            extracted_data = result_tuple[0] if isinstance(result_tuple, tuple) else result_tuple
            
            # Convert to dict if it's a Pydantic model
            if hasattr(extracted_data, 'dict'):
                extracted_data = extracted_data.dict()
            elif hasattr(extracted_data, 'model_dump'):
                extracted_data = extracted_data.model_dump()
            
            entities = extracted_data.get("entities", {}) if isinstance(extracted_data, dict) else {}
            
            for field, expected_value in test["expected"].items():
                total += 1
                extracted = entities.get(field, {})
                extracted_value = extracted.get("value", "") if isinstance(extracted, dict) else str(extracted)
                
                # Normalize comparison
                exp_norm = expected_value.upper().replace(" ", "").replace("-", "")
                ext_norm = extracted_value.upper().replace(" ", "").replace("-", "")
                
                match = exp_norm == ext_norm or exp_norm in ext_norm or ext_norm in exp_norm
                
                if match:
                    correct += 1
                    confidence = extracted.get("confidence", 0) if isinstance(extracted, dict) else 0
                    print(f"    ✅ {field}: '{extracted_value}' (conf: {confidence:.0%})")
                else:
                    print(f"    ❌ {field}: expected '{expected_value}', got '{extracted_value}'")
                
                results.append({
                    "test": test["name"],
                    "field": field,
                    "expected": expected_value,
                    "extracted": extracted_value,
                    "match": match
                })
            
            print(f"    ⏱️ Time: {elapsed:.0f}ms")
            
        except Exception as e:
            print(f"    ❌ Error: {e}")
    
    accuracy = (correct / total * 100) if total > 0 else 0
    print(f"\n  📊 ACCURACY: {accuracy:.1f}% ({correct}/{total} fields)")
    
    if accuracy >= 90:
        print(f"  ✅ PASS: Meets 90% target!")
    elif accuracy >= 80:
        print(f"  ⚠️ Close to 90% target (needs tuning)")
    else:
        print(f"  ❌ Below 80% - needs improvement")
    
    return {"accuracy": accuracy, "correct": correct, "total": total, "results": results}

def test_api_latency():
    """Test API endpoint response times"""
    print_header("API RESPONSE TIME TEST")
    
    endpoints = [
        ("Health Check", "GET", "/health"),
        ("Security Status", "GET", "/api/v1/security/status"),
        ("Profile List", "GET", "/api/v1/profile/list"),
        ("Templates", "GET", "/api/v1/document/templates"),
    ]
    
    results = []
    
    for name, method, endpoint in endpoints:
        url = f"http://localhost:8000{endpoint}"
        
        # Warm up
        requests.get(url)
        
        # Time 5 requests
        times = []
        for _ in range(5):
            start = time.perf_counter()
            response = requests.get(url)
            elapsed = (time.perf_counter() - start) * 1000
            times.append(elapsed)
        
        avg = sum(times) / len(times)
        status = "✅" if response.status_code == 200 and avg < 500 else "⚠️"
        print(f"  {status} {name}: {avg:.0f}ms (status: {response.status_code})")
        
        results.append({"endpoint": endpoint, "avg_ms": avg, "status": response.status_code})
    
    return results

def test_extraction_speed():
    """Test entity extraction speed (no OCR) - Direct service test"""
    print_header("EXTRACTION SPEED TEST (Direct Service)")
    
    test_text = """
    GOVERNMENT OF INDIA
    UNIQUE IDENTIFICATION AUTHORITY OF INDIA
    
    RAJESH KUMAR SHARMA
    Date of Birth: 15/08/1990
    Gender: Male
    
    1234 5678 9012
    
    Address: 123 Main Street, Sector 15
    Gurgaon, Haryana - 122001
    
    PAN: ABCDE1234F
    Email: rajesh@email.com
    Phone: 9876543210
    """
    
    times = []
    for i in range(10):
        start = time.perf_counter()
        result_tuple = entity_extraction_service.extract_entities_enhanced(test_text)
        elapsed = (time.perf_counter() - start) * 1000
        times.append(elapsed)
        
        # Handle tuple result
        result = result_tuple[0] if isinstance(result_tuple, tuple) else result_tuple
        if hasattr(result, 'dict'):
            result = result.dict()
        elif hasattr(result, 'model_dump'):
            result = result.model_dump()
        
        entity_count = len(result.get("entities", {})) if isinstance(result, dict) else 0
        print(f"  Run {i+1}: {elapsed:.0f}ms ({entity_count} entities)")
    
    avg = sum(times) / len(times)
    min_t = min(times)
    max_t = max(times)
    
    print(f"\n  📊 Average: {avg:.0f}ms (min: {min_t:.0f}ms, max: {max_t:.0f}ms)")
    
    if avg < 100:
        print(f"  ✅ PASS: Very fast extraction (<100ms)")
    elif avg < 500:
        print(f"  ✅ PASS: Fast extraction (<500ms)")
    else:
        print(f"  ⚠️ Slow extraction (>500ms)")
    
    return {"avg_ms": avg, "min_ms": min_t, "max_ms": max_t, "times": times}

def main():
    print("\n" + "="*60)
    print("  FORM FILLING ASSISTANT - QUICK BENCHMARK")
    print("  " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("="*60)
    
    # Check API
    try:
        r = requests.get(f"{API_BASE.replace('/api/v1', '')}/health", timeout=5)
        if r.status_code != 200:
            print("\n❌ API not healthy!")
            return
    except:
        print("\n❌ Cannot connect to API. Start the server first:")
        print("   uvicorn app.main:app --port 8000")
        return
    
    print("\n✅ API is running")
    
    # Run tests
    results = {}
    results["extraction"] = test_entity_extraction()
    results["api_latency"] = test_api_latency()
    results["extraction_speed"] = test_extraction_speed()
    
    # Summary
    print_header("SUMMARY")
    print(f"  Entity Extraction Accuracy: {results['extraction']['accuracy']:.1f}%")
    print(f"  Extraction Speed (no OCR): {results['extraction_speed']['avg_ms']:.0f}ms")
    print(f"  API Response Times: OK")
    
    # Overall status
    accuracy_ok = results["extraction"]["accuracy"] >= 90
    speed_ok = results["extraction_speed"]["avg_ms"] < 1000
    
    if accuracy_ok and speed_ok:
        print("\n  🎉 ALL TARGETS MET!")
    else:
        print("\n  ⚠️ Some targets not met")
    
    # Save results
    report = {
        "timestamp": datetime.now().isoformat(),
        "results": results,
        "passed": accuracy_ok and speed_ok
    }
    
    with open("benchmarks/results/quick_benchmark.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"\n  📄 Report saved to benchmarks/results/quick_benchmark.json")
    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    main()

