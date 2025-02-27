# Proxy Converter and Tester

A Python utility for converting proxy strings between different formats and testing proxy connectivity.

## Overview

This tool allows you to:
- Convert proxies between different formats (SOCKS5, HTTP, HTTPS, cURL)
- Test proxies to verify they're working
- Process multiple proxies in bulk
- Save working proxies to a file

## Requirements

- Python 3.6+
- Required packages:
  - requests
  - urllib3
  - PySocks (required for SOCKS proxy testing)

Install all dependencies with:
```
pip install requests urllib3 PySocks
```

> **Note**: Without PySocks, you'll get "Missing dependencies for SOCKS support" error when testing SOCKS proxies.

## Proxy Formats

Input format can be:
- `host:port` (without authentication)
- `host:port:username:password` (with authentication)

Output formats include:
- SOCKS5: `socks5://username:password@host:port`
- HTTP: `http://username:password@host:port`
- HTTPS: `https://username:password@host:port`
- cURL SOCKS5: `--proxy-socks5 host:port -U username:password`
- cURL HTTP: `--proxy-http host:port -U username:password`

## Usage

1. Create a file named `proxies.txt` in the same directory as the script
2. Add your proxies to the file, one per line
3. Run the script:
   ```
   python bot.py
   ```
   or
   ```
   python3 bot.py
   ```
4. Follow the menu prompts to select your desired operation

### Testing Proxies

The utility can test proxies using either SOCKS5 or HTTP protocol. It performs a request to https://httpbin.org/ip through each proxy to verify connectivity.

For SOCKS proxy testing:
- Make sure you have the PySocks package installed
- SOCKS4, SOCKS5, and SOCKS5h protocols are supported

Test results include:
- Success/failure status
- Response time
- IP address (for successful tests)
- Error messages (for failed tests)

## Troubleshooting

Common issues:

1. "Missing dependencies for SOCKS support" error
   - Solution: Run `pip install PySocks`

2. No proxies found
   - Make sure `proxies.txt` exists in the same directory as the script
   - Ensure the file contains at least one proxy

3. Connection timeouts
   - Check if the proxy is still active
   - Increase the `TEST_TIMEOUT` value in the script for slow proxies

4. Authentication failures
   - Verify username and password are correct
   - Ensure the proxy supports authentication

## Output

Results are saved to a file named `logs`:
- For conversion operations: the file contains converted proxy strings
- For test operations: the file contains only the working proxies

## Example

```
==============================================================
PROXY CONVERTER & TESTER
Current Date and Time (UTC): 0000-00-00 00:00:00
Current User's Login: username
==============================================================

Successfully read 10 proxies from file proxies.txt

Choose conversion format:
1. SOCKS5 (socks5://username:password@host:port)
2. HTTP (http://username:password@host:port)
3. HTTPS (https://username:password@host:port)
4. cURL SOCKS5 format
5. cURL HTTP format
6. Test proxies (SOCKS5)
7. Test proxies (HTTP)

Enter choice (1-7): 6
```

## Features

- Multi-threaded testing for faster processing
- Detailed logging with timestamps
- Simple command-line interface
- Format conversion for various use cases
- Efficient proxy validation
- Support for both HTTP and SOCKS proxies
- Handles authenticated and non-authenticated proxies