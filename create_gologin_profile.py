#!/usr/bin/env python3
"""
Create GoLogin Profile

Simple script to create a GoLogin profile for a single user with cookies and proxy from database.
"""

import json
import os
from dotenv import load_dotenv
from multi_network_cookie_getter_cli import get_user_data_for_usernames_env, update_browser_gologin_id_env
from gologin_api_manager import GoLoginAPI, create_profile_with_data, find_profile_by_name, update_existing_profile_data

# Load environment variables
load_dotenv('config.env')


def create_profile_for_user(network: str, username: str, force_update: bool = False):
    """
    Create or update a GoLogin profile for a single user.
    
    Args:
        network (str): Social network name
        username (str): Username
        force_update (bool): Force update existing profile
    """
    
    # Check if config file exists
    if not os.path.exists('config.env'):
        print("Error: config.env file not found!")
        print("Please create config.env file with your GoLogin API configuration.")
        return False
    
    # Initialize GoLogin API with environment token
    try:
        api = GoLoginAPI()
    except ValueError as e:
        print(f"Error: {e}")
        print("Please set GOLOGIN_ACCESS_TOKEN in your config.env file")
        return False
    
    # Test connection
    print("Testing GoLogin API connection...")
    profiles = api.get_profiles()
    if profiles is None:
        print("Failed to connect to GoLogin API")
        return False
    
    print(f"Successfully connected! Found {len(profiles)} profiles")
    
    # Get user data from database
    print(f"\nFetching data for {username} from {network}...")
    results = get_user_data_for_usernames_env(network, [username])
    
    if not results or username not in results:
        print(f"No data found for {username} in {network}")
        return False
    
    user_data = results[username]
    
    # Check if we have any data (cookies or proxy)
    if user_data['status'] not in ['success', 'no_data']:
        print(f"Error getting data for {username}: {user_data.get('error', 'Unknown error')}")
        return False
    
    # Check if profile already exists (check by username pattern)
    existing_profile = None
    profiles = api.get_profiles()
    profiles_list = profiles.get("profiles", []) if isinstance(profiles, dict) else profiles
    
    for profile in profiles_list:
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
    
    if existing_profile and not force_update:
        print(f"Profile for {username} already exists (ID: {existing_profile['id']})")
        choice = input("Update existing profile? (y/n): ").strip().lower()
        
        if choice == 'y':
            success = update_existing_profile_data(api, existing_profile['id'], user_data['cookies'], user_data['proxy'])
            if success:
                # Update the profile ID in database
                if update_browser_gologin_id_env(network, username, existing_profile['id']):
                    print(f"Updated profile ID in database for {username}")
                return True
            return False
        else:
            print("Skipped updating existing profile")
            return False
    
    # Create new profile
    print(f"\nCreating profile for {username}...")
    profile_id = create_profile_with_data(api, network, username, user_data['cookies'], user_data['proxy'])
    
    if profile_id:
        print(f"\n✅ Successfully created profile: {username}_{profile_id}")
        print(f"   Profile ID: {profile_id}")
        
        # Show cookie status
        if user_data['cookies']:
            print(f"   Cookies: {user_data['count']} cookies imported")
        else:
            print(f"   Cookies: None (cookies column was empty)")
        
        # Show proxy status
        if user_data['proxy']:
            proxy = user_data['proxy']
            print(f"   Proxy: {proxy.get('host', 'N/A')}:{proxy.get('port', 'N/A')}")
        else:
            print("   Proxy: Not configured")
        
        # Profile ID is already saved to database in create_profile_with_data function
        print(f"   Database: Profile ID saved to browser_gologin column")
        
        return True
    else:
        print(f"\n❌ Failed to create profile for {username}")
        return False


def main():
    """Main function."""
    
    print("GoLogin Profile Creator")
    print("=" * 30)
    print("Creates profiles with cookies and/or proxy settings")
    print("Works even if cookies column is empty")
    print("Uses environment configuration for API token")
    print()
    
    # Get network
    available_networks = ['facebook', 'instagram', 'tiktok', 'twitter', 'youtube']
    print(f"Available networks: {', '.join(available_networks)}")
    
    network = input("Enter network: ").strip().lower()
    if network not in available_networks:
        print(f"Error: Unsupported network '{network}'")
        return
    
    # Get username
    username = input("Enter username: ").strip()
    if not username:
        print("Error: Username is required")
        return
    
    # Ask about force update
    force_update = input("Force update if profile exists? (y/n): ").strip().lower() == 'y'
    
    # Create profile
    success = create_profile_for_user(network, username, force_update)
    
    if success:
        print(f"\n🎉 Profile creation completed successfully!")
        print(f"   The profile ID has been saved to the database.")
    else:
        print(f"\n💥 Profile creation failed!")


if __name__ == "__main__":
    main() 