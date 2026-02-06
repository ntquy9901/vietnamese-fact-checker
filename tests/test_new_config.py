#!/usr/bin/env python3
"""Test new configuration changes"""
import requests
import time

print("=" * 70)
print("🧪 TEST NEW CONFIGURATION")
print("=" * 70)

# Verify config
print("\n📋 Current Config:")
r = requests.get('http://localhost:8005/config/evidence')
print(f"   • Evidence max_chunks: {r.json()['config']['max_chunks']}")

r = requests.get('http://localhost:8005/config/brave_search')
cfg = r.json()['config']
print(f"   • Brave max_results: {cfg['max_results']}")
print(f"   • Trusted sources: {len(cfg['trusted_sources'])} domains")

r = requests.get('http://localhost:8005/config/logging')
cfg = r.json()['config']
print(f"   • Debug logging: {cfg['log_service_io']}")

# Test
claim = "Việt Nam có bao nhiêu tỉnh thành"
print(f"\n📝 Test claim: {claim}")
print("-" * 70)

start = time.time()
r = requests.post('http://localhost:8005/check', json={'claim': claim}, timeout=180)
elapsed = time.time() - start

result = r.json()
print(f"\n📊 RESULT:")
print(f"   • Verdict: {result['verdict']}")
print(f"   • Confidence: {result['confidence']:.2%}")
print(f"   • Evidence count: {result['evidence_count']}")
print(f"   • Time: {elapsed:.2f}s")

print(f"\n📚 Evidence ({result['evidence_count']} items):")
for i, ev in enumerate(result.get('evidence', []), 1):
    url = ev.get('url', '')
    domain = url.split('/')[2] if '/' in url else 'unknown'
    print(f"   {i}. [{domain}]")
    print(f"      {ev.get('title', '')[:60]}")

print("\n" + "=" * 70)
if result['evidence_count'] >= 6:
    print("✅ SUCCESS: Got 6+ evidence items!")
else:
    print(f"⚠️ Got {result['evidence_count']} evidence (expected 6)")
print("=" * 70)
