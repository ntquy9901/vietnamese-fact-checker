#!/usr/bin/env python3
"""
Verbose debug of Fact Checker vs MiniCheck disconnect
"""

import requests
import json

def test_fact_checker_verbose():
    """Test Fact Checker with verbose logging"""
    
    claim = "Việt Nam có chế độ đa đảng"
    
    print(" Testing Fact Checker with verbose logging...")
    print("="*60)
    
    # Test through Fact Checker (orchestrator)
    try:
        fc_response = requests.post(
            "http://localhost:8005/check",
            json={"claim": claim},
            timeout=60
        )
        if fc_response.status_code == 200:
            fc_data = fc_response.json()
            
            print(f"Verdict: {fc_data.get('verdict')}")
            print(f"Confidence: {fc_data.get('confidence', 0):.3f}")
            
            # Show full debug info
            debug_info = fc_data.get('debug_info', {})
            
            print("\n Translation Debug:")
            trans_debug = debug_info.get('translation', {})
            print(f"  Original Claim: {trans_debug.get('original_claim')}")
            print(f"  English Claim: {trans_debug.get('english_claim')}")
            print(f"  Evidence Count: {len(trans_debug.get('english_evidence', []))}")
            
            print("\n MiniCheck Input Debug:")
            mc_input = debug_info.get('minicheck_input', {})
            print(f"  Claim: {mc_input.get('claim')}")
            print(f"  Evidence Count: {len(mc_input.get('evidence', []))}")
            print(f"  Evidence 1: {mc_input.get('evidence', [''])[0][:100] if mc_input.get('evidence') else 'None'}...")
            
            print("\n MiniCheck Raw Output Debug:")
            mc_raw = debug_info.get('minicheck_raw_output', {})
            print(f"  Raw Label: {mc_raw.get('label')}")
            print(f"  Raw Score: {mc_raw.get('score')}")
            print(f"  Raw Avg Score: {mc_raw.get('avg_score')}")
            print(f"  Raw Evidence Count: {mc_raw.get('evidence_count')}")
            print(f"  Raw All Scores: {len(mc_raw.get('all_scores', []))}")
            
            if mc_raw.get('all_scores'):
                print("  Individual Raw Scores:")
                for i, score_info in enumerate(mc_raw.get('all_scores', [])[:3]):
                    label = score_info.get('label', 'N/A')
                    score = score_info.get('score', 0)
                    print(f"    [{i}] {label}: {score:.3f}")
            
            print("\n MiniCheck Parsed Output Debug:")
            mc_parsed = debug_info.get('minicheck_parsed_output', {})
            print(f"  Parsed Verdict: {mc_parsed.get('verdict')}")
            print(f"  Parsed Confidence: {mc_parsed.get('confidence')}")
            print(f"  Has Raw Result: {'raw_result' in mc_parsed}")
            
            if 'raw_result' in mc_parsed:
                raw_from_parsed = mc_parsed['raw_result']
                print(f"  Raw From Parsed Label: {raw_from_parsed.get('label')}")
                print(f"  Raw From Parsed Score: {raw_from_parsed.get('score')}")
                print(f"  Raw From Parsed All Scores: {len(raw_from_parsed.get('all_scores', []))}")
            
        else:
            print(f" Fact Checker failed: {fc_response.status_code}")
            print(fc_response.text)
    except Exception as e:
        print(f" Fact Checker error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_fact_checker_verbose()
