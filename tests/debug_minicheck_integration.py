#!/usr/bin/env python3
"""
Debug MiniCheck integration in Vietnamese Fact Checker
"""

import requests
import time

def debug_minicheck_integration():
    """Debug MiniCheck integration"""
    print(" Debugging MiniCheck Integration")
    print("=" * 50)
    
    # Test MiniCheck directly
    print("1⃣ Testing MiniCheck API directly...")
    try:
        minicheck_response = requests.post(
            "http://localhost:8002/verify",
            json={
                "claim": "Ho Chi Minh City is the largest city in Vietnam",
                "evidence": ["Ho Chi Minh City is the largest city in Vietnam by population."]
            },
            timeout=30
        )
        
        if minicheck_response.status_code == 200:
            minicheck_result = minicheck_response.json()
            print(f" MiniCheck Direct Result: {minicheck_result.get('label', 'UNKNOWN')}")
            print(f"   Score: {minicheck_result.get('score', 0):.3f}")
            print(f"   Processing Time: {minicheck_result.get('processing_time', 0):.3f}s")
        else:
            print(f" MiniCheck Direct Failed: {minicheck_response.status_code}")
            print(f"   Error: {minicheck_response.text[:200]}...")
            
    except Exception as e:
        print(f" MiniCheck Direct Exception: {e}")
    
    # Test Vietnamese Fact Checker with detailed logging
    print(f"\n2⃣ Testing Vietnamese Fact Checker...")
    
    claim = "Ho Chi Minh City is the largest city in Vietnam"
    
    try:
        response = requests.post(
            "http://localhost:8005/check", 
            json={"claim": claim},
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f" Fact Checker Result:")
            print(f"   Verdict: {result.get('verdict', 'UNKNOWN')}")
            print(f"   Confidence: {result.get('confidence', 0):.3f}")
            print(f"   Evidence Count: {result.get('evidence_count', 0)}")
            print(f"   Processing Time: {result.get('processing_time', 0):.2f}s")
            print(f"   Rationale: {result.get('rationale', 'No rationale')[:300]}...")
            
            # Check if there's detailed info
            if 'details' in result:
                details = result['details']
                print(f"   Details:")
                print(f"     Translation: {details.get('translation', 'N/A')}")
                print(f"     Search Results: {len(details.get('search_results', []))}")
                print(f"     MiniCheck Raw: {details.get('minicheck_raw', 'N/A')}")
        else:
            print(f" Fact Checker Failed: {response.status_code}")
            print(f"   Error: {response.text[:200]}...")
            
    except Exception as e:
        print(f" Fact Checker Exception: {e}")
    
    # Test with mock evidence
    print(f"\n3⃣ Testing MiniCheck with real evidence format...")
    
    try:
        # Get real evidence from Brave Search
        search_response = requests.post(
            "http://localhost:8004/search",
            json={"query": "Ho Chi Minh City largest city Vietnam", "limit": 3},
            timeout=15
        )
        
        if search_response.status_code == 200:
            search_result = search_response.json()
            results = search_result.get("results", [])
            
            print(f" Got {len(results)} search results")
            
            # Extract evidence from search results
            evidence_texts = []
            for item in results:
                evidence_texts.append(item.get('snippet', ''))
                evidence_texts.append(item.get('content', ''))
            
            evidence_texts = [e for e in evidence_texts if e][:3]  # Take first 3 non-empty
            
            print(f" Evidence texts: {len(evidence_texts)}")
            for i, evidence in enumerate(evidence_texts, 1):
                print(f"   {i}. {evidence[:100]}...")
            
            # Test MiniCheck with real evidence
            minicheck_response = requests.post(
                "http://localhost:8002/verify",
                json={
                    "claim": claim,
                    "evidence": evidence_texts
                },
                timeout=30
            )
            
            if minicheck_response.status_code == 200:
                minicheck_result = minicheck_response.json()
                print(f" MiniCheck with Real Evidence: {minicheck_result.get('label', 'UNKNOWN')}")
                print(f"   Score: {minicheck_result.get('score', 0):.3f}")
            else:
                print(f" MiniCheck with Real Evidence Failed: {minicheck_response.status_code}")
                
        else:
            print(f" Search Failed: {search_response.status_code}")
            
    except Exception as e:
        print(f" Evidence Test Exception: {e}")
    
    print(f"\n Debug completed!")

if __name__ == "__main__":
    debug_minicheck_integration()
