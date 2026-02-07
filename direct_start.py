#!/usr/bin/env python3
"""
Direct start Vietnamese Fact Checker
"""

import subprocess
import sys
import os

def direct_start():
    """Direct start Vietnamese Fact Checker"""
    print(" Direct starting Vietnamese Fact Checker...")
    
    # Change directory
    os.chdir("d:/bmad/vietnamese-fact-checker")
    
    # Import and start directly
    sys.path.append(".")
    from start_vietnamese_checker import app
    
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)

if __name__ == "__main__":
    direct_start()
