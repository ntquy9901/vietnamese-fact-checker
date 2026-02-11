"""
Configuration for Vietnamese Translation System
"""

# Backend Configuration
BACKEND_URL = "http://localhost:8003"
BACKEND_HOST = "0.0.0.0"
BACKEND_PORT = 8003

# Model Configuration
MODEL_PATH = "facebook/nllb-200-distilled-600M"
MODEL_NAME = "Facebook NLLB-200"
VI_LANG_CODE = "vie_Latn"
EN_LANG_CODE = "eng_Latn"

# Cache Configuration
CACHE_DIR = "D:/huggingface_cache"
MAX_LENGTH = 512

# Translation Configuration
TRANSLATION_TIMEOUT = 30
BEAM_SIZE = 4
EARLY_STOPPING = True

# Web Configuration
WEB_TITLE = "Vietnamese to English Translation"
WEB_DESCRIPTION = "Vietnamese to English Translation using Facebook NLLB Model"
