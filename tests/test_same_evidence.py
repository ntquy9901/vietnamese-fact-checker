#!/usr/bin/env python3
"""
Test Fact Checker and MiniCheck Direct with IDENTICAL evidence
"""

import requests
import json

def test_with_same_evidence():
    """Test both systems with the same evidence to isolate the logic bug"""
    
    claim = "Việt Nam có chế độ đa đảng"
    
    # Fixed evidence set (same for both tests)
    fixed_evidence = [
        "The one-party system... the Vietnamese revolution allowed to assert: In Vietnam there is no need and no acceptance of multi-party system.",
        "In practice in Vietnam, going to socialism under the leadership of the Communist Party of Vietnam is the right aspiration and choice of our People.",
        "Building a democracy backed by opposition multiparty politics and ideological pluralism is a necessary condition for Vietnam to be civilized and prosperous.",
        "There are also some countries with multi-party systems, but one party plays a key role for a long time.",
        "We cannot provide a description for this page right now."
    ]
    
    print(" TESTING WITH IDENTICAL EVIDENCE")
    print("="*60)
    print(f"Claim: {claim}")
    print(f"Evidence Count: {len(fixed_evidence)}")
    
    # Translate claim
    try:
        trans_response = requests.post(
            "http://localhost:8003/translate",
            json={"text": claim},
            timeout=30
        )
        if trans_response.status_code == 200:
            trans_data = trans_response.json()
            claim_en = trans_data.get("english", claim)
            print(f"Claim EN: {claim_en}")
        else:
            print(f" Translation failed")
            return
    except Exception as e:
        print(f" Translation error: {e}")
        return
    
    # Translate evidence
    try:
        batch_response = requests.post(
            "http://localhost:8003/translate_batch",
            json={"texts": fixed_evidence},
            timeout=30
        )
        if batch_response.status_code == 200:
            batch_data = batch_response.json()
            translations = batch_data.get("translations", [])
            english_evidence = [t["english"] for t in translations]
            print(f" Translated {len(english_evidence)} evidence pieces")
        else:
            print(f" Evidence translation failed")
            return
    except Exception as e:
        print(f" Evidence translation error: {e}")
        return
    
    # Test 1: MiniCheck Direct
    print(f"\n TEST 1: MiniCheck Direct")
    print("-"*40)
    try:
        minicheck_response = requests.post(
            "http://localhost:8002/verify",
            json={"claim": claim_en, "evidence": english_evidence},
            timeout=30
        )
        if minicheck_response.status_code == 200:
            mc_data = minicheck_response.json()
            print(f" MiniCheck Direct Verdict: {mc_data.get('label')}")
            print(f" MiniCheck Direct Score: {mc_data.get('score', 0):.3f}")
            print(f" MiniCheck Avg Score: {mc_data.get('avg_score', 0):.3f}")
            
            # Show individual scores
            all_scores = mc_data.get("all_scores", [])
            print(f" Individual Scores:")
            for i, score_info in enumerate(all_scores):
                label = score_info.get('label', 'N/A')
                score = score_info.get('score', 0)
                print(f"    [{i}] {label}: {score:.3f}")
        else:
            print(f" MiniCheck Direct failed: {minicheck_response.status_code}")
    except Exception as e:
        print(f" MiniCheck Direct error: {e}")
    
    # Test 2: Fact Checker (simulate with same evidence)
    print(f"\n TEST 2: Fact Checker Logic Simulation")
    print("-"*40)
    
    # Simulate what Fact Checker does with the same evidence
    try:
        # Call MiniCheck client directly (same as Fact Checker)
        from vietnamese_fact_checker.src.services.minicheck_client import minicheck_client
        import asyncio
        
        async def test_fact_checker_logic():
            result = await minicheck_client.verify(claim_en, english_evidence)
            return result
        
        # Run async
        result = asyncio.run(test_fact_checker_logic())
        
        print(f" Fact Checker Logic Verdict: {result.get('verdict')}")
        print(f" Fact Checker Logic Confidence: {result.get('confidence', 0):.3f}")
        
        # Show raw result
        raw_result = result.get('raw_result', {})
        print(f" Raw MiniCheck Server Response:")
        print(f"    Label: {raw_result.get('label')}")
        print(f"    Score: {raw_result.get('score', 0):.3f}")
        print(f"    Avg Score: {raw_result.get('avg_score', 0):.3f}")
        
        raw_scores = raw_result.get('all_scores', [])
        if raw_scores:
            print(f" Raw Individual Scores:")
            for i, score_info in enumerate(raw_scores):
                label = score_info.get('label', 'N/A')
                score = score_info.get('score', 0)
                print(f"    [{i}] {label}: {score:.3f}")
        
    except Exception as e:
        print(f" Fact Checker Logic error: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 3: Full Fact Checker (but we can't control evidence)
    print(f"\n TEST 3: Full Fact Checker (for reference)")
    print("-"*40)
    try:
        fc_response = requests.post(
            "http://localhost:8005/check",
            json={"claim": claim},
            timeout=60
        )
        if fc_response.status_code == 200:
            fc_data = fc_response.json()
            print(f" Full Fact Checker Verdict: {fc_data.get('verdict')}")
            print(f" Full Fact Checker Confidence: {fc_data.get('confidence', 0):.3f}")
        else:
            print(f" Full Fact Checker failed: {fc_response.status_code}")
    except Exception as e:
        print(f" Full Fact Checker error: {e}")

if __name__ == "__main__":
    test_with_same_evidence()
