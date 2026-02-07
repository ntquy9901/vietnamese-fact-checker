"""
Vietnamese Fact Checker - Simple Test
======================================
Just calls the Fact Checker service and logs full response for debugging.
The Fact Checker internally calls: Brave Search, Translation, MiniCheck.
"""

import requests
import json
from datetime import datetime

FACT_CHECKER_URL = "http://localhost:8005"

# Test claims - focus on wrong predictions from earlier tests
TEST_CLAIMS = [
    # Should work correctly
    ("Hà Nội là thủ đô của Việt Nam", "SUPPORTED"),
    # Previously wrong predictions  
    ("Việt Nam có đường biên giới với Trung Quốc, Lào và Campuchia", "SUPPORTED"),
    ("Việt Nam có chế độ đa đảng", "REFUTED"),
    ("Việt Nam đã tham dự World Cup bóng đá nam", "REFUTED"),
    ("Áo dài là quốc phục của Việt Nam", "SUPPORTED"),
    ("Việt Nam giáp biên giới với Thái Lan", "REFUTED"),
]


def check_fact(claim: str) -> dict:
    """Call Fact Checker API."""
    try:
        response = requests.post(
            f"{FACT_CHECKER_URL}/check",
            json={"claim": claim},
            timeout=120  # Longer timeout for full pipeline
        )
        print(f"  API Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            # Debug: print raw response structure
            print(f"  Response keys: {list(result.keys())}")
            return result
        else:
            print(f"  Error response: {response.text[:500]}")
            return {"error": f"HTTP {response.status_code}", "text": response.text[:500]}
    except Exception as e:
        print(f"  Exception: {str(e)}")
        return {"error": str(e)}


def main():
    print("=" * 80)
    print("VIETNAMESE FACT CHECKER - SIMPLE TEST")
    print("=" * 80)
    print(f"Endpoint: {FACT_CHECKER_URL}/check")
    print(f"Time: {datetime.now().isoformat()}")
    print("=" * 80)
    
    results = []
    
    for i, (claim, expected) in enumerate(TEST_CLAIMS):
        print(f"\n[{i+1}/{len(TEST_CLAIMS)}] Testing: {claim[:60]}...")
        print(f"Expected: {expected}")
        print("-" * 80)
        
        result = check_fact(claim)
        result["claim"] = claim
        result["expected"] = expected
        
        # Check if error field exists AND is not None/empty
        if not result.get("error"):
            verdict = result.get("verdict", "UNKNOWN")
            confidence = result.get("confidence", 0)
            is_correct = verdict == expected
            result["is_correct"] = is_correct
            
            status = " CORRECT" if is_correct else " WRONG"
            print(f"Verdict: {verdict} (confidence: {confidence:.4f}) {status}")
            
            # Print evidence details
            if "evidence" in result:
                print(f"\nEvidence ({len(result['evidence'])} items):")
                for j, ev in enumerate(result["evidence"][:3]):
                    score = ev.get('score', 0)
                    if isinstance(score, (int, float)):
                        print(f"  [{j+1}] Score: {score:.4f}")
                    else:
                        print(f"  [{j+1}] Score: {score}")
                    print(f"      VI: {str(ev.get('text', ''))[:100]}...")
                    if ev.get('text_en'):
                        print(f"      EN: {str(ev.get('text_en', ''))[:100]}...")
        else:
            print(f"ERROR: {result['error']}")
            result["is_correct"] = False
        
        results.append(result)
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    correct = sum(1 for r in results if r.get("is_correct", False))
    total = len(results)
    print(f"Accuracy: {correct}/{total} ({100*correct/total:.1f}%)")
    
    print("\nWrong predictions:")
    for r in results:
        if not r.get("is_correct", False) and "error" not in r:
            print(f"  - {r['claim'][:50]}...")
            print(f"    Expected: {r['expected']} | Got: {r.get('verdict', 'N/A')}")
    
    # Save full results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"d:/bmad/tests/factchecker_results_{timestamp}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\nFull results saved to: {output_file}")
    print("=" * 80)


if __name__ == "__main__":
    main()
