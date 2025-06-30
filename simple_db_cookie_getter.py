#!/usr/bin/env python3
"""
Simple Database Cookie Getter

This script retrieves cookies from a PostgreSQL database and converts them to browser extension format.
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


def get_cookies_from_db(table_name: str, username: str, **db_config) -> List[Dict[str, Any]]:
    """
    Get cookies from PostgreSQL database for a specific user.
    
    Args:
        table_name (str): Name of the table containing cookies
        username (str): Username to get cookies for
        **db_config: Database configuration
        
    Returns:
        List[Dict[str, Any]]: List of cookies in browser extension format
    """
    # Connect to PostgreSQL database
    try:
        conn = pg8000.connect(**db_config)
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return []
    
    try:
        cursor = conn.cursor()
        
        # Query to get cookies for the username
        query = f"SELECT cookies FROM {table_name} WHERE login = %s"
        cursor.execute(query, (username,))
        result = cursor.fetchone()
        
        if result:
            cookie_string = result[0]
            return cookie_to_browser_format(cookie_string)
        else:
            print(f"No cookies found for username: {username}")
            return []
            
    except Exception as e:
        print(f"Error getting cookies: {e}")
        return []
    finally:
        cursor.close()
        conn.close()


def get_cookies_from_db_env(table_name: str, username: str) -> List[Dict[str, Any]]:
    """
    Get cookies from database using environment configuration.
    
    Args:
        table_name (str): Name of the table containing cookies
        username (str): Username to get cookies for
        
    Returns:
        List[Dict[str, Any]]: List of cookies in browser extension format
    """
    try:
        db_config = get_db_config_from_env()
        return get_cookies_from_db(table_name, username, **db_config)
    except Exception as e:
        print(f"Configuration error: {e}")
        return []


def main():
    """Main function."""
    
    # Check if config file exists
    if not os.path.exists('config.env'):
        print("Error: config.env file not found!")
        print("Please create config.env file with your PostgreSQL configuration.")
        return
    
    # Get table name and username from user input
    table_name = input("Enter table name: ").strip()
    username = input("Enter username: ").strip()
    
    if not table_name or not username:
        print("Error: Both table name and username are required")
        return
    
    # Get cookies from database
    cookies = get_cookies_from_db_env(table_name, username)
    
    if cookies:
        print(f"\nFound {len(cookies)} cookies for {username}:")
        print(json.dumps(cookies, indent=2))
        
        # Save to file
        filename = f"cookies_{username}.json"
        with open(filename, 'w') as f:
            json.dump(cookies, f, indent=2)
        print(f"\nCookies saved to {filename}")
    else:
        print(f"No cookies found for {username}")


if __name__ == "__main__":
    main() 