#!/usr/bin/env python3
"""
Test Brave Search API Server
"""

import requests
import time

def test_brave_search_api():
    """Test Brave Search API server endpoints"""
    print(" Testing Brave Search API Server (Port 8004)")
    print("=" * 50)
    
    base_url = "http://localhost:8004"
    
    try:
        # Test health endpoint
        print("1⃣ Testing health endpoint...")
        response = requests.get(f"{base_url}/", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f" Health Check: {data['status']}")
            print(f" API Key Configured: {data['api_key_configured']}")
            print(f" Search Engine: {data['search_engine']}")
        else:
            print(f" Health check failed: {response.status_code}")
            return False
        
        # Test search endpoint
        print("\n2⃣ Testing search endpoint...")
        
        test_queries = [
            "Hà Nội thủ đô Việt Nam",
            "Việt Nam quốc gia Đông Nam Á",
            "Sài Gòn thành phố lớn nhất"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n Test {i}: '{query}'")
            
            request_data = {
                "query": query,
                "limit": 5
            }
            
            start_time = time.time()
            response = requests.post(f"{base_url}/search", json=request_data, timeout=15)
            end_time = time.time()
            
            if response.status_code == 200:
                result = response.json()
                results = result.get("results", [])
                print(f" Found {len(results)} results")
                print(f"⏱ Time: {end_time - start_time:.3f}s")
                
                for j, item in enumerate(results[:2], 1):
                    print(f"   {j}. {item.get('title', 'No title')}")
                    print(f"      {item.get('url', 'No URL')}")
                    print(f"      {item.get('snippet', 'No snippet')[:80]}...")
            else:
                print(f" Test {i} failed: {response.status_code}")
                try:
                    error_text = response.text
                    print(f"   Error: {error_text[:200]}...")
                except:
                    pass
        
        print("\n Brave Search API test completed!")
        return True
        
    except Exception as e:
        print(f" API test failed: {e}")
        return False

if __name__ == "__main__":
    test_brave_search_api()
