#!/usr/bin/env python3
"""
Integration Test with Detailed Service I/O Logging

This test calls individual services directly to capture ALL input/output
for debugging and root cause analysis.

Services:
- Brave Search (8004): Search Vietnamese web
- Translation (8003): VI -> EN
- MiniCheck (8002): Fact verification
- Fact Checker (8005): Orchestrator
"""

import requests
import json
from datetime import datetime
from typing import List, Dict, Optional
import time

# Service URLs
SERVICES = {
    "brave_search": "http://localhost:8004",
    "translation": "http://localhost:8003",
    "minicheck": "http://localhost:8002",
    "fact_checker": "http://localhost:8005"
}

# Load test dataset
DATASET_FILE = "d:/bmad/tests/test_dataset.json"


def load_dataset() -> List[dict]:
    """Load test cases from JSON file"""
    with open(DATASET_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data['test_cases']


def call_brave_search(query: str, timeout: int = 30) -> dict:
    """Call Brave Search service directly"""
    start = time.time()
    try:
        response = requests.post(
            f"{SERVICES['brave_search']}/search",
            json={"query": query, "count": 5},
            timeout=timeout
        )
        result = response.json()
        return {
            "success": True,
            "input": {"query": query, "count": 5},
            "output": result,
            "duration_ms": (time.time() - start) * 1000
        }
    except Exception as e:
        return {
            "success": False,
            "input": {"query": query},
            "output": None,
            "error": str(e),
            "duration_ms": (time.time() - start) * 1000
        }


def call_translation(text: str, timeout: int = 30) -> dict:
    """Call Translation service directly"""
    start = time.time()
    try:
        response = requests.post(
            f"{SERVICES['translation']}/translate",
            json={"text": text, "source_lang": "vie_Latn", "target_lang": "eng_Latn"},
            timeout=timeout
        )
        result = response.json()
        return {
            "success": True,
            "input": {"text": text},
            "output": result,
            "duration_ms": (time.time() - start) * 1000
        }
    except Exception as e:
        return {
            "success": False,
            "input": {"text": text},
            "output": None,
            "error": str(e),
            "duration_ms": (time.time() - start) * 1000
        }


def call_minicheck(claim: str, evidence: List[str], timeout: int = 60) -> dict:
    """Call MiniCheck service directly"""
    start = time.time()
    try:
        response = requests.post(
            f"{SERVICES['minicheck']}/verify",
            json={"claim": claim, "evidence": evidence},
            timeout=timeout
        )
        result = response.json()
        return {
            "success": True,
            "input": {"claim": claim, "evidence": evidence},
            "output": result,
            "duration_ms": (time.time() - start) * 1000
        }
    except Exception as e:
        return {
            "success": False,
            "input": {"claim": claim, "evidence": evidence},
            "output": None,
            "error": str(e),
            "duration_ms": (time.time() - start) * 1000
        }


def call_fact_checker(claim: str, timeout: int = 120) -> dict:
    """Call Fact Checker orchestrator"""
    start = time.time()
    try:
        response = requests.post(
            f"{SERVICES['fact_checker']}/check",
            json={"claim": claim},
            timeout=timeout
        )
        result = response.json()
        return {
            "success": True,
            "input": {"claim": claim},
            "output": result,
            "duration_ms": (time.time() - start) * 1000
        }
    except Exception as e:
        return {
            "success": False,
            "input": {"claim": claim},
            "output": None,
            "error": str(e),
            "duration_ms": (time.time() - start) * 1000
        }


def run_detailed_test(test_case: dict) -> dict:
    """
    Run a single test case with detailed I/O logging for each service.
    
    Pipeline:
    1. Brave Search (Vietnamese query)
    2. Translation (claim + evidence VI -> EN)
    3. MiniCheck (English claim + evidence)
    4. Also call Fact Checker orchestrator for comparison
    """
    claim = test_case['claim']
    test_id = test_case['id']
    
    print(f"\n{'='*70}")
    print(f"[{test_id}] {claim}")
    print(f"Expected: {test_case['expected']} | Difficulty: {test_case['difficulty']}")
    print(f"{'='*70}")
    
    service_logs = {}
    
    # Step 1: Brave Search
    print("\n[1] BRAVE SEARCH...")
    search_result = call_brave_search(claim)
    service_logs['brave_search'] = search_result
    
    if search_result['success']:
        results = search_result['output'].get('results', [])
        print(f"    Found {len(results)} results")
        for i, r in enumerate(results[:3]):
            print(f"    [{i}] {r.get('title', 'N/A')[:50]}...")
    else:
        print(f"    ERROR: {search_result.get('error')}")
    
    # Extract evidence texts
    evidence_vi = []
    if search_result['success']:
        for r in search_result['output'].get('results', [])[:5]:
            snippet = r.get('snippet', '')
            if snippet:
                evidence_vi.append(snippet)
    
    # Step 2: Translation (claim + evidence)
    print("\n[2] TRANSLATION...")
    translation_logs = []
    
    # Translate claim
    claim_trans = call_translation(claim)
    translation_logs.append({
        "type": "claim",
        "result": claim_trans
    })
    claim_en = claim_trans['output'].get('english', '') if claim_trans['success'] else claim
    print(f"    Claim VI: {claim[:50]}...")
    print(f"    Claim EN: {claim_en[:50]}...")
    
    # Translate evidence
    evidence_en = []
    for i, ev in enumerate(evidence_vi):
        ev_trans = call_translation(ev)
        translation_logs.append({
            "type": f"evidence_{i}",
            "result": ev_trans
        })
        if ev_trans['success']:
            evidence_en.append(ev_trans['output'].get('english', ev))
        else:
            evidence_en.append(ev)
    
    service_logs['translation'] = translation_logs
    print(f"    Translated {len(evidence_en)} evidence texts")
    
    # Step 3: MiniCheck
    print("\n[3] MINICHECK...")
    if evidence_en:
        minicheck_result = call_minicheck(claim_en, evidence_en)
        service_logs['minicheck'] = minicheck_result
        
        if minicheck_result['success']:
            output = minicheck_result['output']
            print(f"    Label: {output.get('label')}")
            print(f"    Score: {output.get('score', 0):.3f}")
            print(f"    Avg Score: {output.get('avg_score', 0):.3f}")
            print(f"    Evidence Count: {output.get('evidence_count', 0)}")
            
            # Show individual evidence scores
            all_scores = output.get('all_scores', [])
            for es in all_scores:
                print(f"      [{es['evidence_index']}] {es['label']}: {es['score']:.3f}")
        else:
            print(f"    ERROR: {minicheck_result.get('error')}")
    else:
        service_logs['minicheck'] = {
            "success": False,
            "error": "No evidence to verify"
        }
        print("    SKIPPED: No evidence")
    
    # Step 4: Fact Checker (orchestrator) for comparison
    print("\n[4] FACT CHECKER (orchestrator)...")
    fc_result = call_fact_checker(claim)
    service_logs['fact_checker'] = fc_result
    
    if fc_result['success']:
        output = fc_result['output']
        verdict = output.get('verdict', 'ERROR')
        confidence = output.get('confidence', 0)
        print(f"    Verdict: {verdict}")
        print(f"    Confidence: {confidence:.3f}")
    else:
        print(f"    ERROR: {fc_result.get('error')}")
        verdict = "ERROR"
        confidence = 0
    
    # Determine actual result
    actual = verdict
    is_correct = (actual == test_case['expected'])
    
    print(f"\n[RESULT] Expected: {test_case['expected']} | Actual: {actual} | {'CORRECT' if is_correct else 'WRONG'}")
    
    return {
        "test_case": test_case,
        "actual": actual,
        "confidence": confidence,
        "is_correct": is_correct,
        "service_logs": service_logs,
        "total_duration_ms": sum([
            service_logs.get('brave_search', {}).get('duration_ms', 0),
            sum(t['result'].get('duration_ms', 0) for t in service_logs.get('translation', [])),
            service_logs.get('minicheck', {}).get('duration_ms', 0),
            service_logs.get('fact_checker', {}).get('duration_ms', 0)
        ])
    }


def check_services_health() -> dict:
    """Check all services are running"""
    health = {}
    for name, url in SERVICES.items():
        try:
            resp = requests.get(f"{url}/health", timeout=5)
            health[name] = {
                "status": "healthy",
                "response": resp.json() if resp.status_code == 200 else None
            }
        except Exception as e:
            try:
                resp = requests.get(url, timeout=5)
                health[name] = {
                    "status": "healthy",
                    "response": resp.json() if resp.status_code == 200 else None
                }
            except Exception as e2:
                health[name] = {"status": "error", "error": str(e2)}
    return health


def main():
    """Run all tests with detailed logging"""
    print("="*70)
    print("INTEGRATION TEST - DETAILED SERVICE I/O LOGGING")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("="*70)
    
    # Check services
    print("\nChecking services...")
    health = check_services_health()
    for name, status in health.items():
        icon = "OK" if status['status'] == 'healthy' else "ERR"
        print(f"  [{icon}] {name}: {status['status']}")
    
    # Load dataset
    print(f"\nLoading dataset from: {DATASET_FILE}")
    test_cases = load_dataset()
    print(f"Loaded {len(test_cases)} test cases")
    
    # Run tests
    results = []
    stats = {
        "total": 0,
        "correct": 0,
        "wrong": 0,
        "error": 0,
        "by_domain": {},
        "by_difficulty": {}
    }
    
    for tc in test_cases:
        result = run_detailed_test(tc)
        results.append(result)
        
        # Update stats
        domain = tc['domain']
        difficulty = tc['difficulty']
        
        stats['total'] += 1
        if domain not in stats['by_domain']:
            stats['by_domain'][domain] = {"total": 0, "correct": 0}
        if difficulty not in stats['by_difficulty']:
            stats['by_difficulty'][difficulty] = {"total": 0, "correct": 0}
        
        stats['by_domain'][domain]['total'] += 1
        stats['by_difficulty'][difficulty]['total'] += 1
        
        if result['actual'] == "ERROR":
            stats['error'] += 1
        elif result['is_correct']:
            stats['correct'] += 1
            stats['by_domain'][domain]['correct'] += 1
            stats['by_difficulty'][difficulty]['correct'] += 1
        else:
            stats['wrong'] += 1
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    
    accuracy = stats['correct'] / stats['total'] * 100 if stats['total'] > 0 else 0
    print(f"\nOverall Accuracy: {stats['correct']}/{stats['total']} ({accuracy:.1f}%)")
    print(f"Errors: {stats['error']}")
    
    print("\nBy Domain:")
    for domain, ds in stats['by_domain'].items():
        acc = ds['correct'] / ds['total'] * 100 if ds['total'] > 0 else 0
        print(f"  {domain}: {ds['correct']}/{ds['total']} ({acc:.1f}%)")
    
    print("\nBy Difficulty:")
    for diff, ds in stats['by_difficulty'].items():
        acc = ds['correct'] / ds['total'] * 100 if ds['total'] > 0 else 0
        print(f"  {diff}: {ds['correct']}/{ds['total']} ({acc:.1f}%)")
    
    # Wrong predictions
    wrong = [r for r in results if not r['is_correct'] and r['actual'] != 'ERROR']
    if wrong:
        print(f"\nWrong Predictions ({len(wrong)}):")
        for w in wrong:
            tc = w['test_case']
            print(f"  - [{tc['id']}] {tc['claim'][:40]}...")
            print(f"    Expected: {tc['expected']}, Got: {w['actual']}")
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"d:/bmad/tests/integration_detailed_{timestamp}.json"
    
    output = {
        "test_name": "integration_test_detailed",
        "timestamp": datetime.now().isoformat(),
        "dataset_file": DATASET_FILE,
        "services": SERVICES,
        "services_health": health,
        "statistics": stats,
        "accuracy": accuracy,
        "test_results": results
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"\nResults saved to: {output_file}")
    print("\nThis file contains ALL input/output from every service for debugging.")
    
    return output


if __name__ == "__main__":
    main()
