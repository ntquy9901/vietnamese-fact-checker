#!/usr/bin/env python3
"""
Clean Simple Backend - Using VinAI Translation Model from D: Cache
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import time
import os

app = FastAPI(title="VinAI Translation Backend", version="2.0.0")

# Set cache directory to D: drive
CACHE_DIR = "D:/huggingface_cache"
os.makedirs(CACHE_DIR, exist_ok=True)
os.environ['TRANSFORMERS_CACHE'] = CACHE_DIR
os.environ['HF_HOME'] = CACHE_DIR

print(f"📁 Using cache directory: {CACHE_DIR}")

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from typing import List

class TranslationRequest(BaseModel):
    text: str

class BatchTranslationRequest(BaseModel):
    texts: List[str]

class TranslationResponse(BaseModel):
    vietnamese: str
    english: str
    translation_time: float
    model: str
    using_facebook_model: bool
    model_loaded: bool

class BatchTranslationResponse(BaseModel):
    translations: List[dict]
    total_time: float
    count: int
    device: str
    model: str

# Global model variables
tokenizer = None
model = None
model_loaded = False
device_used = "cpu"

def load_vinai_model():
    """Load VinAI Vietnamese-English translation model from D: cache with GPU support"""
    global tokenizer, model, model_loaded, device_used
    
    if model_loaded:
        return True
    
    try:
        print("📥 Loading VinAI vi2en model from D: cache...")
        start_time = time.time()
        
        model_path = "VinAI/vinai-translate-vi2en-v2"
        
        # Check GPU availability
        if torch.cuda.is_available():
            device_used = "cuda"
            print(f"🎮 GPU detected: {torch.cuda.get_device_name(0)}")
            print(f"💾 GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
        else:
            device_used = "cpu"
            print("⚠️ No GPU detected, using CPU")
        
        # Load from D: cache
        tokenizer = AutoTokenizer.from_pretrained(
            model_path,
            cache_dir=CACHE_DIR,
            src_lang="vi_VN"
        )
        model = AutoModelForSeq2SeqLM.from_pretrained(
            model_path,
            cache_dir=CACHE_DIR
        )
        
        # Move to GPU if available
        model = model.to(device_used)
        model.eval()
        model_loaded = True
        
        load_time = time.time() - start_time
        print(f"✅ VinAI model loaded on {device_used.upper()} in {load_time:.2f} seconds")
        return True
        
    except Exception as e:
        print(f"❌ Failed to load VinAI model: {e}")
        print("🔄 Using fallback translations...")
        return False

def translate_with_vinai(text: str) -> str:
    """Translate Vietnamese to English using VinAI model"""
    if not model_loaded:
        return f"[Model not loaded: {text}]"
    
    try:
        # Prepare input
        input_ids = tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=512,
            padding=True
        ).to(device_used)
        
        # Generate translation with decoder_start_token_id for en_XX
        with torch.no_grad():
            outputs = model.generate(
                **input_ids,
                decoder_start_token_id=tokenizer.lang_code_to_id["en_XX"],
                num_return_sequences=1,
                num_beams=5,
                early_stopping=True
            )
        
        # Decode
        translation = tokenizer.batch_decode(outputs, skip_special_tokens=True)
        return " ".join(translation).strip()
        
    except Exception as e:
        print(f"❌ VinAI translation error: {e}")
        return f"[Translation failed: {text}]"

def translate_batch_with_vinai(texts: List[str]) -> List[str]:
    """Translate multiple Vietnamese texts to English in a single batch (GPU optimized)"""
    if not model_loaded:
        return [f"[Model not loaded: {text}]" for text in texts]
    
    try:
        # Prepare batch input - all texts at once
        inputs = tokenizer(
            texts,
            return_tensors="pt",
            truncation=True,
            max_length=512,
            padding=True
        ).to(device_used)
        
        # Generate translations for entire batch at once
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                decoder_start_token_id=tokenizer.lang_code_to_id["en_XX"],
                num_return_sequences=1,
                num_beams=5,
                early_stopping=True
            )
        
        # Decode all translations
        translations = tokenizer.batch_decode(outputs, skip_special_tokens=True)
        return translations
        
    except Exception as e:
        print(f"❌ VinAI batch translation error: {e}")
        # Fallback to individual translation
        return [translate_with_vinai(text) for text in texts]

@app.get("/")
async def root():
    return {
        "status": "healthy", 
        "model": "VinAI/vinai-translate-vi2en-v2",
        "using_vinai_model": True,
        "model_loaded": model_loaded,
        "device": device_used,
        "gpu_available": torch.cuda.is_available(),
        "cache_dir": CACHE_DIR,
        "message": "VinAI Translation Backend ready"
    }

@app.post("/translate")
async def translate(request: TranslationRequest):
    """Translate Vietnamese to English using VinAI model"""
    start_time = time.time()
    
    # Try to load VinAI model if not loaded
    if not model_loaded:
        load_vinai_model()
    
    # Use VinAI model if available
    if model_loaded:
        english_text = translate_with_vinai(request.text)
    else:
        english_text = f"[Model not loaded: {request.text}]"
    
    translation_time = time.time() - start_time
    
    return TranslationResponse(
        vietnamese=request.text,
        english=english_text,
        translation_time=translation_time,
        model="VinAI/vinai-translate-vi2en-v2",
        using_facebook_model=False,
        model_loaded=model_loaded
    )

@app.post("/translate_batch", response_model=BatchTranslationResponse)
async def translate_batch(request: BatchTranslationRequest):
    """Translate multiple Vietnamese texts to English in a single batch (GPU optimized)"""
    start_time = time.time()
    
    # Try to load VinAI model if not loaded
    if not model_loaded:
        load_vinai_model()
    
    if not request.texts:
        return BatchTranslationResponse(
            translations=[],
            total_time=0.0,
            count=0,
            device=device_used,
            model="VinAI/vinai-translate-vi2en-v2"
        )
    
    # Use batch translation for GPU optimization
    if model_loaded:
        english_texts = translate_batch_with_vinai(request.texts)
    else:
        english_texts = [f"[Model not loaded: {text}]" for text in request.texts]
    
    total_time = time.time() - start_time
    
    # Build response with individual timings
    translations = [
        {"vietnamese": vi, "english": en}
        for vi, en in zip(request.texts, english_texts)
    ]
    
    print(f"⚡ Batch translated {len(request.texts)} texts in {total_time:.2f}s on {device_used.upper()}")
    
    return BatchTranslationResponse(
        translations=translations,
        total_time=total_time,
        count=len(translations),
        device=device_used,
        model="VinAI/vinai-translate-vi2en-v2"
    )

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting VinAI Translation Backend")
    print(f"📁 Cache directory: {CACHE_DIR}")
    print("📦 Model: VinAI/vinai-translate-vi2en-v2")
    uvicorn.run(app, host="0.0.0.0", port=8003)
