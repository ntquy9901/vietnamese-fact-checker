import requests

def test_brave_search_extended():
    print(" Testing Brave Search Extended Cases")
    print("=" * 50)
    
    test_cases = [
        {
            "query": "Tôi thích ăn phở",
            "description": "Vietnamese food preference"
        },
        {
            "query": "Công nghệ thông tin Việt Nam",
            "description": "Vietnamese technology industry"
        },
        {
            "query": "Chúc mừng năm mới 2024",
            "description": "Vietnamese New Year greeting"
        }
    ]
    
    try:
        # Health check first
        response = requests.get('http://localhost:8004/', timeout=5)
        print(' Health Check:', response.status_code)
        data = response.json()
        print(f' Search Engine: {data["search_engine"]}')
        print(f' API Key: {data["api_key_configured"]}')
        print()
        
        # Test each case
        for i, case in enumerate(test_cases, 1):
            print(f" Test Case {i}: {case['description']}")
            print(f"   Query: '{case['query']}'")
            
            test_data = {
                "query": case['query'],
                "limit": 3
            }
            
            response = requests.post('http://localhost:8004/search', json=test_data, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                print(f'    Results: {result["count"]} found')
                print(f'   ⏱ Time: {result["processing_time"]:.3f}s')
                
                for j, item in enumerate(result['results'][:2], 1):
                    print(f'   {j}. {item["title"]}')
                    print(f'       {item["snippet"][:80]}...')
                    print(f'       {item["language"]}')
                
            else:
                print(f'    Failed: HTTP {response.status_code}')
            
            print()
        
        # Test Vietnamese search endpoint
        print(" Testing Vietnamese Search Endpoint...")
        viet_test = {
            "query": "Hà Nội thủ đô Việt Nam",
            "limit": 2
        }
        
        response = requests.post('http://localhost:8004/search_vietnamese', json=viet_test, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print(' Vietnamese search successful')
            print(f'   Results: {result["count"]}')
            print(f'   Time: {result["processing_time"]:.3f}s')
        else:
            print(f' Vietnamese search failed: {response.status_code}')
        
        return True
        
    except Exception as e:
        print(f' Error: {e}')
        return False

if __name__ == "__main__":
    test_brave_search_extended()
