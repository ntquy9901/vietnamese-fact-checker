#!/usr/bin/env python3
"""
Integration Test v2 - Vietnamese Fact Checker
Test with diverse dataset: 5 domains x 5 claims = 25 test cases

Domains:
1. Geography (Địa lý)
2. History (Lịch sử)
3. Politics (Chính trị)
4. Culture (Văn hóa)
5. Sports (Thể thao)
"""

import requests
import json
from datetime import datetime
from typing import List, Dict
import time

FACT_CHECKER_URL = "http://localhost:8005"

# Dataset: 5 domains x 5 claims
TEST_DATASET = {
    "geography": [
        {
            "claim": "Hà Nội là thủ đô của Việt Nam",
            "expected": "SUPPORTED",
            "difficulty": "easy",
            "note": "Basic geographic fact"
        },
        {
            "claim": "Việt Nam có đường biên giới với Trung Quốc, Lào và Campuchia",
            "expected": "SUPPORTED",
            "difficulty": "medium",
            "note": "Multi-fact claim"
        },
        {
            "claim": "Việt Nam giáp biên giới đất liền với Thái Lan",
            "expected": "REFUTED",
            "difficulty": "medium",
            "note": "False geographic claim"
        },
        {
            "claim": "Sông Mekong chảy qua lãnh thổ Việt Nam",
            "expected": "SUPPORTED",
            "difficulty": "easy",
            "note": "River geography"
        },
        {
            "claim": "Đà Nẵng là thành phố lớn nhất Việt Nam",
            "expected": "REFUTED",
            "difficulty": "medium",
            "note": "HCMC is largest"
        }
    ],
    "history": [
        {
            "claim": "Việt Nam giành độc lập năm 1945",
            "expected": "SUPPORTED",
            "difficulty": "easy",
            "note": "Independence declaration"
        },
        {
            "claim": "Chiến thắng Điện Biên Phủ diễn ra năm 1954",
            "expected": "SUPPORTED",
            "difficulty": "easy",
            "note": "Historic battle"
        },
        {
            "claim": "Việt Nam thống nhất đất nước năm 1976",
            "expected": "REFUTED",
            "difficulty": "medium",
            "note": "Unified in 1975, not 1976"
        },
        {
            "claim": "Triều đại nhà Nguyễn là triều đại phong kiến cuối cùng của Việt Nam",
            "expected": "SUPPORTED",
            "difficulty": "medium",
            "note": "Last feudal dynasty"
        },
        {
            "claim": "Hà Nội từng là thuộc địa của Pháp",
            "expected": "SUPPORTED",
            "difficulty": "easy",
            "note": "French colonization"
        }
    ],
    "politics": [
        {
            "claim": "Việt Nam có chế độ đa đảng",
            "expected": "REFUTED",
            "difficulty": "medium",
            "note": "One-party system"
        },
        {
            "claim": "Việt Nam là thành viên của ASEAN",
            "expected": "SUPPORTED",
            "difficulty": "easy",
            "note": "ASEAN membership"
        },
        {
            "claim": "Việt Nam là thành viên thường trực của Hội đồng Bảo an Liên Hợp Quốc",
            "expected": "REFUTED",
            "difficulty": "medium",
            "note": "Not a permanent member"
        },
        {
            "claim": "Quốc hội Việt Nam có nhiệm kỳ 5 năm",
            "expected": "SUPPORTED",
            "difficulty": "medium",
            "note": "Parliamentary term"
        },
        {
            "claim": "Việt Nam theo chế độ tổng thống",
            "expected": "REFUTED",
            "difficulty": "medium",
            "note": "Socialist republic system"
        }
    ],
    "culture": [
        {
            "claim": "Áo dài là trang phục truyền thống của Việt Nam",
            "expected": "SUPPORTED",
            "difficulty": "easy",
            "note": "Traditional costume"
        },
        {
            "claim": "Phở là món ăn có nguồn gốc từ Việt Nam",
            "expected": "SUPPORTED",
            "difficulty": "easy",
            "note": "Vietnamese cuisine"
        },
        {
            "claim": "Tết Nguyên Đán là ngày lễ lớn nhất của người Việt Nam",
            "expected": "SUPPORTED",
            "difficulty": "easy",
            "note": "Lunar New Year"
        },
        {
            "claim": "Chữ Quốc ngữ được phát minh bởi người Việt Nam",
            "expected": "REFUTED",
            "difficulty": "hard",
            "note": "Created by Portuguese missionaries"
        },
        {
            "claim": "Nhã nhạc cung đình Huế được UNESCO công nhận là di sản văn hóa phi vật thể",
            "expected": "SUPPORTED",
            "difficulty": "medium",
            "note": "UNESCO heritage"
        }
    ],
    "sports": [
        {
            "claim": "Việt Nam đã vô địch AFF Cup",
            "expected": "SUPPORTED",
            "difficulty": "easy",
            "note": "Won AFF Cup multiple times"
        },
        {
            "claim": "Việt Nam đã tham dự vòng chung kết World Cup bóng đá nam",
            "expected": "REFUTED",
            "difficulty": "medium",
            "note": "Never qualified for WC finals"
        },
        {
            "claim": "Park Hang-seo từng là huấn luyện viên đội tuyển Việt Nam",
            "expected": "SUPPORTED",
            "difficulty": "easy",
            "note": "Famous coach"
        },
        {
            "claim": "Việt Nam đã từng đăng cai tổ chức SEA Games",
            "expected": "SUPPORTED",
            "difficulty": "easy",
            "note": "Hosted SEA Games"
        },
        {
            "claim": "Việt Nam có huy chương vàng Olympic môn bóng đá nam",
            "expected": "REFUTED",
            "difficulty": "medium",
            "note": "No Olympic gold in football"
        }
    ]
}

def check_claim(claim: str, timeout: int = 60) -> dict:
    """Call Fact Checker API"""
    try:
        response = requests.post(
            f"{FACT_CHECKER_URL}/check",
            json={"claim": claim},
            timeout=timeout
        )
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def run_tests():
    """Run all tests and collect results"""
    print("="*70)
    print("INTEGRATION TEST v2 - VIETNAMESE FACT CHECKER")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"Target: {FACT_CHECKER_URL}")
    print("="*70)
    
    # Check server health
    try:
        health = requests.get(f"{FACT_CHECKER_URL}/", timeout=5)
        print(f"Server Status: {health.json().get('status', 'unknown')}")
    except Exception as e:
        print(f"ERROR: Cannot connect to server: {e}")
        return None
    
    results = []
    stats = {
        "total": 0,
        "correct": 0,
        "wrong": 0,
        "error": 0,
        "by_domain": {},
        "by_difficulty": {"easy": {"total": 0, "correct": 0}, 
                         "medium": {"total": 0, "correct": 0}, 
                         "hard": {"total": 0, "correct": 0}}
    }
    
    for domain, claims in TEST_DATASET.items():
        print(f"\n{'='*70}")
        print(f"DOMAIN: {domain.upper()}")
        print(f"{'='*70}")
        
        stats["by_domain"][domain] = {"total": 0, "correct": 0}
        
        for i, test_case in enumerate(claims):
            claim = test_case["claim"]
            expected = test_case["expected"]
            difficulty = test_case["difficulty"]
            
            print(f"\n[{domain}:{i+1}] {claim}")
            print(f"Expected: {expected} | Difficulty: {difficulty}")
            
            start_time = time.time()
            response = check_claim(claim)
            duration = time.time() - start_time
            
            # Extract actual verdict
            if "error" in response and response["error"]:
                actual = "ERROR"
                confidence = 0
                stats["error"] += 1
            else:
                actual = response.get("verdict", "ERROR")
                confidence = response.get("confidence", 0)
            
            # Check correctness
            is_correct = (actual == expected)
            
            if actual != "ERROR":
                if is_correct:
                    stats["correct"] += 1
                    stats["by_domain"][domain]["correct"] += 1
                    stats["by_difficulty"][difficulty]["correct"] += 1
                    status = " CORRECT"
                else:
                    stats["wrong"] += 1
                    status = " WRONG"
            else:
                status = " ERROR"
            
            stats["total"] += 1
            stats["by_domain"][domain]["total"] += 1
            stats["by_difficulty"][difficulty]["total"] += 1
            
            print(f"Actual: {actual} (confidence: {confidence:.3f}) | {status} | {duration:.2f}s")
            
            # Store result
            results.append({
                "domain": domain,
                "claim": claim,
                "expected": expected,
                "actual": actual,
                "confidence": confidence,
                "is_correct": is_correct,
                "difficulty": difficulty,
                "duration_seconds": duration,
                "response": response
            })
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    
    accuracy = stats["correct"] / stats["total"] * 100 if stats["total"] > 0 else 0
    print(f"\nOverall Accuracy: {stats['correct']}/{stats['total']} ({accuracy:.1f}%)")
    print(f"Errors: {stats['error']}")
    
    print("\nBy Domain:")
    for domain, domain_stats in stats["by_domain"].items():
        domain_acc = domain_stats["correct"] / domain_stats["total"] * 100 if domain_stats["total"] > 0 else 0
        print(f"  {domain}: {domain_stats['correct']}/{domain_stats['total']} ({domain_acc:.1f}%)")
    
    print("\nBy Difficulty:")
    for diff, diff_stats in stats["by_difficulty"].items():
        if diff_stats["total"] > 0:
            diff_acc = diff_stats["correct"] / diff_stats["total"] * 100
            print(f"  {diff}: {diff_stats['correct']}/{diff_stats['total']} ({diff_acc:.1f}%)")
    
    # Wrong predictions detail
    wrong_predictions = [r for r in results if not r["is_correct"] and r["actual"] != "ERROR"]
    if wrong_predictions:
        print(f"\nWrong Predictions ({len(wrong_predictions)}):")
        for wp in wrong_predictions:
            print(f"  - [{wp['domain']}] {wp['claim'][:50]}...")
            print(f"    Expected: {wp['expected']}, Got: {wp['actual']}")
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"d:/bmad/tests/integration_v2_results_{timestamp}.json"
    
    output = {
        "test_name": "integration_test_v2",
        "timestamp": datetime.now().isoformat(),
        "server_url": FACT_CHECKER_URL,
        "statistics": stats,
        "accuracy": accuracy,
        "test_results": results
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"\nResults saved to: {output_file}")
    
    return output

if __name__ == "__main__":
    run_tests()
