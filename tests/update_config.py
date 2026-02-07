#!/usr/bin/env python3
"""Update configurations and test"""
import requests
import json

BASE = 'http://localhost:8005'

print("=" * 60)
print(" UPDATING CONFIGURATIONS")
print("=" * 60)

# 1. Update evidence max_chunks to 6
print("\n1. Updating evidence max_chunks to 6...")
r1 = requests.post(f'{BASE}/config/evidence', json={
    'section': 'evidence', 
    'updates': {'max_chunks': 6}
})
print(f"    {r1.json().get('message', r1.json())}")

# 2. Add more trusted Vietnamese sources
print("\n2. Adding more trusted Vietnamese sources...")
new_trusted = [
    'wikipedia.org', 'vi.wikipedia.org', 'en.wikipedia.org',
    'gov.vn', 'chinhphu.vn', 'edu.vn',
    'vnexpress.net', 'tuoitre.vn', 'thanhnien.vn', 'nhandan.vn',
    'baochinhphu.vn', 'dangcongsan.vn',
    'vietnamnet.vn', 'dantri.com.vn', 'laodong.vn',
    'vtv.vn', 'vov.vn', 'qdnd.vn',
    'sggp.org.vn', 'hanoimoi.com.vn', 'baotintuc.vn',
    'vietnamplus.vn', 'thesaigontimes.vn', 'vietstock.vn'
]
r2 = requests.post(f'{BASE}/config/brave_search', json={
    'section': 'brave_search', 
    'updates': {'trusted_sources': new_trusted}
})
print(f"    {r2.json().get('message', r2.json())}")

# 3. Enable all debug logging
print("\n3. Enabling all debug logging flags...")
debug_updates = {
    'log_service_io': True,
    'log_timing': True,
    'log_translation_details': True,
    'log_minicheck_all_scores': True,
    'log_search_results': True,
    'include_debug_in_response': True
}
r3 = requests.post(f'{BASE}/config/logging', json={
    'section': 'logging', 
    'updates': debug_updates
})
print(f"    {r3.json().get('message', r3.json())}")

# Verify changes
print("\n" + "=" * 60)
print(" VERIFY CONFIGURATION CHANGES")
print("=" * 60)

r = requests.get(f'{BASE}/config/evidence')
evidence_cfg = r.json()['config']
print(f"\n Evidence Config:")
print(f"   • max_chunks: {evidence_cfg['max_chunks']} (was 3, now 6)")

r = requests.get(f'{BASE}/config/brave_search')
brave_cfg = r.json()['config']
print(f"\n Brave Search Config:")
print(f"   • trusted_sources: {len(brave_cfg['trusted_sources'])} domains (was 12, now 24)")
print(f"   • New sources added: vietnamnet.vn, dantri.com.vn, vtv.vn, vov.vn...")

r = requests.get(f'{BASE}/config/logging')
log_cfg = r.json()['config']
print(f"\n Logging Config (all debug enabled):")
print(f"   • log_service_io: {log_cfg['log_service_io']}")
print(f"   • log_timing: {log_cfg['log_timing']}")
print(f"   • log_translation_details: {log_cfg['log_translation_details']}")
print(f"   • log_minicheck_all_scores: {log_cfg['log_minicheck_all_scores']}")
print(f"   • log_search_results: {log_cfg['log_search_results']}")

print("\n" + "=" * 60)
print(" RUNNING TEST WITH NEW CONFIG")
print("=" * 60)

claim = "Việt Nam có bao nhiêu tỉnh thành"
print(f"\n Test claim: {claim}")
print("   (This should fetch 6 evidence items with detailed logging)\n")

import time
start = time.time()
r = requests.post(f'{BASE}/check', json={'claim': claim}, timeout=180)
elapsed = time.time() - start

if r.status_code == 200:
    result = r.json()
    print(f"\n RESULT:")
    print(f"   • Verdict: {result['verdict']}")
    print(f"   • Confidence: {result['confidence']:.2%}")
    print(f"   • Evidence count: {result['evidence_count']} (expected: 6)")
    print(f"   • Time: {elapsed:.2f}s")
    
    print(f"\n Evidence Sources:")
    for i, ev in enumerate(result.get('evidence', []), 1):
        domain = ev.get('url', '').split('/')[2] if '/' in ev.get('url', '') else 'unknown'
        print(f"   {i}. [{domain}] {ev.get('title', '')[:50]}...")
else:
    print(f" Error: {r.text}")

print("\n" + "=" * 60)
print(" CONFIGURATION UPDATE COMPLETE")
print("=" * 60)
