#!/usr/bin/env python3
import requests

response = requests.post('http://localhost:8004/search', json={'query': 'Vietnam', 'limit': 5})
print(f'Status: {response.status_code}')
if response.status_code == 200:
    data = response.json()
    print(f'Results: {len(data.get("results", []))}')
    for i, result in enumerate(data.get("results", [])[:2], 1):
        print(f'{i}. {result.get("title", "")[:80]}...')
