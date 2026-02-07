#!/usr/bin/env python3
"""
Update trusted sources by domain/category for Vietnamese Fact Checker
Based on research of popular query topics in Vietnam
"""
import requests
import json

BASE = 'http://localhost:8005'

# ============================================================================
# TRUSTED SOURCES BY CATEGORY
# ============================================================================

trusted_sources = {
    # === CHÍNH PHỦ & CƠ QUAN NHÀ NƯỚC ===
    "government": [
        "chinhphu.vn",          # Cổng thông tin Chính phủ
        "gov.vn",               # Các trang .gov.vn
        "quochoi.vn",           # Quốc hội
        "moh.gov.vn",           # Bộ Y tế
        "moet.gov.vn",          # Bộ Giáo dục
        "mof.gov.vn",           # Bộ Tài chính
        "molisa.gov.vn",        # Bộ LĐ-TB-XH
        "moit.gov.vn",          # Bộ Công thương
        "monre.gov.vn",         # Bộ TN-MT
        "most.gov.vn",          # Bộ KH-CN
        "mic.gov.vn",           # Bộ TT-TT
        "moj.gov.vn",           # Bộ Tư pháp
        "mpi.gov.vn",           # Bộ KH-ĐT
        "dangcongsan.vn",       # Đảng Cộng sản
        "baochinhphu.vn",       # Báo Chính phủ
    ],
    
    # === THỐNG KÊ & DỮ LIỆU ===
    "statistics": [
        "gso.gov.vn",           # Tổng cục Thống kê
        "nso.gov.vn",           # Cục Thống kê Quốc gia
        "customs.gov.vn",       # Tổng cục Hải quan
        "sbv.gov.vn",           # Ngân hàng Nhà nước
    ],
    
    # === TIN TỨC CHÍNH THỐNG ===
    "mainstream_news": [
        "vnexpress.net",        # VnExpress (#1 news)
        "tuoitre.vn",           # Tuổi Trẻ
        "thanhnien.vn",         # Thanh Niên
        "nhandan.vn",           # Nhân Dân
        "vietnamnet.vn",        # VietnamNet
        "dantri.com.vn",        # Dân Trí
        "laodong.vn",           # Lao Động
        "tienphong.vn",         # Tiền Phong
        "vietnamplus.vn",       # Vietnam Plus (TTXVN)
        "vov.vn",               # Đài Tiếng nói VN
        "vtv.vn",               # Đài Truyền hình VN
        "qdnd.vn",              # Quân đội Nhân dân
        "congan.com.vn",        # Công an Nhân dân
        "nld.com.vn",           # Người Lao Động
        "sggp.org.vn",          # Sài Gòn Giải Phóng
        "hanoimoi.com.vn",      # Hà Nội Mới
        "baotintuc.vn",         # Báo Tin Tức
    ],
    
    # === KINH TẾ & TÀI CHÍNH ===
    "finance_economy": [
        "thesaigontimes.vn",    # Thời báo Kinh tế Sài Gòn
        "vietstock.vn",         # Vietstock
        "cafef.vn",             # CafeF
        "cafebiz.vn",           # CafeBiz
        "vneconomy.vn",         # VnEconomy
        "thoibaonganhang.vn",   # Thời báo Ngân hàng
        "tapchitaichinh.vn",    # Tạp chí Tài chính
        "tinnhanhchungkhoan.vn", # Tin nhanh Chứng khoán
        "stockbiz.vn",          # Stockbiz
    ],
    
    # === Y TẾ & SỨC KHỎE ===
    "health": [
        "suckhoedoisong.vn",    # Sức khỏe & Đời sống (Bộ Y tế)
        "vnvc.vn",              # VNVC (tiêm chủng)
        "vinmec.com",           # Vinmec
        "medlatec.vn",          # Medlatec
        "bachmai.gov.vn",       # Bệnh viện Bạch Mai
        "benhvien108.vn",       # Bệnh viện 108
        "benhvienchoxanh.vn",   # Bệnh viện Chợ Rẫy
        "hellobacsi.com",       # Hello Bác sĩ
    ],
    
    # === GIÁO DỤC ===
    "education": [
        "edu.vn",               # Các trang .edu.vn
        "vnu.edu.vn",           # ĐH Quốc gia Hà Nội
        "vnuhcm.edu.vn",        # ĐH Quốc gia TP.HCM
        "hust.edu.vn",          # ĐH Bách khoa Hà Nội
        "neu.edu.vn",           # ĐH Kinh tế Quốc dân
        "ueh.edu.vn",           # ĐH Kinh tế TP.HCM
        "ftu.edu.vn",           # ĐH Ngoại thương
        "hmu.edu.vn",           # ĐH Y Hà Nội
        "yds.edu.vn",           # ĐH Y Dược TP.HCM
        "dantri.com.vn",        # Dân Trí (giáo dục)
        "giaoduc.net.vn",       # Báo Giáo dục VN
        "vietnamnet.vn",        # VietnamNet (giáo dục)
    ],
    
    # === PHÁP LUẬT ===
    "law": [
        "thuvienphapluat.vn",   # Thư viện Pháp luật
        "phapluat.vn",          # Pháp Luật VN
        "plo.vn",               # Pháp Luật Online
        "doisongphapluat.com.vn", # Đời sống Pháp luật
        "congbobanan.toaan.gov.vn", # Công bố bản án
        "luatvietnam.vn",       # Luật Việt Nam
    ],
    
    # === THỂ THAO ===
    "sports": [
        "bongda24h.vn",         # Bóng đá 24h
        "thethao247.vn",        # Thể thao 247
        "webthethao.vn",        # Web Thể thao
        "bongdaplus.vn",        # Bóng đá Plus
        "thethaovanhoa.vn",     # Thể thao & Văn hóa
        "vff.org.vn",           # Liên đoàn Bóng đá VN
    ],
    
    # === CÔNG NGHỆ ===
    "technology": [
        "genk.vn",              # Genk
        "techz.vn",             # TechZ
        "tinhte.vn",            # Tinh tế
        "ictnews.vietnamnet.vn", # ICTNews
        "quantrimang.com",      # Quản trị mạng
        "thegioididong.com",    # Thế giới Di động
        "fptshop.com.vn",       # FPT Shop
        "cellphones.com.vn",    # CellphoneS
    ],
    
    # === DU LỊCH ===
    "travel": [
        "vietnamtourism.gov.vn", # Tổng cục Du lịch
        "dulich.tuoitre.vn",    # Du lịch Tuổi Trẻ
        "vntrip.vn",            # VNTrip
        "ivivu.com",            # iVIVU
        "mytour.vn",            # Mytour
        "klook.com",            # Klook
    ],
    
    # === BÁCH KHOA & THAM KHẢO ===
    "reference": [
        "wikipedia.org",        # Wikipedia
        "vi.wikipedia.org",     # Wikipedia tiếng Việt
        "en.wikipedia.org",     # Wikipedia tiếng Anh
        "britannica.com",       # Encyclopaedia Britannica
    ],
    
    # === QUỐC TẾ UY TÍN ===
    "international": [
        "bbc.com",              # BBC
        "reuters.com",          # Reuters
        "apnews.com",           # AP News
        "afp.com",              # AFP
        "who.int",              # WHO (Y tế)
        "worldbank.org",        # World Bank
        "imf.org",              # IMF
        "un.org",               # United Nations
    ],
}

# Flatten all sources
all_trusted_sources = []
for category, sources in trusted_sources.items():
    all_trusted_sources.extend(sources)

# Remove duplicates
all_trusted_sources = list(set(all_trusted_sources))
all_trusted_sources.sort()

print("=" * 70)
print(" UPDATING TRUSTED SOURCES BY DOMAIN")
print("=" * 70)

print(f"\n Sources by Category:")
for category, sources in trusted_sources.items():
    print(f"   • {category}: {len(sources)} domains")

print(f"\n Total unique trusted sources: {len(all_trusted_sources)}")

# Update configuration
print("\n Updating configuration...")
r = requests.post(f'{BASE}/config/brave_search', json={
    'section': 'brave_search',
    'updates': {'trusted_sources': all_trusted_sources}
})

if r.status_code == 200:
    print(f" Updated trusted_sources with {len(all_trusted_sources)} domains")
else:
    print(f" Failed: {r.text}")

# Verify
print("\n Verifying configuration...")
r = requests.get(f'{BASE}/config/brave_search')
cfg = r.json()['config']
print(f"   • trusted_sources count: {len(cfg['trusted_sources'])}")

# Show categories summary
print("\n" + "=" * 70)
print(" TRUSTED SOURCES BY CATEGORY")
print("=" * 70)

for category, sources in trusted_sources.items():
    category_name = {
        "government": "  Chính phủ & Cơ quan Nhà nước",
        "statistics": " Thống kê & Dữ liệu",
        "mainstream_news": " Tin tức Chính thống",
        "finance_economy": " Kinh tế & Tài chính",
        "health": " Y tế & Sức khỏe",
        "education": " Giáo dục",
        "law": "  Pháp luật",
        "sports": " Thể thao",
        "technology": " Công nghệ",
        "travel": "  Du lịch",
        "reference": " Bách khoa & Tham khảo",
        "international": " Quốc tế Uy tín",
    }.get(category, category)
    
    print(f"\n{category_name}:")
    for source in sources[:5]:
        print(f"   • {source}")
    if len(sources) > 5:
        print(f"   ... và {len(sources) - 5} nguồn khác")

print("\n" + "=" * 70)
print(" TRUSTED SOURCES UPDATE COMPLETE")
print("=" * 70)
