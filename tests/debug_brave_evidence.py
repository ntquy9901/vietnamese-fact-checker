#!/usr/bin/env python3
"""
Debug Brave Search evidence content
"""

import requests

def debug_brave_evidence():
    """Debug what Brave Search is returning"""
    print("🔍 Debugging Brave Search Evidence")
    print("=" * 50)
    
    # Test with Vietnamese query
    query = "Thành phố Hồ Chí Minh là thành phố lớn nhất Việt Nam"
    
    print(f"📝 Query: {query}")
    
    try:
        response = requests.post(
            "http://localhost:8004/search",
            json={"query": query, "limit": 5},
            timeout=15
        )
        
        if response.status_code == 200:
            result = response.json()
            results = result.get("results", [])
            
            print(f"✅ Found {len(results)} results")
            
            for i, item in enumerate(results, 1):
                print(f"\n📄 Result {i}:")
                print(f"   Title: {item.get('title', '')}")
                print(f"   URL: {item.get('url', '')}")
                print(f"   Snippet: {item.get('snippet', '')[:200]}...")
                print(f"   Content: {item.get('content', '')[:200]}...")
                
                # Test translation of this specific evidence
                vietnamese_text = item.get('snippet', '') or item.get('content', '')
                if vietnamese_text:
                    print(f"   🔄 Testing translation...")
                    trans_response = requests.post(
                        "http://localhost:8003/translate",
                        json={"text": vietnamese_text},
                        timeout=10
                    )
                    
                    if trans_response.status_code == 200:
                        trans_result = trans_response.json()
                        print(f"      VI: {vietnamese_text[:100]}...")
                        print(f"      EN: {trans_result.get('english', '')[:100]}...")
                    else:
                        print(f"      ❌ Translation failed: {trans_response.status_code}")
                
        else:
            print(f"❌ Search failed: {response.status_code}")
            print(f"   Error: {response.text[:200]}...")
            
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    # Test with English query
    print(f"\n" + "=" * 50)
    print("🔍 Testing with English Query")
    print("=" * 50)
    
    english_query = "Ho Chi Minh City largest city Vietnam"
    print(f"📝 Query: {english_query}")
    
    try:
        response = requests.post(
            "http://localhost:8004/search",
            json={"query": english_query, "limit": 5},
            timeout=15
        )
        
        if response.status_code == 200:
            result = response.json()
            results = result.get("results", [])
            
            print(f"✅ Found {len(results)} results")
            
            for i, item in enumerate(results[:2], 1):
                print(f"\n📄 Result {i}:")
                print(f"   Title: {item.get('title', '')}")
                print(f"   Snippet: {item.get('snippet', '')[:200]}...")
                
        else:
            print(f"❌ Search failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    print(f"\n🎉 Debug completed!")

if __name__ == "__main__":
    debug_brave_evidence()
