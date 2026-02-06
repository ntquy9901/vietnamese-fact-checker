#!/usr/bin/env python3
"""
Simple restart script
"""

import subprocess
import sys
import os

def start_server():
    """Start Vietnamese Fact Checker server"""
    print("🚀 Starting Vietnamese Fact Checker server...")
    
    # Change directory and start server
    os.chdir("d:/bmad/vietnamese-fact-checker")
    
    # Start server
    subprocess.run([sys.executable, "start_vietnamese_checker.py"])

if __name__ == "__main__":
    start_server()
