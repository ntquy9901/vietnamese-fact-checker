#!/usr/bin/env python3
"""
Simple Brave Search Server - 20 words truncation
"""

from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict, Optional
import aiohttp
import asyncio
import os
from dotenv import load_dotenv

app = FastAPI(title="Simple Brave Search Server", version="1.0.0")

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
    
    async def search(self, query: str, limit: int = 5) -> List[Dict]:
        """Search using Brave Search API - SIMPLE VERSION"""
        if not self.api_key or self.api_key == "your_brave_api_key_here":
            raise ValueError("Brave Search API key is required. Please set BRAVE_SEARCH_API_KEY environment variable.")
        
        try:
            # SIMPLE 20 WORDS TRUNCATION
            words = query.split()
            if len(words) > 20:
                query = ' '.join(words[:20])
                print(f"Truncated: {len(words)} -> {len(query.split())} words")
            
            # Remove -site filters
            if "-site:" in query:
                query = query.split("-site:")[0].strip()
                print(f"Removed -site filters")
            
            headers = {
                "Accept": "application/json",
                "Accept-Encoding": "gzip",
                "X-Subscription-Token": self.api_key
            }
            
            params = {
                "q": query,
                "count": limit
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    self.base_url,
                    headers=headers,
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    
                    if response.status == 200:
                        data = await response.json()
                        results = []
                        
                        if "web" in data and "results" in data["web"]:
                            web_results = data["web"]["results"]
                            
                            for item in web_results:
                                result = {
                                    "title": item.get("title", ""),
                                    "url": item.get("url", ""),
                                    "snippet": item.get("description", ""),
                                    "content": item.get("description", ""),
                                    "published_date": item.get("age", ""),
                                    "language": "vi"
                                }
                                results.append(result)
                        
                        return results
                    else:
                        print(f"HTTP Error: {response.status}")
                        return []
        except Exception as e:
            print(f"Exception: {e}")
            return []

# Global search client
search_client = BraveSearchClient()

@app.get("/")
async def root():
    return {
        "status": "healthy",
        "search_engine": "Brave Search",
        "api_key_configured": bool(search_client.api_key and search_client.api_key != "your_brave_api_key_here"),
        "message": "Simple Brave Search Server - 20 words truncation"
    }

@app.post("/search")
async def search(request: SearchRequest):
    """Search using Brave Search API - SIMPLE VERSION"""
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
    """Search Vietnamese content specifically - SIMPLE VERSION"""
    return await search(request)

if __name__ == "__main__":
    import uvicorn
    print("Starting Simple Brave Search Server")
    print("Server will be available at: http://localhost:8004")
    print("BRAVE_SEARCH_API_KEY environment variable is REQUIRED")
    print("Feature: 20 words truncation for Vietnamese queries")
    uvicorn.run(app, host="0.0.0.0", port=8004)
