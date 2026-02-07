"""
Vietnamese Fact Checker - Accuracy Analysis Test Suite
=======================================================
This script tests the fact checker with a comprehensive dataset and logs
all input/output from each service to identify accuracy bottlenecks.

Services tested:
1. Brave Search (8004) - Evidence retrieval
2. Translation (8003) - Vietnamese to English
3. MiniCheck (8002) - Fact verification
4. Fact Checker (8005) - Main orchestration
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum

# ============================================================================
# TEST DATASET - Comprehensive claims for accuracy analysis
# ============================================================================

class ClaimCategory(Enum):
    GEOGRAPHY = "geography"
    HISTORY = "history"
    POLITICS = "politics"
    ECONOMY = "economy"
    SCIENCE = "science"
    SPORTS = "sports"
    CULTURE = "culture"
    FALSE_CLAIMS = "false_claims"
    COMPLEX = "complex"
    NUMERIC = "numeric"

@dataclass
class TestClaim:
    claim: str
    expected_verdict: str  # SUPPORTED, REFUTED, NEI (Not Enough Info)
    category: ClaimCategory
    difficulty: str  # easy, medium, hard
    notes: str = ""

# Comprehensive test dataset
TEST_DATASET: List[TestClaim] = [
    # ========== GEOGRAPHY (Easy - should be highly accurate) ==========
    TestClaim(
        claim="Hà Nội là thủ đô của Việt Nam",
        expected_verdict="SUPPORTED",
        category=ClaimCategory.GEOGRAPHY,
        difficulty="easy",
        notes="Basic fact, should be 100% accurate"
    ),
    TestClaim(
        claim="Thành phố Hồ Chí Minh là thành phố lớn nhất Việt Nam về dân số",
        expected_verdict="SUPPORTED",
        category=ClaimCategory.GEOGRAPHY,
        difficulty="easy",
        notes="Well-known fact"
    ),
    TestClaim(
        claim="Việt Nam có đường biên giới với Trung Quốc, Lào và Campuchia",
        expected_verdict="SUPPORTED",
        category=ClaimCategory.GEOGRAPHY,
        difficulty="easy",
        notes="Basic geography"
    ),
    TestClaim(
        claim="Sông Mekong là con sông dài nhất Việt Nam",
        expected_verdict="REFUTED",
        category=ClaimCategory.GEOGRAPHY,
        difficulty="medium",
        notes="Mekong flows through VN but is not longest in VN (that's Red River or its tributaries)"
    ),
    
    # ========== HISTORY ==========
    TestClaim(
        claim="Việt Nam giành độc lập năm 1945",
        expected_verdict="SUPPORTED",
        category=ClaimCategory.HISTORY,
        difficulty="easy",
        notes="Declaration of Independence Sept 2, 1945"
    ),
    TestClaim(
        claim="Chiến thắng Điện Biên Phủ diễn ra năm 1954",
        expected_verdict="SUPPORTED",
        category=ClaimCategory.HISTORY,
        difficulty="easy",
        notes="May 7, 1954"
    ),
    TestClaim(
        claim="Việt Nam thống nhất năm 1976",
        expected_verdict="REFUTED",
        category=ClaimCategory.HISTORY,
        difficulty="medium",
        notes="Reunification was 1975, officially unified as SRV in 1976"
    ),
    
    # ========== POLITICS ==========
    TestClaim(
        claim="Việt Nam là thành viên của ASEAN",
        expected_verdict="SUPPORTED",
        category=ClaimCategory.POLITICS,
        difficulty="easy",
        notes="Joined ASEAN in 1995"
    ),
    TestClaim(
        claim="Việt Nam có chế độ đa đảng",
        expected_verdict="REFUTED",
        category=ClaimCategory.POLITICS,
        difficulty="easy",
        notes="Vietnam has single-party system"
    ),
    
    # ========== ECONOMY ==========
    TestClaim(
        claim="Việt Nam là một trong những nước xuất khẩu gạo lớn nhất thế giới",
        expected_verdict="SUPPORTED",
        category=ClaimCategory.ECONOMY,
        difficulty="easy",
        notes="Top 3 rice exporters globally"
    ),
    TestClaim(
        claim="GDP của Việt Nam năm 2023 vượt 400 tỷ USD",
        expected_verdict="SUPPORTED",
        category=ClaimCategory.ECONOMY,
        difficulty="medium",
        notes="GDP 2023 was around 430 billion USD"
    ),
    TestClaim(
        claim="Việt Nam là nền kinh tế lớn nhất Đông Nam Á",
        expected_verdict="REFUTED",
        category=ClaimCategory.ECONOMY,
        difficulty="medium",
        notes="Indonesia is largest, Vietnam is 4th-5th"
    ),
    
    # ========== SCIENCE ==========
    TestClaim(
        claim="Việt Nam đã phóng vệ tinh VNREDSat-1 vào năm 2013",
        expected_verdict="SUPPORTED",
        category=ClaimCategory.SCIENCE,
        difficulty="medium",
        notes="First Vietnamese Earth observation satellite"
    ),
    
    # ========== SPORTS ==========
    TestClaim(
        claim="Đội tuyển bóng đá Việt Nam đã vô địch AFF Cup 2018",
        expected_verdict="SUPPORTED",
        category=ClaimCategory.SPORTS,
        difficulty="easy",
        notes="Won AFF Suzuki Cup 2018"
    ),
    TestClaim(
        claim="Việt Nam đã tham dự World Cup bóng đá nam",
        expected_verdict="REFUTED",
        category=ClaimCategory.SPORTS,
        difficulty="easy",
        notes="Never qualified for FIFA World Cup"
    ),
    
    # ========== CULTURE ==========
    TestClaim(
        claim="Phở là món ăn truyền thống của Việt Nam",
        expected_verdict="SUPPORTED",
        category=ClaimCategory.CULTURE,
        difficulty="easy",
        notes="Iconic Vietnamese dish"
    ),
    TestClaim(
        claim="Áo dài là quốc phục của Việt Nam",
        expected_verdict="SUPPORTED",
        category=ClaimCategory.CULTURE,
        difficulty="easy",
        notes="Traditional national costume"
    ),
    
    # ========== FALSE CLAIMS (should be REFUTED) ==========
    TestClaim(
        claim="Đà Nẵng là thủ đô của Việt Nam",
        expected_verdict="REFUTED",
        category=ClaimCategory.FALSE_CLAIMS,
        difficulty="easy",
        notes="Obviously false, Hanoi is capital"
    ),
    TestClaim(
        claim="Việt Nam có dân số hơn 200 triệu người",
        expected_verdict="REFUTED",
        category=ClaimCategory.FALSE_CLAIMS,
        difficulty="easy",
        notes="Population is ~100 million"
    ),
    TestClaim(
        claim="Việt Nam giáp biên giới với Thái Lan",
        expected_verdict="REFUTED",
        category=ClaimCategory.FALSE_CLAIMS,
        difficulty="easy",
        notes="No direct border with Thailand"
    ),
    
    # ========== COMPLEX CLAIMS (multi-fact) ==========
    TestClaim(
        claim="Việt Nam có dân số đông thứ 3 Đông Nam Á sau Indonesia và Philippines",
        expected_verdict="SUPPORTED",
        category=ClaimCategory.COMPLEX,
        difficulty="hard",
        notes="Requires comparing multiple countries"
    ),
    TestClaim(
        claim="Vịnh Hạ Long được UNESCO công nhận là Di sản Thế giới",
        expected_verdict="SUPPORTED",
        category=ClaimCategory.COMPLEX,
        difficulty="medium",
        notes="UNESCO World Heritage Site since 1994"
    ),
    
    # ========== NUMERIC CLAIMS ==========
    TestClaim(
        claim="Việt Nam có 63 tỉnh thành",
        expected_verdict="SUPPORTED",
        category=ClaimCategory.NUMERIC,
        difficulty="medium",
        notes="58 provinces + 5 municipalities"
    ),
    TestClaim(
        claim="Núi Fansipan cao 3143 mét",
        expected_verdict="SUPPORTED",
        category=ClaimCategory.NUMERIC,
        difficulty="medium",
        notes="Exact height is 3,147.3m, close enough"
    ),
]

# ============================================================================
# SERVICE CLIENTS WITH DETAILED LOGGING
# ============================================================================

class ServiceLogger:
    def __init__(self):
        self.logs = []
        
    def log(self, service: str, action: str, input_data: any, output_data: any, 
            duration_ms: float, success: bool, error: str = None):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "service": service,
            "action": action,
            "input": input_data,
            "output": output_data,
            "duration_ms": round(duration_ms, 2),
            "success": success,
            "error": error
        }
        self.logs.append(entry)
        return entry

logger = ServiceLogger()

def test_brave_search(query: str) -> Dict:
    """Test Brave Search service directly"""
    url = "http://localhost:8004/search"
    start = time.time()
    try:
        response = requests.post(url, json={"query": query}, timeout=30)
        duration = (time.time() - start) * 1000
        
        if response.status_code == 200:
            result = response.json()
            logger.log(
                service="brave_search",
                action="search",
                input_data={"query": query},
                output_data={
                    "num_results": len(result.get("results", [])),
                    "results_preview": [
                        {"title": r.get("title", "")[:50], "url": r.get("url", "")}
                        for r in result.get("results", [])[:3]
                    ]
                },
                duration_ms=duration,
                success=True
            )
            return result
        else:
            logger.log(
                service="brave_search",
                action="search",
                input_data={"query": query},
                output_data=None,
                duration_ms=duration,
                success=False,
                error=f"HTTP {response.status_code}: {response.text[:200]}"
            )
            return {"results": [], "error": response.text}
    except Exception as e:
        duration = (time.time() - start) * 1000
        logger.log(
            service="brave_search",
            action="search",
            input_data={"query": query},
            output_data=None,
            duration_ms=duration,
            success=False,
            error=str(e)
        )
        return {"results": [], "error": str(e)}

def test_translation(text: str) -> Dict:
    """Test Translation service directly"""
    url = "http://localhost:8003/translate"
    start = time.time()
    try:
        response = requests.post(url, json={"text": text}, timeout=30)
        duration = (time.time() - start) * 1000
        
        if response.status_code == 200:
            result = response.json()
            logger.log(
                service="translation",
                action="translate_vi_to_en",
                input_data={"vietnamese": text[:100] + "..." if len(text) > 100 else text},
                output_data={"english": result.get("english", "")[:100]},
                duration_ms=duration,
                success=True
            )
            return result
        else:
            logger.log(
                service="translation",
                action="translate_vi_to_en",
                input_data={"vietnamese": text[:100]},
                output_data=None,
                duration_ms=duration,
                success=False,
                error=f"HTTP {response.status_code}"
            )
            return {"english": text, "error": response.text}
    except Exception as e:
        duration = (time.time() - start) * 1000
        logger.log(
            service="translation",
            action="translate_vi_to_en",
            input_data={"vietnamese": text[:100]},
            output_data=None,
            duration_ms=duration,
            success=False,
            error=str(e)
        )
        return {"english": text, "error": str(e)}

def test_minicheck(claim: str, evidence: str) -> Dict:
    """Test MiniCheck service directly"""
    url = "http://localhost:8002/check"
    start = time.time()
    try:
        response = requests.post(
            url, 
            json={"claim": claim, "evidence": evidence}, 
            timeout=60
        )
        duration = (time.time() - start) * 1000
        
        if response.status_code == 200:
            result = response.json()
            logger.log(
                service="minicheck",
                action="verify",
                input_data={
                    "claim": claim[:80] + "..." if len(claim) > 80 else claim,
                    "evidence": evidence[:80] + "..." if len(evidence) > 80 else evidence
                },
                output_data={
                    "label": result.get("label"),
                    "score": result.get("score")
                },
                duration_ms=duration,
                success=True
            )
            return result
        else:
            logger.log(
                service="minicheck",
                action="verify",
                input_data={"claim": claim[:80], "evidence": evidence[:80]},
                output_data=None,
                duration_ms=duration,
                success=False,
                error=f"HTTP {response.status_code}"
            )
            return {"label": "ERROR", "score": 0.0, "error": response.text}
    except Exception as e:
        duration = (time.time() - start) * 1000
        logger.log(
            service="minicheck",
            action="verify",
            input_data={"claim": claim[:80], "evidence": evidence[:80]},
            output_data=None,
            duration_ms=duration,
            success=False,
            error=str(e)
        )
        return {"label": "ERROR", "score": 0.0, "error": str(e)}

def test_fact_checker(claim: str) -> Dict:
    """Test the full Fact Checker pipeline"""
    url = "http://localhost:8005/check"
    start = time.time()
    try:
        response = requests.post(url, json={"claim": claim}, timeout=120)
        duration = (time.time() - start) * 1000
        
        if response.status_code == 200:
            result = response.json()
            logger.log(
                service="fact_checker",
                action="full_pipeline",
                input_data={"claim": claim},
                output_data={
                    "verdict": result.get("verdict"),
                    "confidence": result.get("confidence"),
                    "evidence_count": len(result.get("evidence", []))
                },
                duration_ms=duration,
                success=True
            )
            return result
        else:
            logger.log(
                service="fact_checker",
                action="full_pipeline",
                input_data={"claim": claim},
                output_data=None,
                duration_ms=duration,
                success=False,
                error=f"HTTP {response.status_code}: {response.text[:200]}"
            )
            return {"verdict": "ERROR", "confidence": 0.0, "error": response.text}
    except Exception as e:
        duration = (time.time() - start) * 1000
        logger.log(
            service="fact_checker",
            action="full_pipeline",
            input_data={"claim": claim},
            output_data=None,
            duration_ms=duration,
            success=False,
            error=str(e)
        )
        return {"verdict": "ERROR", "confidence": 0.0, "error": str(e)}

# ============================================================================
# ANALYSIS FUNCTIONS
# ============================================================================

@dataclass
class TestResult:
    claim: TestClaim
    actual_verdict: str
    confidence: float
    is_correct: bool
    duration_ms: float
    error: Optional[str]
    debug_info: Dict

def run_single_test(test_claim: TestClaim) -> TestResult:
    """Run a single test and collect all service I/O"""
    print(f"\n{'='*70}")
    print(f"Testing: {test_claim.claim[:60]}...")
    print(f"Category: {test_claim.category.value} | Difficulty: {test_claim.difficulty}")
    print(f"Expected: {test_claim.expected_verdict}")
    print("-"*70)
    
    start = time.time()
    result = test_fact_checker(test_claim.claim)
    duration = (time.time() - start) * 1000
    
    actual_verdict = result.get("verdict", "ERROR")
    confidence = result.get("confidence", 0.0)
    
    # Normalize verdicts for comparison
    def normalize_verdict(v):
        v = str(v).upper()
        if v in ["SUPPORTED", "TRUE", "SUPPORT"]:
            return "SUPPORTED"
        elif v in ["REFUTED", "FALSE", "REFUTE", "NOT_SUPPORTED"]:
            return "REFUTED"
        else:
            return "NEI"
    
    is_correct = normalize_verdict(actual_verdict) == normalize_verdict(test_claim.expected_verdict)
    
    print(f"Actual: {actual_verdict} (confidence: {confidence:.4f})")
    print(f"Result: {' CORRECT' if is_correct else ' WRONG'}")
    
    return TestResult(
        claim=test_claim,
        actual_verdict=actual_verdict,
        confidence=confidence,
        is_correct=is_correct,
        duration_ms=duration,
        error=result.get("error"),
        debug_info=result.get("debug", {})
    )

def analyze_results(results: List[TestResult]):
    """Analyze test results to identify accuracy issues"""
    print("\n" + "="*70)
    print("ACCURACY ANALYSIS REPORT")
    print("="*70)
    
    # Overall accuracy
    total = len(results)
    correct = sum(1 for r in results if r.is_correct)
    accuracy = correct / total * 100 if total > 0 else 0
    
    print(f"\n## Overall Accuracy: {correct}/{total} ({accuracy:.1f}%)")
    
    # Accuracy by category
    print("\n## Accuracy by Category:")
    categories = {}
    for r in results:
        cat = r.claim.category.value
        if cat not in categories:
            categories[cat] = {"correct": 0, "total": 0}
        categories[cat]["total"] += 1
        if r.is_correct:
            categories[cat]["correct"] += 1
    
    for cat, stats in sorted(categories.items()):
        cat_acc = stats["correct"] / stats["total"] * 100
        print(f"  - {cat}: {stats['correct']}/{stats['total']} ({cat_acc:.1f}%)")
    
    # Accuracy by difficulty
    print("\n## Accuracy by Difficulty:")
    difficulties = {}
    for r in results:
        diff = r.claim.difficulty
        if diff not in difficulties:
            difficulties[diff] = {"correct": 0, "total": 0}
        difficulties[diff]["total"] += 1
        if r.is_correct:
            difficulties[diff]["correct"] += 1
    
    for diff in ["easy", "medium", "hard"]:
        if diff in difficulties:
            stats = difficulties[diff]
            diff_acc = stats["correct"] / stats["total"] * 100
            print(f"  - {diff}: {stats['correct']}/{stats['total']} ({diff_acc:.1f}%)")
    
    # Wrong predictions analysis
    wrong_results = [r for r in results if not r.is_correct]
    if wrong_results:
        print(f"\n## Wrong Predictions ({len(wrong_results)} cases):")
        for r in wrong_results:
            print(f"\n  Claim: {r.claim.claim[:60]}...")
            print(f"  Expected: {r.claim.expected_verdict} | Got: {r.actual_verdict}")
            print(f"  Confidence: {r.confidence:.4f}")
            print(f"  Notes: {r.claim.notes}")
    
    # Service-level analysis from logs
    print("\n## Service Performance Analysis:")
    service_stats = {}
    for log in logger.logs:
        svc = log["service"]
        if svc not in service_stats:
            service_stats[svc] = {
                "total_calls": 0,
                "success": 0,
                "failed": 0,
                "total_duration_ms": 0,
                "errors": []
            }
        service_stats[svc]["total_calls"] += 1
        service_stats[svc]["total_duration_ms"] += log["duration_ms"]
        if log["success"]:
            service_stats[svc]["success"] += 1
        else:
            service_stats[svc]["failed"] += 1
            if log["error"]:
                service_stats[svc]["errors"].append(log["error"][:100])
    
    for svc, stats in service_stats.items():
        avg_duration = stats["total_duration_ms"] / stats["total_calls"] if stats["total_calls"] > 0 else 0
        success_rate = stats["success"] / stats["total_calls"] * 100 if stats["total_calls"] > 0 else 0
        print(f"\n  {svc.upper()}:")
        print(f"    - Calls: {stats['total_calls']}")
        print(f"    - Success rate: {success_rate:.1f}%")
        print(f"    - Avg duration: {avg_duration:.0f}ms")
        if stats["errors"]:
            print(f"    - Sample errors: {stats['errors'][:2]}")
    
    return {
        "overall_accuracy": accuracy,
        "by_category": categories,
        "by_difficulty": difficulties,
        "wrong_count": len(wrong_results),
        "service_stats": service_stats
    }

def save_detailed_logs(results: List[TestResult], analysis: Dict, filename: str):
    """Save detailed logs to JSON file"""
    output = {
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "total_tests": len(results),
            "accuracy": analysis["overall_accuracy"],
            "by_category": analysis["by_category"],
            "by_difficulty": analysis["by_difficulty"]
        },
        "service_logs": logger.logs,
        "test_results": [
            {
                "claim": r.claim.claim,
                "category": r.claim.category.value,
                "difficulty": r.claim.difficulty,
                "expected": r.claim.expected_verdict,
                "actual": r.actual_verdict,
                "confidence": r.confidence,
                "is_correct": r.is_correct,
                "duration_ms": r.duration_ms,
                "error": r.error
            }
            for r in results
        ]
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\nDetailed logs saved to: {filename}")

# ============================================================================
# MAIN
# ============================================================================

def main():
    print("="*70)
    print("VIETNAMESE FACT CHECKER - ACCURACY ANALYSIS TEST")
    print("="*70)
    print(f"Dataset size: {len(TEST_DATASET)} claims")
    print(f"Start time: {datetime.now().isoformat()}")
    
    # Check services
    print("\nChecking services...")
    services = [
        ("MiniCheck", "http://localhost:8002/health"),
        ("Translation", "http://localhost:8003/health"),
        ("Brave Search", "http://localhost:8004/health"),
        ("Fact Checker", "http://localhost:8005/health"),
    ]
    
    all_up = True
    for name, url in services:
        try:
            r = requests.get(url, timeout=5)
            status = " UP" if r.status_code == 200 else f" {r.status_code}"
        except:
            status = " DOWN"
            all_up = False
        print(f"  {name}: {status}")
    
    if not all_up:
        print("\nWARNING: Some services are down. Results may be incomplete.")
    
    # Run tests
    print("\n" + "="*70)
    print("RUNNING TESTS")
    print("="*70)
    
    results = []
    for i, test_claim in enumerate(TEST_DATASET, 1):
        print(f"\n[{i}/{len(TEST_DATASET)}]", end="")
        result = run_single_test(test_claim)
        results.append(result)
        
        # Small delay between tests to avoid rate limiting
        time.sleep(1)
    
    # Analyze results
    analysis = analyze_results(results)
    
    # Save detailed logs
    log_file = f"d:/bmad/tests/accuracy_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    save_detailed_logs(results, analysis, log_file)
    
    print("\n" + "="*70)
    print("TEST COMPLETE")
    print("="*70)
    
    return results, analysis

if __name__ == "__main__":
    results, analysis = main()
