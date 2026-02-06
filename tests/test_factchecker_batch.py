#!/usr/bin/env python3
"""Test Vietnamese Fact Checker with 10 claims dataset"""
import requests
import json
import time

# Test dataset - same as translation test
TEST_CLAIMS = [
    ("Quảng Trị ở miền Nam", "Geography", False),  # FALSE - Quảng Trị ở miền Trung
    ("Việt Nam giành độc lập năm 1945", "History", True),  # TRUE
    ("Trái đất quay quanh mặt trời", "Science", True),  # TRUE
    ("Hồ Chí Minh là người sáng lập nước Việt Nam Dân chủ Cộng hòa", "Person", True),  # TRUE
    ("Đội tuyển Việt Nam vô địch AFF Cup năm 2018", "Sports", True),  # TRUE
    ("Phở là món ăn truyền thống của Việt Nam", "Culture", True),  # TRUE
    ("Việt Nam là nước xuất khẩu gạo lớn thứ hai thế giới", "Economy", True),  # TRUE (roughly)
    ("Người ta có thể sống hơn 100 tuổi", "Health", True),  # TRUE
    ("VinFast là hãng xe điện đầu tiên của Việt Nam", "Technology", True),  # TRUE (debatable)
    ("Đại học Bách khoa Hà Nội là trường đại học kỹ thuật hàng đầu Việt Nam", "Education", True),  # TRUE
]

def test_fact_checker():
    print("=" * 80)
    print("🧪 Vietnamese Fact Checker - 10 Claims Test")
    print("=" * 80)
    
    # Check if server is running
    try:
        health = requests.get('http://localhost:8005/health', timeout=5)
        print(f"✅ Fact Checker Server: Running")
    except:
        print("❌ Fact Checker Server: Not running!")
        return []
    
    results = []
    total_time = 0
    
    for i, (claim, category, expected) in enumerate(TEST_CLAIMS, 1):
        print(f"\n{'='*80}")
        print(f"📝 Claim {i}/10: [{category}]")
        print(f"   VI: {claim}")
        print(f"   Expected: {'TRUE' if expected else 'FALSE'}")
        print("-" * 80)
        
        try:
            start = time.time()
            response = requests.post(
                'http://localhost:8005/check',
                json={'claim': claim},
                timeout=180
            )
            elapsed = time.time() - start
            
            if response.status_code == 200:
                data = response.json()
                verdict = data['verdict']
                confidence = data['confidence']
                evidence_list = data.get('evidence', [])
                sources = data.get('sources', [])
                
                # Determine if verdict matches expected
                is_supported = verdict in ['SUPPORTED', 'SUPPORT']
                is_correct = is_supported == expected
                
                results.append({
                    'id': i,
                    'claim': claim,
                    'category': category,
                    'expected': expected,
                    'verdict': verdict,
                    'confidence': confidence,
                    'correct': is_correct,
                    'time': elapsed,
                    'evidence': evidence_list,
                    'sources': sources
                })
                
                total_time += elapsed
                
                status = "✅" if is_correct else "❌"
                print(f"   Verdict: {verdict} ({confidence:.2%})")
                print(f"   Result: {status} {'CORRECT' if is_correct else 'WRONG'}")
                print(f"   ⏱️  {elapsed:.1f}s")
                
                # Print evidence
                print(f"\n   📚 Evidence ({len(evidence_list)} items):")
                for j, ev in enumerate(evidence_list, 1):
                    text = ev.get('text', '')[:100] + '...' if len(ev.get('text', '')) > 100 else ev.get('text', '')
                    title = ev.get('title', 'No title')
                    print(f"      {j}. [{title[:40]}]")
                    print(f"         {text}")
            else:
                print(f"   ❌ Error: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 FACT CHECKER RESULTS SUMMARY")
    print("=" * 80)
    
    correct = sum(1 for r in results if r['correct'])
    total = len(results)
    
    print(f"\n{'#':<3} {'Category':<12} {'Verdict':<12} {'Conf':<8} {'Expected':<10} {'Result':<8}")
    print("-" * 80)
    
    for r in results:
        exp_str = "TRUE" if r['expected'] else "FALSE"
        res_str = "✅" if r['correct'] else "❌"
        print(f"{r['id']:<3} {r['category']:<12} {r['verdict']:<12} {r['confidence']:.2%}   {exp_str:<10} {res_str:<8}")
    
    print("-" * 80)
    print(f"\n📈 Accuracy: {correct}/{total} ({correct/total:.0%})")
    print(f"⏱️  Total time: {total_time:.1f}s")
    print(f"⏱️  Avg time/claim: {total_time/total:.1f}s")
    
    return results

if __name__ == "__main__":
    test_fact_checker()
