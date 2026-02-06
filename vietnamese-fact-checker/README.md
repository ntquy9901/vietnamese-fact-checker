# Vietnamese Fact Checker

A Vietnamese fact-checking system that combines MiniCheck with web search and bilingual translation to verify Vietnamese claims.

## Architecture

```
Vietnamese Claim → Vietnamese Web Search → Evidence Fetch → Translate to English → MiniCheck → Translate Result → Vietnamese Response
```

## Features

- **Vietnamese Input**: Supports Vietnamese claims with proper normalization
- **Web Search**: Multiple search providers (SerpAPI, Google, DuckDuckGo)
- **Bilingual Translation**: Vietnamese ↔ English using NLLB model
- **MiniCheck Integration**: Uses MiniCheck API for fact verification
- **Parallel Processing**: Optimized for <6 second response time
- **Error Handling**: Graceful fallbacks and timeout handling

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up API Keys

Copy `.env.example` to `.env` and configure your search API:

```bash
cp .env.example .env
```

Edit `.env` and add your API key:
- **SerpAPI** (recommended): Get key from https://serpapi.com/
- **Google Custom Search**: Get key from https://console.cloud.google.com/
- **DuckDuckGo**: Free (no key needed, but less reliable)

### 3. Start MiniCheck API

MiniCheck needs to be running separately. See: https://github.com/Liyan06/MiniCheck

```bash
# Example MiniCheck API server
cd minicheck
python api_server.py  # Runs on http://localhost:8001
```

### 4. Start Vietnamese Fact Checker

```bash
cd src
python -m api.main
```

The API will be available at `http://localhost:8000`

## API Usage

### Check a Vietnamese Claim

```bash
curl -X POST "http://localhost:8000/check" \
     -H "Content-Type: application/json" \
     -d '{"claim": "Hà Nội là thủ đô của Việt Nam"}'
```

### Response Example

```json
{
  "claim": "Hà Nội là thủ đô của Việt Nam",
  "normalized_claim": "ha noi la thu do cua viet nam",
  "verdict": "SUPPORTED",
  "confidence": 0.85,
  "rationale": "Bằng chứng xác nhận rằng Hà Nội là thủ đô của Việt Nam",
  "evidence": [
    {
      "text": "Hà Nội là thủ đô của nước Cộng hòa xã hội chủ nghĩa Việt Nam...",
      "url": "https://example.com/vietnam-capital",
      "title": "Hà Nội - Thủ đô Việt Nam"
    }
  ],
  "evidence_count": 1,
  "processing_time": 4.2,
  "method": "minicheck_web_search",
  "sources": ["https://example.com/vietnam-capital"],
  "error": null
}
```

### Health Check

```bash
curl http://localhost:8000/health
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SERPAPI_KEY` | SerpAPI key for web search | - |
| `GOOGLE_SEARCH_API_KEY` | Google Search API key | - |
| `GOOGLE_SEARCH_ENGINE_ID` | Google Custom Search Engine ID | - |
| `WEB_SEARCH_TIMEOUT` | Web search timeout (seconds) | 2.0 |
| `EVIDENCE_MAX_CHUNKS` | Maximum evidence chunks | 3 |
| `EVIDENCE_MAX_CHARS` | Maximum characters per chunk | 400 |
| `MAX_TOTAL_TIME` | Maximum total processing time | 6.0 |

### Performance Optimization

The system is optimized for **<6 second response time**:

- **Parallel Translation**: Evidence chunks translated simultaneously
- **Timeout Handling**: Web search and content fetching have strict timeouts
- **Evidence Limits**: Limited to 3 chunks of 400 characters each
- **Error Fallbacks**: Graceful degradation when services fail

## Project Structure

```
vietnamese-fact-checker/
├── src/
│   ├── api/
│   │   ├── main.py              # FastAPI application
│   │   └── schemas.py           # Pydantic models
│   ├── core/
│   │   ├── config.py            # Settings
│   │   └── web_search.py        # Web search client
│   └── services/
│       ├── normalizer.py        # Vietnamese text normalization
│       ├── translator.py        # NLLB translation
│       ├── evidence_fetcher.py  # Content extraction
│       ├── minicheck_client.py  # MiniCheck API client
│       └── fact_checker.py      # Main orchestration
├── requirements.txt
├── .env.example
└── README.md
```

## Dependencies

- **FastAPI**: Web framework
- **Transformers**: NLLB translation model
- **aiohttp**: Async HTTP client
- **BeautifulSoup**: HTML parsing
- **Torch**: PyTorch for NLLB model

## Troubleshooting

### Common Issues

1. **MiniCheck API not responding**
   - Ensure MiniCheck server is running on `http://localhost:8001`
   - Check the `MINICHECK_API_URL` in `.env`

2. **Web search not working**
   - Verify API keys are correctly set in `.env`
   - Try different search providers (SerpAPI, Google, DuckDuckGo)

3. **Slow response time**
   - Check internet connection
   - Reduce `EVIDENCE_MAX_CHUNKS` or `WEB_SEARCH_TIMEOUT`
   - Disable `FETCH_FULL_CONTENT` if not needed

4. **Translation errors**
   - Ensure sufficient RAM for NLLB model (~2GB)
   - Check `NLLB_MODEL_PATH` is correct

### Performance Tips

- Use SerpAPI for most reliable results
- Limit evidence chunks for faster processing
- Disable full content fetching if snippets are sufficient
- Use SSD for better model loading performance

## License

MIT License

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request
