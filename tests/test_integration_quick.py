#!/usr/bin/env python3
"""
Quick integration test with 2 test cases to verify model upgrades
"""

import requests
import json
import time
import os
from datetime import datetime

# Test cases from the dataset
TEST_CASES = [
    {
        "id": "geo_002",
        "claim": "Việt Nam có đường biên giới với Trung Quốc, Lào và Campuchia",
        "expected": "SUPPORTED",
        "difficulty": "medium"
    },
    {
        "id": "pol_001", 
        "claim": "Việt Nam có chế độ đa đảng",
        "expected": "REFUTED",
        "difficulty": "medium"
    }
]

def test_service_health():
    """Check if all services are running"""
    services = {
        "Brave Search": "http://localhost:8004/",
        "Translation": "http://localhost:8003/",
        "MiniCheck": "http://localhost:8002/health",
        "Fact Checker": "http://localhost:8005/"
    }
    
    print(" Checking service health...")
    for name, url in services.items():
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f"   {name}: {data.get('status', 'healthy')}")
                if name == "Translation":
                    print(f"     Model: {data.get('model', 'unknown')}")
                elif name == "MiniCheck":
                    print(f"     Model: {data.get('model', 'unknown')}")
            else:
                print(f"   {name}: HTTP {response.status_code}")
                return False
        except Exception as e:
            print(f"   {name}: {e}")
            return False
    
    return True

def test_single_case(test_case):
    """Test a single claim through the full pipeline"""
    claim = test_case["claim"]
    expected = test_case["expected"]
    case_id = test_case["id"]
    
    print(f"\n{'='*60}")
    print(f"[{case_id}] {claim}")
    print(f"Expected: {expected} | Difficulty: {test_case['difficulty']}")
    print('='*60)
    
    # 1. Brave Search
    print("\n[1] BRAVE SEARCH...")
    try:
        search_response = requests.post(
            "http://localhost:8004/search_vietnamese",
            json={"query": claim, "max_results": 5},
            timeout=30
        )
        if search_response.status_code == 200:
            search_data = search_response.json()
            results = search_data.get("results", [])
            print(f"    Found {len(results)} results")
            for i, result in enumerate(results[:3]):
                print(f"    [{i}] {result['title'][:50]}...")
        else:
            print(f"     Search failed: {search_response.status_code}")
            return False
    except Exception as e:
        print(f"     Search error: {e}")
        return False
    
    # 2. Translation
    print("\n[2] TRANSLATION...")
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
            print(f"    Claim VI: {claim[:50]}...")
            print(f"    Claim EN: {claim_en[:50]}...")
        else:
            print(f"     Claim translation failed")
            return False
        
        # Translate evidences
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
                print(f"    Translated {len(english_evidence)} evidence texts")
            else:
                print(f"     Evidence translation failed")
                return False
        else:
            english_evidence = []
    except Exception as e:
        print(f"     Translation error: {e}")
        return False
    
    # 3. MiniCheck
    print("\n[3] MINICHECK...")
    try:
        if english_evidence:
            minicheck_response = requests.post(
                "http://localhost:8002/verify",
                json={"claim": claim_en, "evidence": english_evidence},
                timeout=30
            )
            if minicheck_response.status_code == 200:
                minicheck_data = minicheck_response.json()
                label = minicheck_data.get("label")
                score = minicheck_data.get("score", 0)
                avg_score = minicheck_data.get("avg_score", 0)
                evidence_count = minicheck_data.get("evidence_count", 0)
                
                print(f"    Label: {label}")
                print(f"    Score: {score:.3f}")
                print(f"    Avg Score: {avg_score:.3f}")
                print(f"    Evidence Count: {evidence_count}")
                
                # Show individual scores
                all_scores = minicheck_data.get("all_scores", [])
                for i, score_info in enumerate(all_scores[:3]):
                    print(f"      [{i}] {score_info.get('label', 'N/A')}: {score_info.get('score', 0):.3f}")
            else:
                print(f"     MiniCheck failed: {minicheck_response.status_code}")
                return False
        else:
            print("     No evidence to check")
            return False
    except Exception as e:
        print(f"     MiniCheck error: {e}")
        return False
    
    # 4. Fact Checker (orchestrator)
    print("\n[4] FACT CHECKER (orchestrator)...")
    try:
        fc_response = requests.post(
            "http://localhost:8005/check",
            json={"claim": claim},
            timeout=60
        )
        if fc_response.status_code == 200:
            fc_data = fc_response.json()
            verdict = fc_data.get("verdict")
            confidence = fc_data.get("confidence", 0)
            
            print(f"    Verdict: {verdict}")
            print(f"    Confidence: {confidence:.3f}")
            
            # Check result
            is_correct = verdict == expected
            result = "CORRECT" if is_correct else "WRONG"
            print(f"\n[RESULT] Expected: {expected} | Actual: {verdict} | {result}")
            
            return is_correct
        else:
            print(f"     Fact Checker failed: {fc_response.status_code}")
            return False
    except Exception as e:
        print(f"     Fact Checker error: {e}")
        return False

def main():
    """Run quick integration test"""
    print(" QUICK INTEGRATION TEST - Model Upgrades Verification")
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check service health
    if not test_service_health():
        print("\n Some services are not running. Please start all services first.")
        return
    
    print(f"\n Testing {len(TEST_CASES)} cases...")
    
    # Run tests
    correct_count = 0
    total_count = len(TEST_CASES)
    
    for test_case in TEST_CASES:
        if test_single_case(test_case):
            correct_count += 1
    
    # Summary
    accuracy = (correct_count / total_count) * 100
    print(f"\n{'='*60}")
    print("SUMMARY")
    print('='*60)
    print(f"Overall Accuracy: {correct_count}/{total_count} ({accuracy:.1f}%)")
    
    if accuracy == 100:
        print(" PERFECT! All test cases passed!")
    elif accuracy >= 75:
        print(" GOOD! Most test cases passed.")
    else:
        print(" NEEDS IMPROVEMENT")
    
    print(f"\n Models used:")
    print(f"  Translation: VinAI/vinai-translate-vi2en-v2 (GPU)")
    print(f"  MiniCheck: Flan-T5-Large (GPT-4 level accuracy)")

if __name__ == "__main__":
    main()
