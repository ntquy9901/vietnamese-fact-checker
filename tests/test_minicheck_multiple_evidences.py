#!/usr/bin/env python3
"""
Test MiniCheck with multiple evidences individually
"""

import requests

def test_minicheck_multiple_evidences():
    """Test MiniCheck with multiple evidences individually"""
    print("🧪 Testing MiniCheck with Multiple Evidences Individually")
    print("=" * 70)
    
    base_url = "http://localhost:8002"
    
    # Test case from our Vietnam specific tests
    claim = "Trương Tấn Dũng là tổng thống của Việt Nam"
    english_claim = "Truong Tan Sang is Vietnam president"
    
    # Simulate multiple evidences from Brave Search (real data from our tests)
    evidences = [
        "Nguyen Tan Dung officially became prime minister in 2006, his son-in-law, then 30, had not yet entered politics",
        "At a party congress held in January 2011, Nguyễn Tấn Dũng was ranked 3rd in the hierarchy of the Communist Party of Vietnam, after President Trương Tấ...",
        "At the time, Mr. Tong had announced to the Political Ministry that he would vote unanimously to discipline a Comrade Commissar of the Political..."
    ]
    
    print(f"📝 Claim: {english_claim}")
    print(f"📄 Testing {len(evidences)} evidences individually:")
    
    results = []
    
    for i, evidence in enumerate(evidences, 1):
        print(f"\n🔍 Evidence {i}:")
        print(f"   {evidence[:100]}...")
        
        try:
            response = requests.post(
                f"{base_url}/verify",
                json={
                    "claim": english_claim,
                    "evidence": [evidence]  # Single evidence
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                label = result.get('label', 'ERROR')
                score = result.get('score', 0.0)
                explanation = result.get('explanation', '')
                
                print(f"   ✅ Result: {label}")
                print(f"   📊 Score: {score:.3f}")
                print(f"   💬 {explanation[:80]}...")
                
                results.append({
                    'evidence_num': i,
                    'evidence': evidence,
                    'label': label,
                    'score': score,
                    'explanation': explanation
                })
            else:
                print(f"   ❌ Failed: {response.status_code}")
                results.append({
                    'evidence_num': i,
                    'evidence': evidence,
                    'label': 'ERROR',
                    'score': 0.0,
                    'explanation': f'API Error: {response.status_code}'
                })
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
            results.append({
                'evidence_num': i,
                'evidence': evidence,
                'label': 'EXCEPTION',
                'score': 0.0,
                'explanation': str(e)
            })
    
    # Analysis
    print(f"\n" + "=" * 70)
    print("📊 MULTIPLE EVIDENCE ANALYSIS")
    print("=" * 70)
    
    supported_results = [r for r in results if r['label'] == 'SUPPORTED']
    refuted_results = [r for r in results if r['label'] == 'REFUTED']
    error_results = [r for r in results if r['label'] in ['ERROR', 'EXCEPTION']]
    
    print(f"✅ Supported: {len(supported_results)} evidences")
    print(f"❌ Refuted: {len(refuted_results)} evidences")
    print(f"🚨 Errors: {len(error_results)} evidences")
    
    # Find best evidence
    if results:
        best_result = max(results, key=lambda x: x['score'])
        print(f"\n🎯 Best Evidence:")
        print(f"   Evidence {best_result['evidence_num']}: {best_result['label']} (Score: {best_result['score']:.3f})")
        print(f"   {best_result['evidence'][:100]}...")
    
    # Aggregate decision
    print(f"\n🔍 Aggregate Decision:")
    if supported_results:
        avg_support_score = sum(r['score'] for r in supported_results) / len(supported_results)
        print(f"   ✅ SUPPORTED with {len(supported_results)} evidences")
        print(f"   📊 Average Support Score: {avg_support_score:.3f}")
    
    if refuted_results:
        avg_refute_score = sum(r['score'] for r in refuted_results) / len(refuted_results)
        print(f"   ❌ REFUTED with {len(refuted_results)} evidences")
        print(f"   📊 Average Refute Score: {avg_refute_score:.3f}")
    
    # Test with current Vietnamese Fact Checker approach
    print(f"\n" + "=" * 70)
    print("🔄 Current Vietnamese Fact Checker Approach")
    print("=" * 70)
    
    print(f"📝 Using only FIRST evidence (current approach):")
    if results:
        first_result = results[0]
        print(f"   Evidence 1: {first_result['label']} (Score: {first_result['score']:.3f})")
        print(f"   This is what Vietnamese Fact Checker currently returns!")
    
    print(f"\n💡 Proposed Improvement:")
    print(f"   Test all evidences individually and use the best scoring one")
    print(f"   Or aggregate results from multiple evidences")
    
    return results

def test_with_real_vietnam_evidence():
    """Test with real Vietnam evidence from Brave Search"""
    print(f"\n" + "=" * 70)
    print("🇻🇳 TESTING WITH REAL VIETNAM EVIDENCE")
    print("=" * 70)
    
    base_url = "http://localhost:8002"
    
    # Real claim about VIC stock
    claim = "Cổ phiếu VIC bị giảm ở thị trường Việt Nam hôm nay"
    english_claim = "VIC stock decreased in Vietnam market today"
    
    # Real evidence from Brave Search
    evidences = [
        "VIC's decline over the past week has exhausted much of the market's recovery effort, leaving the VN-Index at a loss of more than 41 points",
        "VIC declined to 6.4% and GEX was on the floor from the ATC session causing the stock to adjust sharply at the last minute, closing down by nearly 30 points",
        "Following a deep morning of adjustments influenced by Vingroup's stock group, the stock gradually recovered during the afternoon session"
    ]
    
    print(f"📝 Claim: {english_claim}")
    print(f"📄 Real Vietnam Stock Evidence:")
    
    for i, evidence in enumerate(evidences, 1):
        print(f"\n🔍 Evidence {i}:")
        print(f"   {evidence[:100]}...")
        
        try:
            response = requests.post(
                f"{base_url}/verify",
                json={
                    "claim": english_claim,
                    "evidence": [evidence]
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Result: {result['label']} (Score: {result['score']:.3f})")
            else:
                print(f"   ❌ Failed: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")

if __name__ == "__main__":
    print("🎯 HYPOTHESIS: Multiple evidences should give better results than single evidence")
    print("=" * 70)
    
    results = test_minicheck_multiple_evidences()
    test_with_real_vietnam_evidence()
    
    print(f"\n🎉 MULTIPLE EVIDENCE TEST COMPLETED!")
    print(f"\n💡 CONCLUSION:")
    print(f"   If multiple evidences give high scores while single evidence gives low scores,")
    print(f"   then the issue is evidence selection, not MiniCheck capability.")
