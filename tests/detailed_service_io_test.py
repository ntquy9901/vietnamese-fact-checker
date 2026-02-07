"""
Vietnamese Fact Checker - Detailed Service I/O Test
====================================================
Logs input/output of EACH service for root cause analysis.
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Optional

# Service endpoints
SERVICES = {
    "brave_search": "http://localhost:8004",
    "translation": "http://localhost:8003", 
    "minicheck": "http://localhost:8002",
    "fact_checker": "http://localhost:8005"
}

class DetailedServiceLogger:
    """Logs detailed I/O for each service call."""
    
    def __init__(self):
        self.logs = []
        
    def log(self, service: str, action: str, input_data: dict, output_data: dict, 
            duration_ms: float, success: bool, error: str = None):
        self.logs.append({
            "timestamp": datetime.now().isoformat(),
            "service": service,
            "action": action,
            "input": input_data,
            "output": output_data,
            "duration_ms": round(duration_ms, 2),
            "success": success,
            "error": error
        })
        
    def save(self, filename: str):
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.logs, f, ensure_ascii=False, indent=2)
        print(f"Saved {len(self.logs)} logs to {filename}")


def test_translation(text: str, source_lang: str, target_lang: str, logger: DetailedServiceLogger) -> Optional[str]:
    """Test Translation service and log I/O."""
    url = f"{SERVICES['translation']}/translate"
    input_data = {
        "text": text,
        "source_lang": source_lang,
        "target_lang": target_lang
    }
    
    start = time.time()
    try:
        response = requests.post(url, json=input_data, timeout=30)
        duration_ms = (time.time() - start) * 1000
        
        if response.status_code == 200:
            output = response.json()
            logger.log("translation", "translate", input_data, output, duration_ms, True)
            # VinAI translation returns 'english' key
            return output.get("english") or output.get("translated_text") or output.get("translation")
        else:
            logger.log("translation", "translate", input_data, 
                      {"status_code": response.status_code, "text": response.text[:500]}, 
                      duration_ms, False, f"HTTP {response.status_code}")
            return None
    except Exception as e:
        duration_ms = (time.time() - start) * 1000
        logger.log("translation", "translate", input_data, {}, duration_ms, False, str(e))
        return None


def test_brave_search(query: str, logger: DetailedServiceLogger) -> Optional[List[dict]]:
    """Test Brave Search service and log I/O."""
    url = f"{SERVICES['brave_search']}/search"
    input_data = {"query": query, "count": 5}
    
    start = time.time()
    try:
        response = requests.post(url, json=input_data, timeout=30)
        duration_ms = (time.time() - start) * 1000
        
        if response.status_code == 200:
            output = response.json()
            logger.log("brave_search", "search", input_data, output, duration_ms, True)
            return output.get("results", [])
        else:
            logger.log("brave_search", "search", input_data,
                      {"status_code": response.status_code, "text": response.text[:500]},
                      duration_ms, False, f"HTTP {response.status_code}")
            return None
    except Exception as e:
        duration_ms = (time.time() - start) * 1000
        logger.log("brave_search", "search", input_data, {}, duration_ms, False, str(e))
        return None


def test_minicheck(claim: str, evidence: str, logger: DetailedServiceLogger) -> Optional[float]:
    """Test MiniCheck service and log I/O."""
    url = f"{SERVICES['minicheck']}/verify"
    # MiniCheck API expects evidence as List[str]
    input_data = {"claim": claim, "evidence": [evidence]}
    
    start = time.time()
    try:
        response = requests.post(url, json=input_data, timeout=30)
        duration_ms = (time.time() - start) * 1000
        
        if response.status_code == 200:
            output = response.json()
            logger.log("minicheck", "verify", input_data, output, duration_ms, True)
            return output.get("score")
        else:
            logger.log("minicheck", "verify", input_data,
                      {"status_code": response.status_code, "text": response.text[:500]},
                      duration_ms, False, f"HTTP {response.status_code}")
            return None
    except Exception as e:
        duration_ms = (time.time() - start) * 1000
        logger.log("minicheck", "verify", input_data, {}, duration_ms, False, str(e))
        return None


def test_full_pipeline(claim: str, logger: DetailedServiceLogger) -> dict:
    """Test full fact-check pipeline with detailed logging of each step."""
    
    pipeline_result = {
        "claim": claim,
        "steps": []
    }
    
    # Step 1: Translate claim VI -> EN
    print(f"\n  [1] Translating claim to English...")
    claim_en = test_translation(claim, "vi", "en", logger)
    pipeline_result["steps"].append({
        "step": "translate_claim",
        "input": claim,
        "output": claim_en
    })
    
    if not claim_en:
        claim_en = claim  # Fallback to original
        print(f"      Translation failed, using original claim")
    else:
        print(f"      EN: {claim_en}")
    
    # Step 2: Search for evidence
    print(f"  [2] Searching for evidence...")
    search_results = test_brave_search(claim_en, logger)
    pipeline_result["steps"].append({
        "step": "brave_search",
        "input": claim_en,
        "output": search_results
    })
    
    if not search_results:
        print(f"      No search results found")
        pipeline_result["error"] = "No search results"
        return pipeline_result
    
    print(f"      Found {len(search_results)} results")
    
    # Step 3: For each result, translate and verify with MiniCheck
    minicheck_scores = []
    for i, result in enumerate(search_results[:3]):  # Test top 3
        title = result.get("title", "")
        snippet = result.get("description", "") or result.get("snippet", "")
        evidence = f"{title}. {snippet}"
        
        print(f"  [3.{i+1}] Processing evidence {i+1}...")
        print(f"        Original: {evidence[:100]}...")
        
        # Translate evidence to English (if not already)
        evidence_en = test_translation(evidence, "vi", "en", logger)
        if not evidence_en:
            evidence_en = evidence
        else:
            print(f"        Translated: {evidence_en[:100]}...")
        
        # Verify with MiniCheck
        score = test_minicheck(claim_en, evidence_en, logger)
        if score is not None:
            minicheck_scores.append({
                "evidence": evidence,
                "evidence_en": evidence_en,
                "score": score
            })
            print(f"        MiniCheck score: {score:.4f}")
    
    pipeline_result["steps"].append({
        "step": "minicheck_verification",
        "scores": minicheck_scores
    })
    
    # Calculate final verdict
    if minicheck_scores:
        max_score = max(s["score"] for s in minicheck_scores)
        if max_score >= 0.5:
            verdict = "SUPPORTED"
        elif max_score <= 0.3:
            verdict = "REFUTED"
        else:
            verdict = "NEITHER"
        
        pipeline_result["verdict"] = verdict
        pipeline_result["confidence"] = max_score
        pipeline_result["best_evidence"] = max(minicheck_scores, key=lambda x: x["score"])
    
    return pipeline_result


# Test claims (subset for detailed analysis)
TEST_CLAIMS = [
    # Correct predictions (for comparison)
    ("Ha Noi la thu do cua Viet Nam", "SUPPORTED"),
    # Wrong predictions (focus on these)
    ("Viet Nam co duong bien gioi voi Trung Quoc, Lao va Campuchia", "SUPPORTED"),
    ("Viet Nam co che do da dang", "REFUTED"),
    ("Viet Nam da tham du World Cup bong da nam", "REFUTED"),
    ("Ao dai la quoc phuc cua Viet Nam", "SUPPORTED"),
    ("Viet Nam giap bien gioi voi Thai Lan", "REFUTED"),
]

# Vietnamese test claims
TEST_CLAIMS_VI = [
    ("Hà Nội là thủ đô của Việt Nam", "SUPPORTED"),
    ("Việt Nam có đường biên giới với Trung Quốc, Lào và Campuchia", "SUPPORTED"),
    ("Việt Nam có chế độ đa đảng", "REFUTED"),
    ("Việt Nam đã tham dự World Cup bóng đá nam", "REFUTED"),
    ("Áo dài là quốc phục của Việt Nam", "SUPPORTED"),
    ("Việt Nam giáp biên giới với Thái Lan", "REFUTED"),
]


def main():
    print("=" * 70)
    print("DETAILED SERVICE I/O TEST")
    print("=" * 70)
    
    logger = DetailedServiceLogger()
    results = []
    
    for i, (claim, expected) in enumerate(TEST_CLAIMS_VI):
        print(f"\n{'=' * 70}")
        print(f"[{i+1}/{len(TEST_CLAIMS_VI)}] Testing: {claim}")
        print(f"Expected: {expected}")
        print("-" * 70)
        
        result = test_full_pipeline(claim, logger)
        result["expected"] = expected
        result["is_correct"] = result.get("verdict") == expected
        results.append(result)
        
        print("-" * 70)
        if "verdict" in result:
            status = "CORRECT" if result["is_correct"] else "WRONG"
            print(f"Result: {result['verdict']} (confidence: {result.get('confidence', 0):.4f}) - {status}")
        else:
            print(f"Result: ERROR - {result.get('error', 'Unknown')}")
    
    # Save detailed logs
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = f"d:/bmad/tests/detailed_service_io_{timestamp}.json"
    logger.save(log_file)
    
    # Save pipeline results
    results_file = f"d:/bmad/tests/pipeline_results_{timestamp}.json"
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\nPipeline results saved to: {results_file}")
    
    print("\n" + "=" * 70)
    print("TEST COMPLETE")
    print("=" * 70)
    print(f"\nDetailed service I/O logs: {log_file}")
    print(f"Pipeline results: {results_file}")


if __name__ == "__main__":
    main()
