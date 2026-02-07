#!/usr/bin/env python3
"""
Test Brave Search with Vietnam specific queries
"""

import requests

def test_brave_vietnam_queries():
    """Test Brave Search with Vietnam specific queries"""
    print(" Testing Brave Search with Vietnam Queries")
    print("=" * 50)
    
    base_url = "http://localhost:8004"
    
    queries = [
        "Cổ phiếu VIC bị giảm ở thị trường Việt Nam hôm nay",
        "Trương Tấn Dũng là tổng thống của Việt Nam",
        "Trường Bách Khoa ở Ngoài Phú Yên"
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"\n Query {i}: {query}")
        
        try:
            response = requests.post(
                f"{base_url}/search",
                json={"query": query, "limit": 3},
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                results = result.get("results", [])
                
                print(f" Found {len(results)} results")
                
                for j, item in enumerate(results, 1):
                    print(f"\n Result {j}:")
                    print(f"   Title: {item.get('title', '')}")
                    print(f"   Snippet: {item.get('snippet', '')[:150]}...")
                    
                    # Test translation
                    vietnamese_text = item.get('snippet', '') or item.get('content', '')
                    if vietnamese_text:
                        trans_response = requests.post(
                            "http://localhost:8003/translate",
                            json={"text": vietnamese_text},
                            timeout=10
                        )
                        
                        if trans_response.status_code == 200:
                            trans_result = trans_response.json()
                            print(f"    EN: {trans_result.get('english', '')[:150]}...")
                
            else:
                print(f" Search failed: {response.status_code}")
                
        except Exception as e:
            print(f" Exception: {e}")
    
    print(f"\n Brave Search test completed!")

if __name__ == "__main__":
    test_brave_vietnam_queries()
