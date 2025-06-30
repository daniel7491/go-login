#!/usr/bin/env python3
"""
Multi-Network Cookie Getter

This script retrieves cookies from different social network tables based on network type
and converts them to browser extension format.
"""

import json
import os
import time
import pg8000
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables from config.env file
load_dotenv('config.env')


def cookie_to_browser_format(cookie_string: str, domain: str = None, expiration_days: int = 30):
    """
    Convert a cookie string to browser extension format.
    
    Args:
        cookie_string (str): Cookie string like "key=value;key2=value2;"
        domain (str): Domain for the cookies (auto-detected if None)
        expiration_days (int): Days until expiration (default: 30)
        
    Returns:
        List of cookie objects in browser extension format
    """
    cookies = []
    
    # Check if cookie string is empty or null
    if not cookie_string or cookie_string.strip() == '':
        return cookies
    
    # Calculate expiration date (current time + expiration_days in seconds)
    expiration_date = int(time.time()) + (expiration_days * 24 * 60 * 60)
    
    # Split by semicolon and process each pair
    for pair in cookie_string.split(';'):
        pair = pair.strip()
        if pair and '=' in pair:
            key, value = pair.split('=', 1)  # Split on first '=' only
            name = key.strip()
            cookie_value = value.strip()
            
            # Create cookie object in browser extension format
            cookie_obj = {
                "name": name,
                "value": cookie_value,
                "domain": domain or ".instagram.com",  # Default fallback
                "path": "/",
                "secure": True,
                "httpOnly": False,
                "sameSite": "no_restriction",
                "session": False,
                "hostOnly": False,
                "expirationDate": expiration_date
            }
            
            # Set specific flags based on cookie name
            if name in ["rur", "ig_did", "sessionid"]:
                cookie_obj["httpOnly"] = True
                cookie_obj["session"] = True
                # Remove expirationDate for session cookies
                cookie_obj.pop("expirationDate", None)
            
            cookies.append(cookie_obj)
    
    return cookies


def get_network_domain(network: str) -> str:
    """
    Get the appropriate domain for a social network.
    
    Args:
        network (str): Network name (facebook, instagram, tiktok, twitter, youtube)
        
    Returns:
        str: Domain for the network
    """
    domains = {
        'facebook': '.facebook.com',
        'instagram': '.instagram.com',
        'tiktok': '.tiktok.com',
        'twitter': '.twitter.com',
        'youtube': '.youtube.com'
    }
    return domains.get(network.lower(), '.instagram.com')


def get_table_name(network: str) -> str:
    """
    Get the table name for a social network.
    
    Args:
        network (str): Network name (facebook, instagram, tiktok, twitter, youtube)
        
    Returns:
        str: Table name for the network
    """
    table_mapping = {
        'facebook': 'cm_social_account_facebook_api',
        'instagram': 'cm_social_account_instagram_api',
        'tiktok': 'cm_social_account_tiktok_api',
        'twitter': 'cm_social_account_twitter_api',
        'youtube': 'cm_social_account_youtube_api'
    }
    return table_mapping.get(network.lower())


def get_db_config_from_env():
    """
    Get database configuration from environment variables.
    
    Returns:
        dict: Database configuration dictionary
    """
    return {
        'host': os.getenv('DB_HOST', 'localhost'),
        'user': os.getenv('DB_USER', 'postgres'),
        'password': os.getenv('DB_PASSWORD', ''),
        'database': os.getenv('DB_NAME', 'cookies_db'),
        'port': int(os.getenv('DB_PORT', 5432))
    }


def get_user_data_for_usernames(network: str, usernames: List[str], **db_config) -> Dict[str, Any]:
    """
    Get cookies and proxy data for multiple usernames from a specific network table.
    
    Args:
        network (str): Network name (facebook, instagram, tiktok, twitter, youtube)
        usernames (List[str]): List of usernames to get data for
        **db_config: Database configuration
        
    Returns:
        Dict[str, Any]: Dictionary with results for each username
    """
    table_name = get_table_name(network)
    if not table_name:
        raise ValueError(f"Unsupported network: {network}")
    
    domain = get_network_domain(network)
    results = {}
    
    # Connect to PostgreSQL database
    try:
        conn = pg8000.connect(**db_config)
    except Exception as e:
        print(f"Error connecting to database: {e}")
        for username in usernames:
            results[username] = {
                "status": "error",
                "error": str(e),
                "cookies": None,
                "proxy": None,
                "count": 0
            }
        return results
    
    try:
        cursor = conn.cursor()
        
        for username in usernames:
            # Query to get cookies and proxy data for the username from the specific table
            query = f"""
                SELECT cookies, proxy_host, proxy_port, proxy_username, proxy_password 
                FROM {table_name} 
                WHERE login = %s
            """
            
            cursor.execute(query, (username,))
            result = cursor.fetchone()
            
            if result:
                cookie_string = result[0]
                proxy_host = result[1]
                proxy_port = result[2]
                proxy_username = result[3]
                proxy_password = result[4]
                
                # Convert to browser extension format (handles empty cookies)
                cookies = cookie_to_browser_format(cookie_string, domain)
                
                # Create proxy configuration
                proxy_config = None
                if proxy_host and proxy_port:
                    proxy_config = {
                        "mode": "http",
                        "host": proxy_host,
                        "port": int(proxy_port) if proxy_port else 8080,
                        "username": proxy_username or "",
                        "password": proxy_password or ""
                    }
                
                # Determine status based on available data
                if cookies or proxy_config:
                    status = "success"
                else:
                    status = "no_data"
                
                results[username] = {
                    "status": status,
                    "cookies": cookies,
                    "proxy": proxy_config,
                    "count": len(cookies)
                }
            else:
                results[username] = {
                    "status": "not_found",
                    "cookies": None,
                    "proxy": None,
                    "count": 0
                }
                
    except Exception as e:
        print(f"Database error: {e}")
        for username in usernames:
            results[username] = {
                "status": "error",
                "error": str(e),
                "cookies": None,
                "proxy": None,
                "count": 0
            }
    finally:
        cursor.close()
        conn.close()
    
    return results


def get_user_data_for_usernames_env(network: str, usernames: List[str]) -> Dict[str, Any]:
    """
    Get user data (cookies and proxy) for multiple usernames using environment configuration.
    
    Args:
        network (str): Network name
        usernames (List[str]): List of usernames
        
    Returns:
        Dict[str, Any]: Results for each username
    """
    try:
        db_config = get_db_config_from_env()
        return get_user_data_for_usernames(network, usernames, **db_config)
    except Exception as e:
        print(f"Configuration error: {e}")
        return {}


def main():
    """Main function."""
    
    # Check if config file exists
    if not os.path.exists('config.env'):
        print("Error: config.env file not found!")
        print("Please create config.env file with your PostgreSQL configuration.")
        return
    
    # Example usage
    network = "instagram"
    usernames = ["user1", "user2", "user3"]
    
    print(f"Getting data for {len(usernames)} users from {network}...")
    
    try:
        results = get_user_data_for_usernames_env(network, usernames)
        
        if results:
            print(f"\nResults for {network}:")
            for username, result in results.items():
                print(f"\nUsername: {username}")
                print(f"Status: {result['status']}")
                
                if result['status'] == 'success':
                    print(f"Cookies found: {result['count']}")
                    if result['cookies']:
                        print("Cookies:")
                        print(json.dumps(result['cookies'], indent=2))
                    if result['proxy']:
                        print("Proxy:")
                        print(json.dumps(result['proxy'], indent=2))
                elif result['status'] == 'no_data':
                    print("No cookies or proxy data found")
                elif result['status'] == 'not_found':
                    print("User not found in database")
                elif result['status'] == 'error':
                    print(f"Error: {result.get('error', 'Unknown error')}")
        else:
            print("No results returned")
            
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main() 