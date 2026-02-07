#!/usr/bin/env python3
"""
Integration Test with Vietnam Specific Cases
"""

import requests
import time

def test_vietnam_specific_cases():
    """Test Vietnamese Fact Checker with specific Vietnam cases"""
    print(" Vietnam Specific Cases Integration Test")
    print("=" * 60)
    
    base_url = "http://localhost:8005"
    
    # Test cases from user
    test_cases = [
        {
            "claim": "Cổ phiếu VIC bị giảm ở thị trường Việt Nam hôm nay",
            "category": "Stock Market",
            "description": "VIC stock price decrease today"
        },
        {
            "claim": "Trương Tấn Dũng là tổng thống của Việt Nam",
            "category": "Politics",
            "description": "Truong Tan Sang is Vietnam president"
        },
        {
            "claim": "Trường Bách Khoa ở Ngoài Phú Yên",
            "category": "Education",
            "description": "Bach Khoa University in Phu Yen"
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n Test {i}: {test_case['claim']}")
        print(f" Category: {test_case['category']}")
        print(f" Description: {test_case['description']}")
        
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
                rationale = result.get('rationale', 'No rationale')
                
                print(f" Result: {verdict}")
                print(f" Confidence: {confidence:.3f}")
                print(f" Evidence Count: {evidence_count}")
                print(f"⏱ Processing Time: {processing_time:.2f}s")
                print(f" Rationale: {rationale[:150]}...")
                
                results.append({
                    'claim': test_case['claim'],
                    'category': test_case['category'],
                    'verdict': verdict,
                    'confidence': confidence,
                    'evidence_count': evidence_count,
                    'processing_time': processing_time,
                    'success': True
                })
                
            else:
                print(f" Failed: HTTP {response.status_code}")
                try:
                    error_text = response.text
                    print(f"   Error: {error_text[:200]}...")
                except:
                    pass
                
                results.append({
                    'claim': test_case['claim'],
                    'category': test_case['category'],
                    'verdict': 'ERROR',
                    'confidence': 0,
                    'evidence_count': 0,
                    'processing_time': 0,
                    'success': False
                })
                
        except Exception as e:
            print(f" Exception: {e}")
            results.append({
                'claim': test_case['claim'],
                'category': test_case['category'],
                'verdict': 'EXCEPTION',
                'confidence': 0,
                'evidence_count': 0,
                'processing_time': 0,
                'success': False
            })
    
    # Summary
    print("\n" + "=" * 60)
    print(" VIETNAM SPECIFIC CASES SUMMARY")
    print("=" * 60)
    
    success_count = sum(1 for r in results if r['success'])
    total_count = len(results)
    success_rate = (success_count / total_count) * 100
    
    print(f" Successful: {success_count}/{total_count} ({success_rate:.1f}%)")
    print(f" Failed: {total_count - success_count}/{total_count}")
    
    print(f"\n Average Processing Time: {sum(r['processing_time'] for r in results)/len(results):.2f}s")
    print(f" Average Evidence Count: {sum(r['evidence_count'] for r in results)/len(results):.1f}")
    
    # Results by category
    print(f"\n RESULTS BY CATEGORY:")
    for result in results:
        status = "" if result['success'] else ""
        print(f"{status} {result['category']}: {result['verdict']} (Confidence: {result['confidence']:.3f})")
        print(f"   Claim: {result['claim'][:60]}...")
    
    # Detailed analysis
    print(f"\n DETAILED ANALYSIS:")
    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result['category']} Case:")
        print(f"   Claim: {result['claim']}")
        print(f"   Verdict: {result['verdict']}")
        print(f"   Evidence Found: {result['evidence_count']} items")
        print(f"   Processing Time: {result['processing_time']:.2f}s")
        
        if result['success']:
            if result['confidence'] > 0.7:
                print(f"    High confidence result - Reliable")
            elif result['confidence'] > 0.4:
                print(f"    Medium confidence result - Moderate reliability")
            else:
                print(f"    Low confidence result - Needs verification")
        else:
            print(f"    Processing failed - System issue")
    
    print(f"\n VIETNAM SPECIFIC CASES TEST COMPLETED!")
    
    return success_rate

if __name__ == "__main__":
    success_rate = test_vietnam_specific_cases()
    
    if success_rate >= 80:
        print(" EXCELLENT! Vietnam-specific fact checking works very well!")
    elif success_rate >= 60:
        print(" GOOD! Vietnam-specific fact checking works reasonably well!")
    else:
        print(" NEEDS IMPROVEMENT! Vietnam-specific fact checking needs tuning!")
