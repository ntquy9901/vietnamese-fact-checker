#!/usr/bin/env python3
"""
Final Brave Search Server - Working 20 words truncation
"""

from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict, Optional
import aiohttp
import asyncio
import os
from dotenv import load_dotenv

app = FastAPI(title="Final Brave Search Server", version="1.0.0")

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
        """Search using Brave Search API - FINAL WORKING VERSION"""
        if not self.api_key or self.api_key == "your_brave_api_key_here":
            raise ValueError("Brave Search API key is required. Please set BRAVE_SEARCH_API_KEY environment variable.")
        
        try:
            # DIRECT TRUNCATION - Apply immediately
            words = query.split()
            original_count = len(words)
            
            if original_count > 20:
                query = ' '.join(words[:20])
                print(f"TRUNCATED: {original_count} -> {len(query.split())} words")
                print(f"NEW QUERY: {query}")
            
            # Remove -site filters - IMPROVED LOGIC
            original_query = query
            while "-site:" in query:
                # Find first -site: occurrence
                site_index = query.find("-site:")
                if site_index == -1:
                    break
                
                # Find next space after -site: to remove the entire filter
                next_space = query.find(" ", site_index)
                if next_space == -1:
                    # No space after -site:, remove everything after it
                    query = query[:site_index].strip()
                else:
                    # Remove from -site: to next space
                    query = query[:site_index] + query[next_space:]
                
                query = query.strip()
            
            if query != original_query:
                print(f"REMOVED -site filters")
                print(f"BEFORE: {original_query[:80]}...")
                print(f"AFTER:  {query[:80]}...")
            
            print(f"FINAL QUERY: {query}")
            print(f"FINAL WORDS: {len(query.split())}")
            
            headers = {
                "Accept": "application/json",
                "Accept-Encoding": "gzip",
                "X-Subscription-Token": self.api_key
            }
            
            params = {
                "q": query,
                "count": limit
            }
            
            print(f"MAKING REQUEST TO: {self.base_url}")
            print(f"PARAMS: {params}")
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    self.base_url,
                    headers=headers,
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    
                    print(f"RESPONSE STATUS: {response.status}")
                    
                    if response.status == 200:
                        data = await response.json()
                        print(f"RESPONSE KEYS: {list(data.keys())}")
                        
                        results = []
                        
                        if "web" in data and "results" in data["web"]:
                            web_results = data["web"]["results"]
                            print(f"FOUND {len(web_results)} WEB RESULTS")
                            
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
                                print(f"RESULT {i+1}: {result['title'][:50]}...")
                        else:
                            print("NO WEB RESULTS FOUND")
                        
                        print(f"RETURNING {len(results)} RESULTS")
                        return results
                    else:
                        error_text = await response.text()
                        print(f"HTTP ERROR {response.status}: {error_text}")
                        return []
        except Exception as e:
            print(f"EXCEPTION: {e}")
            return []

# Global search client
search_client = BraveSearchClient()

@app.get("/")
async def root():
    return {
        "status": "healthy",
        "search_engine": "Brave Search",
        "api_key_configured": bool(search_client.api_key and search_client.api_key != "your_brave_api_key_here"),
        "message": "Final Brave Search Server - Working 20 words truncation"
    }

@app.post("/search")
async def search(request: SearchRequest):
    """Search using Brave Search API - FINAL WORKING VERSION"""
    start_time = asyncio.get_event_loop().time()
    
    print(f"SEARCH REQUEST: {request.query[:50]}...")
    print(f"ORIGINAL WORDS: {len(request.query.split())}")
    
    results = await search_client.search(
        query=request.query,
        limit=request.limit or 5
    )
    
    processing_time = asyncio.get_event_loop().time() - start_time
    
    print(f"SEARCH COMPLETED: {len(results)} results in {processing_time:.2f}s")
    
    return SearchResponse(
        query=request.query,
        results=results,
        count=len(results),
        processing_time=processing_time,
        search_engine="Brave Search"
    )

@app.post("/search_vietnamese")
async def search_vietnamese(request: SearchRequest):
    """Search Vietnamese content specifically - FINAL WORKING VERSION"""
    return await search(request)

if __name__ == "__main__":
    import uvicorn
    print("Starting Final Brave Search Server")
    print("Server will be available at: http://localhost:8004")
    print("BRAVE_SEARCH_API_KEY environment variable is REQUIRED")
    print("Feature: Working 20 words truncation for Vietnamese queries")
    uvicorn.run(app, host="0.0.0.0", port=8004)
