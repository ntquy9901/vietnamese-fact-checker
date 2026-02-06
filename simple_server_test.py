#!/usr/bin/env python3
"""
Simple server test
"""

import subprocess
import sys
import os
import time

def test_translation_system():
    """Test translation system"""
    print("🔄 Testing Translation System...")
    try:
        os.chdir("d:/bmad/vietnamese-translation-system")
        process = subprocess.Popen([sys.executable, "clean_backend.py"])
        time.sleep(5)
        print("✅ Translation System started")
        return process
    except Exception as e:
        print(f"❌ Translation System failed: {e}")
        return None

def test_minicheck():
    """Test MiniCheck"""
    print("🔄 Testing MiniCheck...")
    try:
        os.chdir("d:/bmad/minicheck")
        process = subprocess.Popen([sys.executable, "minicheck_server.py"])
        time.sleep(5)
        print("✅ MiniCheck started")
        return process
    except Exception as e:
        print(f"❌ MiniCheck failed: {e}")
        return None

def test_brave_search():
    """Test Brave Search"""
    print("🔄 Testing Brave Search...")
    try:
        os.chdir("d:/bmad/brave-search-baseline")
        process = subprocess.Popen([sys.executable, "brave_search_server.py"])
        time.sleep(5)
        print("✅ Brave Search started")
        return process
    except Exception as e:
        print(f"❌ Brave Search failed: {e}")
        return None

def main():
    print("🚀 Simple Server Test")
    print("=" * 30)
    
    # Kill existing processes
    subprocess.run(["taskkill", "/F", "/IM", "python.exe"], shell=True, capture_output=True)
    time.sleep(2)
    
    # Start servers
    processes = []
    
    p1 = test_translation_system()
    if p1:
        processes.append(p1)
    
    p2 = test_minicheck()
    if p2:
        processes.append(p2)
    
    p3 = test_brave_search()
    if p3:
        processes.append(p3)
    
    print(f"\n🎉 Started {len(processes)} servers")
    
    # Keep running
    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        print("\n🛑 Stopping servers...")
        for p in processes:
            p.terminate()

if __name__ == "__main__":
    main()
