#!/usr/bin/env python3
"""
Test MiniCheck with simple evidence
"""

import requests

def test_minicheck_simple():
    """Test MiniCheck with simple evidence"""
    print("🧪 Testing MiniCheck with Simple Evidence")
    print("=" * 50)
    
    base_url = "http://localhost:8002"
    
    test_cases = [
        {
            "name": "Simple Supported",
            "claim": "Ho Chi Minh City is the largest city in Vietnam",
            "evidence": ["Ho Chi Minh City is the largest city in Vietnam by population."]
        },
        {
            "name": "Simple Refuted", 
            "claim": "Vietnam is the smallest country in the world",
            "evidence": ["Vietnam is the 65th largest country in the world by total area."]
        },
        {
            "name": "No Evidence",
            "claim": "Test claim",
            "evidence": []
        },
        {
            "name": "Multiple Evidence",
            "claim": "Ho Chi Minh City is the largest city in Vietnam",
            "evidence": [
                "Ho Chi Minh City is the largest city in Vietnam by population.",
                "HCMC has over 9 million people.",
                "It is the economic center of Vietnam."
            ]
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 Test {i}: {test_case['name']}")
        print(f"   Claim: {test_case['claim']}")
        print(f"   Evidence: {len(test_case['evidence'])} items")
        
        try:
            response = requests.post(
                f"{base_url}/verify",
                json={
                    "claim": test_case['claim'],
                    "evidence": test_case['evidence']
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Result: {result['label']}")
                print(f"   📊 Score: {result['score']:.3f}")
                print(f"   ⏱️ Time: {result.get('processing_time', 0):.3f}s")
                print(f"   💬 Explanation: {result['explanation'][:100]}...")
            else:
                print(f"   ❌ Failed: {response.status_code}")
                print(f"   Error: {response.text[:100]}...")
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
    
    print(f"\n🎉 MiniCheck simple test completed!")

if __name__ == "__main__":
    test_minicheck_simple()
