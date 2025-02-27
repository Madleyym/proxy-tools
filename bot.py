import os
import sys
import time
import datetime
import requests
import concurrent.futures
from urllib.parse import urlparse

TEST_URL = "https://httpbin.org/ip"
TEST_TIMEOUT = 10
MAX_WORKERS = 10


def get_current_timestamp():
    return datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%d %H:%M:%S")


def log_message(message, log_file=None):
    timestamp = get_current_timestamp()
    formatted_message = f"[{timestamp}] {message}"
    print(formatted_message)
    if log_file:
        with open(log_file, "a") as f:
            f.write(formatted_message + "\n")


def parse_proxy(proxy_string):
    parts = proxy_string.strip().split(":")
    if len(parts) == 4:
        return {
            "hostname": parts[0],
            "port": parts[1],
            "username": parts[2],
            "password": parts[3],
        }
    elif len(parts) == 2:
        return {
            "hostname": parts[0],
            "port": parts[1],
            "username": None,
            "password": None,
        }
    else:
        return None


def convert_to_socks5(proxy_dict):
    if not proxy_dict:
        return None

    if proxy_dict["username"] and proxy_dict["password"]:
        return f"socks5://{proxy_dict['username']}:{proxy_dict['password']}@{proxy_dict['hostname']}:{proxy_dict['port']}"
    else:
        return f"socks5://{proxy_dict['hostname']}:{proxy_dict['port']}"


def convert_to_http(proxy_dict):
    if not proxy_dict:
        return None

    if proxy_dict["username"] and proxy_dict["password"]:
        return f"http://{proxy_dict['username']}:{proxy_dict['password']}@{proxy_dict['hostname']}:{proxy_dict['port']}"
    else:
        return f"http://{proxy_dict['hostname']}:{proxy_dict['port']}"


def convert_to_https(proxy_dict):
    if not proxy_dict:
        return None

    if proxy_dict["username"] and proxy_dict["password"]:
        return f"https://{proxy_dict['username']}:{proxy_dict['password']}@{proxy_dict['hostname']}:{proxy_dict['port']}"
    else:
        return f"https://{proxy_dict['hostname']}:{proxy_dict['port']}"


def convert_to_curl(proxy_dict, proxy_type="socks5"):
    if not proxy_dict:
        return None

    if proxy_dict["username"] and proxy_dict["password"]:
        return f"--proxy-{proxy_type} {proxy_dict['hostname']}:{proxy_dict['port']} -U {proxy_dict['username']}:{proxy_dict['password']}"
    else:
        return f"--proxy-{proxy_type} {proxy_dict['hostname']}:{proxy_dict['port']}"


def convert_proxy(proxy_string, format_type):
    proxy_dict = parse_proxy(proxy_string)
    if not proxy_dict:
        return None

    if format_type == "socks5":
        return convert_to_socks5(proxy_dict)
    elif format_type == "http":
        return convert_to_http(proxy_dict)
    elif format_type == "https":
        return convert_to_https(proxy_dict)
    elif format_type == "curl_socks5":
        return convert_to_curl(proxy_dict, "socks5")
    elif format_type == "curl_http":
        return convert_to_curl(proxy_dict, "http")
    elif format_type == "raw":
        if proxy_dict["username"] and proxy_dict["password"]:
            return f"{proxy_dict['hostname']}:{proxy_dict['port']}:{proxy_dict['username']}:{proxy_dict['password']}"
        else:
            return f"{proxy_dict['hostname']}:{proxy_dict['port']}"
    else:
        return None


def test_proxy(proxy_string, proxy_type="socks5"):
    proxy_dict = parse_proxy(proxy_string)
    if not proxy_dict:
        return {
            "proxy": proxy_string,
            "status": "error",
            "message": "Invalid proxy format",
        }

    if proxy_type == "socks5":
        formatted_proxy = convert_to_socks5(proxy_dict)
        proxy_config = {"http": formatted_proxy, "https": formatted_proxy}
    elif proxy_type == "http":
        formatted_proxy = convert_to_http(proxy_dict)
        proxy_config = {"http": formatted_proxy, "https": formatted_proxy}
    else:
        return {
            "proxy": proxy_string,
            "status": "error",
            "message": f"Proxy type {proxy_type} not supported",
        }

    try:
        start_time = time.time()
        response = requests.get(TEST_URL, proxies=proxy_config, timeout=TEST_TIMEOUT)
        elapsed_time = time.time() - start_time

        if response.status_code == 200:
            ip_data = response.json()
            return {
                "proxy": proxy_string,
                "status": "success",
                "ip": ip_data.get("origin"),
                "response_time": f"{elapsed_time:.2f}s",
                "formatted_proxy": formatted_proxy,
            }
        else:
            return {
                "proxy": proxy_string,
                "status": "fail",
                "message": f"Status code: {response.status_code}",
                "formatted_proxy": formatted_proxy,
            }
    except requests.exceptions.RequestException as e:
        return {
            "proxy": proxy_string,
            "status": "fail",
            "message": str(e),
            "formatted_proxy": formatted_proxy,
        }


def bulk_test_proxies(proxies, proxy_type="socks5"):
    results = {"success": [], "fail": [], "error": []}

    log_message(f"Starting test of {len(proxies)} proxies with type {proxy_type}...")

    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_proxy = {
            executor.submit(test_proxy, proxy, proxy_type): proxy for proxy in proxies
        }
        for future in concurrent.futures.as_completed(future_to_proxy):
            result = future.result()
            proxy = result["proxy"]

            if result["status"] == "success":
                results["success"].append(result)
                log_message(f"✓ {proxy} → {result['ip']} ({result['response_time']})")
            elif result["status"] == "fail":
                results["fail"].append(result)
                log_message(f"✗ {proxy} → {result['message']}")
            else:
                results["error"].append(result)
                log_message(f"! {proxy} → {result['message']}")

    return results


def read_proxies_from_file(filename):
    try:
        with open(filename, "r") as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        log_message(f"Error: File '{filename}' not found.")
        return []


def save_proxies_to_file(proxies, filename):
    try:
        with open(filename, "w") as f:
            for proxy in proxies:
                f.write(f"{proxy}\n")
        return True
    except Exception as e:
        log_message(f"Error when saving to '{filename}': {str(e)}")
        return False


def convert_bulk_proxies(proxies, format_type):
    results = []
    for proxy in proxies:
        converted = convert_proxy(proxy, format_type)
        if converted:
            results.append(converted)
    return results


def main():
    username = os.getenv("USER") or os.getenv("USERNAME") or "Unknown"
    timestamp = get_current_timestamp()

    print(f"\n{'=' * 60}")
    print(f"PROXY CONVERTER & TESTER")
    print(f"Current Date and Time (UTC): {timestamp}")
    print(f"Current User's Login: {username}")
    print(f"{'=' * 60}\n")

    input_file = "proxies.txt"
    proxies = read_proxies_from_file(input_file)

    if not proxies:
        print(
            "No proxies could be read. Make sure 'proxies.txt' file exists and is not empty."
        )
        return

    print(f"Successfully read {len(proxies)} proxies from file {input_file}\n")

    print("Choose conversion format:")
    print("1. SOCKS5 (socks5://username:password@host:port)")
    print("2. HTTP (http://username:password@host:port)")
    print("3. HTTPS (https://username:password@host:port)")
    print("4. cURL SOCKS5 format")
    print("5. cURL HTTP format")
    print("6. Test proxies (SOCKS5)")
    print("7. Test proxies (HTTP)")

    choice = input("\nEnter choice (1-7): ").strip()

    format_map = {
        "1": "socks5",
        "2": "http",
        "3": "https",
        "4": "curl_socks5",
        "5": "curl_http",
    }

    if choice in format_map:
        format_type = format_map[choice]
        converted_proxies = convert_bulk_proxies(proxies, format_type)
        output_file = "logs"

        if save_proxies_to_file(converted_proxies, output_file):
            print(
                f"\nSuccessfully converted {len(converted_proxies)} proxies to {format_type} format."
            )
            print(f"Conversion results saved to file '{output_file}'")

    elif choice in ["6", "7"]:
        proxy_type = "socks5" if choice == "6" else "http"
        results = bulk_test_proxies(proxies, proxy_type)

        if results["success"]:
            success_proxies = [r["formatted_proxy"] for r in results["success"]]
            save_proxies_to_file(success_proxies, "logs")
            print(
                f"\nSuccessfully saved {len(success_proxies)} working proxies to file 'logs'"
            )

        print(f"\nTest summary:")
        print(f"✓ Success: {len(results['success'])} proxies")
        print(f"✗ Failed: {len(results['fail'])} proxies")
        print(f"! Format errors: {len(results['error'])} proxies")

    else:
        print("Invalid choice.")


if __name__ == "__main__":
    main()
