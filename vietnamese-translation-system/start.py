#!/usr/bin/env python3
"""
Vietnamese Translation System Launcher
Starts both server and opens web interface
"""

import subprocess
import sys
import time
import webbrowser
import os

def start_server():
    """Start the Facebook NLLB translation server"""
    print("🚀 Starting Facebook NLLB Translation Server...")
    try:
        subprocess.Popen([sys.executable, "facebook_backend.py"])
        print("✅ Server starting on http://localhost:8003")
        return True
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        return False

def open_web_interface():
    """Open web interface in browser"""
    time.sleep(3)  # Wait for server to start
    try:
        web_path = os.path.abspath("web/index.html")
        webbrowser.open(f"file://{web_path}")
        print(f"✅ Web interface opened: {web_path}")
        return True
    except Exception as e:
        print(f"❌ Failed to open web interface: {e}")
        return False

def main():
    """Main launcher function"""
    print("🌐 Vietnamese Translation System Launcher")
    print("=" * 50)
    
    # Check if requirements are installed
    try:
        import fastapi
        import uvicorn
        import torch
        import transformers
        print("✅ All dependencies found")
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        return
    
    # Start server
    if not start_server():
        return
    
    # Open web interface
    if not open_web_interface():
        return
    
    print("\n🎉 Facebook NLLB Translation System is ready!")
    print("📝 Server: http://localhost:8003")
    print("🌐 Web Interface: web/index.html")
    print("\nPress Ctrl+C to stop the server")

if __name__ == "__main__":
    main()
