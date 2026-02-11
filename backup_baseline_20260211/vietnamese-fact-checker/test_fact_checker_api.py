#!/usr/bin/env python3
"""
Test Vietnamese Fact Checker Server API
"""

import requests
import time
import json

def test_fact_checker_api():
    """Test Vietnamese Fact Checker API endpoints"""
    
    base_url = "http://localhost:8005"
    
    print(" Testing Vietnamese Fact Checker API")
    print("=" * 50)
    
    # Test 1: Health check
    print("1. Testing health check...")
    try:
        response = requests.get(f"{base_url}/", timeout=10)
        if response.status_code == 200:
            print(" Health check passed")
            print(f"   Response: {response.json()}")
        else:
            print(f" Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f" Health check error: {e}")
        return False
    
    # Test 2: API docs
    print("\n2. Testing API docs...")
    try:
        response = requests.get(f"{base_url}/docs", timeout=10)
        if response.status_code == 200:
            print(" API docs accessible")
        else:
            print(f" API docs failed: {response.status_code}")
    except Exception as e:
        print(f" API docs error: {e}")
    
    # Test 3: Fact check endpoint
    print("\n3. Testing fact check endpoint...")
    test_claims = [
        "Hà Nội là thủ đô của Việt Nam",
        "Tôi thích ăn phở",
        "Việt Nam có dân số 100 triệu người"
    ]
    
    for i, claim in enumerate(test_claims, 1):
        print(f"\n   3.{i} Testing claim: '{claim}'")
        
        try:
            start_time = time.time()
            response = requests.post(
                f"{base_url}/check",
                json={"claim": claim},
                timeout=60  # Longer timeout for fact checking
            )
            
            total_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                print(f"    Fact check completed in {total_time:.2f}s")
                print(f"    Verdict: {result.get('verdict', 'N/A')}")
                print(f"    Confidence: {result.get('confidence', 0):.3f}")
                print(f"    Rationale: {result.get('rationale', 'N/A')[:100]}...")
                print(f"    Evidence count: {result.get('evidence_count', 0)}")
                print(f"   ⏱ Processing time: {result.get('processing_time', 0):.2f}s")
                
                # Check translation debug info
                debug_info = result.get('debug_info', {})
                translation_debug = debug_info.get('translation', {})
                if translation_debug:
                    print(f"    Translation API: {translation_debug.get('translation_api', 'N/A')}")
                    print(f"    Translation model: {translation_debug.get('translation_model', 'N/A')}")
                
            else:
                print(f"    Fact check failed: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"    Error: {error_data}")
                except:
                    print(f"    Response: {response.text[:200]}")
                    
        except Exception as e:
            print(f"    Fact check error: {e}")
    
    # Test 4: Check dependencies
    print("\n4. Testing dependencies...")
    
    # Check translation system
    print("   4.1 Checking translation system (port 8003)...")
    try:
        response = requests.get("http://localhost:8003/", timeout=5)
        if response.status_code == 200:
            print("    Translation system is running")
            data = response.json()
            print(f"    Cache dir: {data.get('cache_dir', 'N/A')}")
            print(f"    Model loaded: {data.get('model_loaded', 'N/A')}")
        else:
            print("    Translation system not responding")
    except Exception as e:
        print(f"    Translation system error: {e}")
    
    # Check MiniCheck API
    print("   4.2 Checking MiniCheck API (port 8002)...")
    try:
        response = requests.get("http://localhost:8002/", timeout=5)
        if response.status_code == 200:
            print("    MiniCheck API is running")
        else:
            print("    MiniCheck API not responding")
    except Exception as e:
        print(f"    MiniCheck API error: {e}")
    
    print("\n API testing completed!")
    return True

if __name__ == "__main__":
    print(" Make sure Vietnamese Fact Checker is running on port 8005")
    print(" Start with: python start_vietnamese_checker.py")
    print(" Translation system should be running on port 8003")
    print(" MiniCheck API should be running on port 8002")
    print()
    
    input("Press Enter to start testing...")
    test_fact_checker_api()
