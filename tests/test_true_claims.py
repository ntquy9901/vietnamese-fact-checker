#!/usr/bin/env python3
"""Test TRUE claims with detailed service output"""
import requests
import time

TRUE_CLAIMS = [
    "Trần Hưng Đạo là một vị tướng tài ở Việt Nam",
    "Hồ Chủ Tịch là lãnh đạo Việt Nam trước đây"
]

def test_claim(claim):
    print(f"\n{'='*100}")
    print(f"📝 CLAIM: {claim}")
    print('='*100)
    
    start = time.time()
    try:
        r = requests.post('http://localhost:8005/check', json={'claim': claim}, timeout=120)
        total_time = time.time() - start
        
        if r.status_code == 200:
            data = r.json()
            
            print(f"\n📊 RESULT:")
            print(f"   Verdict: {data.get('verdict', 'N/A')}")
            print(f"   Confidence: {data.get('confidence', 0):.2%}")
            print(f"   Total Time: {total_time:.2f}s")
            
            print(f"\n📚 EVIDENCE ({data.get('evidence_count', 0)} sources):")
            for i, ev in enumerate(data.get('evidence', []), 1):
                print(f"   {i}. [{ev.get('title', 'N/A')[:60]}]")
                print(f"      URL: {ev.get('url', 'N/A')[:80]}")
                print(f"      Text: {ev.get('text', 'N/A')[:100]}...")
            
            return data
    except Exception as e:
        print(f"❌ ERROR: {e}")
    return None

if __name__ == "__main__":
    print("🧪 TESTING TRUE VIETNAMESE CLAIMS")
    print("="*100)
    
    for claim in TRUE_CLAIMS:
        test_claim(claim)
    
    print("\n" + "="*100)
    print("✅ TEST COMPLETE")
