#!/usr/bin/env python3
"""
Database Cookie Getter Class

This class provides methods to retrieve cookies from a PostgreSQL database
and convert them to browser extension format.
"""

import json
import os
import time
import pg8000
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables from config.env file
load_dotenv('config.env')


class DatabaseCookieGetter:
    def __init__(self, **db_config):
        """
        Initialize the DatabaseCookieGetter.
        
        Args:
            **db_config: Database configuration parameters
        """
        self.db_config = db_config
        self.connection = None
    
    def connect(self):
        """
        Connect to the PostgreSQL database.
        
        Raises:
            Exception: If connection fails
        """
        try:
            self.connection = pg8000.connect(**self.db_config)
        except Exception as e:
            raise Exception(f"Failed to connect to database: {e}")
    
    def disconnect(self):
        """Close the database connection."""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def cookie_to_browser_format(self, cookie_string: str, domain: str = None, expiration_days: int = 30):
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
    
    def get_cookies_for_user(self, table_name: str, username: str) -> List[Dict[str, Any]]:
        """
        Get cookies for a specific user from the database.
        
        Args:
            table_name (str): Name of the table containing cookies
            username (str): Username to get cookies for
            
        Returns:
            List[Dict[str, Any]]: List of cookies in browser extension format
        """
        if not self.connection:
            self.connect()
        
        try:
            cursor = self.connection.cursor()
            
            # Query to get cookies for the username
            query = f"SELECT cookies FROM {table_name} WHERE login = %s"
            cursor.execute(query, (username,))
            result = cursor.fetchone()
            
            if result:
                cookie_string = result[0]
                return self.cookie_to_browser_format(cookie_string)
            else:
                print(f"No cookies found for username: {username}")
                return []
                
        except Exception as e:
            print(f"Error getting cookies: {e}")
            return []
        finally:
            cursor.close()
    
    def get_cookies_for_multiple_users(self, table_name: str, usernames: List[str]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get cookies for multiple users from the database.
        
        Args:
            table_name (str): Name of the table containing cookies
            usernames (List[str]): List of usernames to get cookies for
            
        Returns:
            Dict[str, List[Dict[str, Any]]]: Dictionary mapping usernames to their cookies
        """
        if not self.connection:
            self.connect()
        
        results = {}
        
        try:
            cursor = self.connection.cursor()
            
            for username in usernames:
                # Query to get cookies for the username
                query = f"SELECT cookies FROM {table_name} WHERE login = %s"
                cursor.execute(query, (username,))
                result = cursor.fetchone()
                
                if result:
                    cookie_string = result[0]
                    results[username] = self.cookie_to_browser_format(cookie_string)
                else:
                    print(f"No cookies found for username: {username}")
                    results[username] = []
                    
        except Exception as e:
            print(f"Error getting cookies: {e}")
            for username in usernames:
                results[username] = []
        finally:
            cursor.close()
        
        return results
    
    def save_cookies_to_file(self, cookies: List[Dict[str, Any]], filename: str):
        """
        Save cookies to a JSON file.
        
        Args:
            cookies (List[Dict[str, Any]]): List of cookies to save
            filename (str): Name of the output file
        """
        try:
            with open(filename, 'w') as f:
                json.dump(cookies, f, indent=2)
            print(f"Cookies saved to {filename}")
        except Exception as e:
            print(f"Error saving cookies to file: {e}")


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


def main():
    """Example usage of the DatabaseCookieGetter class."""
    
    # Check if config file exists
    if not os.path.exists('config.env'):
        print("Error: config.env file not found!")
        print("Please create config.env file with your PostgreSQL configuration.")
        return
    
    # Get database configuration
    db_config = get_db_config_from_env()
    
    # Create DatabaseCookieGetter instance
    cookie_getter = DatabaseCookieGetter(**db_config)
    
    try:
        # Example: Get cookies for a single user
        table_name = input("Enter table name: ").strip()
        username = input("Enter username: ").strip()
        
        if not table_name or not username:
            print("Error: Both table name and username are required")
            return
        
        cookies = cookie_getter.get_cookies_for_user(table_name, username)
        
        if cookies:
            print(f"\nFound {len(cookies)} cookies for {username}:")
            print(json.dumps(cookies, indent=2))
            
            # Save to file
            filename = f"cookies_{username}.json"
            cookie_getter.save_cookies_to_file(cookies, filename)
        else:
            print(f"No cookies found for {username}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        cookie_getter.disconnect()


if __name__ == "__main__":
    main() 