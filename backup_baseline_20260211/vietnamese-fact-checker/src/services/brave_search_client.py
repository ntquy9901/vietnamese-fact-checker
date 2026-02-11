"""
Brave Search Client - Uses Brave Search Baseline API
Now with configurable source filtering and re-ranking support.
"""

import aiohttp
import asyncio
from typing import List, Dict, Optional
import json
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.system_config import brave_config, logging_config

class BraveSearchClient:
    """Client for Brave Search Baseline API with source filtering"""
    
    def __init__(self):
        self.config = brave_config
        self.log_config = logging_config
        self.api_url = f"{self.config.proxy_url}/search"
        self.health_check_url = f"{self.config.proxy_url}/"
        self.timeout = float(self.config.timeout)
        
    async def check_health(self) -> bool:
        """Check if Brave Search baseline is running"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.health_check_url, timeout=5) as response:
                    return response.status == 200
        except:
            return False
    
    def _build_filtered_query(self, query: str) -> str:
        """Build query with source filtering based on config"""
        if self.config.source_filter_mode == "exclude":
            # Add -site: exclusions for untrusted sources
            exclusions = " ".join([f"-site:{s}" for s in self.config.untrusted_sources])
            filtered_query = f"{query} {exclusions}"
            
            if self.log_config.log_search_results:
                print(f"   [CONFIG] Source filter mode: exclude")
                print(f"   [CONFIG] Excluding {len(self.config.untrusted_sources)} untrusted sources")
            
            return filtered_query
        
        elif self.config.source_filter_mode == "boost":
            # Add site: preferences for trusted sources (OR query)
            if self.config.trusted_sources:
                trusted = " OR ".join([f"site:{s}" for s in self.config.trusted_sources[:5]])
                filtered_query = f"{query} ({trusted})"
                
                if self.log_config.log_search_results:
                    print(f"   [CONFIG] Source filter mode: boost trusted")
                
                return filtered_query
        
        # Default: no filtering
        return query
    
    def _build_goggles(self) -> Optional[str]:
        """Build Goggles rules for re-ranking"""
        if not self.config.goggles_enabled:
            return None
        
        rules = []
        
        # Boost trusted sources
        for source in self.config.trusted_sources:
            rules.append(f"$boost={self.config.goggles_boost_trusted},site={source}")
        
        # Downrank or discard untrusted sources
        for source in self.config.untrusted_sources:
            if self.config.goggles_discard_blacklist:
                rules.append(f"$discard,site={source}")
            else:
                rules.append(f"$downrank={self.config.goggles_downrank_untrusted},site={source}")
        
        if self.log_config.log_search_results:
            print(f"   [CONFIG] Goggles enabled: {len(rules)} rules")
        
        return "\n".join(rules)
    
    async def search_vietnamese(self, query: str) -> List[Dict]:
        """Search for Vietnamese content using Brave Search baseline API"""
        try:
            # Apply source filtering
            filtered_query = self._build_filtered_query(query)
            
            if self.log_config.log_search_results:
                print(f"   [QUERY] Original query: {query}")
                if filtered_query != query:
                    print(f"   [QUERY] Filtered query: {filtered_query[:100]}...")
            
            request_data = {
                "query": filtered_query,
                "count": self.config.max_results,
                "language": self.config.language,
                "country": self.config.country,
            }
            
            # Add freshness filter if configured
            if self.config.freshness:
                request_data["freshness"] = self.config.freshness
            
            # Add extra snippets if enabled
            if self.config.extra_snippets:
                request_data["extra_snippets"] = True
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.api_url,
                    json=request_data,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        parsed = self._parse_search_results(result)
                        
                        if self.log_config.log_search_results:
                            print(f"   [OK] Retrieved {len(parsed)} results")
                            for i, r in enumerate(parsed, 1):
                                domain = r.get('url', '').split('/')[2] if '/' in r.get('url', '') else 'unknown'
                                print(f"      {i}. [{domain}] {r.get('title', '')[:50]}...")
                        
                        return parsed
                    else:
                        error_text = await response.text()
                        print(f"[ERROR] Brave Search API error: {response.status} - {error_text}")
                        return []
                        
        except aiohttp.ClientError as e:
            print(f"[ERROR] Brave Search network error: {str(e)}")
            return []
        except Exception as e:
            print(f"[ERROR] Brave Search unexpected error: {str(e)}")
            return []
    
    def _parse_search_results(self, result: Dict) -> List[Dict]:
        """Parse Brave Search results to standard format"""
        try:
            results = result.get("results", [])
            parsed_results = []
            
            for item in results:
                parsed_item = {
                    "title": item.get("title", ""),
                    "url": item.get("url", ""),
                    "snippet": item.get("snippet", ""),
                    "content": item.get("snippet", "")
                }
                
                # Add extra snippets if available
                if self.config.extra_snippets and "extra_snippets" in item:
                    parsed_item["extra_snippets"] = item.get("extra_snippets", [])
                
                parsed_results.append(parsed_item)
            
            return parsed_results
            
        except Exception as e:
            print(f"[ERROR] Error parsing search results: {str(e)}")
            return []
    
    def get_config_summary(self) -> Dict:
        """Get current configuration summary"""
        return {
            "api_url": self.api_url,
            "timeout": self.timeout,
            "max_results": self.config.max_results,
            "country": self.config.country,
            "language": self.config.language,
            "source_filter_mode": self.config.source_filter_mode,
            "trusted_sources_count": len(self.config.trusted_sources),
            "untrusted_sources_count": len(self.config.untrusted_sources),
            "goggles_enabled": self.config.goggles_enabled,
            "freshness": self.config.freshness,
            "extra_snippets": self.config.extra_snippets,
        }

# Singleton instance
brave_search_client = BraveSearchClient()
