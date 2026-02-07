#!/usr/bin/env python3
"""
Test Vietnamese Fact Checker with English claim
"""

import requests
import time

def test_english_claim():
    """Test with English claim"""
    print(" Testing Vietnamese Fact Checker with English Claim")
    print("=" * 60)
    
    base_url = "http://localhost:8005"
    
    # Test with English claim
    claim = "Ho Chi Minh City is the largest city in Vietnam"
    
    print(f" Claim: {claim}")
    print(f" Testing fact checking...")
    
    try:
        start_time = time.time()
        response = requests.post(
            f"{base_url}/check", 
            json={"claim": claim},
            timeout=60
        )
        end_time = time.time()
        
        if response.status_code == 200:
            result = response.json()
            
            print(f" Fact Check Result:")
            print(f"   Verdict: {result.get('verdict', 'UNKNOWN')}")
            print(f"   Confidence: {result.get('confidence', 0):.3f}")
            print(f"   Evidence Count: {result.get('evidence_count', 0)}")
            print(f"   Processing Time: {end_time - start_time:.2f}s")
            print(f"   Rationale: {result.get('rationale', 'No rationale')[:200]}...")
            
        else:
            print(f" HTTP Error: {response.status_code}")
                
    except Exception as e:
        print(f" Exception: {e}")

if __name__ == "__main__":
    test_english_claim()
