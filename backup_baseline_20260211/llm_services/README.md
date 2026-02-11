# LLM Services for Vietnamese Fact Checker

## Overview

This folder contains LLM-based services for the Vietnamese Fact Checker system.

## Services

### 1. Qwen Service (Port 8009)
- **Purpose**: Direct Qwen2.5-7B model inference
- **Technology**: HuggingFace Transformers
- **Cache**: D:/huggingface_cache
- **GPU**: CUDA acceleration

#### Files:
- `llm_service.py` - Main LLM service
- `llm_requirements.txt` - Dependencies
- `start_llm_service.py` - Startup script

#### API Endpoints:
- `GET /` - Health check
- `GET /health` - Detailed health
- `POST /generate` - Generate text
- `POST /test` - Test endpoint
- `POST /vietnamese-test` - Vietnamese test

### 2. Decomposer Service (Port 8006)
- **Purpose**: Decompose complex claims into sub-claims
- **Technology**: FastAPI + Qwen2.5-7B
- **Function**: Claim analysis and entity extraction

#### Files:
- `decomposer_service.py` - Main decomposer service
- `start_decomposer_service.py` - Startup script

#### API Endpoints:
- `GET /` - Health check
- `GET /health` - Detailed health
- `POST /decompose` - Decompose claim
- `POST /test` - Test with sample claim
- `POST /vietnamese-test` - Vietnamese political claim test

## Installation

### Prerequisites
- Python 3.10+
- CUDA-compatible GPU (recommended)
- 8GB+ GPU memory for Qwen2.5-7B

### Setup

1. **Install dependencies:**
```bash
cd d:/bmad/llm_services/qwen_service
pip install -r llm_requirements.txt
```

2. **Start services:**
```bash
# Start Qwen Service
cd d:/bmad/llm_services/qwen_service
python start_llm_service.py

# Start Decomposer Service (in another terminal)
cd d:/bmad/llm_services/decomposer_service
python start_decomposer_service.py
```

## Usage

### Qwen Service Example
```bash
curl -X POST http://localhost:8009/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Hello, how are you?",
    "temperature": 0.1,
    "max_tokens": 100
  }'
```

### Decomposer Service Example
```bash
curl -X POST http://localhost:8006/decompose \
  -H "Content-Type: application/json" \
  -d '{
    "claim": "Việt Nam có 63 tỉnh thành và là nước nông nghiệp phát triển",
    "language": "vietnamese",
    "max_sub_claims": 3
  }'
```

## Architecture

```
LLM Services/
├── qwen_service/           # Qwen2.5-7B LLM Service
│   ├── llm_service.py
│   ├── llm_requirements.txt
│   └── start_llm_service.py
├── decomposer_service/      # Claim Decomposer Service
│   ├── decomposer_service.py
│   └── start_decomposer_service.py
└── README.md               # This file
```

## Integration with Main System

The LLM services integrate with the main Vietnamese Fact Checker system:

1. **Fact Checker** calls **Decomposer Service** for claim analysis
2. **Decomposer Service** calls **Qwen Service** for LLM inference
3. **Results** are returned to **Fact Checker** for processing

## Performance

- **Qwen2.5-7B**: ~2-5 seconds per generation
- **Decomposer**: ~5-10 seconds per claim analysis
- **Memory Usage**: ~7GB VRAM for Qwen2.5-7B

## Troubleshooting

### Common Issues

1. **Out of Memory**: Reduce max_tokens or use CPU
2. **Service Not Starting**: Check GPU availability
3. **Slow Response**: Verify CUDA installation

### Health Checks

```bash
# Check Qwen Service
curl http://localhost:8009/health

# Check Decomposer Service
curl http://localhost:8006/health
```

## Future Enhancements

- **Ranker Service** (Port 8007) - Evidence ranking
- **Reconciliation Service** (Port 8008) - Verdict reconciliation
- **Batch Processing** - Multiple claims processing
- **Model Optimization** - Quantization, caching

---

**Version**: 1.0  
**Last Updated**: 2026-02-07  
**Status**: Production Ready
