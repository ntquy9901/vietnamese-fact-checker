import requests

# Test dataset with 10 diverse Vietnamese claims
TEST_CLAIMS = [
    # 1. Địa lý - Geography
    ("Quảng Trị ở miền Nam", "Geography - Location claim"),
    # 2. Sự kiện lịch sử - Historical event
    ("Việt Nam giành độc lập năm 1945", "History - Independence year"),
    # 3. Khoa học - Science
    ("Trái đất quay quanh mặt trời", "Science - Earth orbits sun"),
    # 4. Nhân vật nổi tiếng - Famous person
    ("Hồ Chí Minh là người sáng lập nước Việt Nam Dân chủ Cộng hòa", "Person - Ho Chi Minh"),
    # 5. Thể thao - Sports
    ("Đội tuyển Việt Nam vô địch AFF Cup năm 2018", "Sports - AFF Cup"),
    # 6. Văn hóa - Culture
    ("Phở là món ăn truyền thống của Việt Nam", "Culture - Pho"),
    # 7. Kinh tế - Economy
    ("Việt Nam là nước xuất khẩu gạo lớn thứ hai thế giới", "Economy - Rice export"),
    # 8. Y tế - Health
    ("Người ta có thể sống hơn 100 tuổi", "Health - Longevity"),
    # 9. Công nghệ - Technology
    ("VinFast là hãng xe điện đầu tiên của Việt Nam", "Technology - VinFast"),
    # 10. Giáo dục - Education
    ("Đại học Bách khoa Hà Nội là trường đại học kỹ thuật hàng đầu Việt Nam", "Education - University"),
]

def test_translation_quality():
    print("=" * 80)
    print(" VinAI Translation Quality Test - 10 Vietnamese Claims")
    print("=" * 80)
    
    try:
        # Health check
        response = requests.get('http://localhost:8003/', timeout=5)
        data = response.json()
        print(f" Model: {data.get('model', 'unknown')}")
        print(f" Status: {'Loaded ' if data.get('model_loaded') else 'Not loaded '}")
        print("=" * 80)
        
        results = []
        total_time = 0
        
        for i, (claim, category) in enumerate(TEST_CLAIMS, 1):
            response = requests.post(
                'http://localhost:8003/translate', 
                json={'text': claim}, 
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                total_time += result['translation_time']
                results.append({
                    'id': i,
                    'category': category,
                    'vi': claim,
                    'en': result['english'],
                    'time': result['translation_time']
                })
                
                print(f"\n{i}. [{category}]")
                print(f"   VI: {claim}")
                print(f"   EN: {result['english']}")
                print(f"   ⏱  {result['translation_time']:.2f}s")
            else:
                print(f"\n{i}.  Failed: {claim}")
        
        # Summary
        print("\n" + "=" * 80)
        print(" SUMMARY")
        print("=" * 80)
        print(f"Total claims tested: {len(results)}")
        print(f"Total translation time: {total_time:.2f}s")
        print(f"Average time per claim: {total_time/len(results):.2f}s")
        
        # Quality analysis
        print("\n Translation Results Table:")
        print("-" * 80)
        print(f"{'#':<3} {'Vietnamese':<40} {'English':<35}")
        print("-" * 80)
        for r in results:
            vi_short = r['vi'][:38] + '..' if len(r['vi']) > 40 else r['vi']
            en_short = r['en'][:33] + '..' if len(r['en']) > 35 else r['en']
            print(f"{r['id']:<3} {vi_short:<40} {en_short:<35}")
        print("-" * 80)
        
        return results
            
    except Exception as e:
        print(f' Error: {e}')
        return []

if __name__ == "__main__":
    test_translation_quality()
