#!/usr/bin/env python3
"""
Debug GoLogin Profile Creation

Simple script to test profile creation and see the exact error response.
"""

import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('config.env')

def debug_profile_creation():
    """Debug profile creation with minimal data."""
    
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
    
    # Test with minimal required data
    print("\nTesting POST /browser with minimal data")
    profile_data = {
        "os": "win",
        "navigator": {
            "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.6998.36 Safari/537.36",
            "resolution": "1920x1080",
            "language": "en-US",
            "platform": "Win32"
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

if __name__ == "__main__":
    debug_profile_creation() 