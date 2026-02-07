#!/usr/bin/env python3
"""
Test Brave Search determinism - call same query multiple times
"""

import requests
import json
import time

def test_brave_search_deterministic():
    """Test if Brave Search returns the same results for identical queries"""
    
    query = "Việt Nam có chế độ đa đảng"
    num_calls = 3
    
    print(" TESTING BRAVE SEARCH DETERMINISM")
    print("="*60)
    print(f"Query: {query}")
    print(f"Number of calls: {num_calls}")
    print(f"Max results: 5 (unified config)")
    
    all_results = []
    
    for call_num in range(1, num_calls + 1):
        print(f"\n CALL {call_num}")
        print("-"*40)
        
        try:
            # Call Brave Search
            start_time = time.time()
            response = requests.post(
                "http://localhost:8004/search_vietnamese",
                json={"query": query, "max_results": 5},
                timeout=30
            )
            call_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])
                
                print(f" Response time: {call_time:.2f}s")
                print(f" Results count: {len(results)}")
                
                # Store results for comparison
                call_results = {
                    "call_num": call_num,
                    "timestamp": time.strftime("%H:%M:%S"),
                    "response_time": call_time,
                    "results": results
                }
                all_results.append(call_results)
                
                # Show result previews
                for i, result in enumerate(results):
                    title = result.get("title", "No title")
                    snippet = result.get("snippet", "No snippet")[:100] + "..."
                    print(f"    [{i}] {title}")
                    print(f"        {snippet}")
                
            else:
                print(f" Call {call_num} failed: {response.status_code}")
                print(f"   Response: {response.text}")
                
        except Exception as e:
            print(f" Call {call_num} error: {e}")
    
    # Compare results
    print(f"\n RESULTS COMPARISON")
    print("="*60)
    
    if len(all_results) >= 2:
        print(f"Comparing {len(all_results)} calls...")
        
        # Check if all calls returned the same number of results
        result_counts = [len(call["results"]) for call in all_results]
        same_count = len(set(result_counts)) == 1
        
        print(f"Result counts: {result_counts}")
        print(f"Same count across calls: {' YES' if same_count else ' NO'}")
        
        if same_count and result_counts[0] > 0:
            # Compare content of each result
            num_results = result_counts[0]
            matches_per_position = []
            
            for pos in range(num_results):
                position_matches = []
                
                # Compare this position across all calls
                for i in range(len(all_results) - 1):
                    call1 = all_results[i]
                    call2 = all_results[i + 1]
                    
                    if pos < len(call1["results"]) and pos < len(call2["results"]):
                        result1 = call1["results"][pos]
                        result2 = call2["results"][pos]
                        
                        # Compare key fields
                        title_match = result1.get("title", "") == result2.get("title", "")
                        url_match = result1.get("url", "") == result2.get("url", "")
                        snippet_match = result1.get("snippet", "") == result2.get("snippet", "")
                        
                        exact_match = title_match and url_match and snippet_match
                        position_matches.append(exact_match)
                        
                        if not exact_match:
                            print(f"\n Position {pos} differs between Call {i+1} and Call {i+2}:")
                            print(f"   Call {i+1}: {result1.get('title', 'No title')[:50]}...")
                            print(f"   Call {i+2}: {result2.get('title', 'No title')[:50]}...")
                
                # Count matches for this position
                if position_matches:
                    position_match_rate = sum(position_matches) / len(position_matches)
                    matches_per_position.append(position_match_rate)
            
            # Overall similarity
            if matches_per_position:
                overall_similarity = sum(matches_per_position) / len(matches_per_position)
                print(f"\n Overall Result Similarity: {overall_similarity:.1%}")
                
                if overall_similarity >= 0.9:
                    print(" HIGHLY DETERMINISTIC - Results are very consistent")
                elif overall_similarity >= 0.7:
                    print(" MODERATELY DETERMINISTIC - Results vary somewhat")
                elif overall_similarity >= 0.5:
                    print(" LOW DETERMINISM - Results vary significantly")
                else:
                    print(" VERY NON-DETERMINISTIC - Results are highly variable")
            else:
                print(f"\n Cannot calculate similarity - insufficient data")
        else:
            print(f"\n Cannot compare - different result counts or no results")
    else:
        print(f"\n Insufficient successful calls for comparison (need at least 2)")
    
    # Show detailed comparison if we have results
    if len(all_results) >= 2:
        print(f"\n DETAILED COMPARISON")
        print("="*60)
        
        for i, call in enumerate(all_results):
            print(f"\n CALL {i+1} (at {call['timestamp']}):")
            print(f"   Response time: {call['response_time']:.2f}s")
            print(f"   Results: {len(call['results'])}")
            
            for j, result in enumerate(call["results"]):
                title = result.get("title", "No title")
                url = result.get("url", "No URL")
                print(f"     [{j}] {title}")
                print(f"         {url}")

def test_search_timing():
    """Test if timing affects search results"""
    
    query = "Việt Nam có chế độ đa đảng"
    
    print(f"\n⏰ TIMING TEST")
    print("="*60)
    print("Testing if delay between calls affects results...")
    
    results = []
    
    # Immediate calls
    print("\n IMMEDIATE CALLS (no delay):")
    for i in range(2):
        try:
            response = requests.post(
                "http://localhost:8004/search_vietnamese",
                json={"query": query, "max_results": 3},
                timeout=30
            )
            if response.status_code == 200:
                data = response.json()
                results.append(("immediate", i+1, data.get("results", [])))
                print(f"   Call {i+1}: {len(data.get('results', []))} results")
        except Exception as e:
            print(f"   Call {i+1} error: {e}")
    
    # Delayed calls
    print("\n DELAYED CALLS (5 seconds apart):")
    for i in range(2):
        try:
            response = requests.post(
                "http://localhost:8004/search_vietnamese",
                json={"query": query, "max_results": 3},
                timeout=30
            )
            if response.status_code == 200:
                data = response.json()
                results.append(("delayed", i+1, data.get("results", [])))
                print(f"   Call {i+1}: {len(data.get('results', []))} results")
            
            if i < 1:  # Only delay between calls
                print("    Waiting 5 seconds...")
                time.sleep(5)
                
        except Exception as e:
            print(f"   Call {i+1} error: {e}")
    
    # Compare timing groups
    print(f"\n TIMING COMPARISON:")
    immediate_results = [r for r in results if r[0] == "immediate"]
    delayed_results = [r for r in results if r[0] == "delayed"]
    
    if immediate_results and delayed_results:
        imm_titles = [r[2][0].get("title", "") for r in immediate_results if r[2]]
        del_titles = [r[2][0].get("title", "") for r in delayed_results if r[2]]
        
        if imm_titles and del_titles:
            timing_match = imm_titles[0] == del_titles[0]
            print(f"First result match (immediate vs delayed): {' SAME' if timing_match else ' DIFFERENT'}")
            print(f"Immediate: {imm_titles[0][:50]}...")
            print(f"Delayed: {del_titles[0][:50]}...")

if __name__ == "__main__":
    test_brave_search_deterministic()
    test_search_timing()
