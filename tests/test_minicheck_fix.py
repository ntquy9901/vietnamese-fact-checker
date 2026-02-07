#!/usr/bin/env python3
"""
Unit Test for MiniCheck Fix - Correct 1:1 doc-claim pairing

This test verifies that MiniCheck correctly handles:
1. Multiple evidences for a single claim
2. Returns individual scores for each evidence
3. Aggregates scores using MAX strategy
"""

import requests
import json
from datetime import datetime
from typing import List, Dict

MINICHECK_URL = "http://localhost:8002"

def log_result(test_name: str, input_data: dict, output_data: dict, passed: bool, duration_ms: float) -> dict:
    """Log test result in standard format"""
    return {
        "name": test_name,
        "input": input_data,
        "output": output_data,
        "passed": passed,
        "duration_ms": duration_ms
    }

def test_single_evidence():
    """Test with single evidence"""
    print("\n" + "="*60)
    print("TEST: Single Evidence")
    print("="*60)
    
    input_data = {
        "claim": "Hanoi is the capital of Vietnam",
        "evidence": [
            "Hanoi is the capital city of Vietnam, located in the northern region."
        ]
    }
    
    print(f"Claim: {input_data['claim']}")
    print(f"Evidence count: {len(input_data['evidence'])}")
    
    import time
    start = time.time()
    response = requests.post(f"{MINICHECK_URL}/verify", json=input_data)
    duration_ms = (time.time() - start) * 1000
    
    result = response.json()
    print(f"\nResponse:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    # Assertions
    passed = True
    checks = []
    
    # Check evidence_count
    if result.get("evidence_count") == 1:
        checks.append("evidence_count=1: PASS")
    else:
        checks.append(f"evidence_count=1: FAIL (got {result.get('evidence_count')})")
        passed = False
    
    # Check all_scores length
    if len(result.get("all_scores", [])) == 1:
        checks.append("all_scores length=1: PASS")
    else:
        checks.append(f"all_scores length=1: FAIL (got {len(result.get('all_scores', []))})")
        passed = False
    
    # Check label is SUPPORTED (expected for this input)
    if result.get("label") == "SUPPORTED":
        checks.append("label=SUPPORTED: PASS")
    else:
        checks.append(f"label=SUPPORTED: FAIL (got {result.get('label')})")
        passed = False
    
    print("\nChecks:")
    for c in checks:
        print(f"  - {c}")
    
    print(f"\nResult: {'PASSED' if passed else 'FAILED'}")
    return log_result("test_single_evidence", input_data, result, passed, duration_ms)

def test_multiple_evidences():
    """Test with multiple evidences - should return individual scores"""
    print("\n" + "="*60)
    print("TEST: Multiple Evidences")
    print("="*60)
    
    input_data = {
        "claim": "Vietnam has a border with China",
        "evidence": [
            "Vietnam shares a 1,449 km border with China in the north.",
            "The northern region of Vietnam is mountainous.",
            "Vietnam-China border is one of the longest in Southeast Asia."
        ]
    }
    
    print(f"Claim: {input_data['claim']}")
    print(f"Evidence count: {len(input_data['evidence'])}")
    for i, ev in enumerate(input_data['evidence']):
        print(f"  [{i}] {ev[:60]}...")
    
    import time
    start = time.time()
    response = requests.post(f"{MINICHECK_URL}/verify", json=input_data)
    duration_ms = (time.time() - start) * 1000
    
    result = response.json()
    print(f"\nResponse:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    # Assertions
    passed = True
    checks = []
    
    # Check evidence_count
    if result.get("evidence_count") == 3:
        checks.append("evidence_count=3: PASS")
    else:
        checks.append(f"evidence_count=3: FAIL (got {result.get('evidence_count')})")
        passed = False
    
    # Check all_scores length matches evidence count
    if len(result.get("all_scores", [])) == 3:
        checks.append("all_scores length=3: PASS")
    else:
        checks.append(f"all_scores length=3: FAIL (got {len(result.get('all_scores', []))})")
        passed = False
    
    # Check each all_scores entry has required fields
    all_scores = result.get("all_scores", [])
    for i, score in enumerate(all_scores):
        if "evidence_index" in score and "score" in score and "label" in score:
            checks.append(f"all_scores[{i}] has required fields: PASS")
        else:
            checks.append(f"all_scores[{i}] has required fields: FAIL")
            passed = False
    
    # Check aggregation is max
    if result.get("aggregation") == "max":
        checks.append("aggregation=max: PASS")
    else:
        checks.append(f"aggregation=max: FAIL (got {result.get('aggregation')})")
        passed = False
    
    # Check score equals max of all_scores
    if all_scores:
        max_score = max(s["score"] for s in all_scores)
        if abs(result.get("score", 0) - max_score) < 0.001:
            checks.append(f"score=max(all_scores): PASS ({max_score:.3f})")
        else:
            checks.append(f"score=max(all_scores): FAIL (score={result.get('score')}, max={max_score})")
            passed = False
    
    print("\nChecks:")
    for c in checks:
        print(f"  - {c}")
    
    print(f"\nResult: {'PASSED' if passed else 'FAILED'}")
    return log_result("test_multiple_evidences", input_data, result, passed, duration_ms)

def test_negation_detection():
    """Test if MiniCheck correctly identifies refuting evidence"""
    print("\n" + "="*60)
    print("TEST: Negation Detection")
    print("="*60)
    
    input_data = {
        "claim": "Vietnam has a multi-party political system",
        "evidence": [
            "In Vietnam there is no need and no acceptance of multi-party system.",
            "Vietnam follows a one-party system led by the Communist Party of Vietnam."
        ]
    }
    
    print(f"Claim: {input_data['claim']}")
    print(f"Evidence count: {len(input_data['evidence'])}")
    
    import time
    start = time.time()
    response = requests.post(f"{MINICHECK_URL}/verify", json=input_data)
    duration_ms = (time.time() - start) * 1000
    
    result = response.json()
    print(f"\nResponse:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    # Assertions
    passed = True
    checks = []
    
    # Check evidence_count
    if result.get("evidence_count") == 2:
        checks.append("evidence_count=2: PASS")
    else:
        checks.append(f"evidence_count=2: FAIL (got {result.get('evidence_count')})")
        passed = False
    
    # Check all_scores length
    if len(result.get("all_scores", [])) == 2:
        checks.append("all_scores length=2: PASS")
    else:
        checks.append(f"all_scores length=2: FAIL")
        passed = False
    
    # Note: We expect this to show if MiniCheck detects negation
    # The label might still be wrong (this is what we're trying to fix with Ranker)
    print(f"\nNote: MiniCheck label={result.get('label')}")
    print("This test shows MiniCheck's raw behavior with negation.")
    print("The Ranker service will help correct any missed negations.")
    
    print("\nChecks:")
    for c in checks:
        print(f"  - {c}")
    
    print(f"\nResult: {'PASSED' if passed else 'FAILED'}")
    return log_result("test_negation_detection", input_data, result, passed, duration_ms)

def test_empty_evidence():
    """Test with empty evidence list - should return error"""
    print("\n" + "="*60)
    print("TEST: Empty Evidence")
    print("="*60)
    
    input_data = {
        "claim": "Some claim",
        "evidence": []
    }
    
    print(f"Claim: {input_data['claim']}")
    print(f"Evidence count: {len(input_data['evidence'])}")
    
    import time
    start = time.time()
    response = requests.post(f"{MINICHECK_URL}/verify", json=input_data)
    duration_ms = (time.time() - start) * 1000
    
    result = response.json()
    print(f"\nResponse:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    # Assertions
    passed = True
    checks = []
    
    # Check label is ERROR
    if result.get("label") == "ERROR":
        checks.append("label=ERROR: PASS")
    else:
        checks.append(f"label=ERROR: FAIL (got {result.get('label')})")
        passed = False
    
    print("\nChecks:")
    for c in checks:
        print(f"  - {c}")
    
    print(f"\nResult: {'PASSED' if passed else 'FAILED'}")
    return log_result("test_empty_evidence", input_data, result, passed, duration_ms)

def main():
    """Run all tests and save results"""
    print("="*60)
    print("MINICHECK FIX - UNIT TEST")
    print(f"Target: {MINICHECK_URL}")
    print("="*60)
    
    # Check server health
    try:
        health = requests.get(f"{MINICHECK_URL}/health", timeout=5)
        health_data = health.json()
        print(f"\nServer Status: {health_data.get('status')}")
        print(f"Model Loaded: {health_data.get('model_loaded')}")
        
        if not health_data.get('model_loaded'):
            print("\nWARNING: Model not loaded. First test will be slow.")
    except Exception as e:
        print(f"\nERROR: Cannot connect to MiniCheck server: {e}")
        print("Please start the server first: python minicheck_server.py")
        return
    
    # Run tests
    results = []
    
    results.append(test_single_evidence())
    results.append(test_multiple_evidences())
    results.append(test_negation_detection())
    results.append(test_empty_evidence())
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    total = len(results)
    passed = sum(1 for r in results if r["passed"])
    failed = total - passed
    
    print(f"Total Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Success Rate: {passed/total*100:.1f}%")
    
    # Save results to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"d:/bmad/tests/minicheck_fix_results_{timestamp}.json"
    
    output = {
        "test_name": "minicheck_fix_unit_test",
        "timestamp": datetime.now().isoformat(),
        "server_url": MINICHECK_URL,
        "total_tests": total,
        "passed": passed,
        "failed": failed,
        "test_cases": results
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"\nResults saved to: {output_file}")
    
    if failed > 0:
        print("\n*** SOME TESTS FAILED - Please review ***")
        return False
    else:
        print("\n*** ALL TESTS PASSED ***")
        return True

if __name__ == "__main__":
    main()
