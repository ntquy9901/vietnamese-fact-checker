#!/usr/bin/env python3
"""
Comprehensive Vietnamese Fact Checker Test
"""

import requests
import time

def test_fact_checker():
    """Test Vietnamese Fact Checker with multiple claims"""
    print(" Comprehensive Vietnamese Fact Checker Test")
    print("=" * 60)
    
    base_url = "http://localhost:8005"
    
    test_cases = [
        {
            "claim": "Hà Nội là thủ đô của Việt Nam",
            "expected": "SUPPORTED",
            "description": "Basic geographical fact"
        },
        {
            "claim": "Việt Nam là quốc gia lớn nhất thế giới",
            "expected": "REFUTED", 
            "description": "Incorrect geographical claim"
        },
        {
            "claim": "Sài Gòn là thành phố lớn nhất Việt Nam",
            "expected": "SUPPORTED",
            "description": "City population fact"
        },
        {
            "claim": "Phở là món ăn truyền thống của Việt Nam",
            "expected": "SUPPORTED",
            "description": "Cultural food fact"
        },
        {
            "claim": "Mặt Trời quay quanh Trái Đất",
            "expected": "REFUTED",
            "description": "Astronomical fact (incorrect)"
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n Test {i}: {test_case['claim']}")
        print(f" Description: {test_case['description']}")
        print(f" Expected: {test_case['expected']}")
        
        try:
            start_time = time.time()
            response = requests.post(
                f"{base_url}/check", 
                json={"claim": test_case['claim']},
                timeout=60
            )
            end_time = time.time()
            
            if response.status_code == 200:
                result = response.json()
                verdict = result.get('verdict', 'UNKNOWN')
                confidence = result.get('confidence', 0)
                evidence_count = result.get('evidence_count', 0)
                processing_time = end_time - start_time
                
                print(f" Result: {verdict}")
                print(f" Confidence: {confidence:.3f}")
                print(f" Evidence Count: {evidence_count}")
                print(f"⏱ Processing Time: {processing_time:.2f}s")
                
                # Check if result matches expectation
                if verdict == test_case['expected']:
                    print(" CORRECT!")
                else:
                    print(f" UNEXPECTED (Expected: {test_case['expected']})")
                
                results.append({
                    'claim': test_case['claim'],
                    'expected': test_case['expected'],
                    'actual': verdict,
                    'confidence': confidence,
                    'evidence_count': evidence_count,
                    'processing_time': processing_time,
                    'correct': verdict == test_case['expected']
                })
                
            else:
                print(f" Failed: HTTP {response.status_code}")
                results.append({
                    'claim': test_case['claim'],
                    'expected': test_case['expected'],
                    'actual': 'ERROR',
                    'confidence': 0,
                    'evidence_count': 0,
                    'processing_time': 0,
                    'correct': False
                })
                
        except Exception as e:
            print(f" Exception: {e}")
            results.append({
                'claim': test_case['claim'],
                'expected': test_case['expected'],
                'actual': 'EXCEPTION',
                'confidence': 0,
                'evidence_count': 0,
                'processing_time': 0,
                'correct': False
            })
    
    # Summary
    print("\n" + "=" * 60)
    print(" TEST SUMMARY")
    print("=" * 60)
    
    correct_count = sum(1 for r in results if r['correct'])
    total_count = len(results)
    accuracy = (correct_count / total_count) * 100
    
    print(f" Correct: {correct_count}/{total_count} ({accuracy:.1f}%)")
    print(f" Incorrect: {total_count - correct_count}/{total_count}")
    
    print(f"\n Average Processing Time: {sum(r['processing_time'] for r in results)/len(results):.2f}s")
    print(f" Average Evidence Count: {sum(r['evidence_count'] for r in results)/len(results):.1f}")
    
    # Detailed results
    print(f"\n DETAILED RESULTS:")
    for i, result in enumerate(results, 1):
        status = "" if result['correct'] else ""
        print(f"{status} {i}. {result['claim'][:50]}...")
        print(f"   Expected: {result['expected']} | Got: {result['actual']} | Confidence: {result['confidence']:.3f}")
    
    print(f"\n COMPREHENSIVE TEST COMPLETED!")
    
    return accuracy

if __name__ == "__main__":
    accuracy = test_fact_checker()
    
    if accuracy >= 80:
        print(" EXCELLENT! Fact Checker is working very well!")
    elif accuracy >= 60:
        print(" GOOD! Fact Checker is working reasonably well!")
    else:
        print(" NEEDS IMPROVEMENT! Fact Checker needs tuning!")
