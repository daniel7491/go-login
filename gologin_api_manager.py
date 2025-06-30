#!/usr/bin/env python3
"""
GoLogin API Manager

This script integrates with GoLogin API to manage browser profiles
and import cookies and proxy settings from the database.
"""

import json
import requests
import time
import os
from typing import List, Dict, Any, Optional
from multi_network_cookie_getter_cli import get_user_data_for_usernames_env, update_browser_gologin_id_env
from dotenv import load_dotenv

# Load environment variables
load_dotenv('config.env')


class GoLoginAPI:
    def __init__(self, access_token: str = None, base_url: str = "https://api.gologin.com"):
        """
        Initialize GoLogin API client.
        
        Args:
            access_token (str): GoLogin API access token (uses env var if None)
            base_url (str): GoLogin API base URL
        """
        if access_token is None:
            access_token = os.getenv('GOLOGIN_ACCESS_TOKEN')
            if not access_token:
                raise ValueError("GoLogin access token not found in environment variables")
        
        self.access_token = access_token
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
    
    def get_profiles(self) -> List[Dict[str, Any]]:
        """
        Get all browser profiles.
        
        Returns:
            List[Dict[str, Any]]: List of profiles
        """
        try:
            response = requests.get(f"{self.base_url}/browser/v2", headers=self.headers)
            response.raise_for_status()
            data = response.json()
            return data.get("profiles", []) if isinstance(data, dict) else []
        except requests.exceptions.RequestException as e:
            print(f"Error getting profiles: {e}")
            return []
    
    def get_profile(self, profile_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific profile by ID.
        
        Args:
            profile_id (str): Profile ID
            
        Returns:
            Optional[Dict[str, Any]]: Profile data or None
        """
        try:
            response = requests.get(f"{self.base_url}/browser/custom/{profile_id}", headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error getting profile {profile_id}: {e}")
            return None
    
    def create_profile(self, name: str, notes: str = "", proxy: Dict[str, Any] = None) -> Optional[str]:
        """
        Create a new browser profile.
        
        Args:
            name (str): Profile name
            notes (str): Profile notes
            proxy (Dict[str, Any]): Proxy configuration
            
        Returns:
            Optional[str]: Profile ID if successful, None otherwise
        """
        # Default proxy if none provided
        if proxy is None:
            proxy = {
                "mode": "none",
                "host": "",
                "port": 0,
                "username": "",
                "password": ""
            }
        
        profile_data = {
            "name": name,
            "notes": notes,
            "browserType": "chrome",  # Required
            "os": "win",  # Required
            "navigator": {
                "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.6998.36 Safari/537.36",
                "resolution": "1920x1080",
                "language": "en-US",
                "platform": "Win32"
            },
            "proxy": proxy,
            "webGLMetadata": {
                "mode": "mask",
                "vendor": "Google Inc. (AMD)",
                "renderer": "ANGLE (AMD, AMD Radeon(TM) R5 Graphics (0x000098E4) Direct3D11 vs_5_0 ps_5_0, D3D11)"
            },
            "timezone": {
                "enabled": True,
                "fillBasedOnIp": True,
                "timezone": ""
            },
            "webRTC": {
                "mode": "disabled"
            },
            "storage": {
                "local": True,
                "extensions": True,
                "bookmarks": True,
                "history": True,
                "passwords": True,
                "session": True,
                "indexedDb": False,
                "enableExternalExtensions": False
            },
            "plugins": {
                "enableVulnerable": True,
                "enableFlash": True
            },
            "canvas": {
                "mode": "off"
            },
            "webGL": {
                "mode": "noise"
            },
            "clientRects": {
                "mode": "noise"
            },
            "audioContext": {
                "mode": "noise"
            },
            "mediaDevices": {
                "enableMasking": True,
                "videoInputs": 0,
                "audioInputs": 0,
                "audioOutputs": 0
            },
            "fonts": {
                "families": [
                    "AIGDT",
                    "AMGDT",
                    "Abyssinica Sil Regular",
                    "Alef",
                    "Ani",
                    "AnjaliOldLipi",
                    "Caladea",
                    "Chandas",
                    "Chilanka",
                    "Dancing Script",
                    "David",
                    "David Libre",
                    "DejaVu Sans",
                    "DejaVu Sans Condensed",
                    "DejaVu Sans Light",
                    "DejaVu Sans Mono",
                    "DejaVu Serif",
                    "DejaVu Serif Condensed",
                    "Droid Sans",
                    "Droid Sans Mono",
                    "Dyuthi",
                    "Frank Ruehl",
                    "Frank Ruehl Libre",
                    "Frank Ruehl Libre Black",
                    "Frank Ruehl Libre Light",
                    "FreeMono",
                    "FreeSans",
                    "FreeSerif",
                    "Gargi",
                    "Garuda",
                    "Gubbi",
                    "Jamrul",
                    "KacstBook",
                    "KacstOffice",
                    "Kalapi",
                    "Kalimati",
                    "Karumbi",
                    "Khmer OS",
                    "Khmer UI",
                    "Kinnari",
                    "Laksaman",
                    "Liberation Mono",
                    "Liberation Sans",
                    "Liberation Sans Narrow",
                    "Liberation Serif",
                    "Lohit Devanagari",
                    "Lohit Telugu",
                    "Loma",
                    "Manjari",
                    "Meera",
                    "Meera Inimai",
                    "Miriam",
                    "Miriam Fixed",
                    "Miriam Libre",
                    "Mitra Mono",
                    "Mukti Narrow",
                    "Nakula",
                    "Navuli",
                    "Nimbus Roman",
                    "Nimbus Sans",
                    "Norasi",
                    "Noto Mono",
                    "Noto Sans",
                    "Noto Sans Arabic UI",
                    "Noto Sans CJK HK",
                    "Noto Sans CJK JP",
                    "Noto Sans CJK KR",
                    "Noto Sans CJK SC",
                    "Noto Sans CJK TC",
                    "Noto Sans Lisu",
                    "Noto Sans Mono CJK HK",
                    "Noto Sans Mono CJK JP",
                    "Noto Sans Mono CJK KR",
                    "Noto Sans Mono CJK SC",
                    "Noto Sans Mono CJK TC",
                    "Noto Serif",
                    "Noto Serif CJK JP",
                    "Noto Serif CJK KR",
                    "Noto Serif CJK SC",
                    "Noto Serif CJK TC",
                    "Noto Serif Georgian",
                    "Noto Serif Hebrew",
                    "Noto Serif Italic",
                    "Noto Serif Lao",
                    "OpenSymbol",
                    "Oswald",
                    "Padauk",
                    "Padauk Book",
                    "Pagul",
                    "Phetsarath OT",
                    "Pothana2000",
                    "Purisa",
                    "Rachana",
                    "Rekha",
                    "Roboto",
                    "Roboto Black",
                    "Roboto Light",
                    "Roboto Medium",
                    "Rubik Black",
                    "Rubik Light",
                    "Rubik Medium",
                    "Russo One",
                    "Saab",
                    "Sahadeva",
                    "Samanata",
                    "Samyak Devanagari",
                    "Samyak Gujarati",
                    "Samyak Malayalam",
                    "Samyak Tamil",
                    "Sarai",
                    "Source Code Pro",
                    "Source Code Pro Black",
                    "Source Code Pro Extra Light",
                    "Source Code Pro Light",
                    "Source Code Pro Medium",
                    "Source Code Pro Semibold",
                    "Source Sans Pro",
                    "Source Sans Pro Black",
                    "Source Sans Pro Extra Light",
                    "Source Sans Pro Light",
                    "Source Sans Pro Semibold",
                    "Source Serif Pro",
                    "Source Serif Pro Black",
                    "Source Serif Pro Extra Light",
                    "Source Serif Pro Light",
                    "Source Serif Pro Semibold",
                    "Suruma",
                    "Tibetan Machine Uni",
                    "Tlwg Mono",
                    "Tlwg Typewriter",
                    "Tlwg Typist",
                    "Tlwg Typo",
                    "URW Bookman L",
                    "Ubuntu",
                    "Umpush",
                    "Uroob",
                    "Vemana2000",
                    "Waree"
                ],
                "enableMasking": True,
                "enableDomRect": True
            }
        }
        
        try:
            response = requests.post(f"{self.base_url}/browser", 
                                   headers=self.headers, 
                                   json=profile_data)
            response.raise_for_status()
            result = response.json()
            return result.get("id")
        except requests.exceptions.RequestException as e:
            print(f"Error creating profile: {e}")
            return None
    
    def update_profile(self, profile_id: str, profile_data: Dict[str, Any]) -> bool:
        """
        Update an existing profile.
        
        Args:
            profile_id (str): Profile ID
            profile_data (Dict[str, Any]): Updated profile data
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            response = requests.put(f"{self.base_url}/browser/{profile_id}", 
                                  headers=self.headers, 
                                  json=profile_data)
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            print(f"Error updating profile {profile_id}: {e}")
            return False
    
    def delete_profile(self, profile_id: str) -> bool:
        """
        Delete a profile.
        
        Args:
            profile_id (str): Profile ID
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            response = requests.delete(f"{self.base_url}/browser/custom/{profile_id}", 
                                     headers=self.headers)
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            print(f"Error deleting profile {profile_id}: {e}")
            return False
    
    def update_cookies(self, profile_id: str, cookies: List[Dict[str, Any]]) -> bool:
        """
        Update cookies for a profile.
        
        Args:
            profile_id (str): Profile ID
            cookies (List[Dict[str, Any]]): List of cookies in browser extension format
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            response = requests.post(f"{self.base_url}/browser/{profile_id}/cookies", 
                                  headers=self.headers, 
                                  json=cookies)
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            print(f"Error updating cookies for profile {profile_id}: {e}")
            return False
    
    def get_cookies(self, profile_id: str) -> List[Dict[str, Any]]:
        """
        Get cookies for a profile.
        
        Args:
            profile_id (str): Profile ID
            
        Returns:
            List[Dict[str, Any]]: List of cookies
        """
        try:
            response = requests.get(f"{self.base_url}/browser/custom/{profile_id}/cookies", 
                                  headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error getting cookies for profile {profile_id}: {e}")
            return []


def create_profile_with_data(api: GoLoginAPI, network: str, username: str, cookies: List[Dict[str, Any]], proxy: Dict[str, Any] = None) -> Optional[str]:
    """
    Create a new profile with cookies and proxy for a specific network and username.
    
    Args:
        api (GoLoginAPI): GoLogin API instance
        network (str): Social network name
        username (str): Username
        cookies (List[Dict[str, Any]]): Cookies in browser extension format
        proxy (Dict[str, Any]): Proxy configuration
        
    Returns:
        Optional[str]: Profile ID if successful, None otherwise
    """
    # Create the profile first to get the ID
    temp_profile_name = f"{network}_{username}"
    temp_notes = f"auto created {username}"
    
    # Create the profile with proxy
    profile_id = api.create_profile(temp_profile_name, temp_notes, proxy)
    
    if profile_id:
        # Update the profile name to include the profile ID
        final_profile_name = f"{username}_{profile_id}"
        
        # Update the profile with the new name
        profile_data = {"name": final_profile_name}
        if api.update_profile(profile_id, profile_data):
            print(f"Created profile: {final_profile_name} (ID: {profile_id})")
        else:
            print(f"Created profile: {temp_profile_name} (ID: {profile_id}) - Failed to update name")
        
        if proxy:
            print(f"Configured proxy: {proxy.get('host', 'N/A')}:{proxy.get('port', 'N/A')}")
        else:
            print("No proxy configured")
        
        # Update cookies only if cookies are available
        if cookies:
            if api.update_cookies(profile_id, cookies):
                print(f"Updated cookies for profile {profile_id}")
            else:
                print(f"Failed to update cookies for profile {profile_id}")
        else:
            print("No cookies to update (cookies column was empty)")
        
        # Save profile ID to database
        if update_browser_gologin_id_env(network, username, profile_id):
            print(f"Saved profile ID to database for {username}")
        else:
            print(f"Warning: Failed to save profile ID to database for {username}")
        
        return profile_id
    else:
        print(f"Failed to create profile for {username}")
        return None


def update_existing_profile_data(api: GoLoginAPI, profile_id: str, cookies: List[Dict[str, Any]], proxy: Dict[str, Any] = None) -> bool:
    """
    Update cookies and proxy for an existing profile.
    
    Args:
        api (GoLoginAPI): GoLogin API instance
        profile_id (str): Profile ID
        cookies (List[Dict[str, Any]]): Cookies in browser extension format
        proxy (Dict[str, Any]): Proxy configuration
        
    Returns:
        bool: True if successful, False otherwise
    """
    success = True
    
    # Update cookies only if cookies are available
    if cookies:
        if api.update_cookies(profile_id, cookies):
            print(f"Updated cookies for profile {profile_id}")
        else:
            print(f"Failed to update cookies for profile {profile_id}")
            success = False
    else:
        print("No cookies to update (cookies column was empty)")
    
    # Update proxy if provided
    if proxy:
        profile_data = {"proxy": proxy}
        if api.update_profile(profile_id, profile_data):
            print(f"Updated proxy for profile {profile_id}")
        else:
            print(f"Failed to update proxy for profile {profile_id}")
            success = False
    
    return success


def find_profile_by_name(api: GoLoginAPI, name: str) -> Optional[Dict[str, Any]]:
    """
    Find a profile by name.
    
    Args:
        api (GoLoginAPI): GoLogin API instance
        name (str): Profile name to search for
        
    Returns:
        Optional[Dict[str, Any]]: Profile data if found, None otherwise
    """
    profiles = api.get_profiles()
    for profile in profiles:
        # Handle different profile formats
        if isinstance(profile, dict):
            profile_name = profile.get("name", "")
        elif isinstance(profile, str):
            profile_name = profile
        else:
            profile_name = str(profile)
        
        if profile_name.startswith(f"{name}_"):
            return profile
    return None


def main():
    """Main function to demonstrate GoLogin API integration."""
    
    # Check if config file exists
    if not os.path.exists('config.env'):
        print("Error: config.env file not found!")
        print("Please create config.env file with your GoLogin API configuration.")
        return
    
    # Initialize API with environment token
    try:
        api = GoLoginAPI()
    except ValueError as e:
        print(f"Error: {e}")
        print("Please set GOLOGIN_ACCESS_TOKEN in your config.env file")
        return
    
    # Test connection
    print("Testing GoLogin API connection...")
    profiles = api.get_profiles()
    if profiles is not None:
        print(f"Successfully connected! Found {len(profiles)} profiles")
    else:
        print("Failed to connect to GoLogin API")
        return
    
    # Get network and usernames
    available_networks = ['facebook', 'instagram', 'tiktok', 'twitter', 'youtube']
    
    print(f"\nAvailable networks: {', '.join(available_networks)}")
    network = input("Enter network: ").strip().lower()
    
    if network not in available_networks:
        print(f"Error: Unsupported network '{network}'")
        return
    
    usernames_input = input("Enter usernames (comma-separated): ").strip()
    if not usernames_input:
        print("Error: No usernames provided")
        return
    
    usernames = [u.strip() for u in usernames_input.split(',') if u.strip()]
    
    print(f"\nProcessing {len(usernames)} users for {network}...")
    
    # Get user data (cookies and proxy) from database
    results = get_user_data_for_usernames_env(network, usernames)
    
    if not results:
        print("No results from database")
        return
    
    # Process each user
    success_count = 0
    for username, result in results.items():
        print(f"\nProcessing {username}...")
        
        # Check if we have any data (cookies or proxy)
        if result['status'] in ['success', 'no_data']:
            # Check if profile already exists (check by username pattern)
            existing_profile = None
            profiles = api.get_profiles()
            for profile in profiles:
                # Handle different profile formats
                if isinstance(profile, dict):
                    profile_name = profile.get("name", "")
                elif isinstance(profile, str):
                    profile_name = profile
                else:
                    profile_name = str(profile)
                
                if profile_name.startswith(f"{username}_"):
                    existing_profile = profile
                    break
            
            if existing_profile:
                print(f"Profile for {username} already exists (ID: {existing_profile['id']})")
                choice = input("Update existing profile? (y/n): ").strip().lower()
                
                if choice == 'y':
                    if update_existing_profile_data(api, existing_profile['id'], result['cookies'], result['proxy']):
                        # Update the profile ID in database
                        if update_browser_gologin_id_env(network, username, existing_profile['id']):
                            print(f"Updated profile ID in database for {username}")
                        success_count += 1
                else:
                    print("Skipped updating existing profile")
            else:
                # Create new profile with cookies and proxy
                profile_id = create_profile_with_data(api, network, username, result['cookies'], result['proxy'])
                if profile_id:
                    success_count += 1
        else:
            print(f"No data found for {username} (status: {result['status']})")
    
    print(f"\nSummary: Successfully processed {success_count}/{len(usernames)} users")


if __name__ == "__main__":
    main() 