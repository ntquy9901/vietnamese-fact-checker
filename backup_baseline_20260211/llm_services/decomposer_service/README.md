# Decomposer Service

## Overview

Claim decomposition service that breaks complex Vietnamese claims into simpler, verifiable sub-claims using Qwen2.5-7B LLM.

## Purpose

- **Claim Analysis**: Decompose complex claims into sub-claims
- **Entity Extraction**: Identify key entities and concepts
- **Complexity Assessment**: Evaluate claim complexity
- **Vietnamese Support**: Optimized for Vietnamese language processing

## Files

- `decomposer_service.py` - Main service implementation
- `start_decomposer_service.py` - Startup script
- `README.md` - This documentation

## Features

### Decomposition Capabilities
- **Multi-claim Split**: Break complex claims into 2-5 sub-claims
- **Entity Recognition**: Extract people, places, organizations
- **Complexity Scoring**: Rate claim difficulty (0-1 scale)
- **Confidence Assessment**: Evaluate decomposition quality

### Processing Pipeline
1. **Input**: Vietnamese claim text
2. **LLM Analysis**: Use Qwen2.5-7B for decomposition
3. **JSON Parsing**: Extract structured results
4. **Validation**: Ensure output quality
5. **Response**: Return structured decomposition

## Installation

### Prerequisites
- Qwen2.5-7B LLM Service running on port 8009
- Python 3.10+
- FastAPI and dependencies

### Setup

1. **Start LLM Service first:**
```bash
cd ../qwen_service
python start_llm_service.py
```

2. **Start Decomposer Service:**
```bash
python start_decomposer_service.py
```

## API Endpoints

### Health Check
```bash
GET http://localhost:8006/health
```

### Decompose Claim
```bash
POST http://localhost:8006/decompose
Content-Type: application/json

{
    "claim": "Viet Nam có 63 tỉnh thành và là nước nông nghiệp phát triển",
    "language": "vietnamese",
    "max_sub_claims": 3
}
```

### Test Endpoints
```bash
# General test
curl http://localhost:8006/test

# Vietnamese political claim test
curl http://localhost:8006/vietnamese-test
```

## Request/Response Format

### Request
```json
{
    "claim": "Complex Vietnamese claim here",
    "language": "vietnamese",
    "max_sub_claims": 5
}
```

### Response
```json
{
    "original_claim": "Viet Nam có 63 tỉnh thành và là nước nông nghiệp phát triển",
    "sub_claims": [
        {
            "text": "Viet Nam có 63 tỉnh thành",
            "confidence": 0.95,
            "entities": ["Viet Nam", "63 tỉnh thành"],
            "complexity_score": 0.3
        },
        {
            "text": "Viet Nam là nước nông nghiệp phát triển",
            "confidence": 0.87,
            "entities": ["Viet Nam", "nông nghiệp"],
            "complexity_score": 0.4
        }
    ],
    "entities": ["Viet Nam", "63 tỉnh thành", "nông nghiệp"],
    "complexity_score": 0.6,
    "processing_time": 3.2,
    "success": true
}
```

## Decomposition Logic

### Prompt Engineering
The service uses carefully crafted prompts to ensure:

1. **Clear Instructions**: Specific decomposition requirements
2. **Format Consistency**: JSON output structure
3. **Quality Control**: Confidence and complexity scoring
4. **Vietnamese Context**: Language-specific processing

### Quality Metrics
- **Confidence**: 0.0-1.0 scale for each sub-claim
- **Complexity**: 0.0-1.0 scale for overall claim
- **Entity Coverage**: List of identified entities
- **Processing Time**: Performance measurement

## Integration

### With Main Fact Checker
```python
# In fact_checker.py
import requests

response = requests.post(
    "http://localhost:8006/decompose",
    json={
        "claim": claim_text,
        "language": "vietnamese"
    }
)

decomposition = response.json()
sub_claims = decomposition["sub_claims"]
```

### Pipeline Integration
1. **Input**: Complex claim from user
2. **Decompose**: Break into sub-claims
3. **Process**: Verify each sub-claim individually
4. **Aggregate**: Combine results

## Examples

### Political Claims
```
Input: "Chủ tịch Hồ Chí Minh đã tuyên bố độc lập Việt Nam vào ngày 2 tháng 9 năm 1945 tại Hà Nội"

Output:
- "Chủ tịch Hồ Chí Minh đã tuyên bố độc lập Việt Nam"
- "Việt Nam độc lập vào ngày 2 tháng 9 năm 1945"
- "Sự kiện tuyên bố diễn ra tại Hà Nội"
```

### Geographic Claims
```
Input: "Hà Nội là thủ đô của Việt Nam và có dân số hơn 8 triệu người"

Output:
- "Hà Nội là thủ đô của Việt Nam"
- "Hà Nội có dân số hơn 8 triệu người"
```

### Economic Claims
```
Input: "Việt Nam là nước nông nghiệp phát triển với GDP tăng trưởng 7% mỗi năm"

Output:
- "Việt Nam là nước nông nghiệp phát triển"
- "GDP Việt Nam tăng trưởng 7% mỗi năm"
```

## Performance

### Benchmarks
- **Simple Claims**: ~2-3 seconds
- **Complex Claims**: ~5-8 seconds
- **Multi-claim**: ~8-12 seconds
- **Entity Extraction**: Included in processing time

### Optimization
- **Batch Processing**: Multiple sub-claims in parallel
- **Caching**: Decomposition results for repeated claims
- **Model Tuning**: Optimized prompts for faster processing

## Troubleshooting

### Common Issues

**LLM Service Not Available**
```bash
curl http://localhost:8009/health
```

**JSON Parsing Failed**
- Check LLM response format
- Verify prompt structure
- Review entity extraction

**Poor Decomposition Quality**
- Adjust prompt parameters
- Increase max_sub_claims limit
- Review confidence scores

### Debug Mode
```bash
# Check service logs
python start_decomposer_service.py

# Test with specific claim
curl -X POST http://localhost:8006/decompose \
  -H "Content-Type: application/json" \
  -d '{"claim": "Test claim", "language": "vietnamese"}'
```

## Configuration

### Service Settings
- **Port**: 8006
- **LLM Service**: http://localhost:8009
- **Default Language**: vietnamese
- **Max Sub-Claims**: 5

### Prompt Customization
Edit the `decomposition_prompt` in `decomposer_service.py` to:
- Adjust decomposition criteria
- Modify entity extraction rules
- Change complexity scoring logic

---

**Service Port**: 8006  
**Dependencies**: Qwen Service (8009)  
**Status**: Production Ready
