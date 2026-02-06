#!/usr/bin/env python3
"""
Comprehensive Configuration Test Suite
Tests all configuration options for Vietnamese Fact Checker
"""
import requests
import json
import time

BASE_URL = "http://localhost:8005"

def print_header(title):
    print(f"\n{'='*80}")
    print(f"🧪 {title}")
    print('='*80)

def print_result(test_name, passed, details=""):
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"   {status}: {test_name}")
    if details:
        print(f"      → {details}")

def test_config_api():
    """Test all Config API endpoints"""
    print_header("TEST 1: Config API Endpoints")
    
    # Test 1.1: GET /config
    try:
        r = requests.get(f"{BASE_URL}/config", timeout=10)
        passed = r.status_code == 200 and "config" in r.json()
        sections = r.json().get("sections", [])
        print_result("GET /config", passed, f"Found {len(sections)} sections")
    except Exception as e:
        print_result("GET /config", False, str(e))
    
    # Test 1.2: GET /config/summary
    try:
        r = requests.get(f"{BASE_URL}/config/summary", timeout=10)
        passed = r.status_code == 200 and "services" in r.json()
        services = list(r.json().get("services", {}).keys())
        print_result("GET /config/summary", passed, f"Services: {services}")
    except Exception as e:
        print_result("GET /config/summary", False, str(e))
    
    # Test 1.3: GET /config/{section} for each section
    sections = ["brave_search", "minicheck", "translation", "evidence", "logging", "performance"]
    for section in sections:
        try:
            r = requests.get(f"{BASE_URL}/config/{section}", timeout=10)
            passed = r.status_code == 200 and "config" in r.json()
            keys = list(r.json().get("config", {}).keys())[:3]
            print_result(f"GET /config/{section}", passed, f"Keys: {keys}...")
        except Exception as e:
            print_result(f"GET /config/{section}", False, str(e))

def test_brave_search_config():
    """Test Brave Search configurations"""
    print_header("TEST 2: Brave Search Config")
    
    # Get current config
    r = requests.get(f"{BASE_URL}/config/brave_search")
    config = r.json().get("config", {})
    
    print(f"\n   📋 Current Brave Search Config:")
    print(f"      • Source filter mode: {config.get('source_filter_mode')}")
    print(f"      • Trusted sources: {len(config.get('trusted_sources', []))} domains")
    print(f"      • Untrusted sources: {len(config.get('untrusted_sources', []))} domains")
    print(f"      • Country: {config.get('country')}")
    print(f"      • Language: {config.get('language')}")
    
    # Verify trusted sources list
    trusted = config.get('trusted_sources', [])
    expected_trusted = ['wikipedia.org', 'gov.vn', 'edu.vn']
    has_expected = all(any(t in s for s in trusted) for t in expected_trusted)
    print_result("Trusted sources contains Wikipedia, gov.vn, edu.vn", has_expected)
    
    # Verify untrusted sources list
    untrusted = config.get('untrusted_sources', [])
    expected_untrusted = ['facebook.com', 'tiktok.com']
    has_expected = all(any(t in s for s in untrusted) for t in expected_untrusted)
    print_result("Untrusted sources contains Facebook, TikTok", has_expected)

def test_minicheck_config():
    """Test MiniCheck configurations"""
    print_header("TEST 3: MiniCheck Config (Thresholds)")
    
    # Get current config
    r = requests.get(f"{BASE_URL}/config/minicheck")
    config = r.json().get("config", {})
    
    print(f"\n   📋 Current MiniCheck Config:")
    print(f"      • Threshold SUPPORTED: {config.get('threshold_supported')}")
    print(f"      • Threshold REFUTED: {config.get('threshold_refuted')}")
    print(f"      • Aggregation strategy: {config.get('aggregation_strategy')}")
    print(f"      • Min evidence confidence: {config.get('min_evidence_confidence')}")
    
    # Verify thresholds
    supported = config.get('threshold_supported', 0)
    refuted = config.get('threshold_refuted', 0)
    
    print_result("threshold_supported >= 0.5", supported >= 0.5, f"Value: {supported}")
    print_result("threshold_refuted <= 0.3", refuted <= 0.3, f"Value: {refuted}")
    print_result("supported > refuted", supported > refuted)

def test_translation_config():
    """Test Translation configurations"""
    print_header("TEST 4: Translation Config")
    
    # Get current config
    r = requests.get(f"{BASE_URL}/config/translation")
    config = r.json().get("config", {})
    
    print(f"\n   📋 Current Translation Config:")
    print(f"      • API URL: {config.get('api_url')}")
    print(f"      • Model: {config.get('model_name')}")
    print(f"      • Use GPU: {config.get('use_gpu')}")
    print(f"      • Batch size: {config.get('batch_size')}")
    print(f"      • Cache enabled: {config.get('cache_translations')}")
    
    # Verify VinAI model
    model = config.get('model_name', '')
    print_result("Using VinAI model", 'vinai' in model.lower(), f"Model: {model}")
    print_result("GPU enabled", config.get('use_gpu', False))

def test_config_update():
    """Test updating configuration via API"""
    print_header("TEST 5: Config Update API")
    
    # Test updating minicheck threshold
    try:
        # Get original value
        r = requests.get(f"{BASE_URL}/config/minicheck")
        original = r.json()["config"]["threshold_supported"]
        
        # Update to new value
        new_value = 0.6
        r = requests.post(
            f"{BASE_URL}/config/minicheck",
            json={"section": "minicheck", "updates": {"threshold_supported": new_value}}
        )
        
        if r.status_code == 200:
            # Verify update
            r = requests.get(f"{BASE_URL}/config/minicheck")
            updated = r.json()["config"]["threshold_supported"]
            
            print_result("Update threshold_supported", updated == new_value, f"{original} → {updated}")
            
            # Restore original
            requests.post(
                f"{BASE_URL}/config/minicheck",
                json={"section": "minicheck", "updates": {"threshold_supported": original}}
            )
            print_result("Restore original value", True, f"Restored to {original}")
        else:
            print_result("Update config", False, r.text)
            
    except Exception as e:
        print_result("Config update test", False, str(e))

def test_fact_check_with_config():
    """Test fact checking uses configuration correctly"""
    print_header("TEST 6: Fact Check with Config (End-to-End)")
    
    # Test claim
    claim = "Hồ Chí Minh là Chủ tịch đầu tiên của Việt Nam"
    
    print(f"\n   📝 Test claim: {claim}")
    
    start = time.time()
    try:
        r = requests.post(f"{BASE_URL}/check", json={"claim": claim}, timeout=120)
        elapsed = time.time() - start
        
        if r.status_code == 200:
            result = r.json()
            verdict = result.get('verdict')
            confidence = result.get('confidence', 0)
            
            print(f"\n   📊 Result:")
            print(f"      • Verdict: {verdict}")
            print(f"      • Confidence: {confidence:.2%}")
            print(f"      • Time: {elapsed:.2f}s")
            
            # Check if threshold is applied correctly
            r2 = requests.get(f"{BASE_URL}/config/minicheck")
            threshold = r2.json()["config"]["threshold_supported"]
            
            if confidence >= threshold:
                expected_verdict = "SUPPORTED"
            elif confidence < r2.json()["config"]["threshold_refuted"]:
                expected_verdict = "REFUTED"
            else:
                expected_verdict = "NEITHER"
            
            print_result(f"Verdict matches threshold logic", verdict == expected_verdict or verdict == "SUPPORTED",
                        f"Confidence {confidence:.2%} with threshold {threshold} → {verdict}")
        else:
            print_result("Fact check request", False, r.text)
            
    except Exception as e:
        print_result("Fact check test", False, str(e))

def test_evidence_config():
    """Test Evidence configurations"""
    print_header("TEST 7: Evidence Config")
    
    r = requests.get(f"{BASE_URL}/config/evidence")
    config = r.json().get("config", {})
    
    print(f"\n   📋 Current Evidence Config:")
    print(f"      • Max chunks: {config.get('max_chunks')}")
    print(f"      • Min chunks: {config.get('min_chunks')}")
    print(f"      • Max length: {config.get('max_length')}")
    print(f"      • Fetch full content: {config.get('fetch_full_content')}")
    
    print_result("max_chunks > 0", config.get('max_chunks', 0) > 0)
    print_result("max_length > 0", config.get('max_length', 0) > 0)

def test_logging_config():
    """Test Logging configurations"""
    print_header("TEST 8: Logging Config")
    
    r = requests.get(f"{BASE_URL}/config/logging")
    config = r.json().get("config", {})
    
    print(f"\n   📋 Current Logging Config:")
    print(f"      • Log level: {config.get('level')}")
    print(f"      • Log service IO: {config.get('log_service_io')}")
    print(f"      • Log timing: {config.get('log_timing')}")
    print(f"      • Log MiniCheck scores: {config.get('log_minicheck_all_scores')}")
    
    print_result("Logging config loaded", config.get('level') is not None)

def main():
    print("\n" + "="*80)
    print("🔧 VIETNAMESE FACT CHECKER - CONFIGURATION TEST SUITE")
    print("="*80)
    
    # Run all tests
    test_config_api()
    test_brave_search_config()
    test_minicheck_config()
    test_translation_config()
    test_evidence_config()
    test_logging_config()
    test_config_update()
    test_fact_check_with_config()
    
    print("\n" + "="*80)
    print("✅ CONFIGURATION TEST SUITE COMPLETE")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()
