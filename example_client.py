#!/usr/bin/env python3
"""
Example client script to test the Multi-Repo Ideation API
"""

import requests
import json
import time

API_BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test the health check endpoint"""
    print("🔍 Testing health check...")
    try:
        response = requests.get(f"{API_BASE_URL}/")
        print(f"✅ Health check: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_status():
    """Test the status endpoint"""
    print("\n📊 Testing status endpoint...")
    try:
        response = requests.get(f"{API_BASE_URL}/status")
        print(f"✅ Status: {json.dumps(response.json(), indent=2)}")
        return True
    except Exception as e:
        print(f"❌ Status check failed: {e}")
        return False

def test_ideation(project_idea, max_repos=3):
    """Test the ideation endpoint"""
    print(f"\n💡 Testing ideation for: '{project_idea}'")
    print(f"📦 Max repos to analyze: {max_repos}")
    
    payload = {
        "project_idea": project_idea,
        "max_repos": max_repos
    }
    
    try:
        print("⏳ Sending request... (this may take a while)")
        start_time = time.time()
        
        response = requests.post(
            f"{API_BASE_URL}/ideate",
            json=payload,
            timeout=300  # 5 minutes timeout
        )
        
        end_time = time.time()
        print(f"⏱️ Request completed in {end_time - start_time:.2f} seconds")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Ideation successful!")
            print(f"📈 Analyzed {result['total_repos_processed']} repositories")
            print(f"🔧 Found {len(result['aggregated_features'])} unique features")
            print(f"🛠️ Found {len(result['aggregated_tech_stack'])} unique tech stack items")
            
            print("\n📋 Aggregated Features:")
            for i, feature in enumerate(result['aggregated_features'][:10], 1):  # Show first 10
                print(f"  {i}. {feature}")
            if len(result['aggregated_features']) > 10:
                print(f"  ... and {len(result['aggregated_features']) - 10} more")
            
            print("\n🛠️ Tech Stack:")
            for tech in result['aggregated_tech_stack'][:10]:  # Show first 10
                print(f"  • {tech}")
            if len(result['aggregated_tech_stack']) > 10:
                print(f"  ... and {len(result['aggregated_tech_stack']) - 10} more")
            
            print("\n💡 Suggested New Features:")
            print(result['suggested_features'])
            
            return True
        else:
            print(f"❌ Request failed with status {response.status_code}")
            try:
                error_detail = response.json()
                print(f"Error details: {error_detail}")
            except:
                print(f"Error response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out (took longer than 5 minutes)")
        return False
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return False

def main():
    """Main function to run all tests"""
    print("🚀 Starting Multi-Repo Ideation API Tests\n")
    
    # Test health check
    if not test_health_check():
        print("❌ Health check failed. Is the server running?")
        return
    
    # Test status
    if not test_status():
        print("❌ Status check failed.")
        return
    
    # Test ideation with different project ideas
    test_cases = [
        ("half adder", 2),
    ]
    
    print("\n" + "="*60)
    print("🧪 RUNNING IDEATION TESTS")
    print("="*60)
    
    for project_idea, max_repos in test_cases:
        print("\n" + "-"*60)
        success = test_ideation(project_idea, max_repos)
        if success:
            print(f"✅ Test passed for: {project_idea}")
        else:
            print(f"❌ Test failed for: {project_idea}")
        print("-"*60)
        
        # Wait a bit between tests to avoid overwhelming the API
        time.sleep(2)
    
    print("\n🎉 All tests completed!")

if __name__ == "__main__":
    main()