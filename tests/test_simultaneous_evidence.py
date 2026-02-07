#!/usr/bin/env python3
"""
Test Fact Checker and MiniCheck Direct with SIMULTANEOUS evidence calls
This ensures both get the same evidence from Brave Search
"""

import requests
import json
import asyncio
import time

async def test_simultaneous_evidence():
    """Test both systems with simultaneous evidence calls"""
    
    claim = "Việt Nam có chế độ đa đảng"
    
    print(" TESTING SIMULTANEOUS EVIDENCE CALLS")
    print("="*60)
    print(f"Claim: {claim}")
    
    # Step 1: Get evidence ONCE (simulates what both should use)
    print("\n STEP 1: Get Shared Evidence")
    print("-"*40)
    
    try:
        search_response = requests.post(
            "http://localhost:8004/search_vietnamese",
            json={"query": claim, "max_results": 5},
            timeout=30
        )
        
        if search_response.status_code == 200:
            search_data = search_response.json()
            results = search_data.get("results", [])
            print(f" Got {len(results)} evidence pieces")
            
            # Extract evidence texts
            evidence_texts = [r["content"] for r in results if r.get("content")]
            print(f" Extracted {len(evidence_texts)} evidence texts")
            
        else:
            print(f" Search failed: {search_response.status_code}")
            return
            
    except Exception as e:
        print(f" Search error: {e}")
        return
    
    # Step 2: Translate claim and evidence ONCE
    print("\n STEP 2: Translate Shared Evidence")
    print("-"*40)
    
    try:
        # Translate claim
        claim_response = requests.post(
            "http://localhost:8003/translate",
            json={"text": claim},
            timeout=30
        )
        
        if claim_response.status_code == 200:
            claim_data = claim_response.json()
            claim_en = claim_data.get("english", claim)
            print(f" Claim EN: {claim_en}")
        else:
            print(f" Claim translation failed")
            return
        
        # Translate evidence
        batch_response = requests.post(
            "http://localhost:8003/translate_batch",
            json={"texts": evidence_texts},
            timeout=30
        )
        
        if batch_response.status_code == 200:
            batch_data = batch_response.json()
            translations = batch_data.get("translations", [])
            english_evidence = [t["english"] for t in translations]
            print(f" Translated {len(english_evidence)} evidence texts")
        else:
            print(f" Evidence translation failed")
            return
            
    except Exception as e:
        print(f" Translation error: {e}")
        return
    
    # Step 3: Test MiniCheck Direct with shared evidence
    print("\n STEP 3: MiniCheck Direct (Shared Evidence)")
    print("-"*40)
    
    try:
        minicheck_response = requests.post(
            "http://localhost:8002/verify",
            json={"claim": claim_en, "evidence": english_evidence},
            timeout=30
        )
        
        if minicheck_response.status_code == 200:
            mc_data = minicheck_response.json()
            mc_label = mc_data.get("label")
            mc_score = mc_data.get("score", 0)
            mc_avg_score = mc_data.get("avg_score", 0)
            mc_all_scores = mc_data.get("all_scores", [])
            
            print(f" MiniCheck Direct Verdict: {mc_label}")
            print(f" MiniCheck Direct Score: {mc_score:.3f}")
            print(f" MiniCheck Avg Score: {mc_avg_score:.3f}")
            
            print(f" MiniCheck Individual Scores:")
            for i, score_info in enumerate(mc_all_scores):
                label = score_info.get('label', 'N/A')
                score = score_info.get('score', 0)
                print(f"    [{i}] {label}: {score:.3f}")
        else:
            print(f" MiniCheck Direct failed: {minicheck_response.status_code}")
            return
            
    except Exception as e:
        print(f" MiniCheck Direct error: {e}")
        return
    
    # Step 4: Test Fact Checker (should use same evidence if timing is right)
    print("\n STEP 4: Fact Checker (immediate call)")
    print("-"*40)
    
    try:
        fc_response = requests.post(
            "http://localhost:8005/check",
            json={"claim": claim},
            timeout=60
        )
        
        if fc_response.status_code == 200:
            fc_data = fc_response.json()
            fc_verdict = fc_data.get('verdict')
            fc_confidence = fc_data.get('confidence', 0)
            
            print(f" Fact Checker Verdict: {fc_verdict}")
            print(f" Fact Checker Confidence: {fc_confidence:.3f}")
            
            # Get Fact Checker's MiniCheck raw output
            debug_info = fc_data.get('debug_info', {})
            fc_raw = debug_info.get('minicheck_raw_output', {})
            fc_all_scores = fc_raw.get('all_scores', [])
            
            print(f" Fact Checker MiniCheck Scores:")
            for i, score_info in enumerate(fc_all_scores):
                label = score_info.get('label', 'N/A')
                score = score_info.get('score', 0)
                print(f"    [{i}] {label}: {score:.3f}")
        else:
            print(f" Fact Checker failed: {fc_response.status_code}")
            return
            
    except Exception as e:
        print(f" Fact Checker error: {e}")
        return
    
    # Step 5: Compare Results
    print("\n STEP 5: Results Comparison")
    print("-"*40)
    
    print(f"MiniCheck Direct: {mc_label} (score: {mc_score:.3f})")
    print(f"Fact Checker: {fc_verdict} (confidence: {fc_confidence:.3f})")
    
    if mc_label == fc_verdict:
        print(" VERDICTS MATCH - Logic fix successful!")
    else:
        print(" VERDICTS DIFFERENT - Still has issues")
        
        # Analyze the difference
        print(f"\n Analysis:")
        print(f"MiniCheck aggregated: {mc_label} (avg: {mc_avg_score:.3f})")
        print(f"Fact Checker got: {fc_verdict} (confidence: {fc_confidence:.3f})")
        
        if fc_all_scores:
            # Check if Fact Checker is using individual scores instead of aggregated
            max_individual_score = max(s.get('score', 0) for s in fc_all_scores)
            max_individual_label = next(s.get('label') for s in fc_all_scores if s.get('score', 0) == max_individual_score)
            
            print(f"Fact Checker max individual: {max_individual_label} (score: {max_individual_score:.3f})")
            
            if max_individual_label == fc_verdict and max_individual_score == fc_confidence:
                print(" FACT CHECKER IS STILL USING MAX INDIVIDUAL SCORE!")
                print(" Need to fix aggregation logic")
            else:
                print(" Different issue - need further investigation")

def main():
    """Run the simultaneous evidence test"""
    asyncio.run(test_simultaneous_evidence())

if __name__ == "__main__":
    main()
