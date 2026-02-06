#!/usr/bin/env python3
"""Test claims from different domains to verify trusted sources"""
import requests
import time

BASE = 'http://localhost:8005'

# Test claims from different domains
test_claims = [
    {
        "domain": "🏛️ Chính phủ",
        "claim": "Thủ tướng Việt Nam hiện nay là Phạm Minh Chính"
    },
    {
        "domain": "💰 Kinh tế",
        "claim": "GDP Việt Nam năm 2024 tăng trưởng khoảng 7%"
    },
    {
        "domain": "🏥 Y tế",
        "claim": "Việt Nam đã tiêm vaccine COVID-19 cho hầu hết dân số"
    },
]

print("=" * 70)
print("🧪 TEST CLAIMS FROM DIFFERENT DOMAINS")
print("=" * 70)

# Check current config
r = requests.get(f'{BASE}/config/brave_search')
cfg = r.json()['config']
print(f"\n📋 Current Config:")
print(f"   • Trusted sources: {len(cfg['trusted_sources'])} domains")
print(f"   • Max results: {cfg['max_results']}")

r = requests.get(f'{BASE}/config/evidence')
cfg = r.json()['config']
print(f"   • Max evidence: {cfg['max_chunks']}")

for i, test in enumerate(test_claims, 1):
    print(f"\n{'='*70}")
    print(f"TEST {i}: {test['domain']}")
    print(f"{'='*70}")
    print(f"📝 Claim: {test['claim']}")
    
    start = time.time()
    try:
        r = requests.post(f'{BASE}/check', json={'claim': test['claim']}, timeout=180)
        elapsed = time.time() - start
        
        if r.status_code == 200:
            result = r.json()
            print(f"\n📊 Result:")
            print(f"   • Verdict: {result['verdict']}")
            print(f"   • Confidence: {result['confidence']:.2%}")
            print(f"   • Evidence: {result['evidence_count']} items")
            print(f"   • Time: {elapsed:.2f}s")
            
            print(f"\n📚 Sources:")
            for j, ev in enumerate(result.get('evidence', [])[:3], 1):
                url = ev.get('url', '')
                domain = url.split('/')[2] if '/' in url else 'unknown'
                print(f"   {j}. [{domain}]")
        else:
            print(f"❌ Error: {r.status_code}")
    except Exception as e:
        print(f"❌ Exception: {e}")

print(f"\n{'='*70}")
print("✅ DOMAIN TESTS COMPLETE")
print("="*70)
