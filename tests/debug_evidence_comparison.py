#!/usr/bin/env python3
"""
Comprehensive evidence comparison between MiniCheck Direct and Fact Checker
Using UNIFIED configuration (max_evidence = 5)
"""

import requests
import json

def get_unified_config():
    """Get unified max evidence configuration"""
    # Check system config
    try:
        response = requests.get("http://localhost:8005/config/evidence", timeout=5)
        if response.status_code == 200:
            config = response.json().get('config', {})
            max_chunks = config.get('max_chunks', 5)
            print(f" System Evidence Config: max_chunks = {max_chunks}")
            return max_chunks
    except:
        pass
    
    # Fallback to hardcoded
    print(" Using default config: max_evidence = 5")
    return 5

def print_evidence_comparison(evidence_fc, evidence_mc, title):
    """Print detailed evidence comparison"""
    print(f"\n {title}")
    print("="*80)
    
    print(f"Fact Checker Evidence Count: {len(evidence_fc)}")
    print(f"MiniCheck Direct Evidence Count: {len(evidence_mc)}")
    
    # Compare each evidence piece
    min_count = min(len(evidence_fc), len(evidence_mc))
    
    for i in range(min_count):
        fc_text = evidence_fc[i][:200] + "..." if len(evidence_fc[i]) > 200 else evidence_fc[i]
        mc_text = evidence_mc[i][:200] + "..." if len(evidence_mc[i]) > 200 else evidence_mc[i]
        
        print(f"\n[{i}] FACT CHECKER:")
        print(f"    {fc_text}")
        
        print(f"[{i}] MINICHECK DIRECT:")
        print(f"    {mc_text}")
        
        # Check if they're the same
        if fc_text == mc_text:
            print(f"     SAME")
        else:
            print(f"     DIFFERENT")
    
    # Show extra evidence if counts differ
    if len(evidence_fc) > len(evidence_mc):
        print(f"\n Extra Fact Checker Evidence ({len(evidence_mc)}-{len(evidence_fc)-1}):")
        for i in range(len(evidence_mc), len(evidence_fc)):
            print(f"    [{i}] {evidence_fc[i][:200]}...")
    
    elif len(evidence_mc) > len(evidence_fc):
        print(f"\n Extra MiniCheck Evidence ({len(evidence_fc)}-{len(evidence_mc)-1}):")
        for i in range(len(evidence_fc), len(evidence_mc)):
            print(f"    [{i}] {evidence_mc[i][:200]}...")

def test_evidence_comparison():
    """Compare evidence between Fact Checker and MiniCheck Direct"""
    
    claim = "Việt Nam có chế độ đa đảng"
    max_evidence = get_unified_config()
    
    print(" EVIDENCE COMPARISON TEST")
    print("="*80)
    print(f"Claim: {claim}")
    print(f"Unified Max Evidence: {max_evidence}")
    
    # Step 1: Get evidence from Fact Checker pipeline
    print(f"\n STEP 1: Fact Checker Evidence Pipeline")
    print("-"*50)
    
    try:
        # Get search results through Fact Checker's method
        fc_response = requests.post(
            "http://localhost:8005/check",
            json={"claim": claim},
            timeout=60
        )
        
        if fc_response.status_code == 200:
            fc_data = fc_response.json()
            debug_info = fc_data.get('debug_info', {})
            
            # Get evidence from Fact Checker
            fc_input = debug_info.get('minicheck_input', {})
            fc_evidence = fc_input.get('evidence', [])
            
            # Get MiniCheck raw output from Fact Checker
            fc_raw = debug_info.get('minicheck_raw_output', {})
            fc_scores = fc_raw.get('all_scores', [])
            
            print(f" Fact Checker Evidence: {len(fc_evidence)} pieces")
            print(f" Fact Checker Verdict: {fc_data.get('verdict')}")
            print(f" Fact Checker Confidence: {fc_data.get('confidence', 0):.3f}")
            
            # Show Fact Checker evidence scores
            if fc_scores:
                print(f" Fact Checker Evidence Scores:")
                for i, score_info in enumerate(fc_scores):
                    label = score_info.get('label', 'N/A')
                    score = score_info.get('score', 0)
                    preview = fc_evidence[i][:100] + "..." if i < len(fc_evidence) else "N/A"
                    print(f"    [{i}] {label}: {score:.3f} - {preview}")
        else:
            print(f" Fact Checker failed: {fc_response.status_code}")
            fc_evidence = []
            fc_scores = []
            
    except Exception as e:
        print(f" Fact Checker error: {e}")
        fc_evidence = []
        fc_scores = []
    
    # Step 2: Get evidence from MiniCheck Direct pipeline
    print(f"\n STEP 2: MiniCheck Direct Evidence Pipeline")
    print("-"*50)
    
    try:
        # Translate claim
        trans_response = requests.post(
            "http://localhost:8003/translate",
            json={"text": claim},
            timeout=30
        )
        
        if trans_response.status_code == 200:
            trans_data = trans_response.json()
            claim_en = trans_data.get("english", claim)
            
            # Get search results (same config as Fact Checker)
            search_response = requests.post(
                "http://localhost:8004/search_vietnamese",
                json={"query": claim, "max_results": max_evidence},
                timeout=30
            )
            
            if search_response.status_code == 200:
                search_data = search_response.json()
                results = search_data.get("results", [])
                
                # Extract evidence content (same as Fact Checker)
                evidence_texts = [r["content"] for r in results if r.get("content")]
                
                # Translate evidence
                if evidence_texts:
                    batch_response = requests.post(
                        "http://localhost:8003/translate_batch",
                        json={"texts": evidence_texts},
                        timeout=30
                    )
                    
                    if batch_response.status_code == 200:
                        batch_data = batch_response.json()
                        translations = batch_data.get("translations", [])
                        mc_evidence = [t["english"] for t in translations]
                        
                        # Call MiniCheck directly
                        minicheck_response = requests.post(
                            "http://localhost:8002/verify",
                            json={"claim": claim_en, "evidence": mc_evidence},
                            timeout=30
                        )
                        
                        if minicheck_response.status_code == 200:
                            mc_data = minicheck_response.json()
                            mc_scores = mc_data.get("all_scores", [])
                            
                            print(f" MiniCheck Direct Evidence: {len(mc_evidence)} pieces")
                            print(f" MiniCheck Direct Verdict: {mc_data.get('label')}")
                            print(f" MiniCheck Direct Score: {mc_data.get('score', 0):.3f}")
                            print(f" MiniCheck Direct Avg Score: {mc_data.get('avg_score', 0):.3f}")
                            
                            # Show MiniCheck Direct evidence scores
                            if mc_scores:
                                print(f" MiniCheck Direct Evidence Scores:")
                                for i, score_info in enumerate(mc_scores):
                                    label = score_info.get('label', 'N/A')
                                    score = score_info.get('score', 0)
                                    preview = mc_evidence[i][:100] + "..." if i < len(mc_evidence) else "N/A"
                                    print(f"    [{i}] {label}: {score:.3f} - {preview}")
                        else:
                            print(f" MiniCheck Direct failed: {minicheck_response.status_code}")
                            mc_evidence = []
                            mc_scores = []
                    else:
                        print(f" Evidence translation failed")
                        mc_evidence = []
                        mc_scores = []
                else:
                    print(f" No evidence content")
                    mc_evidence = []
                    mc_scores = []
            else:
                print(f" Search failed: {search_response.status_code}")
                mc_evidence = []
                mc_scores = []
        else:
            print(f" Translation failed: {trans_response.status_code}")
            mc_evidence = []
            mc_scores = []
            
    except Exception as e:
        print(f" MiniCheck Direct error: {e}")
        mc_evidence = []
        mc_scores = []
    
    # Step 3: Compare evidence
    if fc_evidence and mc_evidence:
        print_evidence_comparison(fc_evidence, mc_evidence, "EVIDENCE COMPARISON")
        
        # Step 4: Analyze differences
        print(f"\n ANALYSIS")
        print("="*80)
        
        # Count matching evidence
        matches = 0
        for i in range(min(len(fc_evidence), len(mc_evidence))):
            if fc_evidence[i] == mc_evidence[i]:
                matches += 1
        
        similarity = (matches / min(len(fc_evidence), len(mc_evidence))) * 100
        print(f"Evidence Similarity: {matches}/{min(len(fc_evidence), len(mc_evidence))} ({similarity:.1f}%)")
        
        if similarity == 100:
            print(" PERFECT MATCH - Evidence is identical")
        elif similarity >= 80:
            print(" HIGH SIMILARITY - Most evidence matches")
        elif similarity >= 50:
            print(" MEDIUM SIMILARITY - Some evidence matches")
        else:
            print(" LOW SIMILARITY - Evidence differs significantly")
        
        # Compare verdicts
        fc_verdict = fc_data.get('verdict', 'ERROR') if 'fc_data' in locals() else 'ERROR'
        mc_verdict = mc_data.get('label', 'ERROR') if 'mc_data' in locals() else 'ERROR'
        
        print(f"\n VERDICT COMPARISON:")
        print(f"Fact Checker: {fc_verdict}")
        print(f"MiniCheck Direct: {mc_verdict}")
        
        if fc_verdict == mc_verdict:
            print(" VERDICTS MATCH")
        else:
            print(" VERDICTS DIFFER - This is the bug we need to fix!")
    else:
        print(f"\n Cannot compare - missing evidence data")
        print(f"Fact Checker evidence: {len(fc_evidence)}")
        print(f"MiniCheck Direct evidence: {len(mc_evidence)}")

if __name__ == "__main__":
    test_evidence_comparison()
