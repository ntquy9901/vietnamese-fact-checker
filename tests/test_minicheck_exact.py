#!/usr/bin/env python3
"""
Test MiniCheck with exact evidence from Vietnamese Fact Checker
"""

import requests

def test_minicheck_exact():
    """Test MiniCheck with exact evidence"""
    print(" Testing MiniCheck with Exact Evidence")
    print("=" * 50)
    
    base_url = "http://localhost:8002"
    
    # Exact data from Vietnamese Fact Checker logs
    claim = "Ho Chi Minh City is the largest city in Vietnam"
    evidence = [
        "Ho Chi Minh City (HCMC; Vietnamese:... name Saigon (Vietnamese: Saigon, IPA: [saːj ɣɔŋ]), is the mos..."
    ]
    
    print(f" Claim: {claim}")
    print(f" Evidence: {evidence[0][:100]}...")
    
    try:
        response = requests.post(
            f"{base_url}/verify",
            json={
                "claim": claim,
                "evidence": evidence
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f" Result: {result['label']}")
            print(f" Score: {result['score']:.3f}")
            print(f"⏱ Time: {result.get('processing_time', 0):.3f}s")
            print(f" Explanation: {result['explanation']}")
        else:
            print(f" Failed: {response.status_code}")
            print(f"   Error: {response.text}")
            
    except Exception as e:
        print(f" Exception: {e}")
    
    # Test with cleaner evidence
    print(f"\n" + "=" * 50)
    print(" Testing with Cleaner Evidence")
    print("=" * 50)
    
    clean_evidence = [
        "Ho Chi Minh City is the most populous city in Vietnam"
    ]
    
    print(f" Claim: {claim}")
    print(f" Clean Evidence: {clean_evidence[0]}")
    
    try:
        response = requests.post(
            f"{base_url}/verify",
            json={
                "claim": claim,
                "evidence": clean_evidence
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f" Result: {result['label']}")
            print(f" Score: {result['score']:.3f}")
            print(f"⏱ Time: {result.get('processing_time', 0):.3f}s")
            print(f" Explanation: {result['explanation']}")
        else:
            print(f" Failed: {response.status_code}")
            print(f"   Error: {response.text}")
            
    except Exception as e:
        print(f" Exception: {e}")
    
    print(f"\n Test completed!")

if __name__ == "__main__":
    test_minicheck_exact()
