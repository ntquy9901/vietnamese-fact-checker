#!/usr/bin/env python3
"""
Brave Search Baseline Server - Standalone Web Search API
"""

from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict, Optional
import aiohttp
import asyncio
from urllib.parse import quote
import os
from dotenv import load_dotenv

app = FastAPI(title="Brave Search Baseline API", version="1.0.0")

# Load environment variables
load_dotenv()

class SearchRequest(BaseModel):
    query: str
    limit: Optional[int] = 5
    timeout: Optional[float] = 2.0

class SearchResponse(BaseModel):
    query: str
    results: List[Dict]
    count: int
    processing_time: float
    search_engine: str

class BraveSearchClient:
    def __init__(self):
        self.api_key = os.getenv("BRAVE_SEARCH_API_KEY")
        self.base_url = "https://api.search.brave.com/res/v1/web/search"
        self.timeout = 10.0
        self.min_request_interval = 2.1
        self.last_request_time = 0
    
    async def search(self, query: str, limit: int = 5) -> List[Dict]:
        """Search using Brave Search API - NO MOCK MODE"""
        if not self.api_key or self.api_key == "your_brave_api_key_here":
            raise ValueError("Brave Search API key is required. Please set BRAVE_SEARCH_API_KEY environment variable.")
        
        try:
            # DEBUG: Input parameters
            print("🔍 BRAVE SEARCH DEBUG:")
            print(f"   📥 Query: {query[:200]}...")
            print(f"   📏 Length: {len(query)} chars")
            print(f"   🔢 Limit: {limit}")
            print("   🌐 API: Direct Brave Search - NO RESTRICTIONS")

            # Fix Unicode encoding
            encoded_query = quote(query, safe='')
            print(f"   🔗 Encoded: {encoded_query[:100]}...")

            headers = {
                "Accept": "application/json",
                "Accept-Encoding": "gzip",
                "X-Subscription-Token": self.api_key
            }
            
            params = {
                "q": encoded_query,
                "count": limit
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    self.base_url,
                    headers=headers,
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    self.last_request_time = asyncio.get_event_loop().time()
                    
                    if response.status == 200:
                        data = await response.json()
                        print(f"🔍 API RESPONSE DEBUG:")
                        print(f"   📄 Response keys: {list(data.keys())}")
                        
                        results = self._parse_brave_results(data)
                        
                        # DEBUG: Response details
                        print(f"   📥 Response status: {response.status}")
                        print(f"   📊 Results found: {len(results)}")
                        
                        if results:
                            print(f"   📄 Sample results:")
                            for i, result in enumerate(results[:2]):
                                print(f"      {i+1}. {result.get('title', '')[:50]}...")
                        
                        return results
                    else:
                        print(f"   ❌ HTTP Error: {response.status}")
                        return []
        except Exception as e:
            print(f"❌ Exception: {e}")
            return []
    
    def _parse_brave_results(self, data: Dict) -> List[Dict]:
        """Parse Brave Search results"""
        results = []
        
        print(f"🔍 PARSING DEBUG:")
        print(f"   📄 Data keys: {list(data.keys())}")
        
        if "web" in data:
            web_data = data["web"]
            print(f"   🌐 Web keys: {list(web_data.keys())}")
            
            if "results" in web_data:
                web_results = web_data["results"]
                print(f"   📊 Web results count: {len(web_results)}")
                
                for i, item in enumerate(web_results):
                    print(f"   📄 Item {i+1}: {item.get('title', '')[:30]}...")
                    
                    result = {
                        "title": item.get("title", ""),
                        "url": item.get("url", ""),
                        "snippet": item.get("description", ""),
                        "content": item.get("description", ""),
                        "published_date": item.get("age", ""),
                        "language": "vi"
                    }
                    results.append(result)
            else:
                print(f"   ❌ No 'results' key in web data")
        else:
            print(f"   ❌ No 'web' key in response")
        
        print(f"   ✅ Parsed {len(results)} results")
        return results

# Global search client
search_client = BraveSearchClient()

@app.get("/")
async def root():
    return {
        "status": "healthy",
        "search_engine": "Brave Search",
        "api_key_configured": bool(search_client.api_key and search_client.api_key != "your_brave_api_key_here"),
        "message": "Brave Search baseline server ready - API key required"
    }

@app.post("/search")
async def search(request: SearchRequest):
    """Search using Brave Search API"""
    start_time = asyncio.get_event_loop().time()
    
    results = await search_client.search(
        query=request.query,
        limit=request.limit or 5
    )
    
    processing_time = asyncio.get_event_loop().time() - start_time
    
    return SearchResponse(
        query=request.query,
        results=results,
        count=len(results),
        processing_time=processing_time,
        search_engine="Brave Search"
    )

@app.post("/search_vietnamese")
async def search_vietnamese(request: SearchRequest):
    """Search Vietnamese content specifically"""
    return await search(request)

if __name__ == "__main__":
    import uvicorn
    print(" Starting Brave Search Baseline Server")
    print(" Server will be available at: http://localhost:8004")
    print(" BRAVE_SEARCH_API_KEY environment variable is REQUIRED")
    print(" No mock mode - real API only")
    uvicorn.run(app, host="0.0.0.0", port=8004)
