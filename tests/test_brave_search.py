import requests

def test_brave_search_system():
    print(" Testing Brave Search System (Port 8004)")
    print("=" * 50)
    
    try:
        # Health check
        response = requests.get('http://localhost:8004/', timeout=5)
        print(' Health Check:', response.status_code)
        data = response.json()
        print(' Search Engine:', data['search_engine'])
        print(' API Key Configured:', data['api_key_configured'])
        print(' Message:', data['message'])
        
        # Test search
        test_data = {
            "query": "Hà Nội là thủ đô của Việt Nam",
            "limit": 3
        }
        
        response = requests.post('http://localhost:8004/search', json=test_data, timeout=10)
        if response.status_code == 200:
            result = response.json()
            print(' Search Test:')
            print('   Query:', result['query'])
            print('    Count:', result['count'])
            print('   ⏱ Time:', f"{result['processing_time']:.3f}s")
            print('    Search Engine:', result['search_engine'])
            
            for i, item in enumerate(result['results'][:2], 1):
                print(f'   {i}. {item["title"]}')
                print(f'       {item["snippet"][:100]}...')
                print(f'       {item["url"]}')
            
            return True
        else:
            print(' Search failed:', response.status_code)
            return False
            
    except Exception as e:
        print(' Error:', e)
        return False

if __name__ == "__main__":
    test_brave_search_system()
