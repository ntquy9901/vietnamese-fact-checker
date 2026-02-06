#!/usr/bin/env python3
"""
Test direct Brave API call
"""

import requests
import os

def test_direct_brave_api():
    """Test direct Brave API call"""
    api_key = "BSAsPsXCUU0JnWCWAGdCmoAdGPYCDUR"
    url = "https://api.search.brave.com/res/v1/web/search"
    
    headers = {
        "Accept": "application/json",
        "X-Subscription-Token": api_key
    }
    
    params = {
        "q": "Ho Chi Minh City",
        "count": 5
    }
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            results = data.get("web", {}).get("results", [])
            print(f"Results: {len(results)}")
            return len(results) > 0
        else:
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"Exception: {e}")
        return False

if __name__ == "__main__":
    test_direct_brave_api()
