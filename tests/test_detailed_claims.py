#!/usr/bin/env python3
"""Detailed test for Vietnamese Fact Checker - Shows all service I/O"""
import requests
import json
import time

# 5 Test claims
TEST_CLAIMS = [
    "Việt Nam là quốc gia đông dân nhất",
    "Hoàng Đế Thuận Trị ở Nga",
    "Bán 5 con gà được 9 đồng",
    "Tổng thống Hoàng Hà là bí thư đương thời ở Việt Nam",
    "Hôm qua cổ phiếu tăng toàn bộ ở Việt Nam, riêng Cổ phiếu VIC tăng gấp 3 hôm qua"
]

def test_translation_service(text):
    """Test translation service directly"""
    start = time.time()
    try:
        r = requests.post('http://localhost:8003/translate', json={'text': text}, timeout=60)
        elapsed = time.time() - start
        if r.status_code == 200:
            data = r.json()
            return {
                'success': True,
                'input': text,
                'output': data.get('english', ''),
                'time': elapsed,
                'device': 'GPU' if 'cuda' in str(data.get('model', '')).lower() else 'Unknown'
            }
    except Exception as e:
        return {'success': False, 'error': str(e), 'time': time.time() - start}
    return {'success': False, 'error': 'Unknown', 'time': time.time() - start}

def test_brave_search(query):
    """Test Brave Search service directly"""
    start = time.time()
    try:
        r = requests.post('http://localhost:8004/search', json={'query': query}, timeout=30)
        elapsed = time.time() - start
        if r.status_code == 200:
            data = r.json()
            results = data.get('results', [])
            return {
                'success': True,
                'input': query,
                'output': f"{len(results)} results",
                'results': results[:3],
                'time': elapsed
            }
    except Exception as e:
        return {'success': False, 'error': str(e), 'time': time.time() - start}
    return {'success': False, 'error': 'Unknown', 'time': time.time() - start}

def test_minicheck(claim, evidence):
    """Test MiniCheck service directly"""
    start = time.time()
    try:
        r = requests.post('http://localhost:8002/verify', 
                         json={'claim': claim, 'evidence': evidence}, timeout=30)
        elapsed = time.time() - start
        if r.status_code == 200:
            data = r.json()
            return {
                'success': True,
                'input_claim': claim,
                'input_evidence': evidence[0][:100] + '...' if evidence else '',
                'output_label': data.get('label', 'N/A'),
                'output_score': data.get('score', 0),
                'time': elapsed
            }
    except Exception as e:
        return {'success': False, 'error': str(e), 'time': time.time() - start}
    return {'success': False, 'error': 'Unknown', 'time': time.time() - start}

def test_full_factchecker(claim):
    """Test full Vietnamese Fact Checker"""
    start = time.time()
    try:
        r = requests.post('http://localhost:8005/check', json={'claim': claim}, timeout=180)
        elapsed = time.time() - start
        if r.status_code == 200:
            data = r.json()
            return {
                'success': True,
                'verdict': data.get('verdict', 'N/A'),
                'confidence': data.get('confidence', 0),
                'evidence_count': data.get('evidence_count', 0),
                'evidence': data.get('evidence', []),
                'time': elapsed,
                'debug': data.get('debug_info', {})
            }
    except Exception as e:
        return {'success': False, 'error': str(e), 'time': time.time() - start}
    return {'success': False, 'error': 'Unknown', 'time': time.time() - start}

def main():
    print("=" * 100)
    print("🧪 DETAILED VIETNAMESE FACT CHECKER TEST - 5 CLAIMS")
    print("=" * 100)
    
    for i, claim in enumerate(TEST_CLAIMS, 1):
        print(f"\n{'#' * 100}")
        print(f"# CLAIM {i}/5: {claim}")
        print(f"{'#' * 100}")
        
        # Test full fact checker
        print("\n📊 FULL FACT CHECKER RESULT:")
        print("-" * 80)
        fc_result = test_full_factchecker(claim)
        
        if fc_result['success']:
            print(f"   INPUT (Vietnamese): {claim}")
            print(f"   OUTPUT Verdict: {fc_result['verdict']}")
            print(f"   OUTPUT Confidence: {fc_result['confidence']:.2%}")
            print(f"   Evidence Count: {fc_result['evidence_count']}")
            print(f"   ⏱️  Total Time: {fc_result['time']:.2f}s")
            
            # Show translation details from debug
            debug = fc_result.get('debug', {})
            translation = debug.get('translation', {})
            minicheck_input = debug.get('minicheck_input', {})
            
            print("\n   📝 SERVICE DETAILS:")
            print("   " + "-" * 76)
            
            # Translation Service
            print("\n   🌐 TRANSLATION SERVICE (VinAI):")
            if translation:
                print(f"      INPUT:  {translation.get('normalized_claim', 'N/A')}")
                print(f"      OUTPUT: {translation.get('english_claim', 'N/A')}")
            if minicheck_input:
                print(f"      Claim (EN): {minicheck_input.get('claim', 'N/A')}")
            
            # Evidence translations
            if translation.get('vietnamese_evidence'):
                print("\n   📚 EVIDENCE TRANSLATIONS:")
                vi_ev = translation.get('vietnamese_evidence', [])
                en_ev = translation.get('english_evidence', [])
                for j, (vi, en) in enumerate(zip(vi_ev, en_ev), 1):
                    print(f"      {j}. VI: {vi[:60]}...")
                    print(f"         EN: {en[:60]}...")
            
            # MiniCheck details
            print("\n   🔍 MINICHECK SERVICE:")
            if minicheck_input:
                print(f"      INPUT Claim: {minicheck_input.get('claim', 'N/A')[:80]}...")
                evidence_list = minicheck_input.get('evidence', [])
                if evidence_list:
                    print(f"      INPUT Evidence ({len(evidence_list)} items):")
                    for j, ev in enumerate(evidence_list, 1):
                        print(f"         {j}. {ev[:70]}...")
            
            minicheck_output = debug.get('minicheck_parsed_output', {})
            if minicheck_output:
                print(f"      OUTPUT Verdict: {minicheck_output.get('verdict', 'N/A')}")
                print(f"      OUTPUT Confidence: {minicheck_output.get('confidence', 0):.4f}")
            
            # Evidence sources
            print("\n   🔗 EVIDENCE SOURCES (Brave Search):")
            for j, ev in enumerate(fc_result.get('evidence', []), 1):
                print(f"      {j}. [{ev.get('title', 'N/A')[:50]}]")
                print(f"         URL: {ev.get('url', 'N/A')[:70]}")
        else:
            print(f"   ❌ ERROR: {fc_result.get('error', 'Unknown')}")
        
        print("\n" + "=" * 100)
    
    print("\n📊 SUMMARY")
    print("=" * 100)

if __name__ == "__main__":
    main()
