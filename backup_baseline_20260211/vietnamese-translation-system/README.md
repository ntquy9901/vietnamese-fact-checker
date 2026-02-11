# Vietnamese Translation System

## Quick Start
1. `pip install -r requirements.txt`
2. `python server.py` (starts on localhost:8000)
3. Open `web/index.html` in browser

## Features
- Real NLLB-200 model translation
- FastAPI backend + modern web UI
- ~0.5-1.5s per sentence

## API
- GET `/` - Health check
- POST `/translate` - Translate text

## Model: facebook/nllb-200-distilled-600M
