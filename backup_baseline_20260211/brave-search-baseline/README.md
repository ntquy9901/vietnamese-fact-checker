# Brave Search Baseline

Standalone Brave Search API server for Vietnamese content search.

## Features

- **Search Engine:** Brave Search API
- **Language Support:** Vietnamese optimized
- **API:** RESTful FastAPI server
- **Port:** 8004
- **Mock Mode:** ❌ DISABLED - Real API only

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Configure API key (optional)
cp .env.example .env
# Edit .env with your Brave Search API key

# Start server
python brave_search_server.py

# Test API
curl http://localhost:8004/
curl -X POST http://localhost:8004/search \
  -H "Content-Type: application/json" \
  -d '{"query": "Hà Nội là thủ đô của Việt Nam"}'
```

## API Endpoints

- `GET /` - Health check
- `POST /search` - General search
- `POST /search_vietnamese` - Vietnamese content search

## Configuration

- **API Key:** BRAVE_SEARCH_API_KEY (REQUIRED)
- **Server Port:** 8004
- **Timeout:** 2.0 seconds
- **Rate Limiting:** 2 seconds between requests

## Important Notes

**❌ NO MOCK MODE - This server requires a valid Brave Search API key to function.**

## API Response Format

```json
{
  "query": "search query",
  "results": [
    {
      "title": "Result title",
      "url": "https://example.com",
      "snippet": "Search result snippet",
      "content": "Full content",
      "published_date": "2024",
      "language": "vi"
    }
  ],
  "count": 5,
  "processing_time": 1.23,
  "search_engine": "Brave Search"
}
```
