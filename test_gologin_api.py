#!/usr/bin/env python3
"""
Test GoLogin API Connection

Simple script to test and debug GoLogin API connection.
"""

import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('config.env')

def test_gologin_api():
    """Test GoLogin API connection and endpoints."""
    
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
    
    # Test 1: Get profiles
    print("\n1. Testing GET /browser/v2")
    try:
        response = requests.get(f"{base_url}/browser/v2", headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Body: {response.text[:500]}...")
        
        if response.status_code == 200:
            profiles = response.json()
            print(f"Found {len(profiles)} profiles")
        else:
            print(f"Error: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"Exception: {e}")
    
    # Test 2: Try different endpoint
    print("\n2. Testing GET /browser")
    try:
        response = requests.get(f"{base_url}/browser", headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response Body: {response.text[:500]}...")
    except Exception as e:
        print(f"Exception: {e}")
    
    # Test 3: Try with different headers
    print("\n3. Testing with different headers")
    try:
        headers_alt = {
            "Authorization": f"Bearer {access_token}"
        }
        response = requests.get(f"{base_url}/browser/v2", headers=headers_alt)
        print(f"Status Code: {response.status_code}")
        print(f"Response Body: {response.text[:500]}...")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_gologin_api() 