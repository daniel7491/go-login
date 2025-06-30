#!/usr/bin/env python3
"""
Test GoLogin Profile Creation

Debug script to test profile creation and see the exact error response.
"""

import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('config.env')

def test_profile_creation():
    """Test profile creation with different request formats."""
    
    # Get access token from environment
    access_token = os.getenv('GOLOGIN_ACCESS_TOKEN')
    if not access_token:
        print("Error: GOLOGIN_ACCESS_TOKEN not found in environment")
        return
    
    print(f"Using access token: {access_token[:10]}...")
    
    # Set up headers
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    base_url = "https://api.gologin.com"
    
    # Test 1: Basic profile creation
    print("\n1. Testing POST /browser with complete data")
    profile_data = {
        "name": "test_profile_api",
        "notes": "test created by script",
        "browserType": "chrome",
        "os": "win",
        "vendor": "Google Inc.",
        "navigator": {
            "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "resolution": "1920x1080",
            "language": "en-US,en;q=0.9",
            "platform": "Win32"
        },
        "proxy": {
            "mode": "none",
            "host": "",
            "port": 0,
            "username": "",
            "password": ""
        },
        "timezone": {
            "fillBasedOnIp": True,
            "timezone": ""
        },
        "geolocation": {
            "mode": "prompt",
            "enabled": True,
            "customize": True,
            "fillBasedOnIp": True,
            "latitude": 0,
            "longitude": 0,
            "accuracy": 10
        }
    }
    
    try:
        response = requests.post(f"{base_url}/browser", headers=headers, json=profile_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response Body: {response.text}")
        
        if response.status_code == 200 or response.status_code == 201:
            result = response.json()
            print(f"Success! Profile ID: {result.get('id', 'N/A')}")
        else:
            print(f"Error: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"Exception: {e}")
    
    # Test 2: Profile creation with proxy
    print("\n2. Testing POST /browser with proxy")
    profile_data_with_proxy = {
        "name": "test_profile_with_proxy",
        "notes": "test with proxy",
        "browserType": "chrome",
        "os": "win",
        "vendor": "Google Inc.",
        "navigator": {
            "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "resolution": "1920x1080",
            "language": "en-US,en;q=0.9",
            "platform": "Win32"
        },
        "proxy": {
            "mode": "http",
            "host": "127.0.0.1",
            "port": 8080,
            "username": "",
            "password": ""
        },
        "timezone": {
            "fillBasedOnIp": True,
            "timezone": ""
        },
        "geolocation": {
            "mode": "prompt",
            "enabled": True,
            "customize": True,
            "fillBasedOnIp": True,
            "latitude": 0,
            "longitude": 0,
            "accuracy": 10
        }
    }
    
    try:
        response = requests.post(f"{base_url}/browser", headers=headers, json=profile_data_with_proxy)
        print(f"Status Code: {response.status_code}")
        print(f"Response Body: {response.text}")
        
        if response.status_code == 200 or response.status_code == 201:
            result = response.json()
            print(f"Success! Profile ID: {result.get('id', 'N/A')}")
        else:
            print(f"Error: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"Exception: {e}")
    
    # Test 3: Try different endpoint
    print("\n3. Testing POST /browser/v2")
    try:
        response = requests.post(f"{base_url}/browser/v2", headers=headers, json=profile_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response Body: {response.text}")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_profile_creation() 