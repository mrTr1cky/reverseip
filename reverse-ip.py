import requests
import re
import json
import os
import threading
from colorama import init, Fore, Style
import time
from queue import Queue

# Initialize colorama
init(autoreset=True)

# Banner
banner = r"""
██████  ███████ ██    ██ ██████  ██    ██ ███████ ██████       ██ ██████      ██ ██████      ██
██   ██ ██      ██    ██ ██   ██  ██  ██  ██      ██   ██     ███       ██    ███       ██    ███
██   ██ █████   ██    ██ ██████    ████   █████   ██████       ██  █████       ██  █████       ██
██   ██ ██      ██    ██ ██         ██    ██      ██          ███      ██     ███      ██     ███
██████  ███████  ██████  ██         ██    ███████ ██          ██  ██████      ██  ██████      ██

        Reverse IP v4 Scanner
        by MAD TIGER
        Telegram: @DevidLuice
"""
print(banner)

# User input
ip_file = input(f"{Fore.YELLOW}Enter IP file : ").strip()
thread_count = input(f"{Fore.YELLOW}Enter Threads: ").strip()
output_file = "domains.txt"

# Validate thread count
try:
    thread_count = int(thread_count)
    if thread_count < 1:
        raise ValueError
except ValueError:
    print(f"{Fore.RED}Invalid thread count. Must be a positive integer.")
    exit(1)

# Validate IP file
try:
    with open(ip_file, "r", encoding="utf-8") as f:
        ip_addresses = [line.strip() for line in f if line.strip()]
    if not ip_addresses:
        print(f"{Fore.RED}Error: {ip_file} is empty or contains no valid IPs.")
        exit(1)
except FileNotFoundError:
    print(f"{Fore.RED}Error: {ip_file} not found.")
    exit(1)

# Prepare environment
url_base = "https://reverseipdomain.com/ip/"
excluded_extensions = {
    '.js', '.css', '.png', '.jpg', '.svg', '.push', '.woff', 'ico',
    'github.com', 'zone-xsec.com', 'cloudflareinsights.com', 'favicon'
}
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5"
}

# Clear previous output
open(output_file, "w").close()

# Thread-safe domain set and lock
domain_lock = threading.Lock()
all_domains = set()
ip_queue = Queue()
skipped_count = 0
skipped_lock = threading.Lock()

# Worker function
def process_ip():
    global skipped_count
    while not ip_queue.empty():
        ip = ip_queue.get()
        url = f"{url_base}{ip}"
        response_file = f"response_{ip}.txt"

        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            with open(response_file, "w", encoding="utf-8") as f:
                f.write(response.text)

            domains = []

            # Try JSON
            try:
                data = response.json()
                domains = data.get("domainsSource", [])
            except json.JSONDecodeError:
                json_match = re.search(r'"domainsSource":\s*\[(.*?)\]', response.text, re.DOTALL)
                if json_match:
                    domains_str = f"[{json_match.group(1)}]"
                    try:
                        domains = json.loads(domains_str)
                    except json.JSONDecodeError:
                        domain_pattern = r'"([a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)"'
                        domains = re.findall(domain_pattern, json_match.group(1))
                else:
                    domain_pattern = r'[a-zA-Z0-9-]+\.[a-zA-Z]{2,}(?:\.[a-zA-Z]{2,})?'
                    domains = re.findall(domain_pattern, response.text)

            valid_domains = [
                d for d in domains
                if d and
                re.match(r'^[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', d) and
                not any(d.lower().endswith(ext) for ext in excluded_extensions)
            ]

            if len(valid_domains) >= 3:
                print(f"{Fore.CYAN}{ip} ====> [{len(valid_domains)}]")
                with domain_lock:
                    all_domains.update(valid_domains)
                    with open(output_file, "a", encoding="utf-8") as f:
                        for domain in sorted(valid_domains):
                            f.write(domain + "\n")
            else:
                print(f"{Fore.YELLOW}{ip}====>[DEAD]")
                with skipped_lock:
                    skipped_count += 1

            try:
                os.remove(response_file)
            except OSError:
                pass

        except requests.exceptions.HTTPError as e:
            print(f"{Fore.RED}HTTP Error for {ip}: {e}")
        except requests.exceptions.RequestException as e:
            print(f"{Fore.RED}Request Error for {ip}: {e}")
        except Exception as e:
            print(f"{Fore.RED}General Error for {ip}: {e}")
        finally:
            if os.path.exists(response_file):
                try:
                    os.remove(response_file)
                except OSError:
                    pass
            time.sleep(1)
            ip_queue.task_done()

# Fill queue
for ip in ip_addresses:
    ip_queue.put(ip)

# Launch threads
threads = []
for _ in range(thread_count):
    t = threading.Thread(target=process_ip)
    t.start()
    threads.append(t)

# Wait for all threads to finish
ip_queue.join()

print(f"\n{Fore.MAGENTA + Style.BRIGHT}Total Unique Domains: {len(all_domains)}{Style.RESET_ALL}")
print(f"{Fore.YELLOW}Total Skipped IPs (less than 2 domains): {skipped_count}")
if all_domains:
    print(f"{Fore.GREEN}Domains saved to {output_file}")
else:
    print(f"{Fore.RED}No domains found. Check IPs or website structure.")

print(f"\n{Fore.CYAN + Style.BRIGHT}Processing complete!{Style.RESET_ALL}")
