#!/usr/bin/env python3
"""
Script khởi động toàn bộ hệ thống và kiểm tra nhanh
1. Khởi động lại tất cả services
2. Kiểm tra health của các services
3. Test với 1 câu đơn giản
"""

import subprocess
import time
import requests
import json
import sys
import os

# Configuration
SERVICES = [
    {
        "name": "Translation",
        "script": "clean_backend.py",
        "cwd": "d:/bmad/vietnamese-translation-system",
        "port": 8003,
        "health_url": "http://localhost:8003/",
        "pid": None
    },
    {
        "name": "MiniCheck",
        "script": "minicheck_server.py", 
        "cwd": "d:/bmad/minicheck",
        "port": 8002,
        "health_url": "http://localhost:8002/health",
        "pid": None
    },
    {
        "name": "Brave Search",
        "script": "brave_search_server.py",
        "cwd": "d:/bmad/brave-search-baseline", 
        "port": 8004,
        "health_url": "http://localhost:8004/",
        "pid": None
    },
    {
        "name": "Fact Checker",
        "script": "start_vietnamese_checker.py",
        "cwd": "d:/bmad/vietnamese-fact-checker",
        "port": 8005,
        "health_url": "http://localhost:8005/",
        "pid": None
    }
]

# Test claim
TEST_CLAIM = "Hà Nội là thủ đô của Việt Nam"
EXPECTED_RESULT = "SUPPORTED"

def print_header(title):
    """In header với border"""
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)

def kill_existing_processes():
    """Kill các processes đang chạy trên các port"""
    print_header("KILLING EXISTING PROCESSES")
    
    try:
        # Kill Python processes on our ports
        result = subprocess.run(['netstat', '-ano'], capture_output=True, text=True)
        lines = result.stdout.split('\n')
        
        pids_to_kill = []
        for line in lines:
            if any(str(svc["port"]) in line for svc in SERVICES):
                parts = line.split()
                if len(parts) >= 5:
                    pid = parts[-1]
                    if pid.isdigit():
                        pids_to_kill.append(pid)
        
        # Remove duplicates
        pids_to_kill = list(set(pids_to_kill))
        
        if pids_to_kill:
            print(f" Killing processes: {pids_to_kill}")
            for pid in pids_to_kill:
                try:
                    subprocess.run(['taskkill', '/F', '/PID', pid], capture_output=True)
                    print(f"    Killed PID {pid}")
                except:
                    print(f"    Failed to kill PID {pid}")
        else:
            print(" No processes to kill")
            
    except Exception as e:
        print(f" Error killing processes: {e}")

def start_services():
    """Khởi động tất cả services"""
    print_header("STARTING ALL SERVICES")
    
    for i, service in enumerate(SERVICES):
        print(f"\n[{i+1}/{len(SERVICES)}] Starting {service['name']} (Port {service['port']})...")
        
        try:
            # Start service in background
            process = subprocess.Popen(
                ["python", service["script"]],
                cwd=service["cwd"],
                creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
            )
            
            service["pid"] = process.pid
            print(f"    {service['name']} started (PID: {process.pid})")
            
            # Wait a bit between services
            time.sleep(3)
            
        except Exception as e:
            print(f"    Failed to start {service['name']}: {e}")
            service["pid"] = None

def check_service_health():
    """Kiểm tra health của tất cả services"""
    print_header("CHECKING SERVICE HEALTH")
    
    all_healthy = True
    
    for service in SERVICES:
        print(f"\n Checking {service['name']}...")
        
        try:
            response = requests.get(service["health_url"], timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                status = data.get("status", "healthy")
                
                print(f"    {service['name']}: {status}")
                
                # Show model info if available
                if "model" in data:
                    print(f"      Model: {data['model']}")
                    
            else:
                print(f"    {service['name']}: HTTP {response.status_code}")
                all_healthy = False
                
        except Exception as e:
            print(f"    {service['name']}: {e}")
            all_healthy = False
    
    return all_healthy

def test_fact_checker():
    """Test Fact Checker với câu đơn giản"""
    print_header("TESTING FACT CHECKER")
    
    print(f" Test Claim: {TEST_CLAIM}")
    print(f" Expected: {EXPECTED_RESULT}")
    
    try:
        start_time = time.time()
        response = requests.post(
            "http://localhost:8005/check",
            json={"claim": TEST_CLAIM},
            timeout=60
        )
        end_time = time.time()
        
        if response.status_code == 200:
            data = response.json()
            
            verdict = data.get("verdict", "ERROR")
            confidence = data.get("confidence", 0)
            processing_time = data.get("processing_time", 0)
            evidence_count = data.get("evidence_count", 0)
            
            print(f"\n RESULTS:")
            print(f"   Verdict: {verdict}")
            print(f"   Confidence: {confidence:.3f}")
            print(f"   Evidence Count: {evidence_count}")
            print(f"   Processing Time: {processing_time:.2f}s")
            print(f"   Total Time: {end_time - start_time:.2f}s")
            
            # Check result
            if verdict == EXPECTED_RESULT:
                print(f"\n TEST PASSED - Expected {EXPECTED_RESULT}, got {verdict}")
            else:
                print(f"\n TEST FAILED - Expected {EXPECTED_RESULT}, got {verdict}")
                
            # Show debug info if available
            debug_info = data.get("debug_info", {})
            if debug_info:
                print(f"\n DEBUG INFO:")
                
                # Translation info
                trans_debug = debug_info.get("translation", {})
                if trans_debug:
                    print(f"   Translation Model: {trans_debug.get('translation_model', 'Unknown')}")
                    print(f"   Original Claim: {trans_debug.get('original_claim', 'Unknown')}")
                    print(f"   English Claim: {trans_debug.get('english_claim', 'Unknown')}")
                
                # MiniCheck info
                mc_debug = debug_info.get("minicheck_raw_output", {})
                if mc_debug:
                    print(f"   MiniCheck Label: {mc_debug.get('label', 'Unknown')}")
                    print(f"   MiniCheck Score: {mc_debug.get('score', 0):.3f}")
                    print(f"   MiniCheck Aggregation: {mc_debug.get('aggregation', 'Unknown')}")
                    
                    all_scores = mc_debug.get("all_scores", [])
                    if all_scores:
                        print(f"   Evidence Scores ({len(all_scores)}):")
                        for i, score in enumerate(all_scores[:3]):  # Show first 3
                            label = score.get("label", "N/A")
                            score_val = score.get("score", 0)
                            print(f"     [{i}] {label}: {score_val:.3f}")
            
        else:
            print(f" API Error: HTTP {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f" Test Error: {e}")

def show_summary():
    """Hiển thị summary"""
    print_header("SYSTEM SUMMARY")
    
    print(" Services Status:")
    for service in SERVICES:
        status = " RUNNING" if service["pid"] else " STOPPED"
        print(f"   {service['name']} (Port {service['port']}): {status}")
    
    print(f"\n Service URLs:")
    for service in SERVICES:
        print(f"   {service['name']}: http://localhost:{service['port']}")
    
    print(f"\n Test Info:")
    print(f"   Claim: {TEST_CLAIM}")
    print(f"   Expected: {EXPECTED_RESULT}")

def main():
    """Main function"""
    print(" VIETNAMESE FACT CHECKER - SYSTEM STARTUP & TEST")
    print("="*60)
    
    # Step 1: Kill existing processes
    kill_existing_processes()
    
    # Step 2: Start all services
    start_services()
    
    # Step 3: Wait for services to be ready
    print(f"\n Waiting 10 seconds for services to fully start...")
    time.sleep(10)
    
    # Step 4: Check service health
    all_healthy = check_service_health()
    
    if all_healthy:
        # Step 5: Run test
        test_fact_checker()
    else:
        print(f"\n Some services are not healthy. Skipping test.")
    
    # Step 6: Show summary
    show_summary()
    
    print(f"\n System startup & test completed!")
    print(f" You can now test with: curl -X POST http://localhost:8005/check -H 'Content-Type: application/json' -d '{{\"claim\":\"Your claim here\"}}'")

if __name__ == "__main__":
    main()
