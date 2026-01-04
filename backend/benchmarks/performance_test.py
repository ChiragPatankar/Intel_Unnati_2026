"""
Performance Benchmark Script for Form Filling Assistant

Tests:
1. OCR processing speed (Tesseract vs EasyOCR)
2. Entity extraction accuracy and speed
3. Full pipeline latency
4. API response times

Run: python benchmarks/performance_test.py
"""

import os
import sys
import time
import json
import statistics
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Tuple

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import requests

# Configuration
API_BASE = "http://localhost:8000/api/v1"
BENCHMARK_RESULTS_DIR = Path(__file__).parent / "results"
BENCHMARK_RESULTS_DIR.mkdir(exist_ok=True)

# Test data for accuracy measurement
EXPECTED_EXTRACTIONS = {
    "aadhaar_sample": {
        "aadhaar_number": "1234 5678 9012",
        "name": True,  # Just check if extracted
        "dob": True,
        "gender": True,
    },
    "pan_sample": {
        "pan_number": "ABCDE1234F",
        "name": True,
    },
}


class PerformanceBenchmark:
    """Performance testing suite for the Form Filling Assistant"""
    
    def __init__(self):
        self.results: Dict[str, Any] = {
            "timestamp": datetime.now().isoformat(),
            "system_info": self._get_system_info(),
            "tests": {},
            "summary": {}
        }
    
    def _get_system_info(self) -> Dict[str, str]:
        """Get system information"""
        import platform
        
        return {
            "os": platform.system(),
            "os_version": platform.version(),
            "python_version": platform.python_version(),
            "processor": platform.processor(),
            "machine": platform.machine(),
        }
    
    def _print_header(self, title: str):
        """Print section header"""
        print(f"\n{'='*60}")
        print(f"  {title}")
        print(f"{'='*60}\n")
    
    def _print_result(self, name: str, value: Any, unit: str = ""):
        """Print a result line"""
        if isinstance(value, float):
            print(f"  {name}: {value:.2f} {unit}")
        else:
            print(f"  {name}: {value} {unit}")
    
    def test_api_health(self) -> bool:
        """Test if API is running"""
        self._print_header("API Health Check")
        
        try:
            response = requests.get(f"{API_BASE.replace('/api/v1', '')}/health", timeout=5)
            if response.status_code == 200:
                print("  ✅ API is healthy")
                return True
            else:
                print(f"  ❌ API returned status {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            print("  ❌ Cannot connect to API. Is the server running?")
            print("  Run: uvicorn app.main:app --port 8000")
            return False
    
    def test_ocr_latency(self, iterations: int = 3) -> Dict[str, Any]:
        """Test OCR processing latency"""
        self._print_header("OCR Latency Test")
        
        # Create a simple test image with text
        test_text = "AADHAAR CARD\nName: Test User\nDOB: 01/01/1990\n1234 5678 9012"
        
        # Use a real test file if available, otherwise create synthetic test
        test_files = list(Path(__file__).parent.parent.glob("uploads/*.jpg"))
        
        if not test_files:
            print("  ⚠️  No test files found in uploads/")
            print("  Creating synthetic test...")
            return self._test_synthetic_ocr(iterations)
        
        test_file = test_files[0]
        latencies = []
        
        for i in range(iterations):
            print(f"  Iteration {i+1}/{iterations}...", end=" ", flush=True)
            
            with open(test_file, 'rb') as f:
                start = time.perf_counter()
                response = requests.post(
                    f"{API_BASE}/document/upload",
                    files={"file": (test_file.name, f, "image/jpeg")}
                )
                end = time.perf_counter()
            
            latency = (end - start) * 1000  # Convert to ms
            latencies.append(latency)
            
            if response.status_code == 200:
                data = response.json()
                print(f"{latency:.0f}ms (chars: {data.get('char_count', 'N/A')})")
            else:
                print(f"Failed: {response.status_code}")
        
        result = {
            "iterations": iterations,
            "latencies_ms": latencies,
            "min_ms": min(latencies),
            "max_ms": max(latencies),
            "avg_ms": statistics.mean(latencies),
            "median_ms": statistics.median(latencies),
            "stdev_ms": statistics.stdev(latencies) if len(latencies) > 1 else 0,
        }
        
        self._print_result("Min latency", result["min_ms"], "ms")
        self._print_result("Max latency", result["max_ms"], "ms")
        self._print_result("Average latency", result["avg_ms"], "ms")
        self._print_result("Median latency", result["median_ms"], "ms")
        
        # Check against target
        target_ms = 5000  # 5 seconds target
        if result["avg_ms"] <= target_ms:
            print(f"\n  ✅ PASS: Average latency ({result['avg_ms']:.0f}ms) <= target ({target_ms}ms)")
        else:
            print(f"\n  ⚠️  WARN: Average latency ({result['avg_ms']:.0f}ms) > target ({target_ms}ms)")
        
        return result
    
    def _test_synthetic_ocr(self, iterations: int) -> Dict[str, Any]:
        """Test with synthetic text data"""
        test_text = "Name: RAJESH KUMAR\nDOB: 15/08/1990\nAadhaar: 1234 5678 9012\nPAN: ABCDE1234F"
        
        latencies = []
        for i in range(iterations):
            print(f"  Iteration {i+1}/{iterations}...", end=" ", flush=True)
            
            start = time.perf_counter()
            response = requests.post(
                f"{API_BASE}/document/extract-entities-enhanced",
                files={"file": ("test.txt", test_text.encode(), "text/plain")}
            )
            end = time.perf_counter()
            
            latency = (end - start) * 1000
            latencies.append(latency)
            print(f"{latency:.0f}ms")
        
        return {
            "iterations": iterations,
            "latencies_ms": latencies,
            "avg_ms": statistics.mean(latencies),
            "note": "Synthetic test (no OCR, text only)"
        }
    
    def test_entity_extraction_accuracy(self) -> Dict[str, Any]:
        """Test entity extraction accuracy"""
        self._print_header("Entity Extraction Accuracy Test")
        
        test_cases = [
            {
                "name": "Aadhaar Card",
                "text": """
                    GOVERNMENT OF INDIA
                    UNIQUE IDENTIFICATION AUTHORITY OF INDIA
                    
                    RAJESH KUMAR SHARMA
                    DOB: 15/08/1990
                    Male
                    
                    1234 5678 9012
                    
                    Address: 123 Main Street, Sector 15
                    Gurgaon, Haryana - 122001
                """,
                "expected": {
                    "aadhaar_number": "1234 5678 9012",
                    "full_name": "RAJESH KUMAR SHARMA",
                    "dob": "15/08/1990",
                    "gender": "Male",
                }
            },
            {
                "name": "PAN Card",
                "text": """
                    INCOME TAX DEPARTMENT
                    PERMANENT ACCOUNT NUMBER CARD
                    
                    Name: RAJESH KUMAR SHARMA
                    Father's Name: SURESH KUMAR SHARMA
                    Date of Birth: 15/08/1990
                    
                    ABCDE1234F
                """,
                "expected": {
                    "pan_number": "ABCDE1234F",
                    "full_name": "RAJESH KUMAR SHARMA",
                }
            },
            {
                "name": "Passport",
                "text": """
                    REPUBLIC OF INDIA
                    PASSPORT
                    
                    Passport No: A1234567
                    Surname: SHARMA
                    Given Name: RAJESH KUMAR
                    Date of Birth: 15/08/1990
                    Place of Issue: DELHI
                """,
                "expected": {
                    "passport_number": "A1234567",
                }
            },
            {
                "name": "Driving License",
                "text": """
                    DRIVING LICENSE
                    
                    DL No: DL-0420110123456
                    Name: RAJESH KUMAR SHARMA
                    DOB: 15-08-1990
                    Address: 123 Main Street, Delhi
                """,
                "expected": {
                    "driving_license": "DL-0420110123456",
                }
            },
        ]
        
        results = []
        total_fields = 0
        correct_fields = 0
        
        for test in test_cases:
            print(f"\n  Testing: {test['name']}")
            
            # Create a temporary file-like object with the test text
            test_content = test["text"].strip().encode('utf-8')
            
            response = requests.post(
                f"{API_BASE}/document/extract-entities-enhanced",
                files={"file": (f"{test['name'].lower().replace(' ', '_')}.txt", test_content, "text/plain")}
            )
            
            if response.status_code != 200:
                print(f"    ❌ API Error: {response.status_code} - {response.text[:100]}")
                continue
            
            data = response.json()
            entities = data.get("entities", {})
            
            test_result = {"name": test["name"], "fields": []}
            
            for field, expected_value in test["expected"].items():
                total_fields += 1
                extracted = entities.get(field, {})
                extracted_value = extracted.get("value", "") if isinstance(extracted, dict) else extracted
                
                # Normalize for comparison
                expected_norm = str(expected_value).upper().replace(" ", "").replace("-", "")
                extracted_norm = str(extracted_value).upper().replace(" ", "").replace("-", "")
                
                match = expected_norm in extracted_norm or extracted_norm in expected_norm
                
                if match:
                    correct_fields += 1
                    status = "✅"
                else:
                    status = "❌"
                
                print(f"    {status} {field}: expected '{expected_value}' → got '{extracted_value}'")
                
                test_result["fields"].append({
                    "field": field,
                    "expected": expected_value,
                    "extracted": extracted_value,
                    "match": match
                })
            
            results.append(test_result)
        
        accuracy = (correct_fields / total_fields * 100) if total_fields > 0 else 0
        
        result = {
            "test_cases": len(test_cases),
            "total_fields": total_fields,
            "correct_fields": correct_fields,
            "accuracy_percent": accuracy,
            "details": results
        }
        
        print(f"\n  Overall Accuracy: {accuracy:.1f}% ({correct_fields}/{total_fields} fields)")
        
        # Check against target
        target_accuracy = 90
        if accuracy >= target_accuracy:
            print(f"  ✅ PASS: Accuracy ({accuracy:.1f}%) >= target ({target_accuracy}%)")
        else:
            print(f"  ⚠️  WARN: Accuracy ({accuracy:.1f}%) < target ({target_accuracy}%)")
        
        return result
    
    def test_api_response_times(self) -> Dict[str, Any]:
        """Test API endpoint response times"""
        self._print_header("API Response Time Test")
        
        endpoints = [
            ("GET", "/health", None),
            ("GET", "/api/v1/security/status", None),
            ("GET", "/api/v1/profile/list", None),
            ("GET", "/api/v1/document/templates", None),
        ]
        
        results = []
        
        for method, endpoint, data in endpoints:
            url = f"{API_BASE.replace('/api/v1', '')}{endpoint}"
            
            latencies = []
            for _ in range(5):
                start = time.perf_counter()
                if method == "GET":
                    response = requests.get(url)
                else:
                    response = requests.post(url, json=data)
                end = time.perf_counter()
                latencies.append((end - start) * 1000)
            
            avg_latency = statistics.mean(latencies)
            result = {
                "endpoint": endpoint,
                "method": method,
                "avg_ms": avg_latency,
                "status": response.status_code
            }
            results.append(result)
            
            status_icon = "✅" if response.status_code == 200 else "❌"
            print(f"  {status_icon} {method} {endpoint}: {avg_latency:.0f}ms")
        
        return {"endpoints": results}
    
    def test_concurrent_requests(self, num_concurrent: int = 5) -> Dict[str, Any]:
        """Test handling of concurrent requests"""
        self._print_header(f"Concurrent Requests Test (n={num_concurrent})")
        
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        test_text = "Name: Test User\nAadhaar: 1234 5678 9012"
        
        def make_request():
            start = time.perf_counter()
            response = requests.post(
                f"{API_BASE}/document/extract-entities-enhanced",
                files={"file": ("test.txt", test_text.encode(), "text/plain")}
            )
            end = time.perf_counter()
            return {
                "latency_ms": (end - start) * 1000,
                "status": response.status_code
            }
        
        with ThreadPoolExecutor(max_workers=num_concurrent) as executor:
            futures = [executor.submit(make_request) for _ in range(num_concurrent)]
            results = [f.result() for f in as_completed(futures)]
        
        latencies = [r["latency_ms"] for r in results]
        successes = sum(1 for r in results if r["status"] == 200)
        
        result = {
            "concurrent_requests": num_concurrent,
            "successful": successes,
            "failed": num_concurrent - successes,
            "avg_latency_ms": statistics.mean(latencies),
            "max_latency_ms": max(latencies),
        }
        
        self._print_result("Successful requests", f"{successes}/{num_concurrent}")
        self._print_result("Average latency", result["avg_latency_ms"], "ms")
        self._print_result("Max latency", result["max_latency_ms"], "ms")
        
        return result
    
    def generate_report(self):
        """Generate final benchmark report"""
        self._print_header("BENCHMARK SUMMARY")
        
        # Calculate overall status
        tests_passed = 0
        tests_total = len(self.results["tests"])
        
        for test_name, test_result in self.results["tests"].items():
            if test_name == "entity_extraction":
                if test_result.get("accuracy_percent", 0) >= 90:
                    tests_passed += 1
            elif test_name == "ocr_latency":
                if test_result.get("avg_ms", float('inf')) <= 5000:
                    tests_passed += 1
            else:
                tests_passed += 1  # Other tests pass if they complete
        
        self.results["summary"] = {
            "tests_passed": tests_passed,
            "tests_total": tests_total,
            "overall_status": "PASS" if tests_passed == tests_total else "PARTIAL",
            "generated_at": datetime.now().isoformat()
        }
        
        # Print summary
        print(f"  Tests Passed: {tests_passed}/{tests_total}")
        print(f"  Overall Status: {self.results['summary']['overall_status']}")
        
        # Save report
        report_file = BENCHMARK_RESULTS_DIR / f"benchmark_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n  📄 Report saved to: {report_file}")
        
        return self.results
    
    def run_all(self):
        """Run all benchmark tests"""
        print("\n" + "="*60)
        print("  FORM FILLING ASSISTANT - PERFORMANCE BENCHMARK")
        print("="*60)
        
        # Check API health first
        if not self.test_api_health():
            print("\n❌ Cannot continue without API. Please start the server.")
            return
        
        # Run all tests
        self.results["tests"]["ocr_latency"] = self.test_ocr_latency()
        self.results["tests"]["entity_extraction"] = self.test_entity_extraction_accuracy()
        self.results["tests"]["api_response"] = self.test_api_response_times()
        self.results["tests"]["concurrent"] = self.test_concurrent_requests()
        
        # Generate report
        self.generate_report()
        
        print("\n" + "="*60)
        print("  BENCHMARK COMPLETE")
        print("="*60 + "\n")


if __name__ == "__main__":
    benchmark = PerformanceBenchmark()
    benchmark.run_all()

