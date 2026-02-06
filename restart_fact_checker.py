#!/usr/bin/env python3
"""
Restart Vietnamese Fact Checker Server
"""

import subprocess
import sys
import time
import os

def restart_fact_checker():
    """Restart Vietnamese Fact Checker server"""
    print("🔄 Restarting Vietnamese Fact Checker Server...")
    
    # Change to fact checker directory
    fact_checker_dir = "d:/bmad/vietnamese-fact-checker"
    
    try:
        # Kill any existing Python processes on port 8005
        print("🗑️ Killing existing processes...")
        subprocess.run(["netstat", "-ano", "|", "findstr", ":8005"], shell=True, capture_output=True)
        subprocess.run(["taskkill", "/F", "/IM", "python.exe"], shell=True, capture_output=True)
        
        # Wait a moment
        time.sleep(2)
        
        # Start the server
        print("🚀 Starting Vietnamese Fact Checker server...")
        server_script = os.path.join(fact_checker_dir, "start_vietnamese_checker.py")
        
        # Run in background
        process = subprocess.Popen([
            sys.executable, server_script
        ], cwd=fact_checker_dir, creationflags=subprocess.CREATE_NEW_CONSOLE)
        
        print(f"✅ Server started with PID: {process.pid}")
        print("📍 Server will be available at: http://localhost:8005")
        
        # Wait for server to start
        print("⏳ Waiting for server to start...")
        time.sleep(5)
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to restart server: {e}")
        return False

if __name__ == "__main__":
    success = restart_fact_checker()
    if success:
        print("\n🎉 Vietnamese Fact Checker server restarted successfully!")
    else:
        print("\n❌ Failed to restart Vietnamese Fact Checker server!")
