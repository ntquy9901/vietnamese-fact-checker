#!/usr/bin/env python3
"""
Test script for Vietnamese Translation System
"""

import requests
import json
import time

def test_server():
    """Test if server is running"""
    try:
        response = requests.get('http://localhost:8003/', timeout=5)
        if response.status_code == 200:
            print("✅ Server is running")
            return True
        else:
            print(f"❌ Server returned status: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Server is not running")
        return False
    except Exception as e:
        print(f"❌ Error connecting to server: {e}")
        return False

def test_translations():
    """Test translation functionality"""
    test_cases = [
        "Xin chào",
        "bạn là ai",
        "Hà Nội là thủ đô",
        "Tôi thích ăn phở",
        "Công nghệ thông tin"
    ]
    
    print("\n🔄 Testing translations:")
    print("-" * 50)
    
    for i, text in enumerate(test_cases, 1):
        try:
            start_time = time.time()
            response = requests.post(
                'http://localhost:8003/translate',
                json={'text': text},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                total_time = time.time() - start_time
                print(f"{i}. {text}")
                print(f"   → {result['english']}")
                print(f"   ⏱️  {result['translation_time']:.3f}s (total: {total_time:.3f}s)")
            else:
                print(f"{i}. ❌ Failed: {response.status_code}")
                
        except Exception as e:
            print(f"{i}. ❌ Error: {e}")
    
    print("-" * 50)

def main():
    """Main test function"""
    print("🧪 Vietnamese Translation System Test")
    print("=" * 50)
    
    if not test_server():
        print("\n💡 Please start the server first:")
        print("   python server.py")
        return
    
    test_translations()
    print("\n✅ Test completed!")

if __name__ == "__main__":
    main()
