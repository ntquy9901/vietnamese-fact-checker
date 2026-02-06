#!/usr/bin/env python3
"""
Vietnamese to English Translator using Facebook NLLB-200
Standalone translation service
"""

import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import time
import os

class NLLBTranslator:
    def __init__(self):
        """Initialize NLLB translator"""
        self.model_path = "facebook/nllb-200-distilled-600M"
        self.device = torch.device("cpu")
        self.model = None
        self.tokenizer = None
        self.is_loaded = False
        
        # Set cache directory
        self.cache_dir = "D:/huggingface_cache"
        os.makedirs(self.cache_dir, exist_ok=True)
        os.environ['TRANSFORMERS_CACHE'] = self.cache_dir
        os.environ['HF_HOME'] = self.cache_dir
        
    def load_model(self):
        """Load the NLLB model"""
        if self.is_loaded:
            return
            
        print(f"📥 Loading model: {self.model_path}")
        start_time = time.time()
        
        # Load tokenizer and model
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_path,
            cache_dir=self.cache_dir
        )
        self.model = AutoModelForSeq2SeqLM.from_pretrained(
            self.model_path,
            cache_dir=self.cache_dir
        )
        self.model.eval()
        self.model.to(self.device)
        
        load_time = time.time() - start_time
        print(f"✅ Model loaded in {load_time:.2f} seconds")
        
        # Language codes for NLLB
        self.vi_lang_code = "vie_Latn"
        self.en_lang_code = "eng_Latn"
        self.is_loaded = True
    
    def translate_vi_to_en(self, text: str) -> str:
        """Translate Vietnamese to English"""
        if not self.is_loaded:
            self.load_model()
            
        try:
            # Prepare input
            inputs = self.tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=512
            )
            
            # Set source language
            self.tokenizer.src_lang = self.vi_lang_code
            
            # Move to device
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Generate translation
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    forced_bos_token_id=self.tokenizer.convert_tokens_to_ids(self.en_lang_code),
                    max_length=512,
                    num_beams=4,
                    early_stopping=True
                )
            
            # Decode
            translation = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            return translation.strip()
            
        except Exception as e:
            print(f"❌ Translation error: {e}")
            return text

# Global instance
translator = NLLBTranslator()

def translate_text(text: str) -> str:
    """Global translation function"""
    return translator.translate_vi_to_en(text)
