#!/usr/bin/env python3
"""
Brave Search Final V2 - Fixed truncation for long queries
"""

from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict, Optional
import aiohttp
import asyncio
import os
from dotenv import load_dotenv

app = FastAPI(title="Brave Search Final V2", version="2.0.0")

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
        """Search using Brave Search API - V2 WITH PROPER TRUNCATION"""
        if not self.api_key or self.api_key == "your_brave_api_key_here":
            raise ValueError("Brave Search API key is required. Please set BRAVE_SEARCH_API_KEY environment variable.")
        
        try:
            print(f"🔍 BRAVE SEARCH V2 DEBUG:")
            print(f"   📥 Original Query: {query[:100]}...")
            print(f"   📏 Original Length: {len(query)} chars")
            print(f"   📝 Original Words: {len(query.split())}")
            
            # STEP 1: Remove -site filters FIRST
            original_query = query
            while "-site:" in query:
                site_index = query.find("-site:")
                if site_index == -1:
                    break
                
                next_space = query.find(" ", site_index)
                if next_space == -1:
                    query = query[:site_index].strip()
                else:
                    query = query[:site_index] + query[next_space:]
                query = query.strip()
            
            if query != original_query:
                print(f"   🗑️ Removed -site filters")
            
            # STEP 2: Apply 20 words truncation
            words = query.split()
            original_count = len(words)
            
            if original_count > 20:
                query = ' '.join(words[:20])
                print(f"   ✂️ TRUNCATED: {original_count} -> {len(query.split())} words")
                print(f"   📏 New Length: {len(query)} chars")
            else:
                print(f"   ✅ No truncation needed: {original_count} words")
            
            print(f"   📋 Final Query: {query[:100]}...")
            print(f"   📏 Final Length: {len(query)} chars")
            print(f"   📝 Final Words: {len(query.split())}")
            
            # STEP 3: Make API request
            headers = {
                "Accept": "application/json",
                "Accept-Encoding": "gzip",
                "X-Subscription-Token": self.api_key
            }
            
            params = {
                "q": query,
                "count": limit
            }
            
            print(f"   🌐 Making API request...")
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    self.base_url,
                    headers=headers,
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    
                    print(f"   📊 API Response Status: {response.status}")
                    
                    if response.status == 200:
                        data = await response.json()
                        print(f"   📄 Response keys: {list(data.keys())}")
                        
                        results = []
                        
                        if "web" in data and "results" in data["web"]:
                            web_results = data["web"]["results"]
                            print(f"   📊 Web results count: {len(web_results)}")
                            
                            for i, item in enumerate(web_results):
                                result = {
                                    "title": item.get("title", ""),
                                    "url": item.get("url", ""),
                                    "snippet": item.get("description", ""),
                                    "content": item.get("description", ""),
                                    "published_date": item.get("age", ""),
                                    "language": "vi"
                                }
                                results.append(result)
                                print(f"   📄 Result {i+1}: {result['title'][:50]}...")
                        else:
                            print(f"   ❌ No web results found")
                        
                        print(f"   ✅ Returning {len(results)} results")
                        return results
                    else:
                        error_text = await response.text()
                        print(f"   ❌ HTTP Error {response.status}: {error_text}")
                        return []
        except Exception as e:
            print(f"   ❌ Exception: {e}")
            return []

# Global search client
search_client = BraveSearchClient()

@app.get("/")
async def root():
    return {
        "status": "healthy",
        "search_engine": "Brave Search V2",
        "api_key_configured": bool(search_client.api_key and search_client.api_key != "your_brave_api_key_here"),
        "message": "Brave Search V2 - Fixed truncation for long queries",
        "features": ["20 words truncation", "-site filter removal", "Vietnamese support"]
    }

@app.post("/search")
async def search(request: SearchRequest):
    """Search using Brave Search API - V2"""
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
        search_engine="Brave Search V2"
    )

@app.post("/search_vietnamese")
async def search_vietnamese(request: SearchRequest):
    """Search Vietnamese content specifically - V2"""
    return await search(request)

if __name__ == "__main__":
    import uvicorn
    print("Starting Brave Search Final V2")
    print("Server will be available at: http://localhost:8004")
    print("BRAVE_SEARCH_API_KEY environment variable is REQUIRED")
    print("Features: 20 words truncation + -site filter removal + Vietnamese support")
    uvicorn.run(app, host="0.0.0.0", port=8004)
