# GoLogin Browser Profile Manager

A Python system to manage GoLogin browser profiles using cookies and proxy data stored in a PostgreSQL database. This system automatically creates and updates browser profiles with authentication cookies and proxy settings for various social networks.

## Features

- 🔐 **Automatic Profile Creation**: Creates GoLogin browser profiles with proper authentication
- 🍪 **Cookie Management**: Converts database-stored cookies to GoLogin format
- 🌐 **Proxy Support**: Configures proxy settings for each profile
- 📊 **Multi-Network Support**: Instagram, Facebook, Twitter, TikTok, YouTube
- 💾 **Database Integration**: PostgreSQL database for storing cookies and proxy data
- 🔄 **Batch Processing**: Handle multiple accounts simultaneously
- 🎯 **Smart Updates**: Updates existing profiles or creates new ones

## Prerequisites

- Python 3.7 or higher
- PostgreSQL database
- GoLogin account with API access
- Windows 10/11 (tested on Windows)

## Installation

### 1. Clone or Download the Project

```bash
git clone <repository-url>
cd gologin-profile-manager
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv gologin_env

# Activate virtual environment
# On Windows:
gologin_env\Scripts\activate

# On macOS/Linux:
source gologin_env/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

**Or install manually:**
```bash
pip install pg8000 requests python-dotenv
```

### 4. Create Configuration File

Create a `config.env` file in the project root:

```env
# Database Configuration
DB_HOST=localhost
DB_USER=postgres
DB_PASSWORD=your_password
DB_NAME=cookies_db
DB_PORT=5432

# GoLogin API Configuration
GOLOGIN_ACCESS_TOKEN=your_gologin_api_token
```

### 5. Database Setup

Ensure your PostgreSQL database has tables with the following structure:

```sql
-- Example for Instagram table
CREATE TABLE cm_social_account_instagram_api (
    id SERIAL PRIMARY KEY,
    login VARCHAR(255) NOT NULL,
    cookies TEXT,
    proxy_host VARCHAR(255),
    proxy_port INTEGER,
    proxy_username VARCHAR(255),
    proxy_password VARCHAR(255),
    browser_gologin VARCHAR(255)
);

-- Similar tables for other networks:
-- cm_social_account_facebook_api
-- cm_social_account_twitter_api
-- cm_social_account_tiktok_api
-- cm_social_account_youtube_api
```

## Usage

### Quick Start

1. **Activate virtual environment:**
   ```bash
   gologin_env\Scripts\activate
   ```

2. **Run the main script:**
   ```bash
   python gologin_api_manager.py
   ```

3. **Follow the prompts:**
   - Enter network (instagram, facebook, twitter, tiktok, youtube)
   - Enter usernames (comma-separated)

### Available Scripts

#### 1. Main GoLogin Integration (`gologin_api_manager.py`)
**Purpose**: Create/update GoLogin profiles with cookies and proxy
```bash
python gologin_api_manager.py
```

**Features:**
- Creates new profiles or updates existing ones
- Sets cookies and proxy from database
- Saves profile IDs to database
- Interactive prompts for each account

#### 2. Single Profile Creator (`create_gologin_profile.py`)
**Purpose**: Create profile for a single user
```bash
python create_gologin_profile.py
```

#### 3. Cookie Data Viewer (`multi_network_cookie_getter_cli.py`)
**Purpose**: View cookies and proxy data (doesn't create profiles)
```bash
python multi_network_cookie_getter_cli.py instagram user1,user2,user3
```

### Command Line Examples

#### Batch Processing Multiple Accounts
```bash
# Create/update profiles for multiple Instagram accounts
python gologin_api_manager.py
# Enter: instagram
# Enter: user1,user2,user3,user4

# View cookie data for multiple users
python multi_network_cookie_getter_cli.py instagram user1,user2,user3
```

#### Single Account Operations
```bash
# Create profile for single user
python create_gologin_profile.py
# Enter: instagram
# Enter: username
```

## Cookie Format

The system handles cookies stored in your database as strings and converts them to GoLogin format with proper flags for each network.

### Facebook Cookies
The system comprehensively handles all Facebook cookie types:

**Core Authentication Cookies (httpOnly, secure):**
- `c_user` - User ID
- `xs` - Session token  
- `fr` - Friend request token
- `datr` - Data retention
- `sb` - Secure browsing

**UI/Display Cookies (not httpOnly, secure):**
- `wd` - Window dimensions
- `dbln` - Double login
- `ps_l` - Page speed
- `ps_n` - Page speed
- `x-referer` - Referer information

**Example Facebook Cookie String:**
```
wd=1280x470; sb=1cUNZ4_TRcMn3bE0tzuo3Rpb; c_user=100044304069206; fr=0ytDKh4stPbIMO1JK.AWWoVnzQDW9pf4ko0emVGbYxpPI.BnDGRP..AAA.0.0.BnDcXa.AWW63gW_pvg; datr=T2QMZ3MO8moV0mMnue-QFDlN; xs=22%3ATADd9p-hT4jwnA%3A2%3A1728955866%3A-1%3A6980
```

### Instagram Cookies
**Session Cookies (httpOnly, session):**
- `rur` - Session cookie (no expiration)

**Authentication Cookies (httpOnly, secure):**
- `ig_did` - Device ID
- `sessionid` - Session ID
- `mid` - Machine ID
- `datr` - Data retention
- `sb` - Secure browsing

**Regular Cookies (not httpOnly, secure):**
- `csrftoken` - CSRF token
- `ds_user_id` - User ID
- `ds_user` - Username
- `username` - Username

**Example Instagram Cookie String:**
```
csrftoken=value;rur=value;ds_user_id=value;ig_did=value;sessionid=value;
```

### GoLogin Format
All cookies are converted to GoLogin format:
```json
[
  {
    "name": "c_user",
    "value": "100044304069206",
    "domain": ".facebook.com",
    "path": "/",
    "secure": true,
    "httpOnly": true,
    "sameSite": "no_restriction",
    "session": false,
    "hostOnly": false,
    "expirationDate": 1234567890
  }
]
```

## Supported Networks

| Network | Table Name | Domain |
|---------|------------|---------|
| Instagram | `cm_social_account_instagram_api` | `.instagram.com` |
| Facebook | `cm_social_account_facebook_api` | `.facebook.com` |
| Twitter | `cm_social_account_twitter_api` | `.twitter.com` |
| TikTok | `cm_social_account_tiktok_api` | `.tiktok.com` |
| YouTube | `cm_social_account_youtube_api` | `.youtube.com` |

## File Structure

```
gologin-profile-manager/
├── README.md
├── requirements.txt
├── config.env
├── gologin_api_manager.py          # Main integration script
├── create_gologin_profile.py       # Single profile creator
├── multi_network_cookie_getter_cli.py  # Multi-user cookie getter
└── gologin_env/                    # Virtual environment
```

## Troubleshooting

### Common Issues

1. **"config.env file not found"**
   - Ensure `config.env` exists in the project root
   - Check file permissions

2. **Database connection errors**
   - Verify PostgreSQL is running
   - Check database credentials in `config.env`
   - Ensure database and tables exist

3. **GoLogin API errors**
   - Verify API token in `config.env`
   - Check GoLogin account status
   - Ensure API token has proper permissions

4. **Virtual environment not activated**
   ```bash
   # Windows
   gologin_env\Scripts\activate
   
   # macOS/Linux
   source gologin_env/bin/activate
   ```

5. **Missing dependencies**
   ```bash
   pip install -r requirements.txt
   ```

### Cookie Issues

- **Auto-login not working**: Ensure cookies are in correct format and not expired
- **Missing cookies**: Check database for cookie data
- **Wrong domain**: Verify network selection matches cookie domain

## Configuration Details

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DB_HOST` | PostgreSQL host | `localhost` |
| `DB_USER` | Database username | `postgres` |
| `DB_PASSWORD` | Database password | (required) |
| `DB_NAME` | Database name | `cookies_db` |
| `DB_PORT` | Database port | `5432` |
| `GOLOGIN_ACCESS_TOKEN` | GoLogin API token | (required) |

### Database Schema

Each network table should have these columns:
- `login`: Username/account identifier
- `cookies`: Cookie string or JSON
- `proxy_host`: Proxy server hostname
- `proxy_port`: Proxy server port
- `proxy_username`: Proxy authentication username
- `proxy_password`: Proxy authentication password
- `browser_gologin`: GoLogin profile ID (auto-filled)

## API Endpoints

The system uses these GoLogin API endpoints:
- `GET /browser/v2` - List profiles
- `POST /browser` - Create profile
- `PUT /browser/{id}` - Update profile
- `POST /browser/{id}/cookies` - Update cookies
- `DELETE /browser/{id}` - Delete profile

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the configuration
3. Test with a single account first
4. Create an issue with detailed error information

## Changelog

### Version 1.0.0
- Initial release
- Multi-network support
- GoLogin API integration
- PostgreSQL database support
- Cookie conversion and management
- Proxy configuration
- Batch processing capabilities
# go-login
