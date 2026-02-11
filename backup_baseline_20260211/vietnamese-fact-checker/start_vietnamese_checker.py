#!/usr/bin/env python3
"""
Simple startup script for Vietnamese Fact Checker
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from api.main import app
import uvicorn

if __name__ == "__main__":
    print(" Starting Vietnamese Fact Checker...")
    print(" Server will be available at: http://localhost:8005")
    print(" API docs available at: http://localhost:8005/docs")
    print(" Translation API should be running on http://localhost:8003")
    print(" MiniCheck API should be running on http://localhost:8002")
    
    uvicorn.run(app, host="0.0.0.0", port=8005)
