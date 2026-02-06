#!/usr/bin/env python3
"""Test Vietnamese Fact Checker API"""
import requests
import json

# Test claim
claim = "Quảng Trị ở miền Nam"

print("=" * 60)
print("Vietnamese Fact Checker Test")
print("=" * 60)
print(f"Claim: {claim}")
print("=" * 60)

# Test the API
url = "http://localhost:8005/check"
payload = {"claim": claim}

try:
    response = requests.post(url, json=payload, timeout=120)
    print(f"\nStatus Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print("\n✅ SUCCESS!")
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"\n❌ Error: {response.text}")
        
except requests.exceptions.ConnectionError:
    print("❌ Connection Error: Server not running")
except Exception as e:
    print(f"❌ Error: {e}")
