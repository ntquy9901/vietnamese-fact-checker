import requests

try:
    response = requests.post('http://localhost:8003/translate', json={'text': 'Xin chào'}, timeout=5)
    print(' Translation Status:', response.status_code)
    result = response.json()
    print('Vietnamese:', result['vietnamese'])
    print('English:', result['english'])
    print('Time:', f"{result['translation_time']:.3f}s")
    print('Model:', result['model'])
except Exception as e:
    print(' Error:', e)
