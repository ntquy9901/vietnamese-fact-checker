"""
Vietnamese Fact Checker - Main Service
Now with comprehensive configuration support.
"""

import time
import asyncio
from typing import Dict, List, Optional
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.translation_client import translation_client
from services.evidence_fetcher import EvidenceFetcher
from services.minicheck_client import minicheck_client
from services.brave_search_client import brave_search_client
from core.system_config import (
    system_config, evidence_config, logging_config, 
    performance_config, response_config, error_config
)
from api.schemas import Evidence

class VietnameseFactChecker:
    def __init__(self):
        self.translation_client = translation_client
        self.evidence_fetcher = EvidenceFetcher()
        self.minicheck = minicheck_client
        self.web_search = brave_search_client
        
        # Load configs
        self.evidence_cfg = evidence_config
        self.log_cfg = logging_config
        self.perf_cfg = performance_config
        self.response_cfg = response_config
        self.error_cfg = error_config
    
    async def check_claim(self, claim: str) -> Dict:
        """Main fact-checking method"""
        start_time = time.time()
        
        try:
            print(f"[INFO] Starting fact check for: {claim}")
            
            # Step 1: Web search for Vietnamese evidence
            print("[STEP 1] Web search using Brave Search baseline...")
            search_results = await self.web_search.search_vietnamese(claim)
            print(f"[OK] Found {len(search_results)} search results")
            
            if not search_results:
                return self._build_error_response(
                    claim, 
                    "Không tìm thấy bằng chứng", 
                    "NO_EVIDENCE", 
                    time.time() - start_time
                )
            
            # Step 2: Fetch full content (if enabled)
            print("[STEP 2] Fetching content...")
            if self.evidence_cfg.fetch_full_content:
                urls = [result['url'] for result in search_results[:self.evidence_cfg.max_chunks]]
                full_contents = await self.evidence_fetcher.fetch_evidence(urls)
            else:
                full_contents = [None] * len(search_results)
            
            # Step 3: Prepare evidence chunks
            print("[STEP 3] Preparing evidence...")
            evidence_chunks = self.evidence_fetcher.prepare_evidence_chunks(
                search_results, full_contents
            )
            print(f"[OK] Prepared {len(evidence_chunks)} evidence chunks")
            
            # Step 4: Translate claim AND evidence in SINGLE BATCH request (GPU optimized)
            print("[STEP 4] BATCH translation (single request, GPU optimized)...")
            print(f"   Original Vietnamese claim: {claim}")
            vietnamese_texts = [ev['text'] for ev in evidence_chunks]
            
            # Combine claim + all evidence for batch translation
            all_texts_to_translate = [claim] + vietnamese_texts
            
            translation_start = time.time()
            
            # Use BATCH API - single request for all texts
            all_translations = self.translation_client.translate_multiple_vi_to_en(all_texts_to_translate)
            
            # Split results: first is claim, rest are evidence
            english_claim = all_translations[0] if all_translations else claim
            english_evidence = all_translations[1:] if len(all_translations) > 1 else []
            
            translation_time = time.time() - translation_start
            print(f"   [OK] Translated claim: {english_claim}")
            print(f"   [PERF] Batch translated {len(all_texts_to_translate)} texts in {translation_time:.2f}s")
            for i, text in enumerate(english_evidence):
                print(f"   {i+1}. EN: {text[:100]}...")
            
            # Store translation debug info
            translation_debug = {
                "translation_api": self.translation_client.translation_api_url,
                "translation_model": "facebook/nllb-200-distilled-600M",
                "cache_directory": "D:/huggingface_cache",
                "translation_method": "Baseline Translation System API",
                "original_claim": claim,
                "english_claim": english_claim,
                "vietnamese_evidence": vietnamese_texts,
                "english_evidence": english_evidence
            }
            
            # Step 5: MiniCheck verification with ALL evidence at once
            print("[STEP 5] MiniCheck verification with ALL evidence")
            
            if english_evidence:
                print(f"[INFO] Testing {len(english_evidence)} evidence items together...")
                
                minicheck_start = time.time()
                
                # Call MiniCheck ONCE with ALL evidence (correct approach)
                try:
                    result = await self.minicheck.verify(english_claim, english_evidence)
                    minicheck_result = result
                    
                    minicheck_time = time.time() - minicheck_start
                    print(f"   [PERF] MiniCheck completed in {minicheck_time:.2f}s")
                    
                    # Show individual scores from raw result
                    if "raw_result" in result and "all_scores" in result["raw_result"]:
                        all_scores = result["raw_result"]["all_scores"]
                        print(f"   [SCORES] Individual evidence results:")
                        for i, score_info in enumerate(all_scores):
                            label = score_info.get("label", "N/A")
                            score = score_info.get("score", 0)
                            print(f"      {i+1}. {label}: {score:.3f}")
                    
                except Exception as e:
                    print(f"[ERROR] MiniCheck verification failed: {e}")
                    minicheck_result = {
                        "label": "ERROR",
                        "score": 0.0,
                        "explanation": f"MiniCheck error: {str(e)}",
                        "processing_time": 0.0
                    }
            else:
                # No evidence available
                print("[WARN] No evidence available for MiniCheck verification")
                minicheck_result = {
                    "label": "ERROR",
                    "score": 0.0,
                    "explanation": "No evidence available for verification",
                    "processing_time": 0.0
                }
            
            # Parse MiniCheck result to get verdict and confidence
            # Note: if best_result was found, minicheck_result is already parsed (has 'verdict'/'confidence')
            # Only call _parse_minicheck_result if it's a raw result (has 'label'/'score')
            if 'verdict' in minicheck_result:
                # Already parsed result from verify()
                parsed_result = minicheck_result
            else:
                # Raw result needs parsing
                parsed_result = self.minicheck._parse_minicheck_result(minicheck_result)
            print(f"[OK] MiniCheck result: {parsed_result['verdict']} ({parsed_result['confidence']:.4f})")
            
            # Step 6: Translate rationale back to Vietnamese
            print("[STEP 6] Translating rationale...")
            # For now, keep rationale in English since baseline system doesn't support EN->VI
            vietnamese_rationale = f"[English rationale: {parsed_result['rationale']}]"
            
            # Step 7: Build response
            total_time = time.time() - start_time
            print(f"[TIME] Total time: {total_time:.2f}s")
            
            response = {
                'claim': claim,
                'verdict': parsed_result['verdict'],
                'confidence': parsed_result['confidence'],
                'rationale': vietnamese_rationale,
                'evidence': [
                    Evidence(
                        text=chunk['text'],
                        url=chunk['url'],
                        title=chunk['title']
                    ) for chunk in evidence_chunks
                ],
                'evidence_count': len(evidence_chunks),
                'processing_time': total_time,
                'method': 'minicheck_web_search',
                'sources': [chunk['url'] for chunk in evidence_chunks],
                'error': None,
                'debug_info': {
                    'translation': translation_debug,
                    'minicheck_input': {
                        'claim': english_claim,
                        'evidence': english_evidence
                    },
                    'minicheck_raw_output': minicheck_result.get('raw_result', minicheck_result),
                    'minicheck_parsed_output': parsed_result
                }
            }
            
            print("[OK] Fact check completed successfully!")
            return response
            
        except Exception as e:
            print(f"[ERROR] in fact check: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            return self._build_error_response(
                claim,
                f"Lỗi hệ thống: {str(e)}",
                "SYSTEM_ERROR",
                time.time() - start_time
            )
    
    def _build_error_response(self, claim: str, 
                            error_message: str, error_type: str, 
                            processing_time: float) -> Dict:
        """Build error response"""
        return {
            'claim': claim,
            'verdict': 'ERROR',
            'confidence': 0.0,
            'rationale': error_message,
            'evidence': [],
            'evidence_count': 0,
            'processing_time': processing_time,
            'method': 'minicheck_web_search',
            'sources': [],
            'error': error_type
        }
