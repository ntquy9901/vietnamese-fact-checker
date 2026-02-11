"""
Translation Client - Uses Baseline Translation System API
Now with configurable settings and caching support.
"""

import requests
import asyncio
from typing import List, Dict, Optional
from concurrent.futures import ThreadPoolExecutor
import sys
import os
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.system_config import translation_config, logging_config, performance_config

class TranslationClient:
    """Client for Baseline Translation System API with configuration"""
    
    def __init__(self):
        self.config = translation_config
        self.log_config = logging_config
        self.perf_config = performance_config
        
        self.translation_api_url = f"{self.config.api_url}/translate"
        self.batch_translation_api_url = f"{self.config.api_url}/translate_batch"
        self.health_check_url = f"{self.config.api_url}/"
        self.timeout = self.config.timeout
        
        # Simple cache (if enabled)
        self._cache: Dict[str, str] = {}
        self._cache_times: Dict[str, float] = {}
        
    def check_health(self) -> bool:
        """Check if translation system is running"""
        try:
            response = requests.get(self.health_check_url, timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def _get_from_cache(self, text: str) -> Optional[str]:
        """Get translation from cache if enabled and valid"""
        if not self.config.cache_translations:
            return None
        
        if text in self._cache:
            cache_time = self._cache_times.get(text, 0)
            if time.time() - cache_time < self.config.cache_ttl:
                if self.log_config.log_translation_details:
                    print(f"      [CACHE] Cache hit: {text[:30]}...")
                return self._cache[text]
            else:
                # Cache expired
                del self._cache[text]
                del self._cache_times[text]
        return None
    
    def _save_to_cache(self, text: str, translation: str):
        """Save translation to cache if enabled"""
        if self.config.cache_translations:
            self._cache[text] = translation
            self._cache_times[text] = time.time()
    
    def translate_vi_to_en(self, text: str) -> str:
        """Translate Vietnamese to English using baseline API"""
        # Check cache first
        cached = self._get_from_cache(text)
        if cached:
            return cached
        
        try:
            start_time = time.time()
            response = requests.post(
                self.translation_api_url,
                json={"text": text},
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                translation = result.get("english", f"[Translation failed: {text}]")
                
                if self.log_config.log_translation_details:
                    elapsed = time.time() - start_time
                    print(f"      [OK] Translated in {elapsed:.2f}s: {text[:30]}... -> {translation[:30]}...")
                
                self._save_to_cache(text, translation)
                return translation
            else:
                return f"[API error {response.status_code}: {text}]"
                
        except requests.exceptions.Timeout:
            return f"[Translation timeout: {text}]"
        except Exception as e:
            return f"[Translation error: {text}]"
    
    def translate_multiple_vi_to_en(self, texts: List[str]) -> List[str]:
        """Translate multiple Vietnamese texts to English using BATCH API (GPU optimized)"""
        if not texts:
            return []
        
        # Check if batch translation is enabled
        if not self.perf_config.batch_translation:
            if self.log_config.log_translation_details:
                print(f"      [WARN] Batch translation disabled, using individual")
            return [self.translate_vi_to_en(text) for text in texts]
        
        # Check cache for all texts first
        results = [None] * len(texts)
        texts_to_translate = []
        indices_to_translate = []
        
        for i, text in enumerate(texts):
            cached = self._get_from_cache(text)
            if cached:
                results[i] = cached
            else:
                texts_to_translate.append(text)
                indices_to_translate.append(i)
        
        if not texts_to_translate:
            if self.log_config.log_translation_details:
                print(f"      [CACHE] All {len(texts)} texts from cache")
            return results
        
        try:
            start_time = time.time()
            
            # Use batch API for single request (GPU optimized)
            response = requests.post(
                self.batch_translation_api_url,
                json={"texts": texts_to_translate},
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                translations = result.get("translations", [])
                
                for idx, trans in zip(indices_to_translate, translations):
                    translation = trans.get("english", f"[Translation failed]")
                    results[idx] = translation
                    self._save_to_cache(texts[idx], translation)
                
                if self.log_config.log_translation_details:
                    elapsed = time.time() - start_time
                    cached_count = len(texts) - len(texts_to_translate)
                    print(f"      [PERF] Batch translated {len(texts_to_translate)} texts in {elapsed:.2f}s (cached: {cached_count})")
                
                return results
            else:
                print(f"[WARN] Batch API failed ({response.status_code}), falling back to individual")
                for idx in indices_to_translate:
                    results[idx] = self.translate_vi_to_en(texts[idx])
                return results
                
        except Exception as e:
            print(f"[WARN] Batch translation error: {e}, falling back to individual")
            for idx in indices_to_translate:
                results[idx] = self.translate_vi_to_en(texts[idx])
            return results
    
    async def translate_multiple_vi_to_en_async(self, texts: List[str]) -> List[str]:
        """Async version of multiple translation"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.translate_multiple_vi_to_en, texts)
    
    def get_config_summary(self) -> Dict:
        """Get current configuration summary"""
        return {
            "api_url": self.config.api_url,
            "timeout": self.timeout,
            "model": self.config.model_name,
            "cache_enabled": self.config.cache_translations,
            "cache_ttl": self.config.cache_ttl,
            "cache_size": len(self._cache),
            "batch_enabled": self.perf_config.batch_translation,
            "use_gpu": self.config.use_gpu
        }
    
    def clear_cache(self):
        """Clear translation cache"""
        self._cache.clear()
        self._cache_times.clear()

# Singleton instance
translation_client = TranslationClient()
