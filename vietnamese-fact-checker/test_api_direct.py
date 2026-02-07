#!/usr/bin/env python3
"""
Test Vietnamese Fact Checker API directly
"""

import requests
import json

def test_api():
    """Test the API with Vietnamese claim"""
    
    url = "http://localhost:8003/check"
    
    # Test data
    test_claims = [
        "Hà Nội là thủ đô của Việt Nam",
        "Ha Noi la thu do cua Viet Nam",  # ASCII version
        "Paris là thủ đô của Pháp"
    ]
    
    for claim in test_claims:
        print(f"\n Testing: {claim}")
        print("-" * 40)
        
        data = {"claim": claim}
        
        try:
            response = requests.post(url, json=data, timeout=30)
            
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f" Success!")
                print(f"Verdict: {result.get('verdict')}")
                print(f"Confidence: {result.get('confidence', 0):.4f}")
                print(f"Evidence: {result.get('evidence_count', 0)} sources")
                print(f"Time: {result.get('processing_time', 0):.2f}s")
                print(f"Method: {result.get('method')}")
                
                if result.get('error'):
                    print(f"  Error: {result.get('error')}")
            else:
                print(f" Failed: {response.status_code}")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f" Exception: {e}")

if __name__ == "__main__":
    test_api()
