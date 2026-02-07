#!/usr/bin/env python3
"""
Debug Fact Checker vs MiniCheck disconnect
"""

import requests
import json

def test_pol_001_direct():
    """Test pol_001 case directly through both APIs"""
    
    claim = "Việt Nam có chế độ đa đảng"
    
    print(" Testing pol_001: 'Việt Nam có chế độ đa đảng'")
    print("="*60)
    
    # 1. Test through Fact Checker (orchestrator)
    print("\n[1] FACT CHECKER (orchestrator)...")
    try:
        fc_response = requests.post(
            "http://localhost:8005/check",
            json={"claim": claim},
            timeout=60
        )
        if fc_response.status_code == 200:
            fc_data = fc_response.json()
            print(f"    Verdict: {fc_data.get('verdict')}")
            print(f"    Confidence: {fc_data.get('confidence', 0):.3f}")
            
            # Show MiniCheck debug info
            debug_info = fc_data.get('debug_info', {})
            minicheck_raw = debug_info.get('minicheck_raw_output', {})
            minicheck_parsed = debug_info.get('minicheck_parsed_output', {})
            
            print(f"    MiniCheck Raw Label: {minicheck_raw.get('label')}")
            print(f"    MiniCheck Raw Score: {minicheck_raw.get('score', 0):.3f}")
            print(f"    MiniCheck Parsed Verdict: {minicheck_parsed.get('verdict')}")
            print(f"    MiniCheck Parsed Confidence: {minicheck_parsed.get('confidence', 0):.3f}")
            
            # Show all evidence scores
            all_scores = minicheck_raw.get('all_scores', [])
            print(f"    All Evidence Scores ({len(all_scores)}):")
            for i, score_info in enumerate(all_scores):
                label = score_info.get('label', 'N/A')
                score = score_info.get('score', 0)
                print(f"      [{i}] {label}: {score:.3f}")
        else:
            print(f"     Fact Checker failed: {fc_response.status_code}")
    except Exception as e:
        print(f"     Fact Checker error: {e}")
    
    # 2. Test MiniCheck directly with translated claim
    print("\n[2] MINICHECK (direct)...")
    try:
        # First translate claim
        trans_response = requests.post(
            "http://localhost:8003/translate",
            json={"text": claim},
            timeout=30
        )
        if trans_response.status_code == 200:
            trans_data = trans_response.json()
            claim_en = trans_data.get("english", claim)
            print(f"    Claim EN: {claim_en}")
            
            # Get some evidence
            search_response = requests.post(
                "http://localhost:8004/search_vietnamese",
                json={"query": claim, "max_results": 5},
                timeout=30
            )
            if search_response.status_code == 200:
                search_data = search_response.json()
                results = search_data.get("results", [])
                
                if results:
                    # Translate evidence
                    evidence_texts = [r["content"] for r in results if r.get("content")]
                    if evidence_texts:
                        batch_response = requests.post(
                            "http://localhost:8003/translate_batch",
                            json={"texts": evidence_texts},
                            timeout=30
                        )
                        if batch_response.status_code == 200:
                            batch_data = batch_response.json()
                            translations = batch_data.get("translations", [])
                            english_evidence = [t["english"] for t in translations]
                            
                            # Test MiniCheck directly
                            minicheck_response = requests.post(
                                "http://localhost:8002/verify",
                                json={"claim": claim_en, "evidence": english_evidence},
                                timeout=30
                            )
                            if minicheck_response.status_code == 200:
                                mc_data = minicheck_response.json()
                                print(f"    MiniCheck Direct Label: {mc_data.get('label')}")
                                print(f"    MiniCheck Direct Score: {mc_data.get('score', 0):.3f}")
                                print(f"    MiniCheck Avg Score: {mc_data.get('avg_score', 0):.3f}")
                                
                                # Show individual scores
                                all_scores = mc_data.get("all_scores", [])
                                print(f"    Individual Scores:")
                                for i, score_info in enumerate(all_scores):
                                    label = score_info.get('label', 'N/A')
                                    score = score_info.get('score', 0)
                                    print(f"      [{i}] {label}: {score:.3f}")
                            else:
                                print(f"     MiniCheck direct failed: {minicheck_response.status_code}")
                        else:
                            print(f"     Evidence translation failed")
                    else:
                        print(f"     No evidence content to translate")
                else:
                    print(f"     No search results")
            else:
                print(f"     Search failed: {search_response.status_code}")
        else:
            print(f"     Translation failed: {trans_response.status_code}")
    except Exception as e:
        print(f"     MiniCheck direct error: {e}")

if __name__ == "__main__":
    test_pol_001_direct()
