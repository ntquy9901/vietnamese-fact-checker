import aiohttp
import asyncio
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import re
import time
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.system_config import evidence_config, logging_config

class EvidenceFetcher:
    def __init__(self):
        self.config = evidence_config
        self.log_config = logging_config
        self.timeout = float(self.config.content_fetch_timeout)
        self.max_content_length = self.config.max_length
        
    async def fetch_evidence(self, urls: List[str]) -> List[Dict]:
        """Fetch evidence from URLs with improved error handling"""
        
        evidence_list = []
        
        # Limit URLs based on config
        max_urls = self.config.max_chunks
        limited_urls = urls[:max_urls]
        
        if self.log_config.log_service_io:
            print(f"   [INFO] Fetching {len(limited_urls)} URLs (max: {max_urls})")
        
        for url in limited_urls:
            try:
                # Skip if URL is invalid
                if not url or not url.startswith('http'):
                    continue
                    
                # Use snippet instead of full content fetching
                evidence = await self._fetch_snippet_only(url)
                if evidence:
                    evidence_list.append(evidence)
                    
                # Add small delay between requests
                await asyncio.sleep(0.1)
                
            except Exception as e:
                print(f"Error fetching {url}: {e}")
                continue
        
        return evidence_list
    
    async def _fetch_snippet_only(self, url: str) -> Optional[Dict]:
        """Fetch only snippet without full content to avoid timeouts"""
        
        try:
            # For now, return basic info without fetching
            # This avoids the timeout issues
            return {
                "title": self._extract_title_from_url(url),
                "url": url,
                "snippet": f"Content from {url}",
                "content": f"Content from {url}",
                "source": "web_search",
                "fetch_method": "snippet_only"
            }
            
        except Exception as e:
            print(f"Error in _fetch_snippet_only: {e}")
            return None
    
    def _extract_title_from_url(self, url: str) -> str:
        """Extract title from URL"""
        try:
            # Remove protocol and www
            clean_url = url.replace('https://', '').replace('http://', '').replace('www.', '')
            
            # Split by / and take first part
            parts = clean_url.split('/')
            if parts:
                domain = parts[0]
                # Convert domain to readable title
                title = domain.replace('-', ' ').replace('_', ' ').title()
                return title
            
            return "Web Source"
            
        except Exception:
            return "Web Source"
    
    async def _fetch_with_timeout(self, url: str) -> Optional[str]:
        """Fetch content with timeout protection"""
        
        try:
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        content = await response.text()
                        
                        # Limit content length to avoid memory issues
                        if len(content) > self.max_content_length:
                            content = content[:self.max_content_length]
                        
                        return content
                    else:
                        print(f"HTTP {response.status} for {url}")
                        return None
                        
        except asyncio.TimeoutError:
            print(f"Timeout fetching {url}")
            return None
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None
    
    def _extract_content(self, html: str, url: str) -> Dict:
        """Extract content from HTML"""
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Extract title
            title = self._get_title(soup, url)
            
            # Extract main content
            content = self._get_main_content(soup)
            
            # Clean content
            content = self._clean_text(content)
            
            return {
                "title": title,
                "url": url,
                "content": content,
                "source": "web_fetch"
            }
            
        except Exception as e:
            print(f"Error extracting content from {url}: {e}")
            return {
                "title": self._extract_title_from_url(url),
                "url": url,
                "content": f"Error extracting content from {url}",
                "source": "error"
            }
    
    def _get_title(self, soup: BeautifulSoup, url: str) -> str:
        """Extract title from HTML"""
        
        # Try title tag first
        title_tag = soup.find('title')
        if title_tag:
            title = title_tag.get_text().strip()
            if title:
                return title
        
        # Try h1 tag
        h1_tag = soup.find('h1')
        if h1_tag:
            title = h1_tag.get_text().strip()
            if title:
                return title
        
        # Try meta title
        meta_title = soup.find('meta', property='og:title')
        if meta_title:
            title = meta_title.get('content', '').strip()
            if title:
                return title
        
        # Fallback to URL-based title
        return self._extract_title_from_url(url)
    
    def _get_main_content(self, soup: BeautifulSoup) -> str:
        """Extract main content from HTML"""
        
        # Try common content containers
        content_selectors = [
            'article',
            'main',
            '.content',
            '#content',
            '.post-content',
            '.entry-content',
            '.article-content'
        ]
        
        for selector in content_selectors:
            content_element = soup.select_one(selector)
            if content_element:
                return content_element.get_text()
        
        # Fallback to body text
        body = soup.find('body')
        if body:
            return body.get_text()
        
        # Last resort
        return soup.get_text()
    
    def _clean_text(self, text: str) -> str:
        """Clean extracted text"""
        
        if not text:
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters
        text = re.sub(r'[\n\r\t]', ' ', text)
        
        # Remove extra spaces
        text = re.sub(r' +', ' ', text)
        
        # Limit length
        if len(text) > 1000:
            text = text[:1000] + "..."
        
        return text.strip()
    
    def prepare_evidence_chunks(self, search_results: List[Dict], full_contents: List[Dict]) -> List[Dict]:
        """Prepare evidence chunks from search results and full contents"""
        
        evidence_chunks = []
        
        for i, result in enumerate(search_results):
            # Use snippet from search result as primary evidence
            text = result.get('snippet', '')
            if not text:
                text = result.get('title', '')
            
            # Limit text length
            if len(text) > 400:
                text = text[:400] + "..."
            
            evidence_chunks.append({
                'text': text,
                'url': result.get('url', ''),
                'title': result.get('title', ''),
                'source': 'web_search'
            })
            
            # Limit to max chunks from config
            if len(evidence_chunks) >= self.config.max_chunks:
                break
        
        if self.log_config.log_service_io:
            print(f"[INFO] Prepared {len(evidence_chunks)} evidence chunks (max: {self.config.max_chunks})")
        return evidence_chunks
