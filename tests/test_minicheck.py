import requests

def test_minicheck_system():
    print("🧪 Testing MiniCheck System (Port 8002)")
    print("=" * 50)
    
    try:
        # Health check
        response = requests.get('http://localhost:8002/', timeout=5)
        print('✅ Health Check:', response.status_code)
        data = response.json()
        print('🤖 Model:', data['model'])
        print('📁 Cache Dir:', data['cache_dir'])
        print('🔧 Model Loaded:', data['model_loaded'])
        
        # Test verification
        test_data = {
            "claim": "Hanoi is the capital of Vietnam",
            "evidence": ["Hanoi is the capital city of Vietnam"]
        }
        
        response = requests.post('http://localhost:8002/verify', json=test_data, timeout=30)
        if response.status_code == 200:
            result = response.json()
            print('🔍 Verification Test:')
            print('   Claim:', test_data['claim'])
            print('   Evidence:', test_data['evidence'][0])
            print('   📊 Label:', result['label'])
            print('   📈 Score:', f"{result['score']:.3f}")
            print('   📝 Explanation:', result['explanation'])
            print('   ⏱️ Time:', f"{result['processing_time']:.3f}s")
            return True
        else:
            print('❌ Verification failed:', response.status_code)
            return False
            
    except Exception as e:
        print('❌ Error:', e)
        return False

if __name__ == "__main__":
    test_minicheck_system()
