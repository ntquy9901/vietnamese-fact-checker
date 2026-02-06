"""
MiniCheck Client - Uses MiniCheck Baseline API
Now with configurable thresholds and aggregation strategies.
"""

import aiohttp
import asyncio
from typing import List, Dict, Optional
import json
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.system_config import minicheck_config, logging_config

class MiniCheckClient:
    """Client for MiniCheck Baseline API with configurable thresholds"""
    
    def __init__(self):
        self.config = minicheck_config
        self.log_config = logging_config
        self.api_url = f"{self.config.api_url}{self.config.verify_endpoint}"
        self.health_check_url = f"{self.config.api_url}/"
        self.timeout = float(self.config.timeout)
        
    async def check_health(self) -> bool:
        """Check if MiniCheck baseline is running"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.health_check_url, timeout=5) as response:
                    return response.status == 200
        except:
            return False
    
    async def verify(self, claim: str, evidence: List[str]) -> Dict:
        """Verify claim using MiniCheck baseline API"""
        try:
            request_data = {
                "claim": claim,
                "evidence": evidence
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.api_url,
                    json=request_data,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        return self._parse_minicheck_result(result)
                    else:
                        error_text = await response.text()
                        return {
                            "verdict": "ERROR",
                            "confidence": 0.0,
                            "rationale": f"API error: {response.status} - {error_text}",
                            "processing_time": 0.0
                        }
                        
        except aiohttp.ClientError as e:
            return {
                "verdict": "ERROR",
                "confidence": 0.0,
                "rationale": f"Network error: {str(e)}",
                "processing_time": 0.0
            }
        except Exception as e:
            return {
                "verdict": "ERROR",
                "confidence": 0.0,
                "rationale": f"Unexpected error: {str(e)}",
                "processing_time": 0.0
            }
    
    def _parse_minicheck_result(self, result: Dict) -> Dict:
        """Parse MiniCheck result with configurable thresholds"""
        label = result.get("label", "ERROR")
        score = result.get("score", 0.0)
        
        # Determine verdict based on configurable thresholds
        verdict = self._determine_verdict(score, label)
        
        if self.log_config.log_minicheck_all_scores:
            print(f"      [MINICHECK] score={score:.4f}, threshold_supported={self.config.threshold_supported}, verdict={verdict}")
        
        return {
            "verdict": verdict,
            "confidence": score,
            "rationale": result.get("explanation", f"MiniCheck-roberta-large predicts: {verdict} with confidence {score:.3f}"),
            "raw_result": result,
            "thresholds": {
                "supported": self.config.threshold_supported,
                "refuted": self.config.threshold_refuted
            }
        }
    
    def _determine_verdict(self, score: float, original_label: str) -> str:
        """Determine verdict based on configurable thresholds"""
        # If score is high enough, it's SUPPORTED
        if score >= self.config.threshold_supported:
            return "SUPPORTED"
        # If score is very low, it's REFUTED
        elif score < self.config.threshold_refuted:
            return "REFUTED"
        # Otherwise, it's NEITHER/uncertain
        else:
            return "NEITHER"
    
    def aggregate_results(self, results: List[Dict]) -> Dict:
        """Aggregate multiple evidence results based on configured strategy"""
        if not results:
            return {
                "verdict": "ERROR",
                "confidence": 0.0,
                "rationale": "No evidence to aggregate"
            }
        
        # Filter out low confidence results
        valid_results = [
            r for r in results 
            if r.get("confidence", 0) >= self.config.min_evidence_confidence
        ]
        
        if not valid_results:
            valid_results = results  # Use all if none pass threshold
        
        strategy = self.config.aggregation_strategy
        
        if strategy == "best":
            # Return the result with highest confidence
            best = max(valid_results, key=lambda x: x.get("confidence", 0))
            return best
        
        elif strategy == "average":
            # Average all confidences, use majority verdict
            avg_confidence = sum(r.get("confidence", 0) for r in valid_results) / len(valid_results)
            verdict = self._determine_verdict(avg_confidence, "")
            return {
                "verdict": verdict,
                "confidence": avg_confidence,
                "rationale": f"Aggregated from {len(valid_results)} evidence (average strategy)",
                "aggregation_details": {
                    "strategy": "average",
                    "evidence_count": len(valid_results),
                    "individual_scores": [r.get("confidence", 0) for r in valid_results]
                }
            }
        
        elif strategy == "majority":
            # Vote by verdict
            verdicts = [r.get("verdict", "ERROR") for r in valid_results]
            verdict_counts = {}
            for v in verdicts:
                verdict_counts[v] = verdict_counts.get(v, 0) + 1
            majority_verdict = max(verdict_counts, key=verdict_counts.get)
            avg_confidence = sum(r.get("confidence", 0) for r in valid_results if r.get("verdict") == majority_verdict) / max(1, verdict_counts[majority_verdict])
            return {
                "verdict": majority_verdict,
                "confidence": avg_confidence,
                "rationale": f"Majority vote: {majority_verdict} ({verdict_counts[majority_verdict]}/{len(valid_results)})",
                "aggregation_details": {
                    "strategy": "majority",
                    "verdict_counts": verdict_counts
                }
            }
        
        elif strategy == "weighted":
            # Weighted average by confidence
            total_weight = sum(r.get("confidence", 0) for r in valid_results)
            if total_weight == 0:
                return valid_results[0]
            
            weighted_score = sum(
                r.get("confidence", 0) * r.get("confidence", 0) 
                for r in valid_results
            ) / total_weight
            verdict = self._determine_verdict(weighted_score, "")
            return {
                "verdict": verdict,
                "confidence": weighted_score,
                "rationale": f"Weighted average from {len(valid_results)} evidence",
                "aggregation_details": {
                    "strategy": "weighted",
                    "evidence_count": len(valid_results)
                }
            }
        
        # Default: best
        return max(valid_results, key=lambda x: x.get("confidence", 0))
    
    def get_config_summary(self) -> Dict:
        """Get current configuration summary"""
        return {
            "api_url": self.api_url,
            "timeout": self.timeout,
            "threshold_supported": self.config.threshold_supported,
            "threshold_refuted": self.config.threshold_refuted,
            "aggregation_strategy": self.config.aggregation_strategy,
            "min_evidence_confidence": self.config.min_evidence_confidence,
            "model": self.config.model_name
        }

# Singleton instance
minicheck_client = MiniCheckClient()
