import re
from typing import List

class VietnameseNormalizer:
    def __init__(self):
        # Pre-compiled patterns for speed
        self.whitespace_pattern = re.compile(r'\s+')
        self.punctuation_pattern = re.compile(r'[^\w\s]')
        
    def normalize(self, text: str) -> str:
        """Fast Vietnamese text normalization"""
        # Convert to lowercase
        text = text.lower().strip()
        
        # Normalize whitespace
        text = self.whitespace_pattern.sub(' ', text)
        
        # Basic Vietnamese-specific normalization
        text = self._normalize_vietnamese_chars(text)
        
        return text
    
    def _normalize_vietnamese_chars(self, text: str) -> str:
        """Normalize Vietnamese characters (basic version)"""
        # Handle common Vietnamese character variations
        replacements = {
            'đ': 'd', 'Đ': 'D',
            'ơ': 'o', 'Ơ': 'O',
            'ư': 'u', 'Ư': 'U',
            'ă': 'a', 'Ă': 'A',
            'â': 'a', 'Â': 'A',
            'ê': 'e', 'Ê': 'E',
            'ô': 'o', 'Ô': 'O',
            'ơ': 'o', 'Ơ': 'O',
            'ư': 'u', 'Ư': 'U'
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        return text
