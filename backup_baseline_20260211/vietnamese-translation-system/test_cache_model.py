import requests

test_sentences = [
    "Xin chào",
    "Hà Nội là thủ đô",
    "Tôi thích ăn phở",
    "Cảm ơn bạn",
    "Hôm nay trời đẹp"
]

print(" Testing Facebook NLLB Model from D:/huggingface_cache")
print("=" * 60)

for i, sentence in enumerate(test_sentences, 1):
    try:
        response = requests.post('http://localhost:8003/translate', 
                                json={'text': sentence}, 
                                timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print(f"{i}. {sentence}")
            print(f"   → {result['english']}")
            print(f"   ⏱  {result['translation_time']:.3f}s | Model: {result['model_loaded']}")
        else:
            print(f"{i}. {sentence} - HTTP {response.status_code}")
            
    except Exception as e:
        print(f"{i}. {sentence} - Error: {str(e)[:30]}...")
    
    print()

print(" All tests completed using model from D:/huggingface_cache")
