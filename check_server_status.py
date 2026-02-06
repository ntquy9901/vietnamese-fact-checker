#!/usr/bin/env python3
"""
Check server status and restart if needed
"""

import subprocess
import sys
import os
import time
import requests

def check_and_restart_servers():
    """Check server status and restart if needed"""
    print("🔍 Checking Server Status")
    print("=" * 50)
    
    servers = [
        {
            "name": "Translation System",
            "path": "d:/bmad/vietnamese-translation-system",
            "script": "clean_backend.py",
            "port": 8003,
            "url": "http://localhost:8003/"
        },
        {
            "name": "MiniCheck API",
            "path": "d:/bmad/minicheck",
            "script": "minicheck_server.py",
            "port": 8002,
            "url": "http://localhost:8002/"
        },
        {
            "name": "Brave Search",
            "path": "d:/bmad/brave-search-baseline",
            "script": "brave_search_server.py",
            "port": 8004,
            "url": "http://localhost:8004/"
        },
        {
            "name": "Vietnamese Fact Checker",
            "path": "d:/bmad/vietnamese-fact-checker",
            "script": "start_vietnamese_checker.py",
            "port": 8005,
            "url": "http://localhost:8005/"
        }
    ]
    
    # Kill existing processes
    print("🗑️ Killing existing Python processes...")
    subprocess.run(["taskkill", "/F", "/IM", "python.exe"], shell=True, capture_output=True)
    time.sleep(2)
    
    # Start servers one by one
    for server in servers:
        print(f"\n🔄 Starting {server['name']} (Port {server['port']})...")
        
        try:
            # Change to server directory
            os.chdir(server['path'])
            
            # Start server
            process = subprocess.Popen([
                sys.executable, server['script']
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            # Wait for startup
            time.sleep(5)
            
            # Check if server is responding
            try:
                response = requests.get(server['url'], timeout=10)
                if response.status_code == 200:
                    print(f"✅ {server['name']}: RUNNING and HEALTHY")
                else:
                    print(f"⚠️ {server['name']}: RUNNING but ERROR {response.status_code}")
            except:
                # Check stdout/stderr for errors
                stdout, stderr = process.communicate(timeout=1)
                if stderr:
                    print(f"❌ {server['name']}: ERROR - {stderr[:200]}...")
                else:
                    print(f"⚠️ {server['name']}: STARTING (may need more time)")
            
        except Exception as e:
            print(f"❌ Failed to start {server['name']}: {e}")
    
    print("\n🎉 Server check completed!")

if __name__ == "__main__":
    check_and_restart_servers()
