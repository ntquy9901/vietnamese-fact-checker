#!/usr/bin/env python3
"""
Test Vietnamese Fact Checker with specific claim
"""

import requests
import time

def test_specific_claim():
    """Test Vietnamese Fact Checker with specific claim"""
    print("🧪 Testing Vietnamese Fact Checker")
    print("=" * 50)
    
    base_url = "http://localhost:8005"
    
    # Test case from user
    claim = "Thành phố Hồ Chí Minh là thành phố lớn nhất ở Việt Nam"
    
    print(f"📝 Claim: {claim}")
    print(f"🔍 Testing fact checking...")
    
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
            
            print(f"✅ Fact Check Result:")
            print(f"   Verdict: {result.get('verdict', 'UNKNOWN')}")
            print(f"   Confidence: {result.get('confidence', 0):.3f}")
            print(f"   Evidence Count: {result.get('evidence_count', 0)}")
            print(f"   Processing Time: {end_time - start_time:.2f}s")
            print(f"   Rationale: {result.get('rationale', 'No rationale')[:200]}...")
            
            # Check if we have evidence
            if result.get('evidence_count', 0) > 0:
                print(f"✅ Evidence found - Fact check completed successfully!")
            else:
                print(f"⚠️ No evidence found - Brave Search may need adjustment")
                
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            try:
                error_text = response.text
                print(f"   Error details: {error_text[:300]}...")
            except:
                pass
                
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    # Also test individual components
    print(f"\n🔍 Testing individual components...")
    
    # Test Brave Search directly
    print(f"\n1️⃣ Testing Brave Search API...")
    try:
        search_response = requests.post(
            "http://localhost:8004/search",
            json={"query": claim, "limit": 5},
            timeout=15
        )
        if search_response.status_code == 200:
            search_result = search_response.json()
            results = search_result.get("results", [])
            print(f"✅ Brave Search found {len(results)} results")
            for i, item in enumerate(results[:2], 1):
                print(f"   {i}. {item.get('title', 'No title')}")
                print(f"      {item.get('snippet', 'No snippet')[:100]}...")
        else:
            print(f"❌ Brave Search failed: {search_response.status_code}")
    except Exception as e:
        print(f"❌ Brave Search exception: {e}")
    
    # Test Translation
    print(f"\n2️⃣ Testing Translation API...")
    try:
        trans_response = requests.post(
            "http://localhost:8003/translate",
            json={"text": claim},
            timeout=15
        )
        if trans_response.status_code == 200:
            trans_result = trans_response.json()
            print(f"✅ Translation: {claim} → {trans_result.get('english', 'No translation')}")
        else:
            print(f"❌ Translation failed: {trans_response.status_code}")
    except Exception as e:
        print(f"❌ Translation exception: {e}")
    
    # Test MiniCheck
    print(f"\n3️⃣ Testing MiniCheck API...")
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
            print(f"✅ MiniCheck Result: {minicheck_result.get('label', 'UNKNOWN')}")
            print(f"   Score: {minicheck_result.get('score', 0):.3f}")
        else:
            print(f"❌ MiniCheck failed: {minicheck_response.status_code}")
    except Exception as e:
        print(f"❌ MiniCheck exception: {e}")
    
    print(f"\n🎉 Specific test completed!")

if __name__ == "__main__":
    test_specific_claim()
