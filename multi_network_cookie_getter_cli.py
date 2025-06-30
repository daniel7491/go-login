#!/usr/bin/env python3
"""
Multi-Network Cookie Getter (Command Line Version)

This script retrieves cookies and proxy data from different social network tables based on network type
and converts them to browser extension format.

Usage:
    python multi_network_cookie_getter_cli.py twitter user1,user2,user3
    python multi_network_cookie_getter_cli.py instagram username1,username2
    python multi_network_cookie_getter_cli.py facebook user1 user2 user3
"""

import json
import os
import sys
import time
import pg8000
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables from config.env file
load_dotenv('config.env')


def cookie_to_browser_format(cookie_string: str, domain: str = None, expiration_days: int = 30):
    """
    Convert a cookie string to browser extension format (GoLogin compatible).
    Handles Facebook and Instagram cookies flexibly.
    """
    cookies = []
    if not cookie_string or cookie_string.strip() == '':
        return cookies
    expiration_date = int(time.time()) + (expiration_days * 24 * 60 * 60)
    
    for pair in cookie_string.split(';'):
        pair = pair.strip()
        if pair and '=' in pair:
            key, value = pair.split('=', 1)
            name = key.strip()
            cookie_value = value.strip()
            
            cookie_obj = {
                "name": name,
                "value": cookie_value,
                "domain": domain or ".facebook.com",
                "path": "/",
                "secure": True,
                "httpOnly": False,
                "sameSite": "no_restriction",
                "session": False,
                "hostOnly": False,
                "expirationDate": expiration_date
            }
            
            # Facebook-specific cookie handling
            if domain and '.facebook.com' in domain:
                # Facebook cookies that are always httpOnly
                http_only_cookies = [
                    'c_user', 'xs', 'fr', 'datr', 'sb', 'wd', 'dbln', 'ps_l', 'ps_n',
                    'x-referer', 'presence', 'locale', 'lu', 'act', 'csm', 'spin',
                    'xs', 'fr', 'datr', 'sb', 'wd', 'dbln', 'ps_l', 'ps_n', 'x-referer'
                ]
                
                # Facebook cookies that are session cookies (no expiration)
                session_cookies = [
                    'presence', 'locale', 'lu', 'act', 'csm', 'spin'
                ]
                
                # Facebook cookies that are secure but not httpOnly
                secure_not_http_only = [
                    'wd', 'dbln', 'ps_l', 'ps_n', 'x-referer'
                ]
                
                if name in http_only_cookies:
                    cookie_obj["httpOnly"] = True
                
                if name in session_cookies:
                    cookie_obj["session"] = True
                    cookie_obj.pop("expirationDate", None)
                
                if name in secure_not_http_only:
                    cookie_obj["httpOnly"] = False
                    cookie_obj["secure"] = True
                
                # Special handling for specific Facebook cookies
                if name == "c_user":
                    # User ID cookie - always httpOnly, not session
                    cookie_obj["httpOnly"] = True
                    cookie_obj["session"] = False
                elif name == "xs":
                    # Session token - always httpOnly, not session
                    cookie_obj["httpOnly"] = True
                    cookie_obj["session"] = False
                elif name == "fr":
                    # Friend request token - always httpOnly, not session
                    cookie_obj["httpOnly"] = True
                    cookie_obj["session"] = False
                elif name == "datr":
                    # Data retention - always httpOnly, not session
                    cookie_obj["httpOnly"] = True
                    cookie_obj["session"] = False
                elif name == "sb":
                    # Secure browsing - always httpOnly, not session
                    cookie_obj["httpOnly"] = True
                    cookie_obj["session"] = False
                elif name == "wd":
                    # Window dimensions - not httpOnly, not session
                    cookie_obj["httpOnly"] = False
                    cookie_obj["session"] = False
                elif name == "dbln":
                    # Double login - not httpOnly, not session
                    cookie_obj["httpOnly"] = False
                    cookie_obj["session"] = False
                elif name == "ps_l":
                    # Page speed - not httpOnly, not session
                    cookie_obj["httpOnly"] = False
                    cookie_obj["session"] = False
                elif name == "ps_n":
                    # Page speed - not httpOnly, not session
                    cookie_obj["httpOnly"] = False
                    cookie_obj["session"] = False
                elif name == "x-referer":
                    # Referer - not httpOnly, not session
                    cookie_obj["httpOnly"] = False
                    cookie_obj["session"] = False
                else:
                    # For any other Facebook cookies, use sensible defaults
                    cookie_obj["httpOnly"] = True
                    cookie_obj["session"] = False
            
            # Instagram-specific logic (keeping existing logic)
            elif domain and '.instagram.com' in domain:
                if name == "rur":
                    # rur is always session cookie, no expiration
                    cookie_obj["httpOnly"] = True
                    cookie_obj["session"] = True
                    cookie_obj.pop("expirationDate", None)
                elif name in ["ig_did", "sessionid", "mid", "datr", "sb"]:
                    # These are httpOnly but not session cookies
                    cookie_obj["httpOnly"] = True
                    cookie_obj["session"] = False
                elif name in ["csrftoken", "ds_user_id", "ds_user", "username"]:
                    # These are regular cookies with expiration
                    cookie_obj["httpOnly"] = False
                    cookie_obj["session"] = False
                else:
                    # For any other Instagram cookies, use sensible defaults
                    # Most Instagram cookies are httpOnly but not session
                    cookie_obj["httpOnly"] = True
                    cookie_obj["session"] = False
            
            # Default handling for other domains
            else:
                # For any other domains, use sensible defaults
                cookie_obj["httpOnly"] = True
                cookie_obj["session"] = False
            
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
    return domains.get(network.lower(), '.facebook.com')


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


def update_browser_gologin_id(network: str, username: str, profile_id: str, **db_config) -> bool:
    """
    Update the browser_gologin column with the GoLogin profile ID.
    
    Args:
        network (str): Network name
        username (str): Username
        profile_id (str): GoLogin profile ID
        **db_config: Database configuration
        
    Returns:
        bool: True if successful, False otherwise
    """
    table_name = get_table_name(network)
    if not table_name:
        print(f"Error: Unsupported network: {network}")
        return False
    
    # Connect to PostgreSQL database
    try:
        conn = pg8000.connect(**db_config)
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return False
    
    try:
        cursor = conn.cursor()
        
        # Update the browser_gologin column
        query = f"UPDATE {table_name} SET browser_gologin = %s WHERE login = %s"
        cursor.execute(query, (profile_id, username))
        conn.commit()
        
        if cursor.rowcount > 0:
            print(f"Updated browser_gologin for {username} with profile ID: {profile_id}")
            return True
        else:
            print(f"No rows updated for {username}")
            return False
            
    except Exception as e:
        print(f"Error updating browser_gologin for {username}: {e}")
        return False
    finally:
        cursor.close()
        conn.close()


def update_browser_gologin_id_env(network: str, username: str, profile_id: str) -> bool:
    """
    Update the browser_gologin column using environment configuration.
    
    Args:
        network (str): Network name
        username (str): Username
        profile_id (str): GoLogin profile ID
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        db_config = get_db_config_from_env()
        return update_browser_gologin_id(network, username, profile_id, **db_config)
    except Exception as e:
        print(f"Configuration error: {e}")
        return False


def safe_load_cookies(cookie_data, domain=None):
    # If already a list of dicts, just return
    if isinstance(cookie_data, list) and all(isinstance(c, dict) and 'name' in c for c in cookie_data):
        return cookie_data
    # If string, try to parse as JSON
    if isinstance(cookie_data, str):
        try:
            cookies = json.loads(cookie_data)
            if isinstance(cookies, list) and all('name' in c for c in cookies):
                return cookies
        except Exception:
            pass
    # Fallback: treat as "key=value;..." string (legacy)
    return cookie_to_browser_format(cookie_data, domain)


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
                
                # Use safe loader for cookies
                cookies = safe_load_cookies(cookie_string, domain)
                
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


def print_usage():
    """Print usage instructions."""
    print("Multi-Network User Data Getter (CLI Version)")
    print("=" * 50)
    print()
    print("Usage:")
    print("  python multi_network_cookie_getter_cli.py <network> <usernames>")
    print()
    print("Examples:")
    print("  python multi_network_cookie_getter_cli.py twitter user1,user2,user3")
    print("  python multi_network_cookie_getter_cli.py instagram username1,username2")
    print("  python multi_network_cookie_getter_cli.py facebook user1 user2 user3")
    print()
    print("Available networks:")
    print("  facebook, instagram, tiktok, twitter, youtube")
    print()
    print("Username formats:")
    print("  - Comma-separated: user1,user2,user3")
    print("  - Space-separated: user1 user2 user3")
    print()
    print("Returns:")
    print("  - Cookies in browser extension format (if available)")
    print("  - Proxy configuration (host, port, username, password)")
    print("  - Works even if cookies are empty/null")
    print()
    print("Database: PostgreSQL only")


def main():
    """Main function with command-line argument parsing."""
    
    # Check if config file exists
    if not os.path.exists('config.env'):
        print("Error: config.env file not found!")
        print("Please create config.env file with your PostgreSQL configuration.")
        return
    
    # Check command line arguments
    if len(sys.argv) < 3:
        print_usage()
        return
    
    # Parse arguments
    network = sys.argv[1].lower()
    usernames_input = sys.argv[2:]
    
    # Available networks
    available_networks = ['facebook', 'instagram', 'tiktok', 'twitter', 'youtube']
    
    if network not in available_networks:
        print(f"Error: Unsupported network '{network}'")
        print(f"Available networks: {', '.join(available_networks)}")
        return
    
    # Parse usernames
    usernames = []
    for arg in usernames_input:
        # Handle comma-separated usernames
        if ',' in arg:
            usernames.extend([u.strip() for u in arg.split(',') if u.strip()])
        else:
            usernames.append(arg.strip())
    
    # Remove duplicates and filter empty strings
    usernames = list(set([u for u in usernames if u]))
    
    if not usernames:
        print("Error: No valid usernames provided")
        return
    
    print(f"Network: {network}")
    print(f"Usernames: {', '.join(usernames)}")
    print(f"Total users: {len(usernames)}")
    print()
    
    try:
        # Get user data using environment configuration
        results = get_user_data_for_usernames_env(network, usernames)
        
        if results:
            print(f"Results for {network}:")
            print("=" * 50)
            
            success_count = 0
            no_data_count = 0
            not_found_count = 0
            error_count = 0
            
            for username, result in results.items():
                print(f"\nUsername: {username}")
                print(f"Status: {result['status']}")
                
                if result['status'] == 'success':
                    success_count += 1
                    print(f"Cookies found: {result['count']}")
                    
                    # Display cookies
                    if result['cookies']:
                        print("Cookies:")
                        print(json.dumps(result['cookies'], indent=2))
                    else:
                        print("Cookies: None (empty or null)")
                    
                    # Display proxy info
                    if result['proxy']:
                        print("Proxy Configuration:")
                        print(json.dumps(result['proxy'], indent=2))
                    else:
                        print("Proxy: Not configured")
                        
                elif result['status'] == 'no_data':
                    no_data_count += 1
                    print("No cookies or proxy data found for this user")
                elif result['status'] == 'not_found':
                    not_found_count += 1
                    print("User not found in database")
                elif result['status'] == 'error':
                    error_count += 1
                    print(f"Error: {result.get('error', 'Unknown error')}")
                
                print("-" * 30)
            
            # Summary
            print(f"\nSummary:")
            print(f"  Success: {success_count}")
            print(f"  No data: {no_data_count}")
            print(f"  Not found: {not_found_count}")
            print(f"  Errors: {error_count}")
            print(f"  Total: {len(usernames)}")
        else:
            print("No results returned")
            
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main() 