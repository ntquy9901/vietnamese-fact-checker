#!/usr/bin/env python3
import requests

response = requests.post('http://localhost:8003/translate', json={'text': 'Thành phố Hồ Chí Minh là thành phố lớn nhất Việt Nam'})
print(f'Status: {response.status_code}')
if response.status_code == 200:
    result = response.json()
    print(f'Original: {result.get("vietnamese", "")}')
    print(f'Translated: {result.get("english", "")}')
