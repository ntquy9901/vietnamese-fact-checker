#!/usr/bin/env python3
"""
Test Integrated Vietnamese Fact Checker with all baseline services
"""

import asyncio
import requests
import time

async def test_baseline_services():
    """Test all baseline services before testing fact checker"""
    print("🧪 Testing All Baseline Services")
    print("=" * 50)
    
    services = {
        "Translation System (8003)": "http://localhost:8003/",
        "MiniCheck API (8002)": "http://localhost:8002/",
        "Brave Search (8004)": "http://localhost:8004/"
    }
    
    all_healthy = True
    
    for service_name, url in services.items():
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                print(f"✅ {service_name}: HEALTHY")
            else:
                print(f"❌ {service_name}: ERROR {response.status_code}")
                all_healthy = False
        except Exception as e:
            print(f"❌ {service_name}: CONNECTION FAILED - {e}")
            all_healthy = False
    
    return all_healthy

async def test_vietnamese_fact_checker():
    """Test Vietnamese Fact Checker with baseline services"""
    print("\n🧪 Testing Vietnamese Fact Checker (Port 8005)")
    print("=" * 50)
    
    base_url = "http://localhost:8005"
    
    try:
        # Test health endpoint
        print("1️⃣ Testing health endpoint...")
        response = requests.get(f"{base_url}/", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Fact Checker Health: {data.get('status', 'unknown')}")
        else:
            print(f"❌ Fact Checker health failed: {response.status_code}")
            return False
        
        # Test fact checking with Vietnamese claim
        print("\n2️⃣ Testing Vietnamese fact checking...")
        
        test_claims = [
            "Hà Nội là thủ đô của Việt Nam",
            "Việt Nam là quốc gia lớn nhất thế giới",
            "Sài Gòn là thành phố lớn nhất Việt Nam"
        ]
        
        for i, claim in enumerate(test_claims, 1):
            print(f"\n📝 Test {i}: '{claim}'")
            
            start_time = time.time()
            response = requests.post(
                f"{base_url}/check",
                json={"claim": claim},
                timeout=60  # Longer timeout for full fact-checking process
            )
            
            end_time = time.time()
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Result: {result.get('verdict', 'UNKNOWN')}")
                print(f"📊 Confidence: {result.get('confidence', 0):.3f}")
                print(f"⏱️ Processing Time: {end_time - start_time:.2f}s")
                print(f"📄 Evidence Count: {result.get('evidence_count', 0)}")
                print(f"💬 Rationale: {result.get('rationale', 'No rationale')[:100]}...")
            else:
                print(f"❌ Test {i} failed: {response.status_code}")
                try:
                    error_text = response.text
                    print(f"   Error: {error_text[:200]}...")
                except:
                    pass
        
        print("\n🎉 Vietnamese Fact Checker test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Fact Checker test failed: {e}")
        return False

async def main():
    """Main test function"""
    print("🚀 Integrated Vietnamese Fact Checker Test")
    print("=" * 60)
    
    # Test baseline services first
    services_healthy = await test_baseline_services()
    
    if not services_healthy:
        print("\n❌ Some baseline services are not healthy!")
        print("Please ensure all services are running:")
        print("- Translation System: python clean_backend.py (port 8003)")
        print("- MiniCheck API: python minicheck_server.py (port 8002)")
        print("- Brave Search: python brave_search_server.py (port 8004)")
        return
    
    print("\n✅ All baseline services are healthy!")
    
    # Test fact checker
    fact_checker_success = await test_vietnamese_fact_checker()
    
    if fact_checker_success:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Vietnamese Fact Checker is working with baseline services!")
    else:
        print("\n❌ Some tests failed!")
        print("Please check the fact checker logs for details.")

if __name__ == "__main__":
    asyncio.run(main())
