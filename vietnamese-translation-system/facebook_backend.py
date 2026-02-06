#!/usr/bin/env python3
"""
Backend that REALLY calls Facebook NLLB model
No fallback - only real Facebook model
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import time
import os

app = FastAPI(title="Facebook NLLB Backend", version="1.0.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class TranslationRequest(BaseModel):
    text: str
    max_length: int = 512

class TranslationResponse(BaseModel):
    vietnamese: str
    english: str
    translation_time: float
    model: str
    using_facebook_model: bool

# Facebook NLLB Translator
class FacebookNLLBTranslator:
    def __init__(self):
        self.model_path = "facebook/nllb-200-distilled-600M"
        self.device = torch.device("cpu")
        self.model = None
        self.tokenizer = None
        self.is_loaded = False
        
        # Cache directory
        self.cache_dir = "D:/huggingface_cache"
        os.makedirs(self.cache_dir, exist_ok=True)
        os.environ['TRANSFORMERS_CACHE'] = self.cache_dir
        os.environ['HF_HOME'] = self.cache_dir
        
    def load_model(self):
        """Load Facebook NLLB model"""
        if self.is_loaded:
            return
            
        print(f"📥 Loading Facebook model: {self.model_path}")
        start_time = time.time()
        
        try:
            # Load Facebook tokenizer and model
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
            print(f"✅ Facebook NLLB model loaded in {load_time:.2f} seconds")
            
            # Language codes
            self.vi_lang_code = "vie_Latn"
            self.en_lang_code = "eng_Latn"
            self.is_loaded = True
            
        except Exception as e:
            print(f"❌ Failed to load Facebook model: {e}")
            raise Exception(f"Facebook model loading failed: {e}")
    
    def translate_vi_to_en(self, text: str) -> str:
        """Translate using Facebook NLLB model"""
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
            
            # Generate translation with Facebook model
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
            print(f"❌ Facebook model translation error: {e}")
            raise Exception(f"Facebook model translation failed: {e}")

# Global Facebook translator
facebook_translator = None

@app.on_event("startup")
async def startup_event():
    """Load Facebook model on startup"""
    global facebook_translator
    try:
        print("🚀 Initializing Facebook NLLB translator...")
        facebook_translator = FacebookNLLBTranslator()
        print("✅ Facebook NLLB backend ready!")
    except Exception as e:
        print(f"❌ Failed to initialize Facebook backend: {e}")
        facebook_translator = None

@app.get("/")
async def root():
    return {
        "status": "healthy", 
        "model": "facebook/nllb-200-distilled-600M",
        "using_facebook_model": facebook_translator is not None,
        "facebook_model_loaded": facebook_translator.is_loaded if facebook_translator else False
    }

@app.post("/translate")
async def translate(request: TranslationRequest):
    """Translate using REAL Facebook NLLB model"""
    if not facebook_translator:
        raise Exception("Facebook NLLB translator not available")
    
    if not request.text.strip():
        raise Exception("Text cannot be empty")
    
    try:
        start_time = time.time()
        
        # Call REAL Facebook model
        english_text = facebook_translator.translate_vi_to_en(request.text)
        
        translation_time = time.time() - start_time
        
        return TranslationResponse(
            vietnamese=request.text,
            english=english_text,
            translation_time=translation_time,
            model="facebook/nllb-200-distilled-600M",
            using_facebook_model=True
        )
    except Exception as e:
        raise Exception(f"Facebook NLLB translation failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Facebook NLLB Backend on http://localhost:8003")
    print("📝 This backend ONLY uses Facebook NLLB model - NO FALLBACKS!")
    uvicorn.run(app, host="0.0.0.0", port=8003)
