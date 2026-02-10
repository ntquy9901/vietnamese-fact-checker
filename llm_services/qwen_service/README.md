# Qwen2.5-7B LLM Service

## Overview

Direct HuggingFace Transformers integration for Qwen2.5-7B model without Ollama dependency.

## Features

- **Direct Model Access**: Uses HuggingFace Transformers
- **GPU Acceleration**: CUDA support with automatic fallback to CPU
- **Cache Management**: Models cached in D:/huggingface_cache
- **FastAPI Interface**: RESTful API endpoints
- **Vietnamese Support**: Optimized for Vietnamese text generation

## Files

- `llm_service.py` - Main service implementation
- `llm_requirements.txt` - Python dependencies
- `start_llm_service.py` - Startup script
- `README.md` - This documentation

## Installation

### Requirements
- Python 3.10+
- CUDA-compatible GPU (recommended)
- 8GB+ GPU memory for optimal performance

### Setup

1. **Install dependencies:**
```bash
pip install -r llm_requirements.txt
```

2. **Start service:**
```bash
python start_llm_service.py
```

## API Endpoints

### Health Check
```bash
GET http://localhost:8009/health
```

### Generate Text
```bash
POST http://localhost:8009/generate
Content-Type: application/json

{
    "prompt": "Your text here",
    "temperature": 0.1,
    "max_tokens": 1000
}
```

### Test Endpoints
```bash
# Basic test
curl http://localhost:8009/test

# Vietnamese test
curl http://localhost:8009/vietnamese-test
```

## Configuration

### Model Settings
- **Default Model**: Qwen/Qwen2.5-7B
- **Cache Directory**: D:/huggingface_cache
- **Device**: Auto-detect (CUDA > CPU)
- **Data Type**: float16 (GPU) / float32 (CPU)

### Generation Parameters
- **Temperature**: 0.1 (default, 0.0-1.0)
- **Max Tokens**: 1000 (default)
- **Do Sample**: true (default)

## Performance

### Benchmarks
- **GPU (RTX 4060)**: ~2-3 seconds per generation
- **CPU**: ~10-15 seconds per generation
- **Memory Usage**: ~7GB VRAM (GPU)

### Optimization Tips
1. Use lower `max_tokens` for faster responses
2. Set `temperature=0` for deterministic output
3. Batch multiple requests when possible

## Troubleshooting

### Common Issues

**Model Loading Failed**
```bash
# Check GPU availability
python -c "import torch; print(torch.cuda.is_available())"

# Check cache directory
ls D:/huggingface_cache
```

**Service Not Responding**
```bash
# Check if service is running
curl http://localhost:8009/health

# Check logs
python start_llm_service.py
```

**Out of Memory**
```bash
# Reduce max_tokens in request
# Or use CPU instead of GPU
```

## Integration

### With Decomposer Service
The Decomposer Service calls this service for LLM inference:

```python
# In decomposer_service.py
import requests

response = requests.post(
    "http://localhost:8009/generate",
    json={
        "prompt": decomposition_prompt,
        "temperature": 0.1,
        "max_tokens": 500
    }
)
```

### Direct Usage
```python
from llm_service import QwenService

service = QwenService()
await service.load_model()
result = await service.generate_response("Hello world")
```

## Model Information

- **Model**: Qwen/Qwen2.5-7B
- **Size**: 7.7B parameters
- **Architecture**: Transformer-based
- **Training**: Multilingual, including Vietnamese
- **License**: Apache 2.0

## Cache Location

Models are cached in: `D:/huggingface_cache/models/Qwen--Qwen2.5-7B/`

To clear cache:
```bash
rm -rf D:/huggingface_cache/models/Qwen--Qwen2.5-7B/
```

---

**Service Port**: 8009  
**Status**: Production Ready
