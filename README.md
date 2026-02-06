# Vietnamese Fact Checker System

Hệ thống kiểm tra thông tin tiếng Việt sử dụng AI.

## 📋 Yêu cầu hệ thống

- **Python**: 3.10+
- **GPU**: NVIDIA RTX (khuyến nghị RTX 4060 trở lên)
- **CUDA**: 11.8+
- **RAM**: 16GB+
- **Disk**: 10GB+ cho models

## 🏗️ Cấu trúc dự án

```
D:\bmad\
├── vietnamese-fact-checker/      # Main API server (port 8005)
├── vietnamese-translation-system/ # Translation service (port 8003)
├── minicheck/                     # MiniCheck verification (port 8002)
├── brave-search-baseline/         # Brave Search proxy (port 8004)
├── tests/                         # Test scripts
└── start_all_servers.py           # Script khởi động tất cả
```

## 🚀 Cài đặt

### 1. Clone/Copy project

```bash
# Copy toàn bộ folder bmad vào D:\
```

### 2. Tạo môi trường ảo (khuyến nghị)

```bash
cd D:\bmad
python -m venv venv
.\venv\Scripts\activate
```

### 3. Cài đặt dependencies cho từng service

```bash
# Translation System
cd D:\bmad\vietnamese-translation-system
pip install -r requirements.txt

# MiniCheck
cd D:\bmad\minicheck
pip install -r requirements.txt

# Brave Search Baseline
cd D:\bmad\brave-search-baseline
pip install -r requirements.txt

# Fact Checker
cd D:\bmad\vietnamese-fact-checker
pip install -r requirements.txt
```

### 4. Cấu hình API Keys

Tạo file `.env` trong `D:\bmad\vietnamese-fact-checker\`:

```env
BRAVE_SEARCH_API_KEY=your_brave_api_key_here
```

## ▶️ Khởi động hệ thống

### Cách 1: Khởi động từng service (khuyến nghị để debug)

Mở 4 terminal riêng biệt:

**Terminal 1 - Translation (port 8003):**
```bash
cd D:\bmad\vietnamese-translation-system
python translation_baseline.py
```

**Terminal 2 - MiniCheck (port 8002):**
```bash
cd D:\bmad\minicheck
python minicheck_baseline.py
```

**Terminal 3 - Brave Search (port 8004):**
```bash
cd D:\bmad\brave-search-baseline
python brave_search_baseline.py
```

**Terminal 4 - Fact Checker (port 8005):**
```bash
cd D:\bmad\vietnamese-fact-checker
python start_vietnamese_checker.py
```

### Cách 2: Khởi động tất cả cùng lúc

```bash
cd D:\bmad
python start_all_servers.py
```

## ✅ Kiểm tra hệ thống

### 1. Kiểm tra trạng thái servers

```bash
python check_server_status.py
```

Kết quả mong đợi:
```
✅ Translation (8003): Running
✅ MiniCheck (8002): Running
✅ Brave Search (8004): Running
✅ Fact Checker (8005): Running
```

### 2. Test đơn giản

```bash
cd D:\bmad
python -c "
import requests
claim = 'Hà Nội là thủ đô của Việt Nam'
r = requests.post('http://localhost:8005/check', json={'claim': claim}, timeout=120)
result = r.json()
print(f'Claim: {claim}')
print(f'Verdict: {result[\"verdict\"]}')
print(f'Confidence: {result[\"confidence\"]:.2%}')
print(f'Evidence: {result[\"evidence_count\"]} sources')
"
```

Kết quả mong đợi:
```
Claim: Hà Nội là thủ đô của Việt Nam
Verdict: SUPPORTED
Confidence: 97.xx%
Evidence: 5 sources
```

### 3. Test qua API docs

Mở trình duyệt: http://localhost:8005/docs

## 🔧 Cấu hình

### Xem cấu hình hiện tại

```bash
curl http://localhost:8005/config/summary
```

### Các endpoint cấu hình

| Endpoint | Method | Mô tả |
|----------|--------|-------|
| `/config` | GET | Xem tất cả cấu hình |
| `/config/summary` | GET | Tóm tắt cấu hình |
| `/config/{section}` | GET | Xem cấu hình theo section |
| `/config/{section}` | POST | Cập nhật cấu hình |

### Sections có sẵn

- `brave_search` - Cấu hình tìm kiếm
- `translation` - Cấu hình dịch thuật
- `minicheck` - Cấu hình xác minh
- `evidence` - Cấu hình evidence
- `logging` - Cấu hình logging

## 📊 Sử dụng API

### Kiểm tra claim

```bash
curl -X POST http://localhost:8005/check \
  -H "Content-Type: application/json" \
  -d '{"claim": "Việt Nam có 63 tỉnh thành"}'
```

### Response format

```json
{
  "claim": "Việt Nam có 63 tỉnh thành",
  "verdict": "SUPPORTED",
  "confidence": 0.9774,
  "evidence_count": 5,
  "evidence": [...],
  "processing_time": 12.5
}
```

### Verdict values

| Verdict | Ý nghĩa |
|---------|---------|
| `SUPPORTED` | Thông tin được xác nhận đúng |
| `REFUTED` | Thông tin bị bác bỏ |
| `NEITHER` | Không đủ bằng chứng |

## 🐛 Xử lý lỗi

### Port đang bị chiếm

```powershell
# Kiểm tra port
netstat -ano | findstr :8005

# Kill process
taskkill /PID <process_id> /F
```

### GPU không nhận

```bash
python -c "import torch; print(torch.cuda.is_available())"
```

### Model không tải được

Kiểm tra cache folder: `D:\huggingface_cache`

## 📁 Files quan trọng

| File | Mô tả |
|------|-------|
| `vietnamese-fact-checker/src/core/system_config.py` | Cấu hình hệ thống |
| `vietnamese-fact-checker/src/services/fact_checker.py` | Logic chính |
| `vietnamese-fact-checker/src/api/main.py` | API endpoints |

## 📞 Ports

| Service | Port | URL |
|---------|------|-----|
| Fact Checker | 8005 | http://localhost:8005 |
| Translation | 8003 | http://localhost:8003 |
| MiniCheck | 8002 | http://localhost:8002 |
| Brave Search | 8004 | http://localhost:8004 |

---

**Version**: 1.0  
**Last Updated**: 2026-02-06
