#!/usr/bin/env python3
"""
Start server in background
"""

import subprocess
import sys
import os
import time

def start_background():
    """Start Vietnamese Fact Checker server in background"""
    print("🚀 Starting Vietnamese Fact Checker server in background...")
    
    # Change directory
    os.chdir("d:/bmad/vietnamese-fact-checker")
    
    # Start server in background
    process = subprocess.Popen([
        sys.executable, "start_vietnamese_checker.py"
    ], creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP)
    
    print(f"✅ Server started with PID: {process.pid}")
    print("📍 Server will be available at: http://localhost:8005")
    
    # Wait a moment
    time.sleep(3)
    
    return process.pid

if __name__ == "__main__":
    pid = start_background()
    print(f"\n🎉 Vietnamese Fact Checker server started in background! PID: {pid}")
