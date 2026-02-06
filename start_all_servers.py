#!/usr/bin/env python3
"""
Start All Servers
"""

import subprocess
import sys
import os
import time

def start_all_servers():
    """Start all baseline servers"""
    print("🚀 Starting All Baseline Servers")
    print("=" * 50)
    
    servers = [
        {
            "name": "Translation System",
            "path": "d:/bmad/vietnamese-translation-system",
            "script": "clean_backend.py",
            "port": 8003
        },
        {
            "name": "MiniCheck API",
            "path": "d:/bmad/minicheck",
            "script": "minicheck_server.py",
            "port": 8002
        },
        {
            "name": "Brave Search",
            "path": "d:/bmad/brave-search-baseline",
            "script": "brave_search_server.py",
            "port": 8004
        },
        {
            "name": "Vietnamese Fact Checker",
            "path": "d:/bmad/vietnamese-fact-checker",
            "script": "start_vietnamese_checker.py",
            "port": 8005
        }
    ]
    
    processes = []
    
    for server in servers:
        print(f"\n🔄 Starting {server['name']} (Port {server['port']})...")
        
        try:
            # Change to server directory
            os.chdir(server['path'])
            
            # Start server in background
            process = subprocess.Popen([
                sys.executable, server['script']
            ], creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP)
            
            processes.append({
                "name": server['name'],
                "port": server['port'],
                "pid": process.pid,
                "process": process
            })
            
            print(f"✅ {server['name']} started with PID: {process.pid}")
            
            # Wait a moment between servers
            time.sleep(3)
            
        except Exception as e:
            print(f"❌ Failed to start {server['name']}: {e}")
    
    print(f"\n🎉 All servers started!")
    print("=" * 50)
    
    for server in processes:
        print(f"✅ {server['name']}: Port {server['port']} - PID {server['pid']}")
    
    print("\n📍 Server URLs:")
    print("🌐 Translation System: http://localhost:8003")
    print("🧪 MiniCheck API: http://localhost:8002")
    print("🔍 Brave Search: http://localhost:8004")
    print("🔍 Vietnamese Fact Checker: http://localhost:8005")
    
    return processes

if __name__ == "__main__":
    processes = start_all_servers()
    
    print("\n⏳ Waiting 10 seconds for servers to fully start...")
    time.sleep(10)
    
    print("\n🧪 Testing server health...")
    import requests
    
    for server in processes:
        try:
            url = f"http://localhost:{server['port']}/"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ {server['name']}: HEALTHY")
            else:
                print(f"❌ {server['name']}: ERROR {response.status_code}")
        except Exception as e:
            print(f"❌ {server['name']}: CONNECTION FAILED")
    
    print("\n🎉 Server startup process completed!")
