#!/usr/bin/env python3
"""
Test Vietnamese Fact Checker Integration
"""

import requests
import time

def test_integration():
    """Test Vietnamese Fact Checker integration"""
    print(" Testing Vietnamese Fact Checker Integration")
    print("=" * 50)
    
    base_url = "http://localhost:8005"
    
    try:
        # Test health endpoint
        print("1⃣ Testing health endpoint...")
        response = requests.get(f"{base_url}/", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f" Health Check: {data.get('status', 'unknown')}")
        else:
            print(f" Health check failed: {response.status_code}")
            return False
        
        # Test fact checking
        print("\n2⃣ Testing fact checking...")
        test_claim = "Hà Nội là thủ đô của Việt Nam"
        
        start_time = time.time()
        response = requests.post(f"{base_url}/check", json={"claim": test_claim}, timeout=60)
        end_time = time.time()
        
        if response.status_code == 200:
            result = response.json()
            print(f" Fact Check Result: {result.get('verdict', 'UNKNOWN')}")
            print(f" Confidence: {result.get('confidence', 0):.3f}")
            print(f" Evidence Count: {result.get('evidence_count', 0)}")
            print(f"⏱ Processing Time: {end_time - start_time:.2f}s")
            print(f" Rationale: {result.get('rationale', 'No rationale')[:100]}...")
            return True
        else:
            print(f" Fact check failed: {response.status_code}")
            try:
                error_text = response.text
                print(f"   Error: {error_text[:200]}...")
            except:
                pass
            return False
            
    except Exception as e:
        print(f" Integration test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_integration()
    if success:
        print("\n Integration test PASSED!")
        print(" Vietnamese Fact Checker is working with baseline services!")
    else:
        print("\n Integration test FAILED!")
