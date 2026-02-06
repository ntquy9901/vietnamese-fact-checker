from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # API Keys
    serpapi_key: Optional[str] = None
    google_search_api_key: Optional[str] = None
    google_search_engine_id: Optional[str] = None
    brave_search_api_key: Optional[str] = None
    
    # Model paths
    nllb_model_path: str = "facebook/nllb-200-distilled-600M"
    minicheck_api_url: str = "http://localhost:8002/verify"  # MiniCheck API endpoint
    
    # Web search settings
    web_search_timeout: float = 2.0
    web_search_limit: int = 5
    evidence_max_chunks: int = 3
    evidence_max_chars: int = 400
    
    # Performance settings
    max_total_time: float = 6.0
    parallel_translation: bool = True
    
    # Content fetching
    fetch_full_content: bool = True
    content_fetch_timeout: float = 1.0
    
    class Config:
        env_file = ".env"

settings = Settings()
