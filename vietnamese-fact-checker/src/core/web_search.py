import aiohttp
import asyncio
from typing import List, Dict, Optional
from urllib.parse import quote
from .config import settings
import time

class WebSearchClient:
    def __init__(self):
        self.serpapi_key = settings.serpapi_key
        self.google_api_key = settings.google_search_api_key
        self.google_cse_id = settings.google_search_engine_id
        self.brave_api_key = settings.brave_search_api_key
        self.timeout = settings.web_search_timeout
        self.limit = settings.web_search_limit
        self.last_request_time = 0
        self.min_request_interval = 2.0  # 2 seconds between requests for free plan
    
    async def search_vietnamese(self, query: str) -> List[Dict]:
        """Search for Vietnamese content using Brave Search ONLY"""
        
        print(f"[SEARCH] Searching with Brave Search: {query}")
        
        # Use Brave Search ONLY
        if self.brave_api_key and self.brave_api_key != "your_brave_api_key_here":
            try:
                results = await self._search_brave(query)
                if results:
                    print(f"[OK] Brave Search found {len(results)} results")
                    return results
                else:
                    print(f"[WARN] Brave Search returned no results")
                    return []
            except Exception as e:
                print(f"[ERROR] Brave Search failed: {e}")
                return []
        else:
            print("[ERROR] Brave Search API key not configured")
            return []
    
    async def _search_mock(self, query: str) -> List[Dict]:
        """Mock search for demonstration"""
        mock_data = {
            "Hà Nội là thủ đô của Việt Nam": [
                {
                    "title": "Hanoi - Wikipedia",
                    "url": "https://en.wikipedia.org/wiki/Hanoi",
                    "snippet": "Hanoi is the capital city of Vietnam and the country's second largest city.",
                    "content": "Hanoi is the capital city of Vietnam. It serves as the capital of the country and is an important political center."
                },
                {
                    "title": "Vietnam Capital - Hanoi",
                    "url": "https://example.com/vietnam-capital",
                    "snippet": "Hanoi has been the capital of Vietnam since 1976.",
                    "content": "Hanoi became the capital of Vietnam after the reunification of North and South Vietnam in 1976."
                }
            ],
            "Paris là thủ đô của Pháp": [
                {
                    "title": "Paris - Wikipedia",
                    "url": "https://en.wikipedia.org/wiki/Paris",
                    "snippet": "Paris is the capital and most populous city of France.",
                    "content": "Paris is the capital and most populous city of France, situated on the Seine River in northern France."
                },
                {
                    "title": "France Capital City",
                    "url": "https://example.com/france-capital",
                    "snippet": "Paris has been the capital of France for over 1000 years.",
                    "content": "Paris has served as the capital of France since the Capetian dynasty established it as the seat of power."
                }
            ],
            "Trái đất quay quanh Mặt Trời": [
                {
                    "title": "Earth's Orbit - NASA",
                    "url": "https://solarsystem.nasa.gov/planets/earth/",
                    "snippet": "Earth orbits the Sun once every 365.25 days.",
                    "content": "Earth completes one orbit around the Sun every 365.25 days, which defines our year."
                },
                {
                    "title": "Solar System - Wikipedia",
                    "url": "https://en.wikipedia.org/wiki/Solar_System",
                    "snippet": "The Earth and other planets orbit the Sun.",
                    "content": "The Earth is the third planet from the Sun and orbits around it following Kepler's laws of planetary motion."
                }
            ]
        }
        
        # Try exact match first
        if query in mock_data:
            return mock_data[query]
        
        # Try partial match
        for key, value in mock_data.items():
            if any(word in query.lower() for word in key.lower().split()):
                return value
        
        # Default mock data
        return [
            {
                "title": "Mock Search Result",
                "url": "https://example.com/mock",
                "snippet": f"Mock result for query: {query}",
                "content": f"This is a mock search result for the query: {query}"
            }
        ]
    
    async def _search_brave(self, query: str) -> List[Dict]:
        """Search using Brave Search API with rate limiting"""
        if not self.brave_api_key or self.brave_api_key == "your_brave_api_key_here":
            return []
        
        # Rate limiting: wait minimum interval between requests
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.min_request_interval:
            wait_time = self.min_request_interval - time_since_last
            print(f"[WAIT] Rate limiting: waiting {wait_time:.1f}s...")
            await asyncio.sleep(wait_time)
        
        self.last_request_time = time.time()
        
        url = "https://api.search.brave.com/res/v1/web/search"
        headers = {
            "X-Subscription-Token": self.brave_api_key,
            "Accept": "application/json"
        }
        
        params = {
            "q": query,
            "count": self.limit,
            "text_decorations": "0",
            "safesearch": "moderate"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url, 
                    headers=headers, 
                    params=params, 
                    timeout=aiohttp.ClientTimeout(total=10.0)
                ) as response:
                    
                    print(f"[HTTP] Brave Search API response status: {response.status}")
                    
                    if response.status == 200:
                        data = await response.json()
                        results = []
                        
                        web_results = data.get("web", {}).get("results", [])
                        print(f"[INFO] Brave Search returned {len(web_results)} raw results")
                        
                        for item in web_results:
                            results.append({
                                "title": item.get("title", ""),
                                "url": item.get("url", ""),
                                "snippet": item.get("description", "")
                            })
                        
                        return results
                    elif response.status == 429:
                        error_text = await response.text()
                        print(f"[ERROR] Brave Search rate limited: {error_text}")
                        # Wait longer and retry once
                        await asyncio.sleep(5)
                        return []
                    else:
                        error_text = await response.text()
                        print(f"[ERROR] Brave Search error: {response.status} - {error_text}")
                        return []
                        
        except asyncio.TimeoutError:
            print("[ERROR] Brave Search timeout after 10 seconds")
            return []
        except Exception as e:
            print(f"[ERROR] Brave Search exception: {type(e).__name__}: {e}")
            return []
    
    def _parse_duckduckgo_api_results(self, data: Dict) -> List[Dict]:
        """Parse DuckDuckGo API results"""
        results = []
        
        # DuckDuckGo API returns different structure
        # Check for RelatedTopics (main results)
        related_topics = data.get('RelatedTopics', [])
        
        for topic in related_topics[:self.limit]:
            if 'Text' in topic and 'FirstURL' in topic:
                title = topic.get('Text', '')
                url = topic.get('FirstURL', '')
                
                # Clean up the title
                if title.startswith('['):
                    title = title.split(']', 1)[-1].strip()
                
                results.append({
                    "title": title,
                    "url": url,
                    "snippet": topic.get('Text', '')
                })
        
        # If no related topics, try abstract
        if not results and 'Abstract' in data:
            abstract = data['Abstract']
            abstract_url = data.get('AbstractURL', '')
            abstract_source = data.get('AbstractSource', '')
            
            if abstract:
                results.append({
                    "title": abstract_source or "DuckDuckGo Result",
                    "url": abstract_url,
                    "snippet": abstract
                })
        
        return results
    
    def _parse_serpapi_results(self, data: Dict) -> List[Dict]:
        """Parse SerpAPI results"""
        results = []
        for item in data.get("organic_results", [])[:self.limit]:
            results.append({
                "title": item.get("title", ""),
                "url": item.get("link", ""),
                "snippet": item.get("snippet", "")
            })
        return results
    
    def _parse_google_results(self, data: Dict) -> List[Dict]:
        """Parse Google Custom Search results"""
        results = []
        for item in data.get("items", [])[:self.limit]:
            results.append({
                "title": item.get("title", ""),
                "url": item.get("link", ""),
                "snippet": item.get("snippet", "")
            })
        return results
    
    def _parse_duckduckgo_results(self, html: str) -> List[Dict]:
        """Parse DuckDuckGo HTML results (improved parsing)"""
        import re
        from bs4 import BeautifulSoup
        results = []
        
        try:
            # Try BeautifulSoup parsing first
            soup = BeautifulSoup(html, 'html.parser')
            
            # Find result divs
            result_divs = soup.find_all('div', class_='result')
            
            for result_div in result_divs[:self.limit]:
                # Extract title and link
                title_link = result_div.find('a', class_='result__a')
                if title_link:
                    title = title_link.get_text(strip=True)
                    url = title_link.get('href', '')
                    
                    # Extract snippet
                    snippet_elem = result_div.find('a', class_='result__snippet')
                    snippet = snippet_elem.get_text(strip=True) if snippet_elem else ''
                    
                    if title and url:
                        results.append({
                            "title": title,
                            "url": url,
                            "snippet": snippet
                        })
            
            # If BeautifulSoup didn't work, try regex fallback
            if not results:
                result_pattern = r'<a[^>]*class="result__a"[^>]*href="([^"]*)"[^>]*>(.*?)</a>.*?<a[^>]*class="result__snippet"[^>]*>(.*?)</a>'
                matches = re.findall(result_pattern, html, re.DOTALL | re.IGNORECASE)
                
                for url, title, snippet in matches[:self.limit]:
                    # Clean up HTML entities and tags
                    title = re.sub(r'<[^>]+>', '', title).strip()
                    snippet = re.sub(r'<[^>]+>', '', snippet).strip()
                    url = url.strip()
                    
                    if title and url:
                        results.append({
                            "title": title,
                            "url": url,
                            "snippet": snippet
                        })
        
        except Exception as e:
            print(f"DuckDuckGo parsing error: {e}")
            # Last resort - very simple regex
            simple_pattern = r'<a[^>]*href="([^"]*)"[^>]*>([^<]*)</a>'
            matches = re.findall(simple_pattern, html)[:self.limit]
            
            for url, title in matches:
                if title and url and 'duckduckgo' not in url:
                    results.append({
                        "title": title.strip(),
                        "url": url.strip(),
                        "snippet": ""
                    })
        
        return results
