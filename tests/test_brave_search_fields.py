#!/usr/bin/env python3
"""
Check what fields Brave Search returns - snippet vs content
"""

import requests
import json

def test_brave_search_fields():
    """Check what fields are available in Brave Search results"""
    
    query = "Việt Nam có chế độ đa đảng"
    
    print(" TESTING BRAVE SEARCH FIELDS")
    print("="*60)
    print(f"Query: {query}")
    
    try:
        response = requests.post(
            "http://localhost:8004/search_vietnamese",
            json={"query": query, "max_results": 3},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            results = data.get("results", [])
            
            print(f" Found {len(results)} results")
            
            for i, result in enumerate(results):
                print(f"\n RESULT {i+1}:")
                print(f"   Available fields: {list(result.keys())}")
                
                # Show key fields
                title = result.get("title", "No title")
                url = result.get("url", "No URL")
                snippet = result.get("snippet", "No snippet")
                content = result.get("content", "No content")
                
                print(f"   Title: {title[:80]}...")
                print(f"   URL: {url}")
                print(f"   Snippet: {snippet[:100]}...")
                print(f"   Content: {content[:100]}...")
                
                # Compare snippet vs content
                if snippet and content:
                    snippet_len = len(snippet)
                    content_len = len(content)
                    print(f"   Snippet length: {snippet_len}")
                    print(f"   Content length: {content_len}")
                    
                    if snippet == content:
                        print(f"    Snippet == Content (same field)")
                    else:
                        print(f"    Snippet != Content (different fields)")
                        print(f"   Snippet starts with: {snippet[:50]}...")
                        print(f"   Content starts with: {content[:50]}...")
                elif snippet and not content:
                    print(f"    Only snippet available")
                elif content and not snippet:
                    print(f"    Only content available")
                else:
                    print(f"    Neither snippet nor content available")
        
        else:
            print(f" Search failed: {response.status_code}")
            
    except Exception as e:
        print(f" Error: {e}")

def test_evidence_extraction():
    """Test how Fact Checker extracts evidence vs direct test"""
    
    query = "Việt Nam có chế độ đa đảng"
    
    print(f"\n TESTING EVIDENCE EXTRACTION METHODS")
    print("="*60)
    
    try:
        # Get search results
        response = requests.post(
            "http://localhost:8004/search_vietnamese",
            json={"query": query, "max_results": 3},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            results = data.get("results", [])
            
            print(f" Found {len(results)} results")
            
            # Method 1: Fact Checker way (uses snippet)
            print(f"\n METHOD 1: Fact Checker (snippet field)")
            print("-"*50)
            fc_evidence = []
            for i, result in enumerate(results):
                snippet = result.get('snippet', '')
                if not snippet:
                    snippet = result.get('title', '')
                
                fc_evidence.append(snippet)
                print(f"   [{i}] {snippet[:80]}...")
            
            # Method 2: Direct test way (uses content)
            print(f"\n METHOD 2: Direct Test (content field)")
            print("-"*50)
            direct_evidence = []
            for i, result in enumerate(results):
                content = result.get('content', '')
                direct_evidence.append(content)
                print(f"   [{i}] {content[:80]}...")
            
            # Compare methods
            print(f"\n COMPARISON")
            print("-"*50)
            for i in range(min(len(fc_evidence), len(direct_evidence))):
                fc_text = fc_evidence[i]
                direct_text = direct_evidence[i]
                
                if fc_text == direct_text:
                    print(f"   [{i}]  SAME")
                else:
                    print(f"   [{i}]  DIFFERENT")
                    print(f"       FC: {fc_text[:50]}...")
                    print(f"       Direct: {direct_text[:50]}...")
            
            # Calculate similarity
            matches = sum(1 for i in range(min(len(fc_evidence), len(direct_evidence))) 
                         if fc_evidence[i] == direct_evidence[i])
            total = min(len(fc_evidence), len(direct_evidence))
            similarity = (matches / total) * 100 if total > 0 else 0
            
            print(f"\n Evidence Field Similarity: {matches}/{total} ({similarity:.1f}%)")
            
            if similarity == 100:
                print(" Both methods use the same evidence field")
            else:
                print(" Different evidence fields - THIS IS THE BUG!")
                print(" Solution: Use the same field in both places")
        
        else:
            print(f" Search failed: {response.status_code}")
            
    except Exception as e:
        print(f" Error: {e}")

if __name__ == "__main__":
    test_brave_search_fields()
    test_evidence_extraction()
