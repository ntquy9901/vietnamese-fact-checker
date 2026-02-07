"""
Vietnamese Fact Checker - Comprehensive System Configuration
All configurations for the entire system in one place.
Future: Web UI will allow adjusting these configurations.
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional, List, Tuple
import json
import os

class BraveSearchConfig(BaseSettings):
    """Brave Search API Configuration"""
    
    # API Settings
    api_key: Optional[str] = Field(default=None, env="BRAVE_SEARCH_API_KEY")
    api_url: str = "https://api.search.brave.com/res/v1/web/search"
    proxy_url: str = "http://localhost:8004"
    timeout: int = 10
    max_results: int = 5
    
    # Localization
    country: str = "VN"
    language: str = "vi"
    ui_language: str = "vi"
    
    # Freshness filter: None, "pd" (day), "pw" (week), "pm" (month), "py" (year)
    freshness: Optional[str] = None
    
    # Extra features
    extra_snippets: bool = True
    
    # Source Filtering
    trusted_sources: List[str] = [
        "wikipedia.org",
        "vi.wikipedia.org",
        "en.wikipedia.org",
        "gov.vn",
        "chinhphu.vn",
        "edu.vn",
        "vnexpress.net",
        "tuoitre.vn",
        "thanhnien.vn",
        "nhandan.vn",
        "baochinhphu.vn",
        "dangcongsan.vn",
    ]
    
    untrusted_sources: List[str] = [
        "facebook.com",
        "fb.com",
        "tiktok.com",
        "twitter.com",
        "x.com",
        "instagram.com",
        "youtube.com",
        "reddit.com",
        "quora.com",
        "pinterest.com",
    ]
    
    # Source filter mode: "exclude" (add -site:), "boost" (goggles boost), "goggles" (full goggles)
    source_filter_mode: str = "exclude"
    
    # Goggles settings (when source_filter_mode = "goggles")
    goggles_enabled: bool = False
    goggles_boost_trusted: int = 3
    goggles_downrank_untrusted: int = 5
    goggles_discard_blacklist: bool = True
    
    class Config:
        env_prefix = "BRAVE_"


class TranslationConfig(BaseSettings):
    """Translation Service Configuration"""
    
    # API Settings
    api_url: str = "http://localhost:8003"
    batch_api_url: str = "http://localhost:8003/translate_batch"
    
    # Model Settings
    model_name: str = "VinAI/vinai-translate-vi2en-v2"
    cache_dir: str = "D:/huggingface_cache"
    
    # Processing Settings
    max_length: int = 512
    batch_size: int = 10
    timeout: int = 30
    
    # GPU Settings
    use_gpu: bool = True
    gpu_device: str = "cuda:0"
    
    # Caching
    cache_translations: bool = False
    cache_ttl: int = 3600
    
    class Config:
        env_prefix = "TRANSLATION_"


class MiniCheckConfig(BaseSettings):
    """MiniCheck Service Configuration"""
    
    # API Settings
    api_url: str = "http://localhost:8002"
    verify_endpoint: str = "/verify"
    timeout: int = 30
    
    # Model Settings
    model_name: str = "Bespoke-MiniCheck-7B"
    
    # Verdict Thresholds
    threshold_supported: float = 0.5      # >= 50% → SUPPORTED
    threshold_refuted: float = 0.3        # < 30% → REFUTED
    # 30-50% → NEITHER/UNCERTAIN
    
    # Aggregation Strategy: "best", "average", "majority", "weighted"
    aggregation_strategy: str = "best"
    
    # Minimum confidence to consider evidence
    min_evidence_confidence: float = 0.1
    
    class Config:
        env_prefix = "MINICHECK_"


class EvidenceConfig(BaseSettings):
    """Evidence Processing Configuration"""
    
    # Evidence limits - UNIFIED across all services
    max_chunks: int = 5  # Same as Brave Search max_results
    min_chunks: int = 1
    max_length: int = 500
    
    # Content fetching
    fetch_full_content: bool = True
    content_fetch_timeout: int = 10
    
    # Evidence quality
    min_text_length: int = 50
    max_text_length: int = 1000
    
    class Config:
        env_prefix = "EVIDENCE_"


class LoggingConfig(BaseSettings):
    """Logging and Debug Configuration"""
    
    # Log level: DEBUG, INFO, WARNING, ERROR
    level: str = "INFO"
    
    # Service logging
    log_service_io: bool = True
    log_timing: bool = True
    log_translation_details: bool = True
    log_minicheck_all_scores: bool = True
    log_search_results: bool = True
    
    # File logging
    save_to_file: bool = False
    output_dir: str = "./debug_logs"
    
    # Response debug info
    include_debug_in_response: bool = True
    
    class Config:
        env_prefix = "LOG_"


class PerformanceConfig(BaseSettings):
    """Performance Tuning Configuration"""
    
    # Parallel processing
    parallel_minicheck: bool = True
    parallel_workers: int = 3
    
    # Batch processing
    batch_translation: bool = True
    
    # Timeouts
    request_timeout: int = 120
    max_total_time: float = 60.0
    
    class Config:
        env_prefix = "PERF_"


class APIConfig(BaseSettings):
    """API Endpoints Configuration"""
    
    # Service URLs
    translation_url: str = "http://localhost:8003"
    minicheck_url: str = "http://localhost:8002"
    brave_search_url: str = "http://localhost:8004"
    
    # Fact Checker Server
    fact_checker_host: str = "0.0.0.0"
    fact_checker_port: int = 8005
    
    class Config:
        env_prefix = "API_"


class ResponseConfig(BaseSettings):
    """Response Format Configuration"""
    
    # Debug info
    include_debug_info: bool = True
    include_all_scores: bool = True
    include_sources: bool = True
    
    # Rationale
    translate_rationale: bool = False
    max_rationale_length: int = 500
    
    class Config:
        env_prefix = "RESPONSE_"


class ErrorHandlingConfig(BaseSettings):
    """Error Handling Configuration"""
    
    # Retry settings
    retry_on_error: bool = True
    max_retries: int = 3
    retry_delay: int = 1
    
    # Fallback behavior
    fallback_on_translation_error: bool = True
    fallback_on_search_error: bool = True
    fallback_on_minicheck_error: bool = True
    
    class Config:
        env_prefix = "ERROR_"


class SystemConfig(BaseSettings):
    """Main System Configuration - Combines all configs"""
    
    # Sub-configurations
    brave_search: BraveSearchConfig = Field(default_factory=BraveSearchConfig)
    translation: TranslationConfig = Field(default_factory=TranslationConfig)
    minicheck: MiniCheckConfig = Field(default_factory=MiniCheckConfig)
    evidence: EvidenceConfig = Field(default_factory=EvidenceConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    performance: PerformanceConfig = Field(default_factory=PerformanceConfig)
    api: APIConfig = Field(default_factory=APIConfig)
    response: ResponseConfig = Field(default_factory=ResponseConfig)
    error_handling: ErrorHandlingConfig = Field(default_factory=ErrorHandlingConfig)
    
    class Config:
        env_file = ".env"
        extra = "ignore"  # Ignore extra fields from .env file
    
    def to_dict(self) -> dict:
        """Export all configurations as dictionary"""
        return {
            "brave_search": self.brave_search.model_dump(),
            "translation": self.translation.model_dump(),
            "minicheck": self.minicheck.model_dump(),
            "evidence": self.evidence.model_dump(),
            "logging": self.logging.model_dump(),
            "performance": self.performance.model_dump(),
            "api": self.api.model_dump(),
            "response": self.response.model_dump(),
            "error_handling": self.error_handling.model_dump(),
        }
    
    def to_json(self, indent: int = 2) -> str:
        """Export all configurations as JSON"""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)
    
    def save_to_file(self, filepath: str):
        """Save configurations to JSON file"""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(self.to_json())
    
    @classmethod
    def load_from_file(cls, filepath: str) -> 'SystemConfig':
        """Load configurations from JSON file"""
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            # Create config with loaded values
            return cls(
                brave_search=BraveSearchConfig(**data.get('brave_search', {})),
                translation=TranslationConfig(**data.get('translation', {})),
                minicheck=MiniCheckConfig(**data.get('minicheck', {})),
                evidence=EvidenceConfig(**data.get('evidence', {})),
                logging=LoggingConfig(**data.get('logging', {})),
                performance=PerformanceConfig(**data.get('performance', {})),
                api=APIConfig(**data.get('api', {})),
                response=ResponseConfig(**data.get('response', {})),
                error_handling=ErrorHandlingConfig(**data.get('error_handling', {})),
            )
        return cls()


# Global singleton instance
system_config = SystemConfig()

# Shortcut accessors for backward compatibility
brave_config = system_config.brave_search
translation_config = system_config.translation
minicheck_config = system_config.minicheck
evidence_config = system_config.evidence
logging_config = system_config.logging
performance_config = system_config.performance
api_config = system_config.api
response_config = system_config.response
error_config = system_config.error_handling


def get_config() -> SystemConfig:
    """Get the global system configuration"""
    return system_config


def reload_config():
    """Reload configuration from environment"""
    global system_config, brave_config, translation_config, minicheck_config
    global evidence_config, logging_config, performance_config, api_config
    global response_config, error_config
    
    system_config = SystemConfig()
    brave_config = system_config.brave_search
    translation_config = system_config.translation
    minicheck_config = system_config.minicheck
    evidence_config = system_config.evidence
    logging_config = system_config.logging
    performance_config = system_config.performance
    api_config = system_config.api
    response_config = system_config.response
    error_config = system_config.error_handling


def print_config():
    """Print current configuration"""
    print("=" * 80)
    print("VIETNAMESE FACT CHECKER - SYSTEM CONFIGURATION")
    print("=" * 80)
    print(system_config.to_json())
    print("=" * 80)
