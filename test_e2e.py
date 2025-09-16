#!/usr/bin/env python3
"""
E2E Test for AI Auditor Local-First Architecture
Tests both AI and UI services with minimal audit workflow
"""

import json
import os
import requests
import time
from datetime import datetime


def test_ai_health():
    """Test AI service health endpoint."""
    print("🤖 Testing AI health endpoint...")
    try:
        response = requests.get("http://localhost:8001/healthz", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "healthy" and data.get("ready") is True:
                print("✅ AI health check passed")
                return True
            else:
                print(f"❌ AI health check failed: {data}")
                return False
        else:
            print(f"❌ AI health check failed: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ AI health check error: {e}")
        return False


def test_ui_health():
    """Test UI service health endpoint."""
    print("🖥️ Testing UI health endpoint...")
    try:
        response = requests.get("http://localhost:8501/_stcore/health", timeout=5)
        if response.status_code == 200 and response.text.strip() == "ok":
            print("✅ UI health check passed")
            return True
        else:
            print(f"❌ UI health check failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ UI health check error: {e}")
        return False


def test_analyze_endpoint():
    """Test analyze endpoint with mock audit request."""
    print("🔍 Testing analyze endpoint...")
    try:
        url = "http://localhost:8001/analyze"
        auth = ("user", "TwojPIN123!")
        data = {
            "prompt": "Przeanalizuj faktury i sprawdź zgodność z przepisami podatkowymi",
            "max_new_tokens": 200,
            "temperature": 0.7
        }
        
        response = requests.post(url, json=data, auth=auth, timeout=10)
        if response.status_code == 200:
            result = response.json()
            if result.get("status") == "success" and "output" in result:
                print("✅ Analyze endpoint test passed")
                return True, result
            else:
                print(f"❌ Analyze endpoint failed: {result}")
                return False, None
        else:
            print(f"❌ Analyze endpoint failed: HTTP {response.status_code}")
            return False, None
    except Exception as e:
        print(f"❌ Analyze endpoint error: {e}")
        return False, None


def save_audit_artifact(analysis_result):
    """Save audit artifact to outputs directory."""
    print("💾 Saving audit artifact...")
    try:
        os.makedirs("outputs", exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        artifact = {
            "timestamp": timestamp,
            "analysis": analysis_result,
            "test_type": "e2e_verification",
            "status": "completed"
        }
        
        artifact_path = f"outputs/e2e_test_{timestamp}.json"
        with open(artifact_path, "w", encoding="utf-8") as f:
            json.dump(artifact, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Artifact saved to {artifact_path}")
        return True
    except Exception as e:
        print(f"❌ Failed to save artifact: {e}")
        return False


def main():
    """Run E2E test suite."""
    print("🚀 Starting AI Auditor E2E Test")
    print("=" * 50)
    
    # Test 1: AI Health
    ai_healthy = test_ai_health()
    
    # Test 2: UI Health  
    ui_healthy = test_ui_health()
    
    # Test 3: Analyze Endpoint
    analyze_success, analysis_result = test_analyze_endpoint()
    
    # Test 4: Save Artifact
    artifact_saved = False
    if analyze_success and analysis_result:
        artifact_saved = save_audit_artifact(analysis_result)
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 E2E Test Results:")
    print(f"  AI Health: {'✅ PASS' if ai_healthy else '❌ FAIL'}")
    print(f"  UI Health: {'✅ PASS' if ui_healthy else '❌ FAIL'}")
    print(f"  Analyze: {'✅ PASS' if analyze_success else '❌ FAIL'}")
    print(f"  Artifact: {'✅ PASS' if artifact_saved else '❌ FAIL'}")
    
    all_passed = ai_healthy and ui_healthy and analyze_success and artifact_saved
    print(f"\n🎯 Overall: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
    
    return all_passed


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)

