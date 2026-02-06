#!/usr/bin/env python3
"""
Debug Brave Search API to find root cause
"""

import requests
import time
import json

def debug_brave_search():
    """Debug Brave Search API thoroughly"""
    print("🔍 Debugging Brave Search API")
    print("=" * 50)
    
    base_url = "http://localhost:8004"
    
    # Test 1: Health check
    print("1️⃣ Health Check...")
    try:
        response = requests.get(f"{base_url}/", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status: {data['status']}")
            print(f"🔧 API Key Configured: {data['api_key_configured']}")
            print(f"🔍 Search Engine: {data['search_engine']}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check exception: {e}")
        return
    
    # Test 2: Test with different query formats
    test_queries = [
        # Vietnamese queries (original)
        "Thành phố Hồ Chí Minh là thành phố lớn nhất ở Việt Nam",
        "Hà Nội thủ đô Việt Nam",
        "Việt Nam quốc gia Đông Nam Á",
        
        # English queries
        "Ho Chi Minh City largest city Vietnam",
        "Hanoi capital Vietnam", 
        "Vietnam Southeast Asia country",
        
        # Simple queries
        "Ho Chi Minh City",
        "Vietnam",
        "Hanoi"
    ]
    
    print(f"\n2️⃣ Testing Different Query Formats...")
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📝 Test {i}: '{query}'")
        
        # Test different request formats
        request_formats = [
            {"query": query, "limit": 5},
            {"query": query, "count": 5},
            {"query": query},
            {"q": query, "count": 5},
            {"search": query, "limit": 5}
        ]
        
        for j, request_data in enumerate(request_formats, 1):
            print(f"   Format {j}: {request_data}")
            
            try:
                response = requests.post(
                    f"{base_url}/search",
                    json=request_data,
                    timeout=15
                )
                
                print(f"   Status: {response.status_code}")
                
                if response.status_code == 200:
                    result = response.json()
                    results = result.get("results", [])
                    print(f"   ✅ Found {len(results)} results")
                    
                    if results:
                        for k, item in enumerate(results[:2], 1):
                            print(f"      {k}. {item.get('title', 'No title')}")
                            print(f"         {item.get('snippet', 'No snippet')[:80]}...")
                    else:
                        print(f"   ⚠️ No results found")
                        
                else:
                    print(f"   ❌ Failed: {response.status_code}")
                    try:
                        error_text = response.text
                        print(f"      Error: {error_text[:100]}...")
                    except:
                        pass
                        
            except Exception as e:
                print(f"   ❌ Exception: {e}")
    
    # Test 3: Check server logs by testing with verbose
    print(f"\n3️⃣ Testing with Vietnamese language parameter...")
    
    vietnamese_tests = [
        {"query": "Thành phố Hồ Chí Minh", "limit": 5, "language": "vi"},
        {"query": "Thành phố Hồ Chí Minh", "limit": 5, "lang": "vi"},
        {"query": "Thành phố Hồ Chí Minh", "limit": 5, "search_lang": "vi"},
    ]
    
    for i, request_data in enumerate(vietnamese_tests, 1):
        print(f"\n📝 Vietnamese Test {i}: {request_data}")
        
        try:
            response = requests.post(
                f"{base_url}/search",
                json=request_data,
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                results = result.get("results", [])
                print(f"   ✅ Found {len(results)} results")
            else:
                print(f"   ❌ Failed: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
    
    # Test 4: Test direct Brave API call simulation
    print(f"\n4️⃣ Testing direct API parameters...")
    
    # Check what the server is actually sending to Brave API
    direct_test = {
        "query": "Ho Chi Minh City",
        "count": 5,
        "text_decorations": "false",
        "search_lang": "vi",
        "ui_lang": "vi",
        "safesearch": "moderate"
    }
    
    print(f"📝 Direct test parameters: {direct_test}")
    
    try:
        response = requests.post(
            f"{base_url}/search",
            json={"query": "Ho Chi Minh City", "limit": 5},
            timeout=15
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Direct test result: {json.dumps(result, indent=2)}")
        else:
            print(f"❌ Direct test failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Direct test exception: {e}")
    
    print(f"\n🎉 Debug completed!")

if __name__ == "__main__":
    debug_brave_search()
